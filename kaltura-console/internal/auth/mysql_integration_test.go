//go:build integration

package auth

import (
	"os"
	"strings"
	"testing"
	"time"

	"github.com/go-sql-driver/mysql"
	"github.com/stretchr/testify/require"
	"kaltura-console/internal/config"
	"kaltura-console/internal/database"
	"kaltura-console/internal/models"
)

// TestMariaDBConcurrentLastAdmin requires a dedicated empty database named
// kconsole_test_* and KCONSOLE_TEST_MYSQL_DSN (with parseTime=true).
// It uses independent pools to exercise cross-process-equivalent row locking.
func TestMariaDBConcurrentLastAdmin(t *testing.T) {
	dsn := os.Getenv("KCONSOLE_TEST_MYSQL_DSN")
	if dsn == "" {
		t.Skip("KCONSOLE_TEST_MYSQL_DSN is not set")
	}
	parsed, err := mysql.ParseDSN(dsn)
	require.NoError(t, err)
	require.True(t, strings.HasPrefix(parsed.DBName, "kconsole_test_"),
		"integration test requires a dedicated kconsole_test_* database")
	open := func() *Service {
		db, err := database.Open(config.DatabaseConfig{Driver: "mysql", DSN: dsn})
		require.NoError(t, err)
		sqlDB, err := db.DB()
		require.NoError(t, err)
		t.Cleanup(func() { require.NoError(t, sqlDB.Close()) })
		return NewService(db, time.Hour, time.Hour)
	}
	a, b := open(), open()
	require.NoError(t, database.Migrate(a.db))
	count, err := a.CountUsers()
	require.NoError(t, err)
	require.Zero(t, count, "test database must contain no users")
	t.Cleanup(func() {
		require.NoError(t, a.db.Where("email IN ?", []string{"a@example.test", "b@example.test"}).
			Delete(&models.User{}).Error)
	})
	testConcurrentLastAdmin(t, a, b)
}
