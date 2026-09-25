// Package web contains the compiled frontend; Node is not needed at runtime.
package web

import "embed"

// Assets is the frontend distribution.
//
//go:embed all:dist
var Assets embed.FS
