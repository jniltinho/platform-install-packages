#!/usr/bin/env bash
set -euo pipefail
[[ $# == 3 && $3 =~ ^[a-f0-9]{64}$ && $(id -u) == 1000 ]] || exit 64
case "$1" in original|exp11) ;; *) exit 64;; esac
case "$2" in bootstrap|construct-good|construct-malformed|construct-missing|explicit-ok|magic-ok|explicit-fault|callback-existing|nested-construct|nested-call-ok|nested-call-fault) ;; *) exit 64;; esac
case "$(hostname)" in
 kaltura-php74-baseline) mode=74; php=/usr/bin/php7.4; flags=(-d extension=json) ;;
 kaltura-php83-lab) mode=83; php=/usr/bin/php8.3; flags=() ;;
 *) exit 64;;
esac
base=/home/vagrant/php-xml-lifecycle-private-r2
cd "$base"
verify() {
python3 - "$3" "$mode" <<'PY'
import hashlib,json,sys
from pathlib import Path
root=Path.cwd();p=root/'identities.json'
if p.is_symlink() or hashlib.sha256(p.read_bytes()).hexdigest()!=sys.argv[1]:raise SystemExit('Manifest drift')
data=json.loads(p.read_text())
for name,want in data['files'].items():
 p=root/name
 if p.is_symlink() or not p.resolve().is_relative_to(root) or hashlib.sha256(p.read_bytes()).hexdigest()!=want:raise SystemExit('Fixture drift')
providers=json.loads((root/'providers.json').read_text());provider=providers[sys.argv[2]]
for name,want in provider['files'].items():
 p=Path(name)
 if hashlib.sha256(p.read_bytes()).hexdigest()!=want:raise SystemExit('Provider/runtime/library drift')
PY
}
verify "$@"
trap 'rc=$?; if ! verify "$@"; then exit 70; fi; exit "$rc"' EXIT
soap=$(python3 -c 'import json,sys;print(json.load(open("providers.json"))[sys.argv[1]]["module"])' "$mode")
sudo -n systemd-run --quiet --wait --pipe --collect \
 -p User=vagrant -p Group=vagrant -p PrivateNetwork=yes \
 -p 'SystemCallFilter=~socket socketpair' -p SystemCallErrorNumber=EPERM \
 -p ProtectSystem=strict -p ProtectHome=yes -p PrivateTmp=yes -p PrivateDevices=yes \
 -p NoNewPrivileges=yes -p MemoryMax=192M -p RuntimeMaxSec=60 \
 -p 'InaccessiblePaths=-/opt/kaltura /root -/run/mysqld -/var/lib/mysql' \
 -p "BindReadOnlyPaths=$base:/audit/probe $soap:/audit/soap.so" \
 /usr/bin/env -i PATH=/usr/bin:/bin LC_ALL=C TZ=UTC "$php" -n "${flags[@]}" \
 -d extension=xml -d extension=dom -d extension=/audit/soap.so -d soap.wsdl_cache_enabled=0 \
 -d error_reporting=32767 -d display_errors=stderr -d log_errors=0 \
 -d allow_url_fopen=0 -d allow_url_include=0 -d open_basedir=/audit/probe \
 /audit/probe/probe.php "$1" "$2"
