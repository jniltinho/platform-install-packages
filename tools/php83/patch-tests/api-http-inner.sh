#!/usr/bin/env bash
set -euo pipefail
umask 077
unset PHP_CLI_SERVER_WORKERS
log=$(mktemp)
"$@" -S 127.0.0.1:18383 /audit/tests/api-http-router.php >"$log" 2>&1 &
server=$!
cleanup() { kill "$server" 2>/dev/null || true; wait "$server" 2>/dev/null || true; cat "$log" >&2; rm -f "$log"; }
trap cleanup EXIT
# Wait for TCP availability, without making a fixture request.
python3 - <<'PY'
import socket,time
for _ in range(100):
 try:
  with socket.create_connection(('127.0.0.1',18383),timeout=.1): break
 except OSError: time.sleep(.05)
else: raise RuntimeError('HTTP probe did not start')
PY
python3 /audit/tests/api-http-client.py
