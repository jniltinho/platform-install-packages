#!/usr/bin/env bash
set -euo pipefail
# Requires an already installed/configured isolated test console and agent-browser.
# E2E_BASE_URL, E2E_EMAIL, E2E_PASSWORD_FILE and E2E_VIDEO are required.
cd "$(dirname "$0")/.."
exec python3 tests/e2e.py
