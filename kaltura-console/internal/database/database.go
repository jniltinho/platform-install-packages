// Package database opens the console database (pure-Go SQLite or
// MariaDB/MySQL) and applies versioned migrations with gormigrate.
package database

import (
	"fmt"
	"os"
	"path/filepath"
	"time"

	"github.com/glebarez/sqlite"
	"github.com/go-gormigrate/gormigrate/v2"
	"gorm.io/driver/mysql"
	"gorm.io/gorm"
	"gorm.io/gorm/logger"

	"kaltura-console/internal/config"
	"kaltura-console/internal/models"
)

// Open connects to the configured database. SQLite runs with WAL, a busy
// timeout and foreign keys on, through a single connection so writes never
// contend with each other.
func Open(cfg config.DatabaseConfig) (*gorm.DB, error) {
	gcfg := &gorm.Config{Logger: logger.Default.LogMode(logger.Silent), TranslateError: true}
	if cfg.Debug {
		gcfg.Logger = logger.Default.LogMode(logger.Info)
	}
	var dialector gorm.Dialector
	switch cfg.Driver {
	case "sqlite":
		if dir := filepath.Dir(cfg.DSN); cfg.DSN != ":memory:" && dir != "." {
			if err := os.MkdirAll(dir, 0o750); err != nil {
				return nil, fmt.Errorf("creating database directory: %w", err)
			}
		}
		dialector = sqlite.Open(cfg.DSN + "?_pragma=busy_timeout(5000)&_pragma=journal_mode(WAL)&_pragma=foreign_keys(1)")
	case "mysql":
		dialector = mysql.Open(cfg.DSN)
	default:
		return nil, fmt.Errorf("unsupported database driver %q", cfg.Driver)
	}
	db, err := gorm.Open(dialector, gcfg)
	if err != nil {
		return nil, fmt.Errorf("opening %s database: %w", cfg.Driver, err)
	}
	sqlDB, err := db.DB()
	if err != nil {
		return nil, err
	}
	if cfg.Driver == "sqlite" {
		sqlDB.SetMaxOpenConns(1)
	} else {
		sqlDB.SetMaxOpenConns(10)
		sqlDB.SetMaxIdleConns(5)
		sqlDB.SetConnMaxLifetime(5 * time.Minute)
	}
	return db, nil
}

// migrations is the ordered, append-only schema history. Never edit a
// released migration: add a new one.
func migrations() []*gormigrate.Migration {
	return []*gormigrate.Migration{
		{
			ID: "202609250001_init",
			Migrate: func(tx *gorm.DB) error {
				return tx.AutoMigrate(&models.User{}, &models.Session{}, &models.LoginAttempt{})
			},
			Rollback: func(tx *gorm.DB) error {
				return tx.Migrator().DropTable(&models.LoginAttempt{}, &models.Session{}, &models.User{})
			},
		},
	}
}

// Migrate applies pending migrations inside a transaction and records them
// in the migrations table. It is idempotent.
func Migrate(db *gorm.DB) error {
	opts := *gormigrate.DefaultOptions
	opts.UseTransaction = true
	m := gormigrate.New(db, &opts, migrations())
	if err := m.Migrate(); err != nil {
		return fmt.Errorf("applying migrations: %w", err)
	}
	return nil
}
