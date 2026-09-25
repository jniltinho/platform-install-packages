#!/usr/bin/env bash
set -euo pipefail
case "$(hostname)" in
 kaltura-php74-baseline) php=/usr/bin/php7.4;;
 kaltura-php83-lab) php=/usr/bin/php8.3;;
 *) exit 64;;
esac
case "${1:-}" in native) args=();; candidate) args=(/audit/candidate.php);; *) exit 64;; esac
exec sudo systemd-run --quiet --wait --pipe --collect \
 -p User=nobody -p Group=nogroup -p PrivateNetwork=yes \
 -p 'SystemCallFilter=~socket socketpair' -p SystemCallErrorNumber=EPERM \
 -p PrivateDevices=yes -p ProtectSystem=strict -p ProtectHome=yes -p PrivateTmp=yes \
 -p NoNewPrivileges=yes -p 'InaccessiblePaths=-/opt/kaltura /root' \
 -p BindReadOnlyPaths=/home/vagrant/php-reflection-probe:/audit \
 -p MemoryMax=128M -p RuntimeMaxSec=30 \
 "$php" -d log_errors=0 -d opcache.enable_cli=0 /audit/native.php "${args[@]}"
