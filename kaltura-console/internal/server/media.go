package server

import (
	"context"
	"errors"
	"net/http"
	"strconv"
	"strings"
	"time"
	"unicode/utf8"

	"github.com/labstack/echo/v5"
	"golang.org/x/sync/errgroup"

	"kaltura-console/internal/kaltura"
)

const pageSize = 20

type entryView struct {
	ID          string `json:"id"`
	Name        string `json:"name"`
	Description string `json:"description"`
	Status      int    `json:"status"`
	StatusLabel string `json:"status_label"`
	StatusGroup string `json:"status_group"`
	Duration    int    `json:"duration"`
	CreatedAt   int64  `json:"created_at"`
	UpdatedAt   int64  `json:"updated_at"`
	Plays       int    `json:"plays"`
	Width       int    `json:"width"`
	Height      int    `json:"height"`
	Thumbnail   string `json:"thumbnail_url"`
	Playback    string `json:"playback_url"`
}

func (s *Server) viewEntry(e *kaltura.Entry) entryView {
	return entryView{
		ID: e.ID, Name: e.Name, Description: e.Description, Status: e.Status,
		StatusLabel: kaltura.EntryStatusLabel(e.Status), StatusGroup: kaltura.EntryStatusGroup(e.Status),
		Duration: e.Duration, CreatedAt: e.CreatedAt, UpdatedAt: e.UpdatedAt, Plays: e.Plays,
		Width: e.Width, Height: e.Height,
		Thumbnail: s.cfg.Server.BasePath + "/media/" + e.ID + "/thumbnail", Playback: s.cfg.Server.BasePath + "/media/" + e.ID + "/stream",
	}
}

func (s *Server) viewEntries(in []kaltura.Entry) []entryView {
	out := make([]entryView, len(in))
	for i := range in {
		out[i] = s.viewEntry(&in[i])
	}
	return out
}

// kalturaErr converts Kaltura failures into a 502 (or 404 for unknown
// entries) without exposing upstream details to the browser.
func (s *Server) kalturaErr(c *echo.Context, err error) error {
	var ae *kaltura.APIError
	if errors.As(err, &ae) && (ae.Code == "ENTRY_ID_NOT_FOUND" || ae.Code == "INVALID_ENTRY_ID") {
		return echo.NewHTTPError(http.StatusNotFound, "vídeo não encontrado")
	}
	// Kaltura exception messages can echo KS values; log only the typed code.
	code := "UPSTREAM_FAILURE"
	if errors.As(err, &ae) {
		code = ae.Code
	}
	s.log.Warn("kaltura call failed", "path", c.Request().URL.Path, "code", code)
	return echo.NewHTTPError(http.StatusBadGateway, "falha ao comunicar com o Kaltura")
}

func entryIDParam(c *echo.Context) (string, error) {
	id := c.Param("id")
	if !kaltura.ValidEntryID(id) {
		return "", echo.NewHTTPError(http.StatusNotFound, "vídeo não encontrado")
	}
	return id, nil
}

func (s *Server) dashboard(c *echo.Context) error {
	ctx := c.Request().Context()
	var (
		total, ready, processing, failed int
		recent                           *kaltura.EntryList
	)
	g, gctx := errgroup.WithContext(ctx)
	g.Go(func() (err error) {
		recent, err = s.kc.ListMedia(gctx, kaltura.ListOptions{PageSize: 8})
		if err == nil {
			total = recent.TotalCount
		}
		return err
	})
	g.Go(func() (err error) { ready, err = s.kc.CountByStatuses(gctx, kaltura.StatusReady); return })
	g.Go(func() (err error) { processing, err = s.kc.CountByStatuses(gctx, kaltura.StatusProcessing); return })
	g.Go(func() (err error) { failed, err = s.kc.CountByStatuses(gctx, kaltura.StatusError); return })
	if err := g.Wait(); err != nil {
		return s.kalturaErr(c, err)
	}
	return c.JSON(http.StatusOK, map[string]any{
		"counts": map[string]int{"total": total, "ready": ready, "processing": processing, "error": failed},
		"recent": s.viewEntries(recent.Objects),
	})
}

func (s *Server) listMedia(c *echo.Context) error {
	page, _ := strconv.Atoi(c.QueryParam("page"))
	if page < 1 {
		page = 1
	}
	q := strings.TrimSpace(c.QueryParam("q"))
	if utf8.RuneCountInString(q) > 100 {
		return echo.NewHTTPError(http.StatusBadRequest, "busca muito longa")
	}
	l, err := s.kc.ListMedia(c.Request().Context(), kaltura.ListOptions{NameLike: q, Page: page, PageSize: pageSize})
	if err != nil {
		return s.kalturaErr(c, err)
	}
	pages := (l.TotalCount + pageSize - 1) / pageSize
	if pages < 1 {
		pages = 1
	}
	return c.JSON(http.StatusOK, map[string]any{
		"items": s.viewEntries(l.Objects), "total": l.TotalCount, "page": page, "page_size": pageSize, "pages": pages,
	})
}

func (s *Server) getMedia(c *echo.Context) error {
	id, err := entryIDParam(c)
	if err != nil {
		return err
	}
	e, err := s.kc.GetMedia(c.Request().Context(), id)
	if err != nil {
		return s.kalturaErr(c, err)
	}
	s.ownCache.Store(id, s.now())
	return c.JSON(http.StatusOK, s.viewEntry(e))
}

func (s *Server) mediaStatus(c *echo.Context) error {
	id, err := entryIDParam(c)
	if err != nil {
		return err
	}
	e, err := s.kc.GetMedia(c.Request().Context(), id)
	if err != nil {
		return s.kalturaErr(c, err)
	}
	v := s.viewEntry(e)
	return c.JSON(http.StatusOK, map[string]any{
		"id": v.ID, "status": v.Status, "status_label": v.StatusLabel, "status_group": v.StatusGroup,
		"ready": v.StatusGroup == kaltura.GroupReady, "duration": v.Duration, "width": v.Width, "height": v.Height,
	})
}

type flavorView struct {
	ID          string `json:"id"`
	Type        string `json:"type"`
	Status      int    `json:"status"`
	StatusLabel string `json:"status_label"`
	StatusGroup string `json:"status_group"`
	Width       int    `json:"width"`
	Height      int    `json:"height"`
	SizeKB      int64  `json:"size_kb"`
	Bitrate     int    `json:"bitrate"`
	Format      string `json:"format"`
	Codec       string `json:"codec"`
}

func (s *Server) mediaFlavors(c *echo.Context) error {
	id, err := entryIDParam(c)
	if err != nil {
		return err
	}
	fl, err := s.kc.ListFlavors(c.Request().Context(), id)
	if err != nil {
		return s.kalturaErr(c, err)
	}
	out := make([]flavorView, len(fl))
	for i, f := range fl {
		typ := "Rendition"
		if f.IsOriginal {
			typ = "Original"
		}
		out[i] = flavorView{ID: f.ID, Type: typ, Status: f.Status, StatusLabel: kaltura.FlavorStatusLabel(f.Status),
			StatusGroup: kaltura.FlavorStatusGroup(f.Status), Width: f.Width, Height: f.Height,
			SizeKB: f.Size, Bitrate: f.Bitrate, Format: f.FileExt, Codec: f.VideoCodecID}
	}
	return c.JSON(http.StatusOK, out)
}

func (s *Server) updateMedia(c *echo.Context) error {
	id, err := entryIDParam(c)
	if err != nil {
		return err
	}
	var in struct {
		Name        string `json:"name"`
		Description string `json:"description"`
	}
	if err := c.Bind(&in); err != nil {
		return echo.NewHTTPError(http.StatusBadRequest, "requisição inválida")
	}
	in.Name = strings.TrimSpace(in.Name)
	if in.Name == "" || utf8.RuneCountInString(in.Name) > 255 {
		return echo.NewHTTPError(http.StatusUnprocessableEntity, "o nome é obrigatório (até 255 caracteres)")
	}
	if utf8.RuneCountInString(in.Description) > 5000 {
		return echo.NewHTTPError(http.StatusUnprocessableEntity, "a descrição aceita até 5000 caracteres")
	}
	e, err := s.kc.UpdateMedia(c.Request().Context(), id, in.Name, in.Description)
	if err != nil {
		return s.kalturaErr(c, err)
	}
	return c.JSON(http.StatusOK, s.viewEntry(e))
}

func (s *Server) deleteMedia(c *echo.Context) error {
	id, err := entryIDParam(c)
	if err != nil {
		return err
	}
	if err := s.kc.DeleteMedia(c.Request().Context(), id); err != nil {
		return s.kalturaErr(c, err)
	}
	s.ownCache.Delete(id)
	s.log.Info("media deleted", "entry", id, "user", currentUser(c).Email)
	return c.NoContent(http.StatusNoContent)
}

// ---- health ----

type check struct {
	Group  string `json:"group"`
	Name   string `json:"name"`
	OK     bool   `json:"ok"`
	Detail string `json:"detail"`
}

func (s *Server) health(c *echo.Context) error {
	ctx, cancel := context.WithTimeout(c.Request().Context(), 20*time.Second)
	defer cancel()
	var out []check
	add := func(group, name string, ok bool, good, bad string) {
		d := good
		if !ok {
			d = bad
		}
		out = append(out, check{group, name, ok, d})
	}
	add("console", "Aplicação", true, "Em execução.", "")
	sqlDB, err := s.db.DB()
	add("console", "Banco de dados ("+s.cfg.Database.Driver+")", err == nil && sqlDB.PingContext(ctx) == nil, "Conexão ativa.", "Sem conexão.")
	add("console", "Diretório de upload", writable(s.cfg.Upload.TmpDir), "Gravável.", "Sem permissão de escrita.")
	k := s.cfg.Kaltura
	add("kaltura", "Partner configurado", k.PartnerID != 0, "Partner "+strconv.Itoa(k.PartnerID)+".", "kaltura.partner_id ausente.")
	add("kaltura", "Endpoint de upload", true,
		map[bool]string{true: "Endpoint dedicado configurado.", false: "Usando service_url para uploads."}[k.UploadServiceURL != ""], "")
	add("kaltura", "API acessível (system.ping)", s.kc.Ping(ctx) == nil, "Respondeu.", "Sem resposta.")
	add("kaltura", "Autenticação (KS admin)", s.kc.CheckSession(ctx) == nil, "KS admin obtida.", "Falha ao obter a KS.")
	_, err = s.kc.ListMedia(ctx, kaltura.ListOptions{PageSize: 1})
	add("kaltura", "media.list", err == nil, "Chamada bem-sucedida.", "Falhou.")
	return c.JSON(http.StatusOK, out)
}
