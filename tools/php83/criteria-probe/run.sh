#!/usr/bin/env bash
set -euo pipefail
case "$(hostname)" in
 kaltura-php74-baseline) php=/usr/bin/php7.4;;
 kaltura-php83-lab) php=/usr/bin/php8.3;;
 *) exit 64;;
esac
case "${1:-}" in original|candidate) ;; *) exit 64;; esac
ini=(); [[ "$php" != /usr/bin/php7.4 ]] || ini=(-d extension=json)
base=/home/vagrant/php-criteria-null-probe
exec sudo systemd-run --quiet --wait --pipe --collect \
 -p User=nobody -p Group=nogroup -p PrivateNetwork=yes \
 -p 'SystemCallFilter=~socket socketpair' -p SystemCallErrorNumber=EPERM \
 -p PrivateDevices=yes -p ProtectSystem=strict -p ProtectHome=yes \
 -p PrivateTmp=yes -p NoNewPrivileges=yes -p 'InaccessiblePaths=-/opt/kaltura /root' \
 -p "BindReadOnlyPaths=$base:/audit" -p MemoryMax=128M -p RuntimeMaxSec=30 \
 "$php" -n "${ini[@]}" -d log_errors=0 -d opcache.enable_cli=0 /audit/probe.php "/audit/$1.php"
