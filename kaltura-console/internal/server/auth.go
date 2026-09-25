package server

import (
	"crypto/subtle"
	"errors"
	"net/http"
	"net/url"
	"strconv"
	"strings"

	"github.com/labstack/echo/v5"

	"kaltura-console/internal/auth"
	"kaltura-console/internal/buildinfo"
	"kaltura-console/internal/models"
)

const (
	sessionCookie = "kconsole_session"
	csrfHeader    = "X-CSRF-Token"
	ctxUser       = "kc.user"
	ctxSession    = "kc.session"
)

func isMutating(m string) bool {
	return m == http.MethodPost || m == http.MethodPut || m == http.MethodPatch || m == http.MethodDelete
}

// sameOrigin rejects cross-site mutating requests that carry an Origin
// header for another host (defense in depth next to the CSRF token).
func (s *Server) sameOrigin(r *http.Request) bool {
	o := r.Header.Get("Origin")
	if o == "" {
		return true
	}
	u, err := url.Parse(o)
	if err != nil {
		return false
	}
	scheme := "http"
	if s.isHTTPS(r) {
		scheme = "https"
	}
	return u.Scheme == scheme && strings.EqualFold(u.Host, r.Host) &&
		u.User == nil && u.Path == "" && u.RawQuery == "" && u.Fragment == "" && !u.ForceQuery
}

// sessionMiddleware resolves the session cookie and enforces CSRF on
// mutating requests of an authenticated session.
func (s *Server) sessionMiddleware(next echo.HandlerFunc) echo.HandlerFunc {
	return func(c *echo.Context) error {
		r := c.Request()
		// Never let shared or browser caches retain authenticated content or CSRF tokens.
		if strings.HasPrefix(r.URL.Path, "/api/") || strings.HasPrefix(r.URL.Path, "/media/") {
			c.Response().Header().Set("Cache-Control", "private, no-store")
		}
		if isMutating(r.Method) && !s.sameOrigin(r) {
			return echo.NewHTTPError(http.StatusForbidden, "origem inválida")
		}
		ck, err := c.Cookie(sessionCookie)
		if err != nil || ck.Value == "" {
			return next(c)
		}
		sess, user, err := s.auth.Resolve(ck.Value)
		if err != nil {
			if errors.Is(err, auth.ErrSessionNotFound) {
				c.SetCookie(s.cookie("", -1, r))
				return next(c)
			}
			return err
		}
		if isMutating(r.Method) {
			tok := r.Header.Get(csrfHeader)
			if tok == "" || subtle.ConstantTimeCompare([]byte(tok), []byte(sess.CSRFToken)) != 1 {
				return echo.NewHTTPError(http.StatusForbidden, "token CSRF inválido")
			}
		}
		c.Set(ctxUser, user)
		c.Set(ctxSession, sess)
		return next(c)
	}
}

func currentUser(c *echo.Context) *models.User {
	u, _ := c.Get(ctxUser).(*models.User)
	return u
}

func currentSession(c *echo.Context) *models.Session {
	s, _ := c.Get(ctxSession).(*models.Session)
	return s
}

func (s *Server) requireAuth(next echo.HandlerFunc) echo.HandlerFunc {
	return func(c *echo.Context) error {
		if currentUser(c) == nil {
			return echo.NewHTTPError(http.StatusUnauthorized, "autenticação necessária")
		}
		return next(c)
	}
}

func (s *Server) requireAdmin(next echo.HandlerFunc) echo.HandlerFunc {
	return func(c *echo.Context) error {
		if u := currentUser(c); u == nil || !u.IsAdmin() {
			return echo.NewHTTPError(http.StatusForbidden, "permissão de administrador necessária")
		}
		return next(c)
	}
}

func (s *Server) cookie(value string, maxAge int, r *http.Request) *http.Cookie {
	return &http.Cookie{Name: sessionCookie, Value: value, Path: "/", MaxAge: maxAge,
		HttpOnly: true, Secure: s.isHTTPS(r), SameSite: http.SameSiteLaxMode}
}

type sessionView struct {
	User    userView `json:"user"`
	CSRF    string   `json:"csrf"`
	Partner int      `json:"partner_id"`
	Version string   `json:"version"`
}

type userView struct {
	ID    uint   `json:"id"`
	Name  string `json:"name"`
	Email string `json:"email"`
	Role  string `json:"role"`
}

func viewUser(u *models.User) userView {
	return userView{ID: u.ID, Name: u.Name, Email: u.Email, Role: u.Role}
}

func (s *Server) sessionPayload(u *models.User, sess *models.Session) sessionView {
	return sessionView{User: viewUser(u), CSRF: sess.CSRFToken, Partner: s.cfg.Kaltura.PartnerID, Version: buildinfo.Version}
}

func (s *Server) login(c *echo.Context) error {
	var in struct {
		Email    string `json:"email"`
		Password string `json:"password"`
		Remember bool   `json:"remember"`
	}
	if err := c.Bind(&in); err != nil {
		return echo.NewHTTPError(http.StatusBadRequest, "requisição inválida")
	}
	if old := currentSession(c); old != nil {
		if err := s.auth.Logout(old.ID); err != nil {
			return err
		}
	}
	sess, user, err := s.auth.Login(in.Email, in.Password, c.RealIP(), in.Remember)
	switch {
	case errors.Is(err, auth.ErrLockedOut):
		return echo.NewHTTPError(http.StatusTooManyRequests, "muitas tentativas; aguarde 15 minutos")
	case errors.Is(err, auth.ErrInvalidCredentials):
		return echo.NewHTTPError(http.StatusUnauthorized, "e-mail ou senha inválidos")
	case err != nil:
		return err
	}
	maxAge := 0 // browser-session cookie
	if in.Remember {
		maxAge = int(auth.RememberTTL.Seconds())
	}
	c.SetCookie(s.cookie(sess.ID, maxAge, c.Request()))
	s.log.Info("login", "user", user.Email, "ip", c.RealIP())
	return c.JSON(http.StatusOK, s.sessionPayload(user, sess))
}

func (s *Server) session(c *echo.Context) error {
	return c.JSON(http.StatusOK, s.sessionPayload(currentUser(c), currentSession(c)))
}

func (s *Server) logout(c *echo.Context) error {
	if sess := currentSession(c); sess != nil {
		if err := s.auth.Logout(sess.ID); err != nil {
			return err
		}
	}
	c.SetCookie(s.cookie("", -1, c.Request()))
	return c.NoContent(http.StatusNoContent)
}

func (s *Server) version(c *echo.Context) error {
	return c.JSON(http.StatusOK, map[string]string{"version": buildinfo.Version, "commit": buildinfo.GitCommit, "build_date": buildinfo.BuildDate})
}

// ---- users (admin) ----

func userErr(err error) error {
	switch {
	case errors.Is(err, auth.ErrUserNotFound):
		return echo.NewHTTPError(http.StatusNotFound, "usuário não encontrado")
	case errors.Is(err, auth.ErrEmailTaken):
		return echo.NewHTTPError(http.StatusConflict, "e-mail já cadastrado")
	case errors.Is(err, auth.ErrLastAdmin):
		return echo.NewHTTPError(http.StatusConflict, "o último administrador não pode ser removido nem rebaixado")
	case errors.Is(err, auth.ErrSelfDelete):
		return echo.NewHTTPError(http.StatusConflict, "você não pode excluir a própria conta")
	case errors.Is(err, auth.ErrInvalidRole):
		return echo.NewHTTPError(http.StatusBadRequest, "papel deve ser admin ou viewer")
	case errors.Is(err, auth.ErrWeakPassword):
		return echo.NewHTTPError(http.StatusBadRequest, "a senha precisa ter ao menos 8 caracteres")
	case err != nil && strings.HasPrefix(err.Error(), "auth:"):
		return echo.NewHTTPError(http.StatusBadRequest, strings.TrimPrefix(err.Error(), "auth: "))
	}
	return err
}

func (s *Server) listUsers(c *echo.Context) error {
	users, err := s.auth.ListUsers()
	if err != nil {
		return err
	}
	out := make([]userView, len(users))
	for i := range users {
		out[i] = viewUser(&users[i])
	}
	return c.JSON(http.StatusOK, out)
}

func (s *Server) createUser(c *echo.Context) error {
	var in struct {
		Name     string `json:"name"`
		Email    string `json:"email"`
		Password string `json:"password"`
		Role     string `json:"role"`
	}
	if err := c.Bind(&in); err != nil {
		return echo.NewHTTPError(http.StatusBadRequest, "requisição inválida")
	}
	u, err := s.auth.CreateUser(in.Name, in.Email, in.Password, in.Role)
	if err != nil {
		return userErr(err)
	}
	return c.JSON(http.StatusCreated, viewUser(u))
}

func userIDParam(c *echo.Context) (uint, error) {
	id, err := strconv.ParseUint(c.Param("id"), 10, 32)
	if err != nil || id == 0 {
		return 0, echo.NewHTTPError(http.StatusBadRequest, "id inválido")
	}
	return uint(id), nil
}

func (s *Server) updateUser(c *echo.Context) error {
	id, err := userIDParam(c)
	if err != nil {
		return err
	}
	var in struct {
		Name     string `json:"name"`
		Role     string `json:"role"`
		Password string `json:"password"`
	}
	if err := c.Bind(&in); err != nil {
		return echo.NewHTTPError(http.StatusBadRequest, "requisição inválida")
	}
	u, err := s.auth.UpdateUserWithPassword(id, in.Name, in.Role, in.Password)
	if err != nil {
		return userErr(err)
	}
	return c.JSON(http.StatusOK, viewUser(u))
}

func (s *Server) deleteUser(c *echo.Context) error {
	id, err := userIDParam(c)
	if err != nil {
		return err
	}
	if err := s.auth.DeleteUser(currentUser(c).ID, id); err != nil {
		return userErr(err)
	}
	return c.NoContent(http.StatusNoContent)
}
