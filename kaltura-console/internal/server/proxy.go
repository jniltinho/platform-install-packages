package server

import (
	"context"
	"io"
	"net/http"
	"net/url"
	"strings"
	"time"

	"github.com/labstack/echo/v5"
)

const (
	maxRedirects = 5
	ownCacheTTL  = time.Minute
)

// relayHeaders are copied from the upstream media response.
var relayHeaders = []string{"Content-Type", "Content-Length", "Content-Range", "Accept-Ranges", "ETag", "Last-Modified"}

// allowedHosts returns the host[:port] values the proxy may contact.
func (s *Server) allowedHosts() map[string]bool {
	hosts := map[string]bool{}
	for _, raw := range []string{s.cfg.Kaltura.PlaybackHost, s.cfg.Kaltura.ServiceURL, s.cfg.Kaltura.UploadServiceURL} {
		if u, err := url.Parse(raw); err == nil && u.Host != "" {
			hosts[strings.ToLower(u.Host)] = true
		}
	}
	for _, h := range s.cfg.Kaltura.ExtraMediaHosts {
		hosts[strings.ToLower(h)] = true
	}
	return hosts
}

// ownedEntry verifies (and caches for a minute) that the entry belongs to
// the configured partner: GetMedia validates both the ID and partnerId.
func (s *Server) ownedEntry(c *echo.Context) (string, error) {
	id, err := entryIDParam(c)
	if err != nil {
		return "", err
	}
	if t, ok := s.ownCache.Load(id); ok && s.now().Sub(t.(time.Time)) < ownCacheTTL {
		return id, nil
	}
	if _, err := s.kc.GetMedia(c.Request().Context(), id); err != nil {
		return "", s.kalturaErr(c, err)
	}
	s.ownCache.Store(id, s.now())
	return id, nil
}

func (s *Server) stream(c *echo.Context) error {
	id, err := s.ownedEntry(c)
	if err != nil {
		return err
	}
	return s.proxy(c, s.kc.PlaybackURL(id), true)
}

func (s *Server) thumbnail(c *echo.Context) error {
	id, err := s.ownedEntry(c)
	if err != nil {
		return err
	}
	return s.proxy(c, s.kc.ThumbnailURL(id), false)
}

// proxy streams target to the client. Redirects are followed here, one hop
// at a time, only to allow-listed hosts (SSRF guard). Only Range/If-Range
// are forwarded: browser cookies and credentials never reach Kaltura.
func (s *Server) proxy(c *echo.Context, target string, forwardRange bool) error {
	r := c.Request()
	allowed := s.allowedHosts()
	// Streams may last longer than the server write timeout.
	_ = http.NewResponseController(c.Response()).SetWriteDeadline(time.Time{})

	var resp *http.Response
	for hop := 0; ; hop++ {
		u, err := url.Parse(target)
		if err != nil || (u.Scheme != "http" && u.Scheme != "https") || u.User != nil || !allowed[strings.ToLower(u.Host)] {
			s.log.Warn("media proxy refused target", "host", hostOf(target))
			return echo.NewHTTPError(http.StatusBadGateway, "origem de mídia não permitida")
		}
		req, err := http.NewRequestWithContext(r.Context(), r.Method, u.String(), nil)
		if err != nil {
			return echo.NewHTTPError(http.StatusBadGateway, "falha ao buscar a mídia")
		}
		if forwardRange {
			for _, h := range []string{"Range", "If-Range"} {
				if v := r.Header.Get(h); v != "" {
					req.Header.Set(h, v)
				}
			}
		}
		resp, err = s.kc.HTTP().Do(req)
		if err != nil {
			if r.Context().Err() != nil {
				return nil // client went away
			}
			s.log.Warn("media proxy upstream error", "error", err)
			return echo.NewHTTPError(http.StatusBadGateway, "falha ao buscar a mídia")
		}
		if resp.StatusCode >= 300 && resp.StatusCode < 400 && resp.Header.Get("Location") != "" {
			loc, lerr := u.Parse(resp.Header.Get("Location"))
			_ = resp.Body.Close()
			if lerr != nil || hop+1 >= maxRedirects {
				return echo.NewHTTPError(http.StatusBadGateway, "redirecionamento de mídia inválido")
			}
			target = loc.String()
			continue
		}
		break
	}
	defer resp.Body.Close() //nolint:errcheck // streamed body

	switch resp.StatusCode {
	case http.StatusOK, http.StatusPartialContent, http.StatusRequestedRangeNotSatisfiable, http.StatusNotModified:
	default:
		s.log.Warn("media proxy upstream status", "status", resp.StatusCode)
		return echo.NewHTTPError(http.StatusBadGateway, "a mídia não está disponível")
	}
	h := c.Response().Header()
	h.Set("Cache-Control", "private, no-store")
	for _, k := range relayHeaders {
		if v := resp.Header.Get(k); v != "" {
			h.Set(k, v)
		}
	}
	if h.Get("Accept-Ranges") == "" && forwardRange {
		h.Set("Accept-Ranges", "bytes")
	}
	c.Response().WriteHeader(resp.StatusCode)
	if r.Method == http.MethodHead {
		return nil
	}
	// Past this point headers are sent: errors can only abort the stream.
	if _, err := io.Copy(c.Response(), resp.Body); err != nil && r.Context().Err() == nil &&
		!errorsIsCanceled(err) {
		s.log.Warn("media proxy stream aborted", "error", err)
		panic(http.ErrAbortHandler)
	}
	return nil
}

func errorsIsCanceled(err error) bool {
	return err == context.Canceled || strings.Contains(err.Error(), "broken pipe") ||
		strings.Contains(err.Error(), "connection reset")
}

func hostOf(raw string) string {
	if u, err := url.Parse(raw); err == nil {
		return u.Host
	}
	return ""
}
