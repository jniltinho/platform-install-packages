#!/usr/bin/env bash
set -euo pipefail
[[ $# == 4 && $4 =~ ^[a-f0-9]{64}$ && $(id -u) == 1000 && $(hostname) == kaltura-php83-lab ]] || exit 64
case "$1:$2" in
 behavior:baseline|behavior:candidate)
 case "$3" in bootstrap|construct-good|construct-malformed|construct-missing|explicit-ok|magic-ok|explicit-fault|callback-existing|nested-construct|nested-call-ok|nested-call-fault|callback-deny|callback-throw) ;; *) exit 64;; esac
 probe=behavior.php; args=("$2" "$3") ;;
 scope:candidate)
 case "$3" in default|custom-allow|custom-deny|custom-throw|nested|custom-wrapper|foreign-mutation|non-lifo|invalid-token|primary-exception-chain|idempotent-init|standalone) ;; *) exit 64;; esac
 probe=scope-probe.php; args=("$3") ;;
 *) exit 64;;
esac
base=/home/vagrant/php-xml-lifecycle-fix-r1
cd "$base"
verify() {
python3 - "$4" <<'PY'
import hashlib,json,sys
from pathlib import Path
root=Path.cwd();p=root/'identities.json'
if p.is_symlink() or hashlib.sha256(p.read_bytes()).hexdigest()!=sys.argv[1]:raise SystemExit('Manifest drift')
data=json.loads(p.read_text())
if data['phase']!='xml-lifecycle-held-A-r1' or data['application_patch_selected'] is not False:raise SystemExit('Wrong phase')
for name,want in data['files'].items():
 p=root/name
 if p.is_symlink() or not p.resolve().is_relative_to(root) or hashlib.sha256(p.read_bytes()).hexdigest()!=want:raise SystemExit('Fixture drift')
provider=json.loads((root/'provider.json').read_text())
for name,want in provider['files'].items():
 if hashlib.sha256(Path(name).read_bytes()).hexdigest()!=want:raise SystemExit('Provider/runtime/library drift')
PY
}
verify "$@"
trap 'rc=$?; if ! verify "$@"; then exit 70; fi; exit "$rc"' EXIT
soap=$(python3 -c 'import json;print(json.load(open("provider.json"))["module"])')
sudo -n systemd-run --quiet --wait --pipe --collect \
 -p User=vagrant -p Group=vagrant -p PrivateNetwork=yes \
 -p 'SystemCallFilter=~socket socketpair' -p SystemCallErrorNumber=EPERM \
 -p ProtectSystem=strict -p ProtectHome=yes -p PrivateTmp=yes -p PrivateDevices=yes \
 -p NoNewPrivileges=yes -p MemoryMax=192M -p RuntimeMaxSec=60 \
 -p 'InaccessiblePaths=-/opt/kaltura /root -/run/mysqld -/var/lib/mysql' \
 -p "BindReadOnlyPaths=$base:/audit/probe $soap:/audit/soap.so" \
 /usr/bin/env -i PATH=/usr/bin:/bin LC_ALL=C TZ=UTC /usr/bin/php8.3 -n \
 -d extension=xml -d extension=dom -d extension=/audit/soap.so -d soap.wsdl_cache_enabled=0 \
 -d error_reporting=32767 -d display_errors=stderr -d log_errors=0 \
 -d allow_url_fopen=0 -d allow_url_include=0 -d open_basedir=/audit/probe \
 "/audit/probe/$probe" "${args[@]}"
