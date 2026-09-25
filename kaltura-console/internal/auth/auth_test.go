package auth

import (
	"path/filepath"
	"testing"
	"time"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
	"golang.org/x/crypto/bcrypt"

	"kaltura-console/internal/config"
	"kaltura-console/internal/database"
	"kaltura-console/internal/models"
)

// Keep tests fast; production uses cost 12.
func init() {
	bcryptCost = bcrypt.MinCost
	dummyHash, _ = bcrypt.GenerateFromPassword([]byte("x"), bcrypt.MinCost)
}

func newSvc(t *testing.T) *Service {
	t.Helper()
	db, err := database.Open(config.DatabaseConfig{Driver: "sqlite", DSN: filepath.Join(t.TempDir(), "a.db")})
	require.NoError(t, err)
	require.NoError(t, database.Migrate(db))
	return NewService(db, time.Hour, 12*time.Hour)
}

func TestLoginFlowAndRotation(t *testing.T) {
	s := newSvc(t)
	_, err := s.CreateUser("Ana", "Ana@Example.com", "Str0ng#pass", models.RoleAdmin)
	require.NoError(t, err)

	s1, u, err := s.Login("ana@example.com", "Str0ng#pass", "10.0.0.1", false)
	require.NoError(t, err)
	assert.Equal(t, "ana@example.com", u.Email)
	s2, _, err := s.Login("ana@example.com", "Str0ng#pass", "10.0.0.1", false)
	require.NoError(t, err)
	assert.NotEqual(t, s1.ID, s2.ID, "every login gets a fresh session id")
	assert.NotEqual(t, s1.CSRFToken, s2.CSRFToken)

	_, got, err := s.Resolve(s1.ID)
	require.NoError(t, err)
	assert.Equal(t, u.ID, got.ID)

	require.NoError(t, s.Logout(s1.ID))
	_, _, err = s.Resolve(s1.ID)
	assert.ErrorIs(t, err, ErrSessionNotFound)
}

func TestWrongPasswordAndLockout(t *testing.T) {
	s := newSvc(t)
	_, err := s.CreateUser("", "bob@x.io", "Str0ng#pass", models.RoleViewer)
	require.NoError(t, err)
	for i := 0; i < LockoutMax; i++ {
		_, _, err := s.Login("bob@x.io", "wrong", "1.2.3.4", false)
		assert.ErrorIs(t, err, ErrInvalidCredentials)
	}
	_, _, err = s.Login("bob@x.io", "Str0ng#pass", "1.2.3.4", false)
	assert.ErrorIs(t, err, ErrLockedOut, "correct password is not checked while locked out")
	_, _, err = s.Login("bob@x.io", "Str0ng#pass", "5.6.7.8", false)
	assert.NoError(t, err, "lockout is per e-mail+IP")

	_, _, err = s.Login("ghost@x.io", "whatever", "1.1.1.1", false)
	assert.ErrorIs(t, err, ErrInvalidCredentials)
}

func TestIdleAndAbsoluteExpiry(t *testing.T) {
	s := newSvc(t)
	_, err := s.CreateUser("", "c@x.io", "Str0ng#pass", models.RoleViewer)
	require.NoError(t, err)
	base := time.Now()
	s.now = func() time.Time { return base }
	sess, _, err := s.Login("c@x.io", "Str0ng#pass", "ip", false)
	require.NoError(t, err)
	s.now = func() time.Time { return base.Add(2 * time.Hour) }
	_, _, err = s.Resolve(sess.ID)
	assert.ErrorIs(t, err, ErrSessionNotFound, "idle timeout")

	s.now = func() time.Time { return base }
	rem, _, err := s.Login("c@x.io", "Str0ng#pass", "ip", true)
	require.NoError(t, err)
	s.now = func() time.Time { return base.Add(10 * 24 * time.Hour) }
	_, _, err = s.Resolve(rem.ID)
	assert.NoError(t, err, "remembered sessions ignore the idle timeout")
	s.now = func() time.Time { return base.Add(31 * 24 * time.Hour) }
	_, _, err = s.Resolve(rem.ID)
	assert.ErrorIs(t, err, ErrSessionNotFound, "absolute cap")
}

func TestRevocationOnPasswordAndRoleChange(t *testing.T) {
	s := newSvc(t)
	admin, _ := s.CreateUser("", "admin@x.io", "Str0ng#pass", models.RoleAdmin)
	_, _ = s.CreateUser("", "admin2@x.io", "Str0ng#pass", models.RoleAdmin)
	sess, _, err := s.Login("admin@x.io", "Str0ng#pass", "ip", false)
	require.NoError(t, err)
	require.NoError(t, s.SetPassword(admin.ID, "N3w#password"))
	_, _, err = s.Resolve(sess.ID)
	assert.ErrorIs(t, err, ErrSessionNotFound)

	sess, _, err = s.Login("admin@x.io", "N3w#password", "ip", false)
	require.NoError(t, err)
	_, err = s.UpdateUser(admin.ID, "", models.RoleViewer)
	require.NoError(t, err)
	_, _, err = s.Resolve(sess.ID)
	assert.ErrorIs(t, err, ErrSessionNotFound)
}

func TestUserRules(t *testing.T) {
	s := newSvc(t)
	a, err := s.CreateUser("", "a@x.io", "Str0ng#pass", models.RoleAdmin)
	require.NoError(t, err)
	v, err := s.CreateUser("", "v@x.io", "Str0ng#pass", models.RoleViewer)
	require.NoError(t, err)

	_, err = s.CreateUser("", "A@X.io", "Str0ng#pass", models.RoleViewer)
	assert.ErrorIs(t, err, ErrEmailTaken)
	_, err = s.CreateUser("", "z@x.io", "short", models.RoleViewer)
	assert.ErrorIs(t, err, ErrWeakPassword)
	_, err = s.CreateUser("", "z@x.io", "Str0ng#pass", "root")
	assert.ErrorIs(t, err, ErrInvalidRole)

	_, err = s.UpdateUser(a.ID, "", models.RoleViewer)
	assert.ErrorIs(t, err, ErrLastAdmin)
	assert.ErrorIs(t, s.DeleteUser(v.ID, a.ID), ErrLastAdmin)
	assert.ErrorIs(t, s.DeleteUser(a.ID, a.ID), ErrSelfDelete)
	assert.NoError(t, s.DeleteUser(a.ID, v.ID))
	_, err = s.GetUser(v.ID)
	assert.ErrorIs(t, err, ErrUserNotFound)
}
