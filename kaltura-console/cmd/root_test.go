package cmd

import (
	"bytes"
	"github.com/stretchr/testify/require"
	"os"
	"path/filepath"
	"testing"
)

func TestVersionDoesNotLoadConfig(t *testing.T) {
	c := newRoot()
	var out bytes.Buffer
	c.SetOut(&out)
	c.SetArgs([]string{"--config", "/missing", "version"})
	require.NoError(t, c.Execute())
	require.Contains(t, out.String(), "commit=")
}

func TestConfigInitDoesNotOverwrite(t *testing.T) {
	path := filepath.Join(t.TempDir(), "config.toml")
	for i := range 2 {
		c := newRoot()
		c.SetArgs([]string{"config", "init", "--output", path})
		if i == 0 {
			require.NoError(t, c.Execute())
		} else {
			require.Error(t, c.Execute())
		}
	}
	info, err := os.Stat(path)
	require.NoError(t, err)
	require.Equal(t, os.FileMode(0o600), info.Mode().Perm())
}
