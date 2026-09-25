package config

import (
	"github.com/stretchr/testify/require"
	"os"
	"path/filepath"
	"testing"
)

func TestEnvKeysAbsentFromFile(t *testing.T) {
	t.Setenv("KCONSOLE_KALTURA_ADMIN_SECRET", "environment-secret")
	t.Setenv("KCONSOLE_KALTURA_PARTNER_ID", "102")
	t.Setenv("KCONSOLE_KALTURA_SERVICE_URL", "http://example.test/api_v3")
	t.Setenv("KCONSOLE_KALTURA_PLAYBACK_HOST", "http://example.test")
	cfg, err := Load(writeConfig(t, ""))
	require.NoError(t, err)
	require.NoError(t, cfg.Validate())
	require.Equal(t, "environment-secret", cfg.Kaltura.AdminSecret)
}

func TestConfigSearchAndExplicitPrecedence(t *testing.T) {
	dir := t.TempDir()
	t.Chdir(dir)
	require.NoError(t, os.WriteFile(filepath.Join(dir, "config.toml"), []byte(validTOML), 0o600))
	cfg, err := Load("")
	require.NoError(t, err)
	require.Equal(t, 102, cfg.Kaltura.PartnerID)
	cfg, err = Load(writeConfig(t, "[server]\nport=9001"))
	require.NoError(t, err)
	require.Equal(t, 9001, cfg.Server.Port)
	require.Zero(t, cfg.Kaltura.PartnerID)
}
