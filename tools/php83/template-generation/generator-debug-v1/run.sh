#!/usr/bin/env bash
set -euo pipefail
[[ $(hostname) == kaltura-php74-baseline && $(id -u) == 1000 && $# == 4 ]] || exit 64
case "$1" in 74) runtime=/usr/bin/php7.4; extra=(-d extension=json) ;; 83) runtime=/audit/runtime83/php8.3; extra=() ;; *) exit 64 ;; esac
case "$2" in prerequisite|debug) ;; *) exit 64 ;; esac
case "$3" in method|generate|negative) [[ "$4" =~ ^[a-z-]+$ ]] || exit 64; invocation=(/audit/probe.php "$3" "$4") ;; lint) [[ "$4" == stdin ]] || exit 64; invocation=(-l) ;; *) exit 64 ;; esac
stage=/home/vagrant/php-generator-debug-v1
exec sudo -n systemd-run --quiet --wait --pipe --collect \
 -p User=vagrant -p Group=vagrant -p PrivateNetwork=yes \
 -p 'SystemCallFilter=~socket socketpair' -p SystemCallErrorNumber=EPERM \
 -p ProtectSystem=strict -p ProtectHome=yes -p PrivateTmp=yes -p PrivateDevices=yes \
 -p NoNewPrivileges=yes -p MemoryMax=256M -p RuntimeMaxSec=45 \
 -p 'InaccessiblePaths=-/opt/kaltura /root -/run/mysqld -/var/lib/mysql' \
 -p "BindReadOnlyPaths=$stage/$2:/audit/source $stage/probe.php:/audit/probe.php /home/vagrant/php-mysql-probe/runtime83:/audit/runtime83" \
 /usr/bin/env -i PATH=/usr/bin:/bin LC_ALL=C TZ=UTC "$runtime" -n "${extra[@]}" \
 -d error_reporting=32767 -d display_errors=stderr -d log_errors=0 \
 -d allow_url_fopen=0 -d allow_url_include=0 "${invocation[@]}"
