package server

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io"
	"mime/multipart"
	"net/http"
	"net/http/httptest"
	"os"
	"path/filepath"
	"strings"
	"testing"
	"testing/fstest"
	"time"

	"github.com/labstack/echo/v5"
	"github.com/stretchr/testify/require"
	"kaltura-console/internal/auth"
	"kaltura-console/internal/config"
	"kaltura-console/internal/database"
	"kaltura-console/internal/kaltura"
)

type harness struct {
	e      *echo.Echo
	s      *Server
	cookie *http.Cookie
	csrf   string
}

func setup(t *testing.T, upstream string, role string) harness {
	t.Helper()
	cfg, err := config.Load("")
	require.NoError(t, err)
	cfg.Database.DSN = filepath.Join(t.TempDir(), "test.db")
	cfg.Upload.TmpDir = t.TempDir()
	cfg.Upload.MinFreeMB = 0
	cfg.Upload.MaxMB = 1
	cfg.Kaltura.ServiceURL, cfg.Kaltura.PlaybackHost = upstream, upstream
	cfg.Kaltura.PartnerID = 102
	db, err := database.Open(cfg.Database)
	require.NoError(t, err)
	require.NoError(t, database.Migrate(db))
	sqlDB, err := db.DB()
	require.NoError(t, err)
	t.Cleanup(func() { require.NoError(t, sqlDB.Close()) })
	svc := auth.NewService(db, time.Hour, time.Hour)
	_, err = svc.CreateUser("Test", "test@example.test", "password-test", role)
	require.NoError(t, err)
	kc := kaltura.NewClient(kaltura.Config{ServiceURL: upstream, PlaybackHost: upstream, PartnerID: 102})
	t.Cleanup(kc.HTTP().CloseIdleConnections)
	e, s, err := New(cfg, db, svc, kc, fstest.MapFS{"index.html": &fstest.MapFile{Data: []byte("<html>console</html>")}})
	require.NoError(t, err)
	r := httptest.NewRequest("POST", "/api/login", strings.NewReader(`{"email":"test@example.test","password":"password-test"}`))
	r.Header.Set("Content-Type", "application/json")
	w := httptest.NewRecorder()
	e.ServeHTTP(w, r)
	require.Equal(t, 200, w.Code, w.Body.String())
	require.Equal(t, "private, no-store", w.Header().Get("Cache-Control"))
	var view sessionView
	require.NoError(t, json.Unmarshal(w.Body.Bytes(), &view))
	return harness{e, s, w.Result().Cookies()[0], view.CSRF}
}

func (h harness) request(method, target, body string, authenticated, csrf bool) *httptest.ResponseRecorder {
	r := httptest.NewRequest(method, target, strings.NewReader(body))
	r.Header.Set("Content-Type", "application/json")
	if authenticated {
		r.AddCookie(h.cookie)
	}
	if csrf {
		r.Header.Set(csrfHeader, h.csrf)
	}
	w := httptest.NewRecorder()
	h.e.ServeHTTP(w, r)
	return w
}

func TestAuthorizationAndSPA(t *testing.T) {
	h := setup(t, "http://127.0.0.1:1", "viewer")
	tests := []struct {
		name, method, path string
		auth, csrf         bool
		status             int
	}{
		{"anonymous API", "GET", "/api/media", false, false, 401},
		{"anonymous version", "GET", "/api/version", false, false, 401},
		{"csrf", "DELETE", "/api/media/0_abcdefgh", true, false, 403},
		{"viewer mutation", "DELETE", "/api/media/0_abcdefgh", true, true, 403},
		{"viewer upload", "POST", "/api/media", true, true, 403},
		{"viewer users", "GET", "/api/users", true, false, 403},
		{"private page", "GET", "/media/0_abcdefgh", false, false, 303},
		{"login page", "GET", "/login", false, false, 200},
		{"private SPA", "GET", "/dashboard", true, false, 200},
		{"missing API", "GET", "/api/missing", true, false, 404},
		{"missing asset", "GET", "/assets/missing.js", false, false, 404},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			require.Equal(t, tt.status, h.request(tt.method, tt.path, "", tt.auth, tt.csrf).Code)
		})
	}
	require.Equal(t, 204, h.request("POST", "/api/logout", "", true, true).Code)
	require.Equal(t, 401, h.request("GET", "/api/session", "", true, false).Code)
}

func TestProxyMatrix(t *testing.T) {
	for _, status := range []int{200, 206, 416} {
		for _, method := range []string{"GET", "HEAD"} {
			t.Run(fmt.Sprintf("%s-%d", method, status), func(t *testing.T) {
				upstream := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
					if r.Method == "POST" {
						require.NoError(t, r.ParseForm())
						if r.Form.Get("service") == "session" {
							if _, err := fmt.Fprint(w, `"ks-test"`); err != nil {
								t.Errorf("writing fake response: %v", err)
							}
							return
						}
						if r.Form.Get("service") == "flavorAsset" {
							_, err := fmt.Fprint(w, `{"objects":[{"id":"0_ijklmnop","entryId":"0_abcdefgh","status":2,"fileExt":"mp4","videoCodecId":"avc1","width":1920,"height":1080}]}`)
							require.NoError(t, err)
							return
						}
						if _, err := fmt.Fprint(w, `{"id":"0_abcdefgh","partnerId":102}`); err != nil {
							t.Errorf("writing fake response: %v", err)
						}
						return
					}
					require.Empty(t, r.Header.Get("Cookie"))
					require.Empty(t, r.Header.Get("Authorization"))
					require.Equal(t, "bytes=1-2", r.Header.Get("Range"))
					require.Contains(t, r.URL.Path, "/flavorIds/0_ijklmnop/")
					w.Header().Set("Content-Type", "video/mp4")
					w.Header().Set("Cache-Control", "public, max-age=3600")
					w.Header().Set("Content-Range", "bytes 1-2/3")
					w.Header().Set("Content-Length", "2")
					w.WriteHeader(status)
					if r.Method != "HEAD" {
						if _, err := fmt.Fprint(w, "ab"); err != nil {
							t.Errorf("writing fake response: %v", err)
						}
					}
				}))
				defer upstream.Close()
				h := setup(t, upstream.URL, "viewer")
				front := httptest.NewServer(h.e)
				defer front.Close()
				r, err := http.NewRequest(method, front.URL+"/media/0_abcdefgh/stream", nil)
				require.NoError(t, err)
				r.AddCookie(h.cookie)
				r.Header.Set("Range", "bytes=1-2")
				resp, err := front.Client().Do(r)
				require.NoError(t, err)
				defer func() { require.NoError(t, resp.Body.Close()) }()
				require.Equal(t, status, resp.StatusCode)
				require.Equal(t, "private, no-store", resp.Header.Get("Cache-Control"))
				body, err := io.ReadAll(resp.Body)
				require.NoError(t, err)
				if method == "GET" {
					require.Equal(t, "ab", string(body))
				} else {
					require.Empty(t, body)
				}
				require.Equal(t, "bytes 1-2/3", resp.Header.Get("Content-Range"))
			})
		}
	}
}

func TestProxyRejectsRedirect(t *testing.T) {
	contacted := false
	forbidden := httptest.NewServer(http.HandlerFunc(func(http.ResponseWriter, *http.Request) { contacted = true }))
	defer forbidden.Close()
	upstream := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		if r.Method == "POST" {
			require.NoError(t, r.ParseForm())
			if r.Form.Get("service") == "session" {
				if _, err := fmt.Fprint(w, `"ks"`); err != nil {
					t.Errorf("writing fake response: %v", err)
				}
				return
			}
			if _, err := fmt.Fprint(w, `{"id":"0_abcdefgh","partnerId":102}`); err != nil {
				t.Errorf("writing fake response: %v", err)
			}
			return
		}
		http.Redirect(w, r, forbidden.URL, http.StatusFound)
	}))
	defer upstream.Close()
	h := setup(t, upstream.URL, "viewer")
	require.Equal(t, 502, h.request("GET", "/media/0_abcdefgh/stream", "", true, false).Code)
	require.False(t, contacted)
}

func TestUploadValidationAndCleanup(t *testing.T) {
	h := setup(t, "http://127.0.0.1:1", "admin")
	for _, test := range []struct {
		name, filename, data string
		status               int
	}{
		{"invalid extension", "test.exe", "anything", 422},
		{"invalid container", "test.mp4", "not a video", 422},
		{"oversize", "test.mp4", strings.Repeat("x", (1<<20)+1), 413},
	} {
		t.Run(test.name, func(t *testing.T) {
			var body bytes.Buffer
			mw := multipart.NewWriter(&body)
			require.NoError(t, mw.WriteField("name", "Test"))
			f, err := mw.CreateFormFile("file", test.filename)
			require.NoError(t, err)
			_, err = io.WriteString(f, test.data)
			require.NoError(t, err)
			require.NoError(t, mw.Close())
			r := httptest.NewRequest("POST", "/api/media", &body)
			r.Header.Set("Content-Type", mw.FormDataContentType())
			r.Header.Set(csrfHeader, h.csrf)
			r.AddCookie(h.cookie)
			w := httptest.NewRecorder()
			h.e.ServeHTTP(w, r)
			require.Equal(t, test.status, w.Code, w.Body.String())
			files, err := os.ReadDir(h.s.cfg.Upload.TmpDir)
			require.NoError(t, err)
			require.Empty(t, files)
		})
	}
	for range cap(h.s.uploads) {
		h.s.uploads <- struct{}{}
	}
	require.Equal(t, 429, h.request("POST", "/api/media", "", true, true).Code)
}
