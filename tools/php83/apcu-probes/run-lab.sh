#!/usr/bin/env bash
# Run only synthetic, process-local cache probes in the existing isolated labs.
set -euo pipefail
[[ $# == 2 ]] || { echo 'Usage: run-lab.sh 74|83 control|adapter' >&2; exit 64; }
version=$1 mode=$2
case "$version" in
 74) config=/tmp/kaltura-php74-ssh.conf; alias=baseline74; host=kaltura-php74-baseline; port=2201 ;;
 83) config=/tmp/kaltura-php83-ssh.conf; alias=php83; host=kaltura-php83-lab; port=2200 ;;
 *) exit 64 ;;
esac
case "$mode" in control|adapter) ;; *) exit 64 ;; esac
here=$(cd -- "$(dirname -- "$0")" && pwd)
# Refuse DNS/non-loopback targets, other ports/users and SSH forwarding/proxies.
resolved=$(ssh -G -F "$config" "$alias")
for expected in "hostname 127.0.0.1" "port $port" 'user vagrant' 'clearallforwardings no'; do
 grep -Fxq "$expected" <<< "$resolved" || { echo "SSH configuration mismatch: $expected" >&2; exit 64; }
done
if grep -Eq '^(proxycommand|proxyjump|localforward|remoteforward|dynamicforward) ' <<< "$resolved"; then
 echo 'Unexpected SSH routing' >&2; exit 64
fi
# Only public fixture content crosses SSH. No production tree or data is copied.
tar -C "$here" -cf - wrapper.php | ssh -T -F "$config" -o ClearAllForwardings=yes "$alias" "bash -c 'set -euo pipefail
[[ \$(hostname) == $host ]] || exit 64
d=\$(mktemp -d /tmp/php83-apcu-probe.XXXXXXXX)
trap '\''rm -rf -- \"\$d\"'\'' EXIT
chmod 755 \"\$d\"
tar -xf - -C \"\$d\"
chmod 644 \"\$d/wrapper.php\"
sudo systemd-run --quiet --wait --pipe --collect \\
 -p User=nobody -p Group=nogroup -p PrivateNetwork=yes \\
 -p '\''SystemCallFilter=~socket socketpair'\'' -p SystemCallErrorNumber=EPERM \\
 -p PrivateDevices=yes -p ProtectSystem=strict -p ProtectHome=yes \\
 -p PrivateTmp=yes -p NoNewPrivileges=yes -p '\''InaccessiblePaths=-/opt/kaltura /root'\'' \\
 -p \"BindReadOnlyPaths=/home/vagrant/php${version}-audit/packaged/opt/kaltura/app:/audit/app \$d:/audit/tests\" \\
 -p MemoryMax=256M -p RuntimeMaxSec=30 \\
 /usr/bin/php${version:0:1}.${version:1:1} -d apc.enable_cli=1 -d apc.use_request_time=0 \\
 -d opcache.enable_cli=0 -d allow_url_fopen=0 -d allow_url_include=0 \\
 /audit/tests/wrapper.php /audit/app $mode
'"
