#!/usr/bin/env bash
set -euo pipefail
[[ $# == 2 && $2 =~ ^[0-9a-f]{64}$ && $(hostname) == kaltura-php74-baseline ]] || exit 64
case "$1" in original|public-comparison|attribute-comparison) ;; *) exit 64;; esac
base=/home/vagrant/php-dispatcher74-observation-v1
cd "$base"
pin=$2
verify() { echo "$pin  SHA256SUMS" | sha256sum --check --strict >/dev/null; sha256sum --check --strict SHA256SUMS >/dev/null; [[ -z $(find . -type l -print -quit) ]]; }
verify
finish() { status=$?; trap - EXIT; verify || exit 70; exit "$status"; }
trap finish EXIT
probe=dispatcher74-probe.php;args=("/audit/probe/$1.php")
if [[ $1 == rank ]]; then probe=rank-metadata-probe.php;args=();fi
sudo -n systemd-run --quiet --wait --pipe --collect \
 -p User=nobody -p Group=nogroup -p PrivateNetwork=yes \
 -p 'SystemCallFilter=~socket socketpair' -p SystemCallErrorNumber=EPERM \
 -p PrivateDevices=yes -p ProtectSystem=strict -p ProtectHome=yes -p PrivateTmp=yes \
 -p NoNewPrivileges=yes -p 'InaccessiblePaths=-/opt/kaltura /root' \
 -p "BindReadOnlyPaths=$base:/audit/probe" -p MemoryMax=128M -p RuntimeMaxSec=30 \
 /usr/bin/php7.4 -n -d extension=json -d display_errors=stderr -d log_errors=0 \
 -d allow_url_fopen=0 -d allow_url_include=0 /audit/probe/"$probe" "${args[@]}"
