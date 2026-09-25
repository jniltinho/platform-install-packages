package config

import _ "embed"

// Example is the initial configuration installed by config init.
//
//go:embed example.toml
var Example []byte
