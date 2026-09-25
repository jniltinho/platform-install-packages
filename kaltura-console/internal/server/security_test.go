package server

import (
	"crypto/tls"
	"fmt"
	"net"
	"net/http/httptest"
	"testing"

	"github.com/stretchr/testify/require"
)

func TestOriginUsesTrustedScheme(t *testing.T) {
	_, trusted, err := net.ParseCIDR("127.0.0.0/8")
	require.NoError(t, err)
	s := &Server{trusted: []*net.IPNet{trusted}}
	for _, tc := range []struct {
		name, origin, peer, forwarded string
		tls, want                     bool
	}{
		{"plain same", "http://console.test", "192.0.2.1:123", "", false, true},
		{"wrong scheme", "https://console.test", "192.0.2.1:123", "", false, false},
		{"TLS same", "https://console.test", "192.0.2.1:123", "", true, true},
		{"TLS downgrade", "http://console.test", "192.0.2.1:123", "", true, false},
		{"trusted proxy", "https://console.test", "127.0.0.1:123", "https", false, true},
		{"untrusted proxy", "https://console.test", "192.0.2.1:123", "https", false, false},
		{"different host", "http://evil.test", "192.0.2.1:123", "", false, false},
		{"userinfo", "http://user@console.test", "192.0.2.1:123", "", false, false},
		{"opaque null", "null", "192.0.2.1:123", "", false, false},
		{"path", "http://console.test/path", "192.0.2.1:123", "", false, false},
		{"missing", "", "192.0.2.1:123", "", false, true},
	} {
		t.Run(tc.name, func(t *testing.T) {
			r := httptest.NewRequest("POST", "http://console.test/api/login", nil)
			r.RemoteAddr = tc.peer
			r.Header.Set("Origin", tc.origin)
			r.Header.Set("X-Forwarded-Proto", tc.forwarded)
			if tc.tls {
				r.TLS = &tls.ConnectionState{}
			}
			require.Equal(t, tc.want, s.sameOrigin(r))
		})
	}
}

func TestAPIResponsesAreNotCached(t *testing.T) {
	h := setup(t, "http://127.0.0.1:1", "viewer")
	for _, path := range []string{"/api/session", "/api/version", "/api/missing"} {
		for _, authenticated := range []bool{false, true} {
			w := h.request("GET", path, "", authenticated, false)
			require.Equal(t, "private, no-store", w.Header().Get("Cache-Control"))
		}
	}
}

func TestRejectedUserPatchPreservesPasswordAndSession(t *testing.T) {
	h := setup(t, "http://127.0.0.1:1", "admin")
	user, err := h.s.auth.GetUserByEmail("test@example.test")
	require.NoError(t, err)
	w := h.request("PATCH", fmt.Sprintf("/api/users/%d", user.ID),
		`{"name":"Changed","role":"viewer","password":"changed-password"}`, true, true)
	require.Equal(t, 409, w.Code, w.Body.String())
	unchanged, err := h.s.auth.GetUser(user.ID)
	require.NoError(t, err)
	require.Equal(t, user.PasswordHash, unchanged.PasswordHash)
	require.Equal(t, user.Name, unchanged.Name)
	require.Equal(t, 200, h.request("GET", "/api/session", "", true, false).Code)
}
