// Package config loads kaltura-console settings from config.toml via Viper.
//
// Precedence: KCONSOLE_* environment variables (e.g. KCONSOLE_KALTURA_ADMIN_SECRET)
// override file values, which override the built-in defaults.
// File search order: --config path → ./config.toml → /etc/kaltura-console/config.toml.
package config

import (
	"errors"
	"fmt"
	"log/slog"
	"math"
	"net"
	"net/url"
	"regexp"
	"strconv"
	"strings"
	"time"

	"github.com/spf13/viper"
)

// Config is the root configuration object.
type Config struct {
	Server   ServerConfig   `mapstructure:"server"`
	Database DatabaseConfig `mapstructure:"database"`
	Kaltura  KalturaConfig  `mapstructure:"kaltura"`
	Upload   UploadConfig   `mapstructure:"upload"`
	Log      LogConfig      `mapstructure:"log"`
	// ConfigFile is the file actually read (empty when running on defaults/env only).
	ConfigFile string `mapstructure:"-"`
}

// ServerConfig holds HTTP listener and session settings.
type ServerConfig struct {
	Host     string `mapstructure:"host"`
	Port     int    `mapstructure:"port"`
	HTTPS    bool   `mapstructure:"https"`
	TLSCert  string `mapstructure:"tls_cert"`
	TLSKey   string `mapstructure:"tls_key"`
	TLSDir   string `mapstructure:"tls_dir"`
	BasePath string `mapstructure:"base_path"`
	// TrustedProxies lists CIDRs allowed to set X-Forwarded-For/-Proto.
	TrustedProxies []string `mapstructure:"trusted_proxies"`
	// SessionTTL is the idle timeout of a session.
	SessionTTL time.Duration `mapstructure:"session_ttl"`
	// SessionMax is the absolute lifetime of a session (without "remember me").
	SessionMax time.Duration `mapstructure:"session_max"`
}

// DatabaseConfig selects the console database (users and sessions only).
type DatabaseConfig struct {
	// Driver is "sqlite" (default) or "mysql" (MariaDB/MySQL).
	Driver string `mapstructure:"driver"`
	// DSN is a file path for sqlite or a go-sql-driver DSN for mysql.
	DSN   string `mapstructure:"dsn"`
	Debug bool   `mapstructure:"debug"`
}

// KalturaConfig describes the Kaltura partner the console manages.
type KalturaConfig struct {
	// ServiceURL is the api_v3 base, e.g. http://kaltura.local/api_v3.
	ServiceURL string `mapstructure:"service_url"`
	// UploadServiceURL overrides ServiceURL for uploadToken.upload (empty = ServiceURL).
	UploadServiceURL string `mapstructure:"upload_service_url"`
	PartnerID        int    `mapstructure:"partner_id"`
	AdminSecret      string `mapstructure:"admin_secret"`
	UserID           string `mapstructure:"user_id"`
	// SessionExpiry is the lifetime requested for the admin KS.
	SessionExpiry time.Duration `mapstructure:"session_expiry"`
	// PlaybackHost is the delivery base, e.g. http://kaltura.local.
	PlaybackHost string `mapstructure:"playback_host"`
	// ExtraMediaHosts are additional host[:port] values the media proxy may follow redirects to.
	ExtraMediaHosts []string      `mapstructure:"extra_media_hosts"`
	HTTPTimeout     time.Duration `mapstructure:"http_timeout"`
	ConnectTimeout  time.Duration `mapstructure:"connect_timeout"`
	UploadTimeout   time.Duration `mapstructure:"upload_timeout"`
}

// UploadConfig bounds browser uploads staged on disk before going to Kaltura.
type UploadConfig struct {
	TmpDir        string   `mapstructure:"tmp_dir"`
	MaxMB         int64    `mapstructure:"max_mb"`
	MaxConcurrent int      `mapstructure:"max_concurrent"`
	MinFreeMB     int64    `mapstructure:"min_free_mb"`
	AllowedExt    []string `mapstructure:"allowed_ext"`
}

// LogConfig controls the slog level (debug, info, warn, error).
type LogConfig struct {
	Level string `mapstructure:"level"`
}

// Slog maps the configured level to a slog.Level (info when unknown).
func (l LogConfig) Slog() slog.Level {
	switch strings.ToLower(l.Level) {
	case "debug":
		return slog.LevelDebug
	case "warn", "warning":
		return slog.LevelWarn
	case "error":
		return slog.LevelError
	default:
		return slog.LevelInfo
	}
}

// Addr returns host:port for the listener.
func (s ServerConfig) Addr() string { return net.JoinHostPort(s.Host, strconv.Itoa(s.Port)) }

// EffectiveUploadURL returns the api_v3 URL used for uploads.
func (k KalturaConfig) EffectiveUploadURL() string {
	if k.UploadServiceURL != "" {
		return k.UploadServiceURL
	}
	return k.ServiceURL
}

func setDefaults(v *viper.Viper) {
	v.SetDefault("server.host", "0.0.0.0")
	v.SetDefault("server.port", 8080)
	v.SetDefault("server.https", false)
	v.SetDefault("server.base_path", "")
	v.SetDefault("server.tls_dir", "/var/lib/kaltura-console/tls")
	v.SetDefault("server.trusted_proxies", []string{})
	v.SetDefault("server.session_ttl", "2h")
	v.SetDefault("server.session_max", "12h")
	v.SetDefault("database.driver", "sqlite")
	v.SetDefault("database.dsn", "/var/lib/kaltura-console/console.db")
	v.SetDefault("kaltura.user_id", "kaltura-console")
	v.SetDefault("kaltura.session_expiry", "24h")
	v.SetDefault("kaltura.http_timeout", "15s")
	v.SetDefault("kaltura.connect_timeout", "5s")
	v.SetDefault("kaltura.upload_timeout", "30m")
	v.SetDefault("upload.tmp_dir", "/var/lib/kaltura-console/tmp")
	v.SetDefault("upload.max_mb", 2048)
	v.SetDefault("upload.max_concurrent", 2)
	v.SetDefault("upload.min_free_mb", 1024)
	v.SetDefault("upload.allowed_ext", []string{".mp4"})
	v.SetDefault("log.level", "info")
}

// Load reads configuration from path (or the default search path when empty).
// A missing file is not an error: defaults and environment variables apply.
func Load(path string) (*Config, error) {
	v := viper.New()
	setDefaults(v)
	v.SetConfigType("toml")
	if path != "" {
		v.SetConfigFile(path)
	} else {
		v.SetConfigName("config")
		v.AddConfigPath(".")
		v.AddConfigPath("/etc/kaltura-console/")
	}
	v.SetEnvPrefix("KCONSOLE")
	v.SetEnvKeyReplacer(strings.NewReplacer(".", "_"))
	v.AutomaticEnv()
	// Viper only unmarshals known keys; bind optional keys for env-only installs.
	for _, key := range []string{
		"kaltura.partner_id", "kaltura.admin_secret", "kaltura.service_url", "kaltura.playback_host",
		"kaltura.upload_service_url", "kaltura.extra_media_hosts", "server.tls_cert", "server.tls_key", "database.debug",
	} {
		if err := v.BindEnv(key); err != nil {
			return nil, fmt.Errorf("binding config key %s: %w", key, err)
		}
	}

	if err := v.ReadInConfig(); err != nil {
		var notFound viper.ConfigFileNotFoundError
		if !errors.As(err, &notFound) || path != "" {
			return nil, fmt.Errorf("reading config: %w", err)
		}
	}
	cfg := &Config{}
	if err := v.Unmarshal(cfg); err != nil {
		return nil, fmt.Errorf("parsing config: %w", err)
	}
	cfg.ConfigFile = v.ConfigFileUsed()
	return cfg, nil
}

// Validate checks the settings required by the serve command. It never
// includes secret values in its error messages.
func (c *Config) Validate() error {
	var errs []error
	if err := ValidateBasePath(c.Server.BasePath); err != nil {
		errs = append(errs, err)
	}
	if c.Kaltura.PartnerID <= 0 {
		errs = append(errs, errors.New("kaltura.partner_id is required"))
	}
	if c.Kaltura.AdminSecret == "" {
		errs = append(errs, errors.New("kaltura.admin_secret is required"))
	}
	urls := map[string]string{"kaltura.service_url": c.Kaltura.ServiceURL, "kaltura.playback_host": c.Kaltura.PlaybackHost}
	if c.Kaltura.UploadServiceURL != "" {
		urls["kaltura.upload_service_url"] = c.Kaltura.UploadServiceURL
	}
	for key, raw := range urls {
		if raw == "" {
			errs = append(errs, fmt.Errorf("%s is required", key))
			continue
		}
		if u, err := url.Parse(raw); err != nil || (u.Scheme != "http" && u.Scheme != "https") || u.Host == "" || u.User != nil || u.Fragment != "" {
			errs = append(errs, fmt.Errorf("%s must be an absolute http(s) URL", key))
		}
	}
	switch c.Database.Driver {
	case "sqlite", "mysql":
	default:
		errs = append(errs, fmt.Errorf("database.driver must be sqlite or mysql, got %q", c.Database.Driver))
	}
	if (c.Server.TLSCert == "") != (c.Server.TLSKey == "") {
		errs = append(errs, errors.New("server.https requires server.tls_cert and server.tls_key"))
	}
	if c.Upload.MaxMB <= 0 || c.Upload.MaxConcurrent <= 0 {
		errs = append(errs, errors.New("upload.max_mb and upload.max_concurrent must be positive"))
	}
	if c.Server.Port < 1 || c.Server.Port > 65535 {
		errs = append(errs, errors.New("server.port must be between 1 and 65535"))
	}
	for key, d := range map[string]time.Duration{
		"server.session_ttl": c.Server.SessionTTL, "server.session_max": c.Server.SessionMax,
		"kaltura.session_expiry": c.Kaltura.SessionExpiry, "kaltura.http_timeout": c.Kaltura.HTTPTimeout,
		"kaltura.connect_timeout": c.Kaltura.ConnectTimeout, "kaltura.upload_timeout": c.Kaltura.UploadTimeout,
	} {
		if d <= 0 {
			errs = append(errs, fmt.Errorf("%s must be positive", key))
		}
	}
	if c.Kaltura.SessionExpiry < time.Second {
		errs = append(errs, errors.New("kaltura.session_expiry must be at least one second"))
	}
	if c.Upload.MaxMB > (math.MaxInt64-(64<<10))>>20 {
		errs = append(errs, errors.New("upload.max_mb exceeds the byte limit"))
	}
	if c.Upload.MinFreeMB < 0 || c.Upload.MinFreeMB > math.MaxInt64>>20 {
		errs = append(errs, errors.New("upload.min_free_mb must fit a nonnegative byte limit"))
	}
	if c.Upload.MaxConcurrent > 1024 {
		errs = append(errs, errors.New("upload.max_concurrent must not exceed 1024"))
	}
	return errors.Join(errs...)
}

// ValidateBasePath permits canonical, unescaped URL path segments only.
func ValidateBasePath(p string) error {
	if p == "" {
		return nil
	}
	if !regexp.MustCompile(`^(/[A-Za-z0-9_-]+)+$`).MatchString(p) {
		return errors.New("server.base_path must be empty or a canonical path such as /console (no trailing slash)")
	}
	return nil
}
