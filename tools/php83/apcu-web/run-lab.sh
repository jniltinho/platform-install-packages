#!/usr/bin/env bash
# Run only synthetic, isolated HTTP cache probes in the existing isolated labs.
set -euo pipefail
[[ $# == 2 ]] || { echo 'Usage: run-lab.sh 74|83 original|aliases' >&2; exit 64; }
version=$1 mode=$2
case "$version" in
 74) config=/tmp/kaltura-php74-ssh.conf; alias=baseline74; host=kaltura-php74-baseline; port=2201 ;;
 83) config=/tmp/kaltura-php83-ssh.conf; alias=php83; host=kaltura-php83-lab; port=2200 ;;
 *) exit 64 ;;
esac
case "$mode" in original|aliases) ;; *) exit 64 ;; esac
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
tar -C "$here" -cf - endpoint.php client.py apache-inner.sh | ssh -T -F "$config" -o ClearAllForwardings=yes "$alias" "bash -c 'set -euo pipefail
[[ \$(hostname) == $host ]] || exit 64
d=\$(mktemp -d /tmp/php83-apcu-web.XXXXXXXX)
trap '\''rm -rf -- \"\$d\"'\'' EXIT
chmod 755 \"\$d\"
tar -xf - -C \"\$d\"
chmod 644 \"\$d/endpoint.php\" \"\$d/client.py\" \"\$d/apache-inner.sh\"
sudo systemd-run --quiet --wait --pipe --collect \\
 -p User=vagrant -p Group=vagrant -p PrivateNetwork=yes \\
 -p '\''RestrictAddressFamilies=AF_UNIX AF_INET'\'' \\
 -p PrivateDevices=yes -p ProtectSystem=strict -p ProtectHome=yes \\
 -p PrivateTmp=yes -p NoNewPrivileges=yes -p '\''InaccessiblePaths=-/opt/kaltura /root -/run/mysqld -/var/lib/mysql'\'' \\
 -p \"BindReadOnlyPaths=/home/vagrant/php${version}-audit/packaged/opt/kaltura/app:/audit/app \$d:/audit/tests\" \\
 -p MemoryMax=256M -p RuntimeMaxSec=60 \\
 /bin/bash /audit/tests/apache-inner.sh $version $mode
'"
