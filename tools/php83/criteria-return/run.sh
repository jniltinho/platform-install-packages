#!/usr/bin/env bash
set -euo pipefail
case "$(hostname)" in kaltura-php74-baseline) php=/usr/bin/php7.4;; kaltura-php83-lab) php=/usr/bin/php8.3;; *) exit 64;; esac
case "${1:-}" in previous) ;; candidate) [[ $php == /usr/bin/php8.3 ]] || exit 64;; *) exit 64;; esac
base=/home/vagrant/php-criteria-return
exec sudo systemd-run --quiet --wait --pipe --collect \
 -p User=nobody -p Group=nogroup -p PrivateNetwork=yes \
 -p 'SystemCallFilter=~socket socketpair' -p SystemCallErrorNumber=EPERM \
 -p PrivateDevices=yes -p ProtectSystem=strict -p ProtectHome=yes -p PrivateTmp=yes \
 -p NoNewPrivileges=yes -p 'InaccessiblePaths=-/opt/kaltura /root' \
 -p "BindReadOnlyPaths=$base:/audit/probe $base/$1.php:/audit/Criteria.php /home/vagrant/php-exp7-regression/source/server-Rigel-18.20.0:/audit/app" \
 -p MemoryMax=128M -p RuntimeMaxSec=30 \
 "$php" -d log_errors=0 -d opcache.enable_cli=0 -d allow_url_fopen=0 -d allow_url_include=0 \
 /audit/probe/probe.php /audit/Criteria.php
