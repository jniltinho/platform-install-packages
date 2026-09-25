package config

import (
	"math"
	"testing"
	"time"

	"github.com/stretchr/testify/require"
)

func TestRejectUnsafeSettings(t *testing.T) {
	tests := map[string]func(*Config){
		"negative partner":        func(c *Config) { c.Kaltura.PartnerID = -1 },
		"negative port":           func(c *Config) { c.Server.Port = -1 },
		"overflow port":           func(c *Config) { c.Server.Port = 65536 },
		"negative idle":           func(c *Config) { c.Server.SessionTTL = -time.Second },
		"zero absolute":           func(c *Config) { c.Server.SessionMax = 0 },
		"zero HTTP":               func(c *Config) { c.Kaltura.HTTPTimeout = 0 },
		"negative connect":        func(c *Config) { c.Kaltura.ConnectTimeout = -1 },
		"negative upload timeout": func(c *Config) { c.Kaltura.UploadTimeout = -1 },
		"fractional KS expiry":    func(c *Config) { c.Kaltura.SessionExpiry = time.Millisecond },
		"file overflow":           func(c *Config) { c.Upload.MaxMB = math.MaxInt64 },
		"negative reserve":        func(c *Config) { c.Upload.MinFreeMB = -1 },
		"reserve overflow":        func(c *Config) { c.Upload.MinFreeMB = math.MaxInt64 },
		"concurrency allocation":  func(c *Config) { c.Upload.MaxConcurrent = math.MaxInt },
		"upload URL":              func(c *Config) { c.Kaltura.UploadServiceURL = "file:///tmp/a" },
		"upload userinfo":         func(c *Config) { c.Kaltura.UploadServiceURL = "https://secret:password@k/api_v3" },
		"service userinfo":        func(c *Config) { c.Kaltura.ServiceURL = "https://secret:password@k/api_v3" },
	}
	for name, mutate := range tests {
		t.Run(name, func(t *testing.T) {
			cfg, err := Load(writeConfig(t, validTOML))
			require.NoError(t, err)
			mutate(cfg)
			err = cfg.Validate()
			require.Error(t, err)
			require.NotContains(t, err.Error(), "password")
		})
	}
}

func TestRejectOverflowDuration(t *testing.T) {
	_, err := Load(writeConfig(t, validTOML+"\n[server]\nsession_ttl = \"999999999999999999999h\""))
	require.Error(t, err)
}

func TestIPv6ListenerAddress(t *testing.T) {
	require.Equal(t, "[::1]:8080", (ServerConfig{Host: "::1", Port: 8080}).Addr())
}
