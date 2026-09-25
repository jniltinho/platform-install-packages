package config

import (
	"github.com/stretchr/testify/require"
	"testing"
)

func TestBasePathValidation(t *testing.T) {
	for _, p := range []string{"", "/console", "/apps/console-1"} {
		t.Run("valid"+p, func(t *testing.T) { require.NoError(t, ValidateBasePath(p)) })
	}
	for _, p := range []string{"/", "console", "//host", "/console/", "/../a", "/a%2fb", "/a?b", "/a\\b", "/<script>"} {
		t.Run("invalid"+p, func(t *testing.T) { require.Error(t, ValidateBasePath(p)) })
	}
}
func TestDeploymentEnv(t *testing.T) {
	t.Setenv("KCONSOLE_SERVER_BASE_PATH", "/console")
	t.Setenv("KCONSOLE_SERVER_HTTPS", "true")
	t.Setenv("KCONSOLE_SERVER_TLS_DIR", "/tmp/tls")
	c, err := Load(writeConfig(t, validTOML))
	require.NoError(t, err)
	require.NoError(t, c.Validate())
	require.Equal(t, "/console", c.Server.BasePath)
	require.True(t, c.Server.HTTPS)
	require.Equal(t, "/tmp/tls", c.Server.TLSDir)
}
