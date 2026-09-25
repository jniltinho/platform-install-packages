#!/usr/bin/env bash
set -euo pipefail
[[ $(hostname) == kaltura-php74-baseline && $(id -u) == 1000 && $# == 2 ]] || exit 64
case "$1" in 74) runtime=/usr/bin/php7.4; extra=(-d extension=json) ;; 83) runtime=/audit/runtime83/php8.3; extra=() ;; *) exit 64 ;; esac
case "$2" in empty|true) ;; *) exit 64 ;; esac
stage=/home/vagrant/php-template-arity-v1
exec sudo -n systemd-run --quiet --wait --pipe --collect \
 -p User=vagrant -p Group=vagrant -p PrivateNetwork=yes \
 -p 'SystemCallFilter=~socket socketpair' -p SystemCallErrorNumber=EPERM \
 -p ProtectSystem=strict -p ProtectHome=yes -p PrivateTmp=yes -p PrivateDevices=yes \
 -p NoNewPrivileges=yes -p MemoryMax=128M -p RuntimeMaxSec=20 \
 -p 'InaccessiblePaths=-/opt/kaltura /root -/run/mysqld -/var/lib/mysql' \
 -p "BindReadOnlyPaths=$stage/$2.php:/audit/case.php /home/vagrant/php-mysql-probe/runtime83:/audit/runtime83" \
 /usr/bin/env -i PATH=/usr/bin:/bin LC_ALL=C TZ=UTC "$runtime" -n "${extra[@]}" \
 -d error_reporting=32767 -d display_errors=stderr -d log_errors=0 \
 -d allow_url_fopen=0 -d allow_url_include=0 /audit/case.php
