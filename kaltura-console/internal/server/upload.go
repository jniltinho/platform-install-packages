package server

import (
	"encoding/binary"
	"errors"
	"io"
	"net/http"
	"os"
	"path/filepath"
	"slices"
	"strings"
	"time"
	"unicode/utf8"

	"github.com/labstack/echo/v5"
	"golang.org/x/sys/unix"
	"kaltura-console/internal/kaltura"
)

// PrepareUploads creates private staging storage and removes abandoned uploads.
func PrepareUploads(dir string) error {
	if err := os.MkdirAll(dir, 0o750); err != nil {
		return err
	}
	entries, err := os.ReadDir(dir)
	if err != nil {
		return err
	}
	for _, e := range entries {
		if e.IsDir() || !strings.HasPrefix(e.Name(), "kconsole-upload-") {
			continue
		}
		info, err := e.Info()
		if err != nil {
			return err
		}
		if time.Since(info.ModTime()) > time.Hour {
			if err := os.Remove(filepath.Join(dir, e.Name())); err != nil {
				return err
			}
		}
	}
	return nil
}

func writable(dir string) bool {
	f, err := os.CreateTemp(dir, "kconsole-check-")
	if err != nil {
		return false
	}
	name := f.Name()
	closeErr := f.Close()
	removeErr := os.Remove(name)
	return closeErr == nil && removeErr == nil
}

func uploadBodyError(err error) error {
	var large *http.MaxBytesError
	if errors.As(err, &large) {
		return echo.NewHTTPError(http.StatusRequestEntityTooLarge, "arquivo muito grande")
	}
	return echo.NewHTTPError(http.StatusBadRequest, "upload incompleto ou inválido")
}

func (s *Server) upload(c *echo.Context) error {
	r := c.Request()
	limit := s.cfg.Upload.MaxMB << 20
	// Permit a small bounded multipart envelope in addition to the file limit.
	bodyLimit := limit + (64 << 10)
	if r.ContentLength > bodyLimit {
		return echo.NewHTTPError(413, "arquivo muito grande")
	}
	r.Body = http.MaxBytesReader(c.Response(), r.Body, bodyLimit)
	select {
	case s.uploads <- struct{}{}:
		defer func() { <-s.uploads }()
	default:
		return echo.NewHTTPError(429, "limite de uploads simultâneos atingido")
	}
	var stat unix.Statfs_t
	if err := unix.Statfs(s.cfg.Upload.TmpDir, &stat); err != nil {
		return err
	}
	if stat.Bavail*uint64(stat.Bsize) < uint64(s.cfg.Upload.MinFreeMB)<<20 {
		return echo.NewHTTPError(507, "espaço insuficiente para upload")
	}
	_ = http.NewResponseController(c.Response()).SetWriteDeadline(time.Now().Add(s.cfg.Kaltura.UploadTimeout))
	_ = http.NewResponseController(c.Response()).SetReadDeadline(time.Now().Add(s.cfg.Kaltura.UploadTimeout))
	mr, err := r.MultipartReader()
	if err != nil {
		return uploadBodyError(err)
	}
	name, description, path, filename := "", "", "", ""
	defer func() {
		if path != "" {
			_ = os.Remove(path)
		}
	}()
	for {
		part, err := mr.NextPart()
		if errors.Is(err, io.EOF) {
			break
		}
		if err != nil {
			return uploadBodyError(err)
		}
		if part.FileName() == "" {
			value, err := io.ReadAll(io.LimitReader(part, 20001))
			if err != nil {
				return uploadBodyError(err)
			}
			if len(value) > 20000 {
				return echo.NewHTTPError(422, "campo muito longo")
			}
			switch part.FormName() {
			case "name":
				name = strings.TrimSpace(string(value))
			case "description":
				description = string(value)
			default:
				return echo.NewHTTPError(400, "campo de upload desconhecido")
			}
			continue
		}
		if path != "" || part.FormName() != "file" {
			return echo.NewHTTPError(400, "envie apenas um arquivo")
		}
		filename = filepath.Base(part.FileName())
		if !slices.Contains(s.cfg.Upload.AllowedExt, strings.ToLower(filepath.Ext(filename))) {
			return echo.NewHTTPError(422, "extensão não permitida")
		}
		f, err := os.CreateTemp(s.cfg.Upload.TmpDir, "kconsole-upload-")
		if err != nil {
			return err
		}
		path = f.Name()
		n, copyErr := io.Copy(f, io.LimitReader(part, limit+1))
		closeErr := f.Close()
		if copyErr != nil {
			return uploadBodyError(copyErr)
		}
		if closeErr != nil {
			return closeErr
		}
		if n > limit {
			return echo.NewHTTPError(413, "arquivo muito grande")
		}
		if !validBMFF(path, n) {
			return echo.NewHTTPError(422, "arquivo ISO-BMFF inválido")
		}
	}
	if path == "" || name == "" || utf8.RuneCountInString(name) > 255 || utf8.RuneCountInString(description) > 5000 {
		return echo.NewHTTPError(422, "arquivo e nome são obrigatórios; nome até 255 e descrição até 5000 caracteres")
	}
	entry, err := s.kc.UploadFile(
		r.Context(), path, filename, name, description, nil,
	)
	if err != nil {
		var ue *kaltura.UploadError
		if errors.As(err, &ue) {
			messages := map[string]string{
				kaltura.StepAdd: "falha ao criar a entrada", kaltura.StepToken: "falha ao criar o token de upload",
				kaltura.StepUpload: "falha ao enviar o arquivo ao Kaltura", kaltura.StepAttach: "falha ao anexar o conteúdo",
			}
			return echo.NewHTTPError(502, messages[ue.Step])
		}
		return s.kalturaErr(c, err)
	}
	return c.JSON(http.StatusCreated, viewEntry(entry))
}

func validBMFF(path string, size int64) bool {
	f, err := os.Open(path)
	if err != nil {
		return false
	}
	var header [16]byte
	_, readErr := io.ReadFull(f, header[:])
	closeErr := f.Close()
	if readErr != nil || closeErr != nil {
		return false
	}
	boxSize := int64(binary.BigEndian.Uint32(header[:4]))
	return string(header[4:8]) == "ftyp" && boxSize >= 16 && boxSize <= size
}
