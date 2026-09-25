#!/bin/sh
set -eu
# Debian upgrade and RPM upgrade leave the running service for postinstall restart.
case "${1:-}" in upgrade|1) exit 0 ;; esac
if [ -d /run/systemd/system ]; then
    systemctl stop kaltura-console.service
    systemctl disable kaltura-console.service
fi
