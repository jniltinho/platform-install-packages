#!/usr/bin/env bash
set -euo pipefail
[[ $# == 3 && $3 =~ ^[a-f0-9]{64}$ && $(id -u) == 1000 ]] || exit 64
case "$1" in enabled|legacy|default|deny) ;; *) exit 64;; esac
case "$2" in dom|simplexml|xmlreader) ;; *) exit 64;; esac
case "$(hostname)" in
 kaltura-php74-baseline) php=/usr/bin/php7.4; flags=(-d extension=json) ;;
 kaltura-php83-lab) php=/usr/bin/php8.3; flags=() ;;
 *) exit 64;;
esac
base=/home/vagrant/php-xml-loader-r1
cd "$base"
verify() {
python3 - "$3" <<'PY'
import hashlib,json,sys
from pathlib import Path
root=Path.cwd();p=root/'identities.json'
if p.is_symlink() or hashlib.sha256(p.read_bytes()).hexdigest()!=sys.argv[1]:raise SystemExit('Manifest drift')
data=json.loads(p.read_text())
for name,want in data['files'].items():
 p=root/name
 if p.is_symlink() or not p.resolve().is_relative_to(root) or hashlib.sha256(p.read_bytes()).hexdigest()!=want:raise SystemExit('Fixture drift')
PY
}
verify "$@"
trap 'rc=$?; if ! verify "$@"; then exit 70; fi; exit "$rc"' EXIT
sudo -n systemd-run --quiet --wait --pipe --collect \
 -p User=vagrant -p Group=vagrant -p PrivateNetwork=yes \
 -p 'SystemCallFilter=~socket socketpair' -p SystemCallErrorNumber=EPERM \
 -p ProtectSystem=strict -p ProtectHome=yes -p PrivateTmp=yes -p PrivateDevices=yes \
 -p NoNewPrivileges=yes -p MemoryMax=192M -p RuntimeMaxSec=60 \
 -p 'InaccessiblePaths=-/opt/kaltura /root -/run/mysqld -/var/lib/mysql' \
 -p "BindReadOnlyPaths=$base:/audit/probe" \
 /usr/bin/env -i PATH=/usr/bin:/bin LC_ALL=C TZ=UTC "$php" -n "${flags[@]}" \
 -d extension=xml -d extension=dom -d extension=simplexml -d extension=xmlreader \
 -d error_reporting=32767 -d display_errors=stderr -d log_errors=0 \
 -d allow_url_fopen=0 -d allow_url_include=0 -d open_basedir=/audit/probe \
 /audit/probe/probe.php "$1" "$2"
