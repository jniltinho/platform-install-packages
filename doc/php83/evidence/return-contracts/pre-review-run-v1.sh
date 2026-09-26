#!/usr/bin/env bash
set -euo pipefail
[[ $# == 3 && $3 =~ ^[0-9a-f]{64}$ ]] || exit 64
case "$1" in exp12|prerequisite|candidate) ;; *) exit 64;; esac
case "$2" in hierarchy|configuration|exception) ;; *) exit 64;; esac
[[ $(hostname) == kaltura-php83-lab ]] || exit 64
base=/home/vagrant/php-return-contracts-observation-v1
source=/home/vagrant/php-exp12-regression/source/server-Rigel-18.20.0
cd "$base"
echo "$3  identities.json" | sha256sum --check --strict >/dev/null
python3 verify.py "$base" "$3"
# Save arguments in globals: EXIT trap function has its own positional arguments.
pin=$3
finish() { result=$?; trap - EXIT; python3 "$base/verify.py" "$base" "$pin" || exit 70; exit "$result"; }
trap finish EXIT
binds=(-p "BindReadOnlyPaths=$source:/audit/app" -p "BindReadOnlyPaths=$base:/audit/probe")
while IFS= read -r path; do
  [[ $path != /* && $path != *..* && $path =~ ^[A-Za-z0-9_./-]+$ ]] || exit 64
  binds+=(-p "BindReadOnlyPaths=$base/$1/$path:/audit/app/$path")
done < <(python3 -c 'import json; d=json.load(open("identities.json"));print("\n".join(sorted(d["variants"]["exp12"])))')
sudo -n systemd-run --quiet --wait --pipe --collect \
 -p User=nobody -p Group=nogroup -p PrivateNetwork=yes \
 -p 'SystemCallFilter=~socket socketpair' -p SystemCallErrorNumber=EPERM \
 -p PrivateDevices=yes -p ProtectSystem=strict -p ProtectHome=yes -p PrivateTmp=yes \
 -p NoNewPrivileges=yes -p 'InaccessiblePaths=-/opt/kaltura /root' \
 "${binds[@]}" -p MemoryMax=128M -p RuntimeMaxSec=30 \
 /usr/bin/php8.3 -n -d extension=pdo -d display_errors=stderr -d log_errors=0 \
 -d allow_url_fopen=0 -d allow_url_include=0 /audit/probe/probe.php "$2"
