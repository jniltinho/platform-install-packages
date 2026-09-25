package server

import (
	"context"
	"encoding/json"
	"io"
	"net/http"
	"net/http/httptest"
	"net/url"
	"strings"
	"testing"
	"time"

	"github.com/stretchr/testify/require"
)

// proxyFixture serves ownership checks independently of delivery behavior.
func proxyFixture(t *testing.T, delivery http.HandlerFunc) (*httptest.Server, harness) {
	t.Helper()
	upstream := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		if r.Method != http.MethodPost {
			delivery(w, r)
			return
		}
		if err := r.ParseForm(); err != nil {
			t.Error(err)
			return
		}
		if r.Form.Get("service") == "flavorAsset" {
			require.NoError(t, json.NewEncoder(w).Encode(map[string]any{"objects": []map[string]any{{
				"id": "0_ijklmnop", "entryId": "0_abcdefgh", "status": 2, "fileExt": "mp4", "videoCodecId": "avc1", "width": 1920, "height": 1080,
			}}}))
			return
		}
		var reply any = map[string]any{"id": "0_abcdefgh", "partnerId": 102}
		if r.Form.Get("service") == "session" {
			reply = "test-ks"
		}
		if err := json.NewEncoder(w).Encode(reply); err != nil {
			t.Error(err)
		}
	}))
	t.Cleanup(upstream.Close)
	h := setup(t, upstream.URL, "viewer")
	front := httptest.NewServer(h.e)
	t.Cleanup(front.Close)
	return front, h
}

func proxyRequest(t *testing.T, ctx context.Context, front *httptest.Server, h harness) *http.Request {
	t.Helper()
	r, err := http.NewRequestWithContext(ctx, "GET", front.URL+"/media/0_abcdefgh/stream", nil)
	require.NoError(t, err)
	r.AddCookie(h.cookie)
	r.Header.Set("Range", "bytes=0-2")
	return r
}

func TestProxyAllowedRedirect(t *testing.T) {
	destination := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		if r.Header.Get("Cookie") != "" || r.Header.Get("Authorization") != "" {
			t.Error("credentials relayed")
		}
		if r.Header.Get("Range") != "bytes=0-2" {
			t.Error("range not relayed")
		}
		w.Header().Set("Content-Range", "bytes 0-2/10")
		w.WriteHeader(http.StatusPartialContent)
		if _, err := io.WriteString(w, "abc"); err != nil {
			t.Error(err)
		}
	}))
	defer destination.Close()
	front, h := proxyFixture(t, func(w http.ResponseWriter, r *http.Request) {
		http.Redirect(w, r, destination.URL+"/video", http.StatusFound)
	})
	u, err := url.Parse(destination.URL)
	require.NoError(t, err)
	h.s.cfg.Kaltura.ExtraMediaHosts = []string{u.Host}
	resp, err := front.Client().Do(proxyRequest(t, context.Background(), front, h))
	require.NoError(t, err)
	defer func() { require.NoError(t, resp.Body.Close()) }()
	body, err := io.ReadAll(resp.Body)
	require.NoError(t, err)
	require.Equal(t, http.StatusPartialContent, resp.StatusCode)
	require.Equal(t, "abc", string(body))
	require.Equal(t, "bytes 0-2/10", resp.Header.Get("Content-Range"))
}

func TestProxyFailureBeforeHeaders(t *testing.T) {
	front, h := proxyFixture(t, func(w http.ResponseWriter, _ *http.Request) {
		conn, _, err := w.(http.Hijacker).Hijack()
		if err != nil {
			t.Error(err)
			return
		}
		if err := conn.Close(); err != nil {
			t.Error(err)
		}
	})
	resp, err := front.Client().Do(proxyRequest(t, context.Background(), front, h))
	require.NoError(t, err)
	defer func() { require.NoError(t, resp.Body.Close()) }()
	require.Equal(t, http.StatusBadGateway, resp.StatusCode)
	body, err := io.ReadAll(resp.Body)
	require.NoError(t, err)
	require.Contains(t, string(body), "falha ao buscar")
}

func TestProxyFailureAfterHeadersAbortsBody(t *testing.T) {
	front, h := proxyFixture(t, func(w http.ResponseWriter, _ *http.Request) {
		w.Header().Set("Content-Length", "100000")
		w.Header().Set("Content-Type", "video/mp4")
		if _, err := io.WriteString(w, strings.Repeat("x", 32768)); err != nil {
			t.Error(err)
			return
		}
		w.(http.Flusher).Flush()
		panic(http.ErrAbortHandler)
	})
	resp, err := front.Client().Do(proxyRequest(t, context.Background(), front, h))
	// If the proxy detects truncation before flushing, the whole connection aborts.
	if err != nil {
		return
	}
	defer func() { require.NoError(t, resp.Body.Close()) }()
	require.Equal(t, http.StatusOK, resp.StatusCode)
	body, err := io.ReadAll(resp.Body)
	require.Error(t, err, "a truncated upstream must not look like a complete success")
	require.Less(t, len(body), 100000)
	require.NotContains(t, string(body), "message")
}

func TestProxyClientDisconnectCancelsUpstream(t *testing.T) {
	stopped := make(chan struct{})
	release := make(chan struct{})
	defer close(release)
	front, h := proxyFixture(t, func(w http.ResponseWriter, r *http.Request) {
		if _, err := io.WriteString(w, strings.Repeat("x", 65536)); err != nil {
			return
		}
		w.(http.Flusher).Flush()
		select {
		case <-r.Context().Done():
			close(stopped)
		case <-release:
		}
	})
	ctx, cancel := context.WithCancel(context.Background())
	defer cancel()
	resp, err := front.Client().Do(proxyRequest(t, ctx, front, h))
	require.NoError(t, err)
	buffer := make([]byte, 1)
	_, err = resp.Body.Read(buffer)
	require.NoError(t, err)
	cancel()
	require.NoError(t, resp.Body.Close())
	select {
	case <-stopped:
	case <-time.After(5 * time.Second):
		t.Fatal("upstream was not canceled when browser disconnected")
	}
}

func TestProxyFlavorSelectionFailure(t *testing.T) {
	for _, tt := range []struct{ name, reply string }{
		{"no compatible flavor", `{"objects":[]}`},
		{"listing failure", `{"objectType":"KalturaAPIException","code":"SERVICE_FORBIDDEN","message":"private detail"}`},
		{"other entry flavor", `{"objects":[{"id":"0_ijklmnop","entryId":"0_wrongone","status":2,"fileExt":"mp4","videoCodecId":"avc1","width":1920,"height":1080}]}`},
	} {
		t.Run(tt.name, func(t *testing.T) {
			up := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
				require.Equal(t, http.MethodPost, r.Method, "must never contact delivery")
				require.NoError(t, r.ParseForm())
				reply := `{"id":"0_abcdefgh","partnerId":102}`
				switch r.Form.Get("service") {
				case "session":
					reply = `"test-ks"`
				case "flavorAsset":
					reply = tt.reply
				}
				_, err := io.WriteString(w, reply)
				require.NoError(t, err)
			}))
			defer up.Close()
			h := setup(t, up.URL, "viewer")
			w := h.request("GET", "/media/0_abcdefgh/stream", "", true, false)
			require.Equal(t, 502, w.Code)
			require.NotContains(t, w.Body.String(), "private detail")
		})
	}
}
