package cmd

import (
	"context"
	"errors"
	"io/fs"
	"log/slog"
	"net/http"
	"os"
	"os/signal"
	"syscall"
	"time"

	"github.com/spf13/cobra"
	"gorm.io/gorm"
	"kaltura-console/internal/auth"
	"kaltura-console/internal/config"
	"kaltura-console/internal/kaltura"
	"kaltura-console/internal/server"
	"kaltura-console/web"
)

func serve(c *cobra.Command, cfg *config.Config, db *gorm.DB, svc *auth.Service) error {
	slog.SetDefault(slog.New(slog.NewJSONHandler(c.ErrOrStderr(), &slog.HandlerOptions{Level: cfg.Log.Slog()})))
	if err := server.PrepareUploads(cfg.Upload.TmpDir); err != nil {
		return err
	}
	n, err := svc.CountUsers()
	if err != nil {
		return err
	}
	if n == 0 {
		slog.Warn("no users: run kaltura-console user add --email EMAIL --role admin")
	}
	k := cfg.Kaltura
	kc := kaltura.NewClient(kaltura.Config{
		ServiceURL: k.ServiceURL, UploadServiceURL: k.EffectiveUploadURL(), PartnerID: k.PartnerID,
		AdminSecret: k.AdminSecret, UserID: k.UserID, SessionExpiry: k.SessionExpiry,
		PlaybackHost: k.PlaybackHost, HTTPTimeout: k.HTTPTimeout, ConnectTimeout: k.ConnectTimeout,
		UploadTimeout: k.UploadTimeout,
	})
	defer kc.HTTP().CloseIdleConnections()
	dist, err := fs.Sub(web.Assets, "dist")
	if err != nil {
		return err
	}
	e, _, err := server.New(cfg, db, svc, kc, dist)
	if err != nil {
		return err
	}
	h := &http.Server{Addr: cfg.Server.Addr(), Handler: e, ReadHeaderTimeout: 10 * time.Second,
		IdleTimeout: 120 * time.Second, WriteTimeout: 60 * time.Second, MaxHeaderBytes: 1 << 20}
	ctx, stop := signal.NotifyContext(c.Context(), os.Interrupt, syscall.SIGTERM)
	defer stop()
	done := make(chan error, 1)
	go func() {
		if cfg.Server.HTTPS {
			done <- h.ListenAndServeTLS(cfg.Server.TLSCert, cfg.Server.TLSKey)
			return
		}
		done <- h.ListenAndServe()
	}()
	ticker := time.NewTicker(15 * time.Minute)
	defer ticker.Stop()
	for {
		select {
		case err := <-done:
			if errors.Is(err, http.ErrServerClosed) {
				return nil
			}
			return err
		case <-ticker.C:
			svc.PurgeExpired()
		case <-ctx.Done():
			shutdown, cancel := context.WithTimeout(context.Background(), 30*time.Second)
			defer cancel()
			if err := h.Shutdown(shutdown); err != nil {
				return errors.Join(err, h.Close())
			}
			return nil
		}
	}
}
