#!/usr/bin/env bash
# Called only on the existing synthetic baseline lab; owns a new DB each time.
set -euo pipefail
[[ $(hostname) == kaltura-php74-baseline && $(id -u) == 1000 ]] || exit 64
[[ $# == 1 && $1 =~ ^[a-f0-9]{32}$ ]] || exit 64
d=/tmp/kaltura-pdo-mysql.$1
mkdir -m 700 "$d"
unit=php83-exp4-api-${d##*.}
started=no
cleanup_failure() {
 status=$?
 if [[ $status != 0 ]]; then
  [[ $started != yes ]] || sudo systemctl stop "$unit" || true
  echo "Owned synthetic setup failed; retained $d" >&2
 fi
}
trap cleanup_failure EXIT
mariadb-install-db --no-defaults --datadir="$d/data" --tmpdir="$d" \
 --auth-root-authentication-method=socket --auth-root-socket-user=vagrant \
 --skip-test-db > "$d/bootstrap.log" 2>&1
sudo systemd-run --quiet --unit="$unit" --collect \
 -p User=vagrant -p Group=vagrant -p PrivateNetwork=yes \
 -p RestrictAddressFamilies=AF_UNIX -p ProtectSystem=strict \
 -p ReadWritePaths="$d" -p MemoryMax=1G -p RuntimeMaxSec=600 \
 /usr/sbin/mariadbd --no-defaults --datadir="$d/data" --tmpdir="$d" \
 --socket="$d/mysql.sock" --skip-networking --pid-file="$d/server.pid" \
 --log-error="$d/server.log"
started=yes
for attempt in $(seq 1 100); do
 if [[ -S "$d/mysql.sock" ]] && mariadb-admin --no-defaults --socket="$d/mysql.sock" --user=vagrant ping >/dev/null 2>&1; then
  printf '{"datadir":"%s","unit":"%s"}\n' "$d" "$unit"
  exit 0
 fi
 sleep .1
done
exit 1
