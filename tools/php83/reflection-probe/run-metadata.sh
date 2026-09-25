#!/usr/bin/env bash
set -euo pipefail
case "$(hostname)" in kaltura-php74-baseline) php=/usr/bin/php7.4;; kaltura-php83-lab) php=/usr/bin/php8.3;; *) exit 64;; esac
base=/home/vagrant/php-reflection-probe
source=/home/vagrant/php-exp5-regression
bind="$source/source/server-Rigel-18.20.0:/audit/app $source/tests:/audit/tests $base:/audit/probe"
case "${1:-}" in original) ;; candidate) bind+=" $base/candidate.php:/audit/app/api_v3/lib/reflection/KalturaActionReflector.php";; *) exit 64;; esac
exec sudo systemd-run --quiet --wait --pipe --collect \
 -p User=nobody -p Group=nogroup -p PrivateNetwork=yes -p MountFlags=private \
 -p 'SystemCallFilter=~socket socketpair' -p SystemCallErrorNumber=EPERM \
 -p PrivateDevices=yes -p ProtectSystem=strict -p ProtectHome=yes -p PrivateTmp=yes \
 -p NoNewPrivileges=yes -p 'InaccessiblePaths=-/opt/kaltura /root' \
 -p 'TemporaryFileSystem=/audit/app/cache:rw,nosuid,nodev,mode=1777 /audit/app/configurations:rw,nosuid,nodev,mode=1777' \
 -p "BindReadOnlyPaths=$bind" -p MemoryMax=512M -p RuntimeMaxSec=60 \
 "$php" -d log_errors=0 -d opcache.enable_cli=0 -d allow_url_fopen=0 -d allow_url_include=0 \
 -d date.timezone=UTC /audit/probe/metadata.php
