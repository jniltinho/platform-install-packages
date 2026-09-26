#!/usr/bin/env bash
set -euo pipefail
[[ $# == 4 && $4 =~ ^[a-f0-9]{64}$ && $(id -u) == 1000  ]] || exit 64
case "$(hostname)" in
 kaltura-php83-lab) lab=native83; php=/usr/bin/php8.3; extensions=();;
 kaltura-php74-baseline) lab=baseline74; php=/usr/bin/php7.4; extensions=(-d extension=/usr/lib/php/20190902/json.so); [[ $1 == original ]] || exit 64;;
 *) exit 64;;
esac
case "$1" in original|cachefix|candidate);; *) exit 64;; esac
if [[ $2 == cache ]]; then
 case "$3" in hit|expired|malformed|refresh-hit|refresh-miss|invalid-utf8|read-C|read-O);; *) exit 64;; esac
 probe=cache-probe.php; args=("$3")
else
 case "$2" in plain|null|decorator|role|profile|cacheable);; *) exit 64;; esac
 case "$3" in roundtrip|read|malformed|invalid-utf8);; *) exit 64;; esac
 probe=probe.php; args=("$2" "$3")
fi
base=/home/vagrant/php-serialization-wire-cache-r2
cd "$base"
verify() {
python3 - "$4" "$lab" <<'PY'
import hashlib,json,sys
from pathlib import Path
root=Path.cwd();p=root/'identities.json'
if p.is_symlink() or hashlib.sha256(p.read_bytes()).hexdigest()!=sys.argv[1]:raise SystemExit('Manifest mismatch')
x=json.loads(p.read_text())
if x['phase']!='serialization-native83-wire-cache-r2' or x['application_selected'] is not False:raise SystemExit('Wrong phase')
actual={str(f.relative_to(root)) for f in root.rglob('*') if f.is_file()}
if actual!=set(x['files'])|{'identities.json'}:raise SystemExit('Inventory mismatch')
for name,want in x['files'].items():
 f=root/name
 if f.is_symlink() or not f.resolve().is_relative_to(root) or hashlib.sha256(f.read_bytes()).hexdigest()!=want:raise SystemExit('Source drift')
for name,want in x['runtime_files'][sys.argv[2]].items():
 if hashlib.sha256(Path(name).read_bytes()).hexdigest()!=want:raise SystemExit('Runtime drift')
PY
}
verify "$@"
trap 'rc=$?; if ! verify "$@"; then exit 70; fi; exit "$rc"' EXIT
sudo -n systemd-run --quiet --wait --pipe --collect \
 -p User=vagrant -p Group=vagrant -p PrivateNetwork=yes \
 -p 'SystemCallFilter=~socket socketpair' -p SystemCallErrorNumber=EPERM \
 -p ProtectSystem=strict -p ProtectHome=yes -p PrivateTmp=yes -p PrivateDevices=yes \
 -p NoNewPrivileges=yes -p MemoryMax=192M -p RuntimeMaxSec=30 \
 -p 'InaccessiblePaths=-/opt/kaltura /root -/run/mysqld -/var/lib/mysql' \
 -p "BindReadOnlyPaths=$base:/audit/probe" \
 /usr/bin/env -i PATH=/usr/bin:/bin LC_ALL=C TZ=UTC "$php" -n "${extensions[@]}" \
 -d error_reporting=32767 -d display_errors=stderr -d log_errors=0 \
 -d allow_url_fopen=0 -d allow_url_include=0 -d open_basedir=/audit/probe:/tmp \
 "/audit/probe/$probe" "/audit/probe/$1" "${args[@]}"
