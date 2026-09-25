package auth

import (
	"testing"
	"time"

	"github.com/stretchr/testify/require"
	"kaltura-console/internal/config"
	"kaltura-console/internal/database"
	"kaltura-console/internal/models"
)

func TestPatchIsAtomic(t *testing.T) {
	s := newSvc(t)
	admin, err := s.CreateUser("Original", "a@example.test", "original-pass", models.RoleAdmin)
	require.NoError(t, err)
	sess, _, err := s.Login(admin.Email, "original-pass", "test", false)
	require.NoError(t, err)
	for _, role := range []string{models.RoleViewer, "invalid"} {
		_, err = s.UpdateUserWithPassword(admin.ID, "Changed", role, "changed-pass")
		require.Error(t, err)
		got, err := s.GetUser(admin.ID)
		require.NoError(t, err)
		require.Equal(t, admin.PasswordHash, got.PasswordHash)
		require.Equal(t, "Original", got.Name)
		_, _, err = s.Resolve(sess.ID)
		require.NoError(t, err)
	}
	_, err = s.UpdateUserWithPassword(admin.ID, "Changed", "", "changed-pass")
	require.NoError(t, err)
	_, _, err = s.Resolve(sess.ID)
	require.ErrorIs(t, err, ErrSessionNotFound)
	_, _, err = s.Login(admin.Email, "changed-pass", "test", false)
	require.NoError(t, err)
}

func testConcurrentLastAdmin(t *testing.T, a, b *Service) {
	t.Helper()
	first, err := a.CreateUser("", "a@example.test", "original-pass", models.RoleAdmin)
	require.NoError(t, err)
	second, err := a.CreateUser("", "b@example.test", "original-pass", models.RoleAdmin)
	require.NoError(t, err)
	start := make(chan struct{})
	results := make(chan error, 2)
	go func() {
		<-start
		_, err := a.UpdateUser(first.ID, "", models.RoleViewer)
		results <- err
	}()
	go func() {
		<-start
		results <- b.DeleteUser(0, second.ID)
	}()
	close(start)
	one, two := <-results, <-results
	if one == nil {
		require.ErrorIs(t, two, ErrLastAdmin)
	} else {
		require.ErrorIs(t, one, ErrLastAdmin)
		require.NoError(t, two)
	}
	n, err := a.adminCount(a.db)
	require.NoError(t, err)
	require.EqualValues(t, 1, n)
}

func TestLastAdminAcrossDatabaseConnections(t *testing.T) {
	cfg := config.DatabaseConfig{Driver: "sqlite", DSN: t.TempDir() + "/shared.db"}
	open := func() *Service {
		db, err := database.Open(cfg)
		require.NoError(t, err)
		sqlDB, err := db.DB()
		require.NoError(t, err)
		t.Cleanup(func() { require.NoError(t, sqlDB.Close()) })
		require.NoError(t, database.Migrate(db))
		return NewService(db, time.Hour, time.Hour)
	}
	testConcurrentLastAdmin(t, open(), open())
}
