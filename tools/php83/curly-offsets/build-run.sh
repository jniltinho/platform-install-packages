#!/usr/bin/env bash
set -euo pipefail
[[ $# == 0 && $(hostname) == kaltura-php83-lab && $(id -u) == 1000 ]] || exit 64
stage=/home/vagrant/php-curly-offsets-r3
exec sudo systemd-run --quiet --wait --pipe --collect \
 -p User=vagrant -p Group=vagrant -p PrivateNetwork=yes \
 -p 'SystemCallFilter=~socket socketpair' -p SystemCallErrorNumber=EPERM \
 -p RestrictAddressFamilies=AF_UNIX -p ProtectSystem=strict -p ProtectHome=yes \
 -p PrivateTmp=yes -p PrivateDevices=yes -p NoNewPrivileges=yes \
 -p MemoryMax=1G -p RuntimeMaxSec=1800 \
 -p 'InaccessiblePaths=-/opt/kaltura /root -/run/mysqld -/var/lib/mysql' \
 -p "BindReadOnlyPaths=$stage:/audit/stage /home/vagrant/php83-tools:/audit/analyzer" \
 /usr/bin/env -i PATH=/usr/bin:/bin LC_ALL=C TZ=UTC /usr/bin/python3 -B /audit/stage/tools/build-lab.py
