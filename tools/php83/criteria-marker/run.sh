#!/usr/bin/env bash
set -euo pipefail
[[ $# == 2 && $2 =~ ^[0-9a-f]{64}$ ]] || exit 64
case "$1" in original|declaration) ;; *) exit 64;; esac
case "$(hostname)" in kaltura-php74-baseline) php=/usr/bin/php7.4; extra=(-d extension=json);; kaltura-php83-lab) php=/usr/bin/php8.3; extra=();; *) exit 64;; esac
base=/home/vagrant/php-criteria-marker
cd "$base"
# Expected manifest hash is supplied by the parent host, never learned remotely.
pin=$2
verify() { python3 "$base/verify.py" "$base" "$pin"; }
verify
finish() { status=$?; trap - EXIT; verify || exit 70; exit "$status"; }
trap finish EXIT
sudo systemd-run --quiet --wait --pipe --collect \
 -p User=nobody -p Group=nogroup -p PrivateNetwork=yes \
 -p 'SystemCallFilter=~socket socketpair' -p SystemCallErrorNumber=EPERM \
 -p PrivateDevices=yes -p ProtectSystem=strict -p ProtectHome=yes -p PrivateTmp=yes \
 -p NoNewPrivileges=yes -p 'InaccessiblePaths=-/opt/kaltura /root' \
 -p "BindReadOnlyPaths=$base:/audit/probe" -p MemoryMax=128M -p RuntimeMaxSec=30 \
 "$php" -n "${extra[@]}" -d display_errors=stderr -d log_errors=0 -d allow_url_fopen=0 -d allow_url_include=0 \
 /audit/probe/probe.php "$1"
