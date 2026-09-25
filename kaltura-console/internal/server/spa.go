package server

import (
	"bytes"
	"html"
	"io/fs"
	"net/http"
	"net/url"
	"path"
	"strings"

	"github.com/labstack/echo/v5"
)

func registerSPA(e *echo.Group, dist fs.FS, base string) {
	files := http.FileServer(http.FS(dist))
	handler := func(c *echo.Context) error {
		r := c.Request()
		clean := strings.TrimPrefix(path.Clean(strings.TrimPrefix(r.URL.Path, base)), "/")
		if clean == "api" || strings.HasPrefix(clean, "api/") {
			return echo.ErrNotFound
		}
		if clean != "" && clean != "." && clean != "index.html" {
			if info, err := fs.Stat(dist, clean); err == nil && !info.IsDir() {
				http.StripPrefix(base, files).ServeHTTP(c.Response(), r)
				return nil
			}
			if strings.HasPrefix(clean, "assets/") {
				return echo.ErrNotFound
			}
		}
		if clean != "login" && currentUser(c) == nil {
			return c.Redirect(http.StatusSeeOther, base+"/login?return="+url.QueryEscape(strings.TrimPrefix(r.URL.RequestURI(), base)))
		}
		body, err := fs.ReadFile(dist, "index.html")
		if err != nil {
			return err
		}
		body = bytes.Replace(body, []byte("<head>"), []byte("<head><base href=\""+html.EscapeString(base+"/")+"\">"), 1)
		c.Response().Header().Set("Cache-Control", "no-store")
		if r.Method == http.MethodHead {
			return c.NoContent(http.StatusOK)
		}
		return c.Blob(http.StatusOK, "text/html; charset=utf-8", body)
	}
	e.GET("/*", handler)
	e.HEAD("/*", handler)
}
