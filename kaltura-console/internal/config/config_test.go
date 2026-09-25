package config

import (
	"os"
	"path/filepath"
	"testing"
	"time"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

const validTOML = `
[kaltura]
service_url = "http://kaltura.local/api_v3"
playback_host = "http://kaltura.local"
partner_id = 102
admin_secret = "s3cret-value"
`

func writeConfig(t *testing.T, body string) string {
	t.Helper()
	p := filepath.Join(t.TempDir(), "config.toml")
	require.NoError(t, os.WriteFile(p, []byte(body), 0o600))
	return p
}

func TestLoadDefaultsAndFile(t *testing.T) {
	cfg, err := Load(writeConfig(t, validTOML))
	require.NoError(t, err)
	assert.Equal(t, 102, cfg.Kaltura.PartnerID)
	assert.Equal(t, "sqlite", cfg.Database.Driver)
	assert.Equal(t, 8080, cfg.Server.Port)
	assert.Equal(t, 2*time.Hour, cfg.Server.SessionTTL)
	assert.Equal(t, []string{".mp4"}, cfg.Upload.AllowedExt)
	assert.Equal(t, cfg.Kaltura.ServiceURL, cfg.Kaltura.EffectiveUploadURL())
	assert.NoError(t, cfg.Validate())
}

func TestEnvOverridesFile(t *testing.T) {
	t.Setenv("KCONSOLE_KALTURA_PARTNER_ID", "555")
	t.Setenv("KCONSOLE_SERVER_PORT", "9999")
	cfg, err := Load(writeConfig(t, validTOML))
	require.NoError(t, err)
	assert.Equal(t, 555, cfg.Kaltura.PartnerID)
	assert.Equal(t, 9999, cfg.Server.Port)
}

func TestValidateNeverLeaksSecret(t *testing.T) {
	tests := []struct {
		name    string
		body    string
		wantErr string
	}{
		{"missing secret", `[kaltura]
service_url = "http://k/api_v3"
playback_host = "http://k"
partner_id = 1`, "kaltura.admin_secret is required"},
		{"missing partner", `[kaltura]
service_url = "http://k/api_v3"
playback_host = "http://k"
admin_secret = "abc"`, "kaltura.partner_id is required"},
		{"bad url", `[kaltura]
service_url = "k/api_v3"
playback_host = "http://k"
partner_id = 1
admin_secret = "topsecret"`, "kaltura.service_url must be an absolute http(s) URL"},
		{"bad driver", validTOML + `
[database]
driver = "postgres"`, "database.driver must be sqlite or mysql"},
		{"https incomplete pair", validTOML + `
[server]
https = true
tls_cert = "cert.pem"`, "server.https requires"},
	}
	for _, tc := range tests {
		t.Run(tc.name, func(t *testing.T) {
			cfg, err := Load(writeConfig(t, tc.body))
			require.NoError(t, err)
			err = cfg.Validate()
			require.Error(t, err)
			assert.Contains(t, err.Error(), tc.wantErr)
			assert.NotContains(t, err.Error(), "topsecret")
		})
	}
}

func TestExplicitMissingFileIsError(t *testing.T) {
	_, err := Load(filepath.Join(t.TempDir(), "nope.toml"))
	assert.Error(t, err)
}
