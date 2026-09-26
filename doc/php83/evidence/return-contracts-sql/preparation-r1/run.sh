#!/usr/bin/env bash
set -euo pipefail
[[ $# == 4 && $(hostname) == kaltura-php74-baseline && $(id -u) == 1000 ]] || exit 64
[[ $1 =~ ^/home/vagrant/php-return-sql\.[a-f0-9]{32}$ && $3 =~ ^[a-f0-9]{32}$ && $4 =~ ^[a-f0-9]{64}$ ]] || exit 64
case $2 in prerequisite|candidate) ;; *) exit 64;; esac
base=$1; variant=$2; db=/tmp/kaltura-return-sql.$3;pin=$4
[[ -d $base && ! -L $base && -S $db/mysql.sock && ! -L $db/mysql.sock && $(realpath "$db") == "$db" ]] || exit 64
verify(){ python3 "$base/verify.py" "$base" "$pin" >/dev/null; }
verify
finish(){ status=$?;trap - EXIT;verify || exit 70;exit "$status"; };trap finish EXIT
sudo -n systemd-run --quiet --wait --pipe --collect \
 -p User=vagrant -p Group=vagrant -p PrivateNetwork=yes -p RestrictAddressFamilies=AF_UNIX \
 -p ProtectSystem=strict -p ProtectHome=yes -p PrivateTmp=yes -p PrivateDevices=yes \
 -p NoNewPrivileges=yes -p MemoryMax=512M -p RuntimeMaxSec=90 \
 -p 'InaccessiblePaths=-/opt/kaltura /root -/run/mysqld -/var/lib/mysql' \
 -p "BindReadOnlyPaths=$base:/audit/probe $base/$variant:/audit/app /home/vagrant/php-mysql-probe/runtime83:/audit/runtime83 $db:/audit/db" \
 /usr/bin/env "PHP83_PROBE_DATADIR=$db/data/" /audit/runtime83/php8.3 -n \
 -d extension=/audit/runtime83/mysqlnd.so -d extension=/audit/runtime83/pdo.so -d extension=/audit/runtime83/pdo_mysql.so \
 -d display_errors=stderr -d log_errors=0 -d allow_url_fopen=0 -d allow_url_include=0 -d date.timezone=UTC /audit/probe/probe.php
