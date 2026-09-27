#!/usr/bin/env bash
set -euo pipefail
[[ $# == 4 && $(hostname) == kaltura-php74-baseline && $(id -u) == 1000 ]] || exit 64
[[ $1 =~ ^/home/vagrant/php-display-sql\.[a-f0-9]{32}$ && $3 =~ ^[a-f0-9]{32}$ && $4 =~ ^[a-f0-9]{64}$ ]] || exit 64
base=$1; cohort=$2; db=/tmp/kaltura-display-sql.$3; pin=$4
case $cohort in
 original74) src=original/original.php; engine=74; mode=before;;
 display74) src=original/KalturaStatement.php; engine=74; mode=display;;
 exp14statement83) src=exp14/original.php; engine=83; mode=before;;
 display83) src=exp14/KalturaStatement.php; engine=83; mode=display;;
 *) exit 64;;
esac
[[ -d $base && ! -L $base && -S $db/mysql.sock && ! -L $db/mysql.sock && $(realpath "$db") == "$db" ]] || exit 64
verify(){ python3 -B "$base/verify.py" "$base" "$pin" >/dev/null; }
verify
finish(){ status=$?;trap - EXIT;verify || exit 70;exit "$status"; };trap finish EXIT
if [[ $engine == 74 ]]; then
 php=/usr/bin/php7.4; modules=/usr/lib/php/20190902; flags=(-d extension=$modules/json.so)
else
 php=/audit/runtime83/php8.3; modules=/audit/runtime83; flags=()
fi
sudo -n systemd-run --quiet --wait --pipe --collect \
 -p User=vagrant -p Group=vagrant -p PrivateNetwork=yes -p RestrictAddressFamilies=AF_UNIX \
 -p ProtectSystem=strict -p ProtectHome=yes -p PrivateTmp=yes -p PrivateDevices=yes \
 -p NoNewPrivileges=yes -p MemoryMax=512M -p RuntimeMaxSec=90 \
 -p 'InaccessiblePaths=-/opt/kaltura /root -/run/mysqld -/var/lib/mysql' \
 -p "BindReadOnlyPaths=$base:/audit/probe /home/vagrant/php-mysql-probe/runtime83:/audit/runtime83 $db:/audit/db" \
 /usr/bin/env "PHP83_PROBE_DATADIR=$db/data/" "$php" -n "${flags[@]}" \
 -d extension=$modules/mysqlnd.so -d extension=$modules/pdo.so -d extension=$modules/pdo_mysql.so \
 -d error_reporting=-1 -d display_errors=stderr -d log_errors=0 -d allow_url_fopen=0 -d allow_url_include=0 \
 -d date.timezone=UTC /audit/probe/probe.php "/audit/probe/$src" "$mode"
