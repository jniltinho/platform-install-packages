package database

import (
	"path/filepath"
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"

	"kaltura-console/internal/config"
	"kaltura-console/internal/models"
)

func TestSQLiteMigrateIsIdempotentAndEnforcesConstraints(t *testing.T) {
	db, err := Open(config.DatabaseConfig{Driver: "sqlite", DSN: filepath.Join(t.TempDir(), "sub", "c.db")})
	require.NoError(t, err)
	require.NoError(t, Migrate(db))
	require.NoError(t, Migrate(db)) // second run is a no-op

	u := models.User{Name: "A", Email: "a@x", PasswordHash: "h", Role: models.RoleAdmin}
	require.NoError(t, db.Create(&u).Error)
	dup := models.User{Name: "B", Email: "a@x", PasswordHash: "h"}
	assert.Error(t, db.Create(&dup).Error, "email must be unique")

	var fk int
	require.NoError(t, db.Raw("PRAGMA foreign_keys").Scan(&fk).Error)
	assert.Equal(t, 1, fk)
}

func TestUnsupportedDriver(t *testing.T) {
	_, err := Open(config.DatabaseConfig{Driver: "postgres"})
	assert.Error(t, err)
}
