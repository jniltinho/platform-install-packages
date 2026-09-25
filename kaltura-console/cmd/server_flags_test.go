package cmd

import (
	"github.com/stretchr/testify/require"
	"kaltura-console/internal/config"
	"testing"
)

func TestServerFlagsOverrideOnlyWhenProvided(t *testing.T) {
	root := newRoot()
	cmd, _, err := root.Find([]string{"serve"})
	require.NoError(t, err)
	cfg := config.ServerConfig{HTTPS: true, TLSCert: "original.pem", TLSKey: "original.key", TLSDir: "/state/tls", BasePath: "/old"}
	applyServerFlags(cmd, &cfg)
	require.Equal(t, "/old", cfg.BasePath)
	require.True(t, cfg.HTTPS)
	require.NoError(t, cmd.Flags().Set("https", "false"))
	require.NoError(t, cmd.Flags().Set("base-path", "/console"))
	require.NoError(t, cmd.Flags().Set("tls-cert", "new.pem"))
	require.NoError(t, cmd.Flags().Set("tls-key", "new.key"))
	require.NoError(t, cmd.Flags().Set("tls-dir", "/new/tls"))
	applyServerFlags(cmd, &cfg)
	require.False(t, cfg.HTTPS)
	require.Equal(t, "/console", cfg.BasePath)
	require.Equal(t, "new.pem", cfg.TLSCert)
	require.Equal(t, "new.key", cfg.TLSKey)
	require.Equal(t, "/new/tls", cfg.TLSDir)
}
