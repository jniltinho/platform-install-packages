#!/usr/bin/env bash
# Replay reviewed held-patch corpora against the actual full exp11 artifact.
set -euo pipefail
[[ $(hostname) == kaltura-php74-baseline && $(id -u) == 1000 && $# == 2 ]] || exit 64
stage=/home/vagrant/php-exp11-regression
case "$1:$2" in
 ternary:matrix) probe=base-object-ternary/probe.php; args=() ;;
 autoload:hp|autoload:core-simple|autoload:core-full|autoload:cli-version|autoload:cli-version-queue|autoload:cli-tasks-configured) probe=autoload83/probe.php; args=("$2") ;;
 composition:hp-append|composition:hp-prepend|composition:hp-throw|composition:hp-repeat|composition:core-repeat|composition:cli-append|composition:cli-prepend|composition:cli-throw-front|composition:cli-throw-tail|composition:cli-repeat) probe=autoload83-composition/probe.php; args=("$2") ;;
 *) exit 64 ;;
esac
exec sudo systemd-run --quiet --wait --pipe --collect \
 -p User=vagrant -p Group=vagrant -p PrivateNetwork=yes \
 -p 'SystemCallFilter=~socket socketpair' -p SystemCallErrorNumber=EPERM \
 -p ProtectSystem=strict -p ProtectHome=yes -p PrivateTmp=yes -p PrivateDevices=yes \
 -p NoNewPrivileges=yes -p MemoryMax=512M -p RuntimeMaxSec=60 \
 -p 'InaccessiblePaths=-/opt/kaltura /root -/run/mysqld -/var/lib/mysql' \
 -p "BindReadOnlyPaths=$stage/source/server-Rigel-18.20.0:/audit/source $stage/$probe:/audit/probe.php $stage/autoload83/fixtures:/audit/fixtures $stage/autoload83-composition/fixtures:/audit/composition-fixtures /home/vagrant/php-mysql-probe/runtime83:/audit/runtime83" \
 /usr/bin/env -i PATH=/usr/bin:/bin LC_ALL=C TZ=UTC TERM=dumb /audit/runtime83/php8.3 -n \
 -d error_reporting=32767 -d display_errors=stderr -d log_errors=0 \
 -d allow_url_fopen=0 -d allow_url_include=0 /audit/probe.php "${args[@]}"
