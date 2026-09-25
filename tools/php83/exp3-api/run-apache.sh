#!/usr/bin/env bash
# Run on the disposable 7.4 baseline VM only. The 8.3 binary/modules are copied
# from the 8.3 lab, never installed or selected as the system interpreter.
set -euo pipefail
[[ "$(hostname)" == kaltura-php74-baseline ]] || exit 64
[[ $# == 3 ]] || exit 64
case "$1" in
 74) runtime=/usr/bin/php7.4; modules=/usr/lib/php/20190902 ;;
 83) runtime=/audit/runtime83/php8.3; modules=/audit/runtime83 ;;
 *) exit 64 ;;
esac
case "$2" in
 original) tree=/home/vagrant/php74-audit/packaged/opt/kaltura/app ;;
 exp3) tree=/home/vagrant/php-exp3-regression/source/server-Rigel-18.20.0 ;;
 *) exit 64 ;;
esac
[[ "$3" =~ ^/tmp/kaltura-pdo-mysql\.[a-zA-Z0-9]+$ && -S "$3/mysql.sock" ]] || exit 64
[[ "$(realpath -- "$3")" == "$3" && ! -L "$3/mysql.sock" ]] || exit 64
scripts=/home/vagrant/php-exp3-regression/tests
exec sudo systemd-run --quiet --wait --pipe --collect \
 -p User=vagrant -p Group=vagrant -p PrivateNetwork=yes -p 'RestrictAddressFamilies=AF_UNIX AF_INET' \
 -p MountFlags=private -p ProtectSystem=strict -p ProtectHome=yes -p PrivateTmp=yes -p PrivateDevices=yes \
 -p 'TemporaryFileSystem=/audit/app/cache:rw,nosuid,nodev,mode=1777 /audit/app/configurations:rw,nosuid,nodev,mode=1777' \
 -p NoNewPrivileges=yes -p MemoryMax=512M -p RuntimeMaxSec=180 \
 -p 'InaccessiblePaths=-/opt/kaltura /root -/run/mysqld -/var/lib/mysql' \
 -p "BindReadOnlyPaths=$tree:/audit/app $scripts:/audit/tests /home/vagrant/php-mysql-probe/runtime83:/audit/runtime83 $3:/audit/db" \
 /usr/bin/env "PHP83_EXPECTED_RUNTIME=$1" "PHP83_PROBE_DATADIR=$3/data/" /bin/bash /audit/tests/api-apache-inner.sh "$1"
