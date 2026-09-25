// Package buildinfo holds version metadata injected at build time via
// -ldflags "-X kaltura-console/internal/buildinfo.Version=…".
package buildinfo

var (
	// Version is the release version (git tag without the kaltura-console/v prefix).
	Version = "dev"
	// GitCommit is the short commit hash of the build.
	GitCommit = "unknown"
	// BuildDate is the UTC build timestamp.
	BuildDate = "unknown"
)
