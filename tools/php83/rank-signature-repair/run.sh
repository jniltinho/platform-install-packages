#!/usr/bin/env bash
set -euo pipefail
[[ $# == 4 && $(hostname) == kaltura-php74-baseline ]] || exit 64
[[ $1 =~ ^/home/vagrant/php-rank-signature\.[a-f0-9]{32}$ && $4 =~ ^[a-f0-9]{64}$ ]] || exit 64
case $2 in 74|83) ;; *) exit 64;; esac
case $3 in original|candidate) ;; *) exit 64;; esac
base=$1; runtime=$2; variant=$3; pin=$4
[[ -d $base && ! -L $base && $(realpath "$base") == "$base" ]] || exit 64
cd "$base"
verify(){ echo "$pin  SHA256SUMS" | sha256sum --check --strict >/dev/null; sha256sum --check --strict SHA256SUMS >/dev/null; [[ -z $(find . -type l -print -quit) ]]; }
verify
finish(){ status=$?;trap - EXIT;verify || exit 70;exit "$status"; };trap finish EXIT
binds="$base:/audit/probe"; php=(/usr/bin/php7.4 -n -d extension=json)
if [[ $runtime == 83 ]]; then binds+=" /home/vagrant/php-mysql-probe/runtime83:/audit/runtime83";php=(/audit/runtime83/php8.3 -n);fi
sudo -n systemd-run --quiet --wait --pipe --collect \
 -p User=nobody -p Group=nogroup -p PrivateNetwork=yes \
 -p 'SystemCallFilter=~socket socketpair' -p SystemCallErrorNumber=EPERM \
 -p PrivateDevices=yes -p ProtectSystem=strict -p ProtectHome=yes -p PrivateTmp=yes \
 -p NoNewPrivileges=yes -p 'InaccessiblePaths=-/opt/kaltura /root' \
 -p "BindReadOnlyPaths=$binds" -p MemoryMax=128M -p RuntimeMaxSec=30 \
 /usr/bin/env "${php[@]}" -d display_errors=stderr -d log_errors=0 -d allow_url_fopen=0 -d allow_url_include=0 \
 /audit/probe/probe.php "$runtime" "$variant"
