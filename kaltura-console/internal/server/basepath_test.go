package server

import (
	"encoding/json"
	"net/http/httptest"
	"strings"
	"testing"
	"testing/fstest"

	"github.com/stretchr/testify/require"
	"kaltura-console/internal/kaltura"
)

func TestPrefixedRoutesAndTrustedProxy(t *testing.T) {
	h := setup(t, "http://127.0.0.1:1", "admin")
	h.s.cfg.Server.BasePath = "/console"
	h.s.cfg.Server.TrustedProxies = []string{"127.0.0.1/32"}
	dist := fstest.MapFS{"index.html": {Data: []byte(`<html><head></head><body><script src="./assets/app.js"></script></body></html>`)}, "assets/app.js": {Data: []byte("asset")}}
	e, s, err := New(h.s.cfg, h.s.db, h.s.auth, h.s.kc, dist)
	require.NoError(t, err)
	h.e = e
	h.s = s
	for _, tt := range []struct {
		name, path string
		code       int
	}{
		{"health", "/console/healthz", 200}, {"root isolated", "/healthz", 404},
		{"api isolated", "/api/session", 404}, {"login", "/console/login", 200},
		{"asset", "/console/assets/app.js", 200}, {"missing asset", "/console/assets/absent.js", 404},
		{"canonical", "/console", 308}, {"outside prefix", "/console-other", 404},
		{"deep link", "/console/media/0_abcd", 303}, {"unknown api", "/console/api/absent", 404},
	} {
		t.Run(tt.name, func(t *testing.T) {
			w := h.request("GET", tt.path, "", false, false)
			require.Equal(t, tt.code, w.Code, w.Body.String())
		})
	}
	w := h.request("GET", "/console/login", "", false, false)
	require.Contains(t, w.Body.String(), `<base href="/console/">`)
	w = h.request("GET", "/console/media/0_abcd?q=a", "", false, false)
	require.Equal(t, "/console/login?return=%2Fmedia%2F0_abcd%3Fq%3Da", w.Header().Get("Location"))
	for _, tt := range []struct {
		name, remote string
		secure       bool
	}{{"trusted", "127.0.0.1:5000", true}, {"untrusted", "192.0.2.10:5000", false}} {
		t.Run(tt.name, func(t *testing.T) {
			r := httptest.NewRequest("POST", "http://console.test/console/api/login", strings.NewReader(`{"email":"test@example.test","password":"password-test"}`))
			r.RemoteAddr = tt.remote
			r.Header.Set("Content-Type", "application/json")
			r.Header.Set("X-Forwarded-Proto", "https")
			origin := "http://console.test"
			if tt.secure {
				origin = "https://console.test"
			}
			r.Header.Set("Origin", origin)
			w := httptest.NewRecorder()
			e.ServeHTTP(w, r)
			require.Equal(t, 200, w.Code, w.Body.String())
			cookie := w.Result().Cookies()[0]
			require.Equal(t, "/console", cookie.Path)
			require.Equal(t, tt.secure, cookie.Secure)
			require.Equal(t, "private, no-store", w.Header().Get("Cache-Control"))
			var sess sessionView
			require.NoError(t, json.Unmarshal(w.Body.Bytes(), &sess))
			h.cookie = cookie
			h.csrf = sess.CSRF
			require.Equal(t, 200, h.request("GET", "/console/api/session", "", true, false).Code)
			require.Equal(t, 403, h.request("POST", "/console/api/logout", "", true, false).Code)
			logout := h.request("POST", "/console/api/logout", "", true, true)
			require.Equal(t, 204, logout.Code)
			require.Equal(t, "/console", logout.Result().Cookies()[0].Path)
		})
	}
	view := s.viewEntry(&kaltura.Entry{ID: "0_abcd"})
	require.Equal(t, "/console/media/0_abcd/stream", view.Playback)
	require.Equal(t, "/console/media/0_abcd/thumbnail", view.Thumbnail)
}
