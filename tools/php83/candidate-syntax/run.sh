#!/usr/bin/env bash
# Compile only: no application includes or entrypoints. Only isolated php83lab.
set -euo pipefail
[[ $# == 0 && $(hostname) == kaltura-php83-lab && $(id -u) == 1000 ]] || exit 64
stage=/home/vagrant/php-candidate-syntax-exp9
[[ -d $stage && ! -L $stage ]] || exit 64
exec sudo systemd-run --quiet --wait --pipe --collect \
 -p User=vagrant -p Group=vagrant -p PrivateNetwork=yes \
 -p 'SystemCallFilter=~socket socketpair' -p SystemCallErrorNumber=EPERM -p RestrictAddressFamilies=AF_UNIX \
 -p ProtectSystem=strict -p ProtectHome=yes -p PrivateTmp=yes -p PrivateDevices=yes \
 -p NoNewPrivileges=yes -p MemoryMax=1G -p RuntimeMaxSec=2400 \
 -p 'InaccessiblePaths=-/opt/kaltura /root -/run/mysqld -/var/lib/mysql' \
 -p "BindReadOnlyPaths=$stage/tools:/audit/tools $stage/original.zip:/audit/original.zip $stage/exp9.zip:/audit/exp9.zip $stage/original/server-Rigel-18.20.0:/audit/original $stage/exp9/server-Rigel-18.20.0:/audit/exp9" \
 /usr/bin/env -i PATH=/usr/bin:/bin LC_ALL=C TZ=UTC /usr/bin/python3 -B /audit/tools/scan.py
