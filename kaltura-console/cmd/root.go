// Package cmd defines the operational CLI for Kaltura Console.
package cmd

import (
	"bufio"
	"errors"
	"fmt"
	"os"
	"strings"

	"github.com/spf13/cobra"
	"golang.org/x/term"
	"gorm.io/gorm"

	"kaltura-console/internal/auth"
	"kaltura-console/internal/buildinfo"
	"kaltura-console/internal/config"
	"kaltura-console/internal/database"
)

// Execute runs a fresh command tree.
func Execute() error { return newRoot().Execute() }

func newRoot() *cobra.Command {
	var path string
	var cfg *config.Config
	root := &cobra.Command{Use: "kaltura-console", Short: "Kaltura media console", SilenceUsage: true, SilenceErrors: true}
	root.PersistentFlags().StringVar(&path, "config", "", "configuration file")
	root.PersistentPreRunE = func(c *cobra.Command, _ []string) error {
		if c.Name() == "version" || c.Name() == "init" {
			return nil
		}
		var err error
		cfg, err = config.Load(path)
		return err
	}
	root.AddCommand(&cobra.Command{Use: "version", Args: cobra.NoArgs, RunE: func(c *cobra.Command, _ []string) error {
		_, err := fmt.Fprintf(c.OutOrStdout(), "%s commit=%s built=%s\n", buildinfo.Version, buildinfo.GitCommit, buildinfo.BuildDate)
		return err
	}})
	conf := &cobra.Command{Use: "config"}
	var output string
	initCmd := &cobra.Command{Use: "init", Args: cobra.NoArgs, RunE: func(c *cobra.Command, _ []string) error {
		f, err := os.OpenFile(output, os.O_WRONLY|os.O_CREATE|os.O_EXCL, 0o600)
		if err != nil {
			return fmt.Errorf("creating configuration: %w", err)
		}
		_, writeErr := f.Write(config.Example)
		return errors.Join(writeErr, f.Close())
	}}
	initCmd.Flags().StringVar(&output, "output", "config.toml", "new configuration path (never overwritten)")
	conf.AddCommand(initCmd)
	root.AddCommand(conf)
	withDB := func(fn func(*cobra.Command, *gorm.DB, *auth.Service) error) func(*cobra.Command, []string) error {
		return func(c *cobra.Command, _ []string) (runErr error) {
			db, err := database.Open(cfg.Database)
			if err != nil {
				return err
			}
			sqlDB, err := db.DB()
			if err != nil {
				return err
			}
			defer func() {
				if err := sqlDB.Close(); err != nil {
					runErr = errors.Join(runErr, fmt.Errorf("closing database: %w", err))
				}
			}()
			if err := database.Migrate(db); err != nil {
				return err
			}
			return fn(c, db, auth.NewService(db, cfg.Server.SessionTTL, cfg.Server.SessionMax))
		}
	}
	root.AddCommand(&cobra.Command{Use: "migrate", Args: cobra.NoArgs, RunE: withDB(func(*cobra.Command, *gorm.DB, *auth.Service) error { return nil })})
	serveCmd := &cobra.Command{Use: "serve", Args: cobra.NoArgs, RunE: func(c *cobra.Command, args []string) error {
		applyServerFlags(c, &cfg.Server)
		if err := cfg.Validate(); err != nil {
			return err
		}
		return withDB(func(c *cobra.Command, db *gorm.DB, svc *auth.Service) error { return serve(c, cfg, db, svc) })(c, args)
	}}
	serveCmd.Flags().Bool("https", false, "serve standalone HTTPS")
	serveCmd.Flags().String("tls-cert", "", "TLS certificate file")
	serveCmd.Flags().String("tls-key", "", "TLS private key file")
	serveCmd.Flags().String("tls-dir", "", "self-signed certificate storage directory")
	serveCmd.Flags().String("base-path", "", "URL prefix, e.g. /console (proxy must preserve it)")
	root.AddCommand(serveCmd)
	users := &cobra.Command{Use: "user", Short: "Manage local users"}
	for _, operation := range []string{"add", "passwd", "delete", "list"} {
		var email, name, role string
		var stdin bool
		sub := &cobra.Command{Use: operation, Args: cobra.NoArgs}
		if operation != "list" {
			sub.Flags().StringVar(&email, "email", "", "user e-mail")
			if err := sub.MarkFlagRequired("email"); err != nil {
				panic(err)
			}
		}
		if operation == "add" {
			sub.Flags().StringVar(&name, "name", "", "display name")
			sub.Flags().StringVar(&role, "role", "viewer", "admin or viewer")
		}
		if operation == "add" || operation == "passwd" {
			sub.Flags().BoolVar(&stdin, "password-stdin", false, "read password from stdin instead of a terminal")
		}
		sub.RunE = withDB(func(c *cobra.Command, _ *gorm.DB, svc *auth.Service) error {
			if operation == "list" {
				all, err := svc.ListUsers()
				if err != nil {
					return err
				}
				for _, u := range all {
					if _, err := fmt.Fprintf(c.OutOrStdout(), "%d\t%s\t%s\n", u.ID, u.Email, u.Role); err != nil {
						return err
					}
				}
				return nil
			}
			if operation == "add" {
				pw, err := password(c, stdin)
				if err != nil {
					return err
				}
				_, err = svc.CreateUser(name, email, pw, role)
				return err
			}
			u, err := svc.GetUserByEmail(email)
			if err != nil {
				return err
			}
			if operation == "delete" {
				return svc.DeleteUser(0, u.ID)
			}
			pw, err := password(c, stdin)
			if err != nil {
				return err
			}
			return svc.SetPassword(u.ID, pw)
		})
		users.AddCommand(sub)
	}
	root.AddCommand(users)
	return root
}

func password(c *cobra.Command, stdin bool) (string, error) {
	if stdin {
		scanner := bufio.NewScanner(c.InOrStdin())
		if !scanner.Scan() {
			return "", errors.New("password input is empty")
		}
		return strings.TrimSuffix(scanner.Text(), "\r"), scanner.Err()
	}
	f, ok := c.InOrStdin().(*os.File)
	if !ok || !term.IsTerminal(int(f.Fd())) {
		return "", errors.New("password requires a terminal or --password-stdin")
	}
	if _, err := fmt.Fprint(c.ErrOrStderr(), "Password: "); err != nil {
		return "", err
	}
	b, err := term.ReadPassword(int(f.Fd()))
	if _, printErr := fmt.Fprintln(c.ErrOrStderr()); printErr != nil {
		return "", printErr
	}
	return string(b), err
}

func applyServerFlags(c *cobra.Command, cfg *config.ServerConfig) {
	if c.Flags().Changed("https") {
		cfg.HTTPS, _ = c.Flags().GetBool("https")
	}
	for name, target := range map[string]*string{"tls-cert": &cfg.TLSCert, "tls-key": &cfg.TLSKey, "tls-dir": &cfg.TLSDir, "base-path": &cfg.BasePath} {
		if c.Flags().Changed(name) {
			*target, _ = c.Flags().GetString(name)
		}
	}
}
