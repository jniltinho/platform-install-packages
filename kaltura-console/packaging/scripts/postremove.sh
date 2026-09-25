#!/bin/sh
set -eu
if [ "${1:-}" = purge ]; then
    # Explicit Debian purge removes only this application's state.
    rm -rf /var/lib/kaltura-console
fi
if [ -d /run/systemd/system ]; then systemctl daemon-reload; fi
