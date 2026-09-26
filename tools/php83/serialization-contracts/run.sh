#!/usr/bin/env bash
set -euo pipefail
[[ $# == 4 && $4 =~ ^[a-f0-9]{64}$ && $(id -u) == 1000 && $(hostname) == kaltura-php83-lab ]] || exit 64
case "$1" in original|candidate);; *) exit 64;; esac
case "$2" in plain|null|decorator|role|profile|cacheable);; *) exit 64;; esac
case "$3" in roundtrip|read|malformed|invalid-utf8);; *) exit 64;; esac
base=/home/vagrant/php-serialization-wire-r1
cd "$base"
verify() {
python3 - "$4" <<'PY'
import hashlib,json,sys
from pathlib import Path
root=Path.cwd();p=root/'identities.json'
if p.is_symlink() or hashlib.sha256(p.read_bytes()).hexdigest()!=sys.argv[1]:raise SystemExit('Manifest mismatch')
x=json.loads(p.read_text())
if x['phase']!='serialization-native83-wire-r1' or x['application_selected'] is not False:raise SystemExit('Wrong phase')
actual={str(f.relative_to(root)) for f in root.rglob('*') if f.is_file()}
if actual!=set(x['files'])|{'identities.json'}:raise SystemExit('Inventory mismatch')
for name,want in x['files'].items():
 f=root/name
 if f.is_symlink() or not f.resolve().is_relative_to(root) or hashlib.sha256(f.read_bytes()).hexdigest()!=want:raise SystemExit('Source drift')
for name,want in x['runtime_files'].items():
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
 /usr/bin/env -i PATH=/usr/bin:/bin LC_ALL=C TZ=UTC /usr/bin/php8.3 -n \
 -d error_reporting=32767 -d display_errors=stderr -d log_errors=0 \
 -d allow_url_fopen=0 -d allow_url_include=0 -d open_basedir=/audit/probe \
 /audit/probe/probe.php "/audit/probe/$1" "$2" "$3"
