#!/usr/bin/env bash
# Synthetic writes only, guarded against every non-lab HTTP destination.
set +x
set -euo pipefail
[[ $EUID -eq 0 && $(hostname) == kaltura-php74-baseline ]]
ip -4 -o addr show | grep -q '192\.168\.56\.74/24'
[[ -r /root/kaltura-baseline-private/mysql-password ]]
[[ -r /tmp/php74-baseline-sanity.sh ]]
# Only the already-reviewed, copied legacy script is executed.
EXPECTED_SHA=aaf36e09e1cf87dfb1dfc610f03821903e1ef899a175dc7ef2e2ce1f9cf334e7
printf '%s  %s\n' "$EXPECTED_SHA" /tmp/php74-baseline-sanity.sh | sha256sum -c -
CHAIN=KALTURA_BASELINE_TEST
iptables -N "$CHAIN" # Existing chain is a blocker; do not modify someone else's rules.
cleanup() {
    iptables -D OUTPUT -j "$CHAIN" 2>/dev/null || true
    iptables -F "$CHAIN"
    iptables -X "$CHAIN"
    unset MYSQL_ROOT_PASSWD
}
trap cleanup EXIT
iptables -A "$CHAIN" -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT
iptables -A "$CHAIN" -d 127.0.0.0/8 -j ACCEPT
iptables -A "$CHAIN" -d 192.168.56.74 -j ACCEPT
iptables -A "$CHAIN" -j REJECT
iptables -I OUTPUT 1 -j "$CHAIN"
export HOST_IP=192.168.56.74 URL=http://192.168.56.74
MYSQL_ROOT_PASSWD=$(cat /root/kaltura-baseline-private/mysql-password)
export MYSQL_ROOT_PASSWD
bash /tmp/php74-baseline-sanity.sh
