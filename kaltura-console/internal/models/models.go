// Package models defines the console's own tables: local users, their
// server-side sessions and login attempts used for brute-force lockout.
// Kaltura data (entries, flavors) is never stored locally.
package models

import "time"

// Role values of User.Role.
const (
	RoleAdmin  = "admin"
	RoleViewer = "viewer"
)

// User is a console account (not a Kaltura user).
type User struct {
	ID           uint      `gorm:"primaryKey" json:"id"`
	Name         string    `gorm:"size:255;not null" json:"name"`
	Email        string    `gorm:"size:255;not null;uniqueIndex" json:"email"`
	PasswordHash string    `gorm:"size:255;not null" json:"-"`
	Role         string    `gorm:"size:16;not null;default:viewer" json:"role"`
	CreatedAt    time.Time `json:"created_at"`
	UpdatedAt    time.Time `json:"updated_at"`
}

// IsAdmin reports whether the user may change data.
func (u *User) IsAdmin() bool { return u.Role == RoleAdmin }

// Session is a server-side login session referenced by an opaque cookie.
type Session struct {
	ID        string    `gorm:"primaryKey;size:64"`
	UserID    uint      `gorm:"not null;index"`
	User      User      `gorm:"constraint:OnDelete:CASCADE"`
	CSRFToken string    `gorm:"size:64;not null"`
	Remember  bool      `gorm:"not null;default:false"`
	CreatedAt time.Time `gorm:"not null"`
	LastSeen  time.Time `gorm:"not null"`
	ExpiresAt time.Time `gorm:"not null;index"`
}

// LoginAttempt records a failed login for lockout accounting.
type LoginAttempt struct {
	ID        uint      `gorm:"primaryKey"`
	Email     string    `gorm:"size:255;not null;index:idx_attempt_key"`
	IP        string    `gorm:"size:64;not null;index:idx_attempt_key"`
	CreatedAt time.Time `gorm:"not null;index"`
}
