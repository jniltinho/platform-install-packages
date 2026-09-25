// Package server wires the Echo v5 HTTP server: middleware, the JSON API
// used by the embedded SPA, the media proxy and the SPA fallback.
package server

import (
	"errors"
	"io/fs"
	"log/slog"
	"net"
	"net/http"
	"strings"
	"sync"
	"time"

	"github.com/labstack/echo/v5"
	"github.com/labstack/echo/v5/middleware"
	"gorm.io/gorm"

	"kaltura-console/internal/auth"
	"kaltura-console/internal/config"
	"kaltura-console/internal/kaltura"
)

// Server holds the handler dependencies.
type Server struct {
	cfg      *config.Config
	db       *gorm.DB
	auth     *auth.Service
	kc       *kaltura.Client
	trusted  []*net.IPNet
	uploads  chan struct{}
	ownCache sync.Map // entryID -> time.Time (verified to belong to the partner)
	now      func() time.Time
	log      *slog.Logger
}

// New builds the Echo instance with every route registered. dist is the
// embedded SPA build (web/dist); it may be nil in tests.
func New(cfg *config.Config, db *gorm.DB, authSvc *auth.Service, kc *kaltura.Client, dist fs.FS) (*echo.Echo, *Server, error) {
	s := &Server{cfg: cfg, db: db, auth: authSvc, kc: kc, now: time.Now, log: slog.Default(),
		uploads: make(chan struct{}, cfg.Upload.MaxConcurrent)}
	for _, cidr := range cfg.Server.TrustedProxies {
		_, n, err := net.ParseCIDR(cidr)
		if err != nil {
			return nil, nil, errors.New("server.trusted_proxies: invalid CIDR " + cidr)
		}
		s.trusted = append(s.trusted, n)
	}

	e := echo.New()
	if len(s.trusted) > 0 {
		opts := []echo.TrustOption{echo.TrustLoopback(false), echo.TrustLinkLocal(false), echo.TrustPrivateNet(false)}
		for _, n := range s.trusted {
			opts = append(opts, echo.TrustIPRange(n))
		}
		e.IPExtractor = echo.ExtractIPFromXFFHeader(opts...)
	} else {
		e.IPExtractor = echo.ExtractIPDirect()
	}
	e.HTTPErrorHandler = errorHandler
	e.Use(middleware.Recover())
	e.Use(middleware.RequestID())
	e.Use(middleware.RequestLoggerWithConfig(middleware.RequestLoggerConfig{
		LogMethod: true, LogURIPath: true, LogStatus: true, LogLatency: true, LogRequestID: true, LogRemoteIP: true,
		HandleError: true,
		LogValuesFunc: func(_ *echo.Context, v middleware.RequestLoggerValues) error {
			attrs := []any{"method", v.Method, "path", v.URIPath, "status", v.Status,
				"latency_ms", v.Latency.Milliseconds(), "ip", v.RemoteIP, "request_id", v.RequestID}
			if v.Error != nil {
				attrs = append(attrs, "error", v.Error.Error())
			}
			s.log.Info("request", attrs...)
			return nil
		},
	}))
	e.Use(middleware.SecureWithConfig(middleware.SecureConfig{
		ContentTypeNosniff: "nosniff",
		XFrameOptions:      "DENY",
		ReferrerPolicy:     "same-origin",
		ContentSecurityPolicy: "default-src 'self'; img-src 'self' data: blob:; media-src 'self' blob:; " +
			"style-src 'self' 'unsafe-inline'; font-src 'self'; connect-src 'self'; frame-ancestors 'none'; base-uri 'self'; form-action 'self'",
	}))
	e.Use(s.sessionMiddleware)

	e.GET("/healthz", func(c *echo.Context) error { return c.String(http.StatusOK, "ok") })

	api := e.Group("/api", middleware.BodyLimit(1<<20))
	api.POST("/login", s.login)
	api.GET("/session", s.session, s.requireAuth)
	api.POST("/logout", s.logout, s.requireAuth)
	api.GET("/dashboard", s.dashboard, s.requireAuth)
	api.GET("/media", s.listMedia, s.requireAuth)
	api.GET("/media/:id", s.getMedia, s.requireAuth)
	api.GET("/media/:id/status", s.mediaStatus, s.requireAuth)
	api.GET("/media/:id/flavors", s.mediaFlavors, s.requireAuth)
	api.PATCH("/media/:id", s.updateMedia, s.requireAuth, s.requireAdmin)
	api.DELETE("/media/:id", s.deleteMedia, s.requireAuth, s.requireAdmin)
	api.GET("/users", s.listUsers, s.requireAuth, s.requireAdmin)
	api.POST("/users", s.createUser, s.requireAuth, s.requireAdmin)
	api.PATCH("/users/:id", s.updateUser, s.requireAuth, s.requireAdmin)
	api.DELETE("/users/:id", s.deleteUser, s.requireAuth, s.requireAdmin)
	api.GET("/health", s.health, s.requireAuth)
	api.GET("/version", s.version, s.requireAuth)
	// The upload route has its own (large) body limit.
	e.POST("/api/media", s.upload, s.requireAuth, s.requireAdmin)

	for _, m := range []string{http.MethodGet, http.MethodHead} {
		e.Add(m, "/media/:id/stream", s.stream, s.requireAuth)
		e.Add(m, "/media/:id/thumbnail", s.thumbnail, s.requireAuth)
	}

	if dist != nil {
		registerSPA(e, dist)
	}
	return e, s, nil
}

// errorHandler renders every error as JSON {"message": …} without leaking internals.
func errorHandler(c *echo.Context, err error) {
	if resp, uErr := echo.UnwrapResponse(c.Response()); uErr == nil && resp.Committed {
		return
	}
	code := http.StatusInternalServerError
	msg := "erro interno"
	var he *echo.HTTPError
	if errors.As(err, &he) {
		code = he.Code
		msg = he.Message
		if msg == "" {
			msg = http.StatusText(code)
		}
	} else if status := echo.StatusCode(err); status != 0 {
		code = status
		msg = http.StatusText(status)
	} else {
		slog.Error("unhandled error", "path", c.Request().URL.Path, "error", err)
	}
	if c.Request().Method == http.MethodHead {
		_ = c.NoContent(code)
		return
	}
	_ = c.JSON(code, map[string]string{"message": msg})
}

// isHTTPS reports whether the client connection is TLS, honoring
// X-Forwarded-Proto only from trusted proxies.
func (s *Server) isHTTPS(r *http.Request) bool {
	if r.TLS != nil {
		return true
	}
	host, _, err := net.SplitHostPort(r.RemoteAddr)
	if err != nil {
		return false
	}
	ip := net.ParseIP(host)
	for _, n := range s.trusted {
		if ip != nil && n.Contains(ip) {
			return strings.EqualFold(r.Header.Get("X-Forwarded-Proto"), "https")
		}
	}
	return false
}
