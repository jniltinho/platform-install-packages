// Package auth implements console authentication: bcrypt passwords,
// DB-backed revocable sessions with a per-session CSRF token, login
// lockout, and the user management rules (unique e-mail, last admin).
package auth

import (
	"crypto/rand"
	"encoding/hex"
	"errors"
	"fmt"
	"strings"
	"time"

	"golang.org/x/crypto/bcrypt"
	"gorm.io/gorm"
	"gorm.io/gorm/clause"

	"kaltura-console/internal/models"
)

// Errors returned by the service. Handlers map them to HTTP statuses.
var (
	ErrInvalidCredentials = errors.New("auth: invalid e-mail or password")
	ErrLockedOut          = errors.New("auth: too many failed attempts, try again later")
	ErrSessionNotFound    = errors.New("auth: session not found or expired")
	ErrEmailTaken         = errors.New("auth: e-mail already in use")
	ErrLastAdmin          = errors.New("auth: the last admin cannot be removed or demoted")
	ErrSelfDelete         = errors.New("auth: you cannot delete your own account")
	ErrInvalidRole        = errors.New("auth: role must be admin or viewer")
	ErrWeakPassword       = errors.New("auth: password must have at least 8 characters")
	ErrUserNotFound       = errors.New("auth: user not found")
)

const (
	// RememberTTL is the absolute lifetime of a "remember me" session.
	RememberTTL = 30 * 24 * time.Hour
	// LockoutWindow and LockoutMax bound failed logins per e-mail+IP.
	LockoutWindow = 15 * time.Minute
	LockoutMax    = 5
)

// bcryptCost is a variable only so tests can lower it.
var bcryptCost = 12

// Service holds the auth state backed by the console database.
type Service struct {
	db         *gorm.DB
	idleTTL    time.Duration
	absoluteTT time.Duration
	now        func() time.Time
}

// NewService returns an auth service with the given idle and absolute session lifetimes.
func NewService(db *gorm.DB, idleTTL, absoluteTTL time.Duration) *Service {
	if idleTTL <= 0 {
		idleTTL = 2 * time.Hour
	}
	if absoluteTTL <= 0 {
		absoluteTTL = 12 * time.Hour
	}
	return &Service{db: db, idleTTL: idleTTL, absoluteTT: absoluteTTL, now: time.Now}
}

// HashPassword returns the bcrypt hash of a password that passes the policy.
func HashPassword(pw string) (string, error) {
	if len(pw) < 8 {
		return "", ErrWeakPassword
	}
	h, err := bcrypt.GenerateFromPassword([]byte(pw), bcryptCost)
	if err != nil {
		return "", fmt.Errorf("hashing password: %w", err)
	}
	return string(h), nil
}

func randomToken() (string, error) {
	b := make([]byte, 32)
	if _, err := rand.Read(b); err != nil {
		return "", fmt.Errorf("generating token: %w", err)
	}
	return hex.EncodeToString(b), nil
}

func normEmail(e string) string { return strings.ToLower(strings.TrimSpace(e)) }

// dummyHash is compared against when the user does not exist, so login
// timing does not reveal which e-mails are registered.
var dummyHash, _ = bcrypt.GenerateFromPassword([]byte("kaltura-console-dummy"), bcryptCost)

// Login verifies the credentials, enforces the lockout and creates a new
// session (fresh ID and CSRF token — the rotation on login).
func (s *Service) Login(email, password, ip string, remember bool) (*models.Session, *models.User, error) {
	email = normEmail(email)
	since := s.now().Add(-LockoutWindow)
	var failures int64
	if err := s.db.Model(&models.LoginAttempt{}).
		Where("email = ? AND ip = ? AND created_at > ?", email, ip, since).
		Count(&failures).Error; err != nil {
		return nil, nil, err
	}
	if failures >= LockoutMax {
		return nil, nil, ErrLockedOut
	}
	var u models.User
	err := s.db.Where("email = ?", email).First(&u).Error
	hash := dummyHash
	if err == nil {
		hash = []byte(u.PasswordHash)
	} else if !errors.Is(err, gorm.ErrRecordNotFound) {
		return nil, nil, err
	}
	if bcrypt.CompareHashAndPassword(hash, []byte(password)) != nil || err != nil {
		if err := s.db.Create(&models.LoginAttempt{Email: email, IP: ip, CreatedAt: s.now()}).Error; err != nil {
			return nil, nil, err
		}
		return nil, nil, ErrInvalidCredentials
	}
	if err := s.db.Where("email = ? AND ip = ?", email, ip).Delete(&models.LoginAttempt{}).Error; err != nil {
		return nil, nil, err
	}
	sess, err := s.createSession(u.ID, remember)
	if err != nil {
		return nil, nil, err
	}
	return sess, &u, nil
}

func (s *Service) createSession(userID uint, remember bool) (*models.Session, error) {
	id, err := randomToken()
	if err != nil {
		return nil, err
	}
	csrf, err := randomToken()
	if err != nil {
		return nil, err
	}
	now := s.now()
	ttl := s.absoluteTT
	if remember {
		ttl = RememberTTL
	}
	sess := &models.Session{ID: id, UserID: userID, CSRFToken: csrf, Remember: remember,
		CreatedAt: now, LastSeen: now, ExpiresAt: now.Add(ttl)}
	if err := s.db.Create(sess).Error; err != nil {
		return nil, fmt.Errorf("creating session: %w", err)
	}
	return sess, nil
}

// Resolve returns the session and its user, enforcing the absolute expiry
// and (for non-remembered sessions) the idle timeout. It slides LastSeen.
func (s *Service) Resolve(id string) (*models.Session, *models.User, error) {
	if id == "" {
		return nil, nil, ErrSessionNotFound
	}
	var sess models.Session
	if err := s.db.Preload("User").Where("id = ?", id).First(&sess).Error; err != nil {
		if errors.Is(err, gorm.ErrRecordNotFound) {
			return nil, nil, ErrSessionNotFound
		}
		return nil, nil, err
	}
	now := s.now()
	if now.After(sess.ExpiresAt) || (!sess.Remember && now.Sub(sess.LastSeen) > s.idleTTL) {
		s.db.Delete(&models.Session{}, "id = ?", id)
		return nil, nil, ErrSessionNotFound
	}
	if now.Sub(sess.LastSeen) > time.Minute {
		s.db.Model(&models.Session{}).Where("id = ?", id).Update("last_seen", now)
	}
	return &sess, &sess.User, nil
}

// Logout deletes one session.
func (s *Service) Logout(id string) error {
	return s.db.Delete(&models.Session{}, "id = ?", id).Error
}

// RevokeUser deletes every session of a user.
func (s *Service) RevokeUser(userID uint) error {
	return s.db.Delete(&models.Session{}, "user_id = ?", userID).Error
}

// PurgeExpired removes expired sessions and old login attempts.
func (s *Service) PurgeExpired() {
	now := s.now()
	s.db.Delete(&models.Session{}, "expires_at < ?", now)
	s.db.Delete(&models.LoginAttempt{}, "created_at < ?", now.Add(-LockoutWindow))
}

// ---- user management ----

// CountUsers returns the number of accounts.
func (s *Service) CountUsers() (int64, error) {
	var n int64
	err := s.db.Model(&models.User{}).Count(&n).Error
	return n, err
}

// ListUsers returns every account ordered by e-mail.
func (s *Service) ListUsers() ([]models.User, error) {
	var users []models.User
	err := s.db.Order("email").Find(&users).Error
	return users, err
}

// GetUser loads a user by ID.
func (s *Service) GetUser(id uint) (*models.User, error) {
	var u models.User
	if err := s.db.First(&u, id).Error; err != nil {
		if errors.Is(err, gorm.ErrRecordNotFound) {
			return nil, ErrUserNotFound
		}
		return nil, err
	}
	return &u, nil
}

// GetUserByEmail loads a user by e-mail.
func (s *Service) GetUserByEmail(email string) (*models.User, error) {
	var u models.User
	if err := s.db.Where("email = ?", normEmail(email)).First(&u).Error; err != nil {
		if errors.Is(err, gorm.ErrRecordNotFound) {
			return nil, ErrUserNotFound
		}
		return nil, err
	}
	return &u, nil
}

func validRole(r string) bool { return r == models.RoleAdmin || r == models.RoleViewer }

// CreateUser adds an account.
func (s *Service) CreateUser(name, email, password, role string) (*models.User, error) {
	if !validRole(role) {
		return nil, ErrInvalidRole
	}
	email = normEmail(email)
	if email == "" || !strings.Contains(email, "@") {
		return nil, errors.New("auth: a valid e-mail is required")
	}
	hash, err := HashPassword(password)
	if err != nil {
		return nil, err
	}
	if strings.TrimSpace(name) == "" {
		name = email
	}
	u := &models.User{Name: strings.TrimSpace(name), Email: email, PasswordHash: hash, Role: role}
	if err := s.db.Create(u).Error; err != nil {
		if errors.Is(err, gorm.ErrDuplicatedKey) {
			return nil, ErrEmailTaken
		}
		return nil, err
	}
	return u, nil
}

func (s *Service) adminCount(tx *gorm.DB) (int64, error) {
	var n int64
	err := tx.Model(&models.User{}).Where("role = ?", models.RoleAdmin).Count(&n).Error
	return n, err
}

// lockUsers serializes account edits across server processes, before any
// snapshot reads. Locking the whole small account set in primary-key order
// gives deletion and demotion the same lock even when they target different users.
func lockUsers(tx *gorm.DB) error {
	if tx.Name() == "sqlite" {
		// SQLite has no FOR UPDATE; obtain its database write lock before reading.
		return tx.Exec("UPDATE users SET id = id WHERE id = (SELECT MIN(id) FROM users)").Error
	}
	ids := []uint{}
	return tx.Model(&models.User{}).Clauses(clause.Locking{Strength: "UPDATE"}).
		Order("id").Pluck("id", &ids).Error
}

// UpdateUser changes name and/or role. Changing the role revokes the user's sessions.
func (s *Service) UpdateUser(id uint, name, role string) (*models.User, error) {
	return s.UpdateUserWithPassword(id, name, role, "")
}

// UpdateUserWithPassword atomically changes account fields and an optional
// password. A rejected role change leaves both password and sessions intact.
func (s *Service) UpdateUserWithPassword(id uint, name, role, password string) (*models.User, error) {
	var hash string
	if password != "" {
		var err error
		hash, err = HashPassword(password)
		if err != nil {
			return nil, err
		}
	}
	var out *models.User
	err := s.db.Transaction(func(tx *gorm.DB) error {
		if err := lockUsers(tx); err != nil {
			return err
		}
		var u models.User
		if err := tx.First(&u, id).Error; err != nil {
			if errors.Is(err, gorm.ErrRecordNotFound) {
				return ErrUserNotFound
			}
			return err
		}
		if role != "" && role != u.Role {
			if !validRole(role) {
				return ErrInvalidRole
			}
			if u.Role == models.RoleAdmin {
				n, err := s.adminCount(tx)
				if err != nil {
					return err
				}
				if n <= 1 {
					return ErrLastAdmin
				}
			}
			u.Role = role
			if err := tx.Delete(&models.Session{}, "user_id = ?", u.ID).Error; err != nil {
				return err
			}
		}
		if hash != "" {
			u.PasswordHash = hash
			if err := tx.Delete(&models.Session{}, "user_id = ?", u.ID).Error; err != nil {
				return err
			}
		}
		if strings.TrimSpace(name) != "" {
			u.Name = strings.TrimSpace(name)
		}
		if err := tx.Save(&u).Error; err != nil {
			return err
		}
		out = &u
		return nil
	})
	return out, err
}

// SetPassword replaces the password and revokes every session of the user.
func (s *Service) SetPassword(id uint, password string) error {
	hash, err := HashPassword(password)
	if err != nil {
		return err
	}
	return s.db.Transaction(func(tx *gorm.DB) error {
		if err := lockUsers(tx); err != nil {
			return err
		}
		res := tx.Model(&models.User{}).Where("id = ?", id).Update("password_hash", hash)
		if res.Error != nil {
			return res.Error
		}
		if res.RowsAffected == 0 {
			return ErrUserNotFound
		}
		return tx.Delete(&models.Session{}, "user_id = ?", id).Error
	})
}

// DeleteUser removes an account (and its sessions). actorID is the admin
// performing the action; admins cannot delete themselves or the last admin.
func (s *Service) DeleteUser(actorID, id uint) error {
	if actorID == id {
		return ErrSelfDelete
	}
	return s.db.Transaction(func(tx *gorm.DB) error {
		if err := lockUsers(tx); err != nil {
			return err
		}
		var u models.User
		if err := tx.First(&u, id).Error; err != nil {
			if errors.Is(err, gorm.ErrRecordNotFound) {
				return ErrUserNotFound
			}
			return err
		}
		if u.Role == models.RoleAdmin {
			n, err := s.adminCount(tx)
			if err != nil {
				return err
			}
			if n <= 1 {
				return ErrLastAdmin
			}
		}
		if err := tx.Delete(&models.Session{}, "user_id = ?", id).Error; err != nil {
			return err
		}
		return tx.Delete(&u).Error
	})
}
