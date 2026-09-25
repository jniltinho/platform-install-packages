package tlsconfig

import (
	"crypto/tls"
	"crypto/x509"
	"io"
	"net/http"
	"net/http/httptest"
	"os"
	"path/filepath"
	"testing"
	"time"

	"github.com/stretchr/testify/require"
)

func TestSelfSignedReuseAndHTTPS(t *testing.T) {
	dir := t.TempDir()
	require.NoError(t, os.Chmod(dir, 0o700))
	cfg, err := Prepare("", "", dir, "console.test")
	require.NoError(t, err)
	info, err := os.Stat(filepath.Join(dir, "key.pem"))
	require.NoError(t, err)
	require.Equal(t, os.FileMode(0o600), info.Mode().Perm())
	cert, err := x509.ParseCertificate(cfg.Certificates[0].Certificate[0])
	require.NoError(t, err)
	require.NoError(t, cert.VerifyHostname("console.test"))
	require.NoError(t, cert.VerifyHostname("127.0.0.1"))
	require.Greater(t, time.Until(cert.NotAfter), 9*365*24*time.Hour)
	again, err := Prepare("", "", dir, "console.test")
	require.NoError(t, err)
	require.Equal(t, cfg.Certificates[0].Certificate, again.Certificates[0].Certificate)
	require.Equal(t, uint16(tls.VersionTLS12), cfg.MinVersion)
	s := httptest.NewUnstartedServer(http.HandlerFunc(func(w http.ResponseWriter, _ *http.Request) { _, _ = io.WriteString(w, "ok") }))
	s.TLS = cfg
	s.StartTLS()
	defer s.Close()
	pool := x509.NewCertPool()
	pool.AddCert(cert)
	client := &http.Client{Transport: &http.Transport{TLSClientConfig: &tls.Config{RootCAs: pool, MinVersion: tls.VersionTLS12}}}
	defer client.CloseIdleConnections()
	resp, err := client.Get(s.URL)
	require.NoError(t, err)
	defer func() { require.NoError(t, resp.Body.Close()) }()
	require.Equal(t, 200, resp.StatusCode)
	_, err = Prepare(filepath.Join(dir, "cert.pem"), filepath.Join(dir, "key.pem"), "", "")
	require.NoError(t, err)
}
func TestRefusePartialAndUnsafeMaterial(t *testing.T) {
	for _, name := range []string{"partial", "invalid", "symlink", "permissions"} {
		t.Run(name, func(t *testing.T) {
			dir := t.TempDir()
			require.NoError(t, os.Chmod(dir, 0o700))
			key := filepath.Join(dir, "key.pem")
			switch name {
			case "partial":
				require.NoError(t, os.WriteFile(key, []byte("keep"), 0o600))
			case "invalid":
				require.NoError(t, os.WriteFile(key, []byte("keep"), 0o600))
				require.NoError(t, os.WriteFile(filepath.Join(dir, "cert.pem"), []byte("bad"), 0o644))
			default:
				_, err := Prepare("", "", dir, "")
				require.NoError(t, err)
				if name == "permissions" {
					require.NoError(t, os.Chmod(key, 0o644))
				} else {
					require.NoError(t, os.Rename(key, key+".original"))
					require.NoError(t, os.Symlink(key+".original", key))
				}
			}
			before, err := os.ReadFile(key)
			require.NoError(t, err)
			_, err = Prepare("", "", dir, "")
			require.Error(t, err)
			after, err := os.ReadFile(key)
			require.NoError(t, err)
			require.Equal(t, before, after)
		})
	}
	_, err := Prepare("cert", "", "", "")
	require.Error(t, err)
	_, err = Prepare("", "", "", "")
	require.Error(t, err)
}
