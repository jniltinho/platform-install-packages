#!/usr/bin/env bash
# Only via run-lab.sh's private-network/mount namespace; no service/config edits.
set -euo pipefail
[[ $(id -u) == 1000 && $# == 2 ]] || exit 64
case "$(hostname):$1" in
 kaltura-php74-baseline:74) module=/usr/lib/apache2/modules/libphp7.4.so; module_name=php7_module; extensions=/usr/lib/php/20190902 ;;
 kaltura-php83-lab:83) module=/usr/lib/apache2/modules/libphp8.3.so; module_name=php_module; extensions=/usr/lib/php/20230831 ;;
 *) exit 64 ;;
esac
case "$2" in original|aliases) ;; *) exit 64 ;; esac
umask 077
dir=$(mktemp -d)
server=
cleanup() {
 if [[ -n "$server" ]]; then kill "$server" 2>/dev/null || true; wait "$server" 2>/dev/null || true; fi
 [[ ! -f "$dir/error.log" ]] || cat "$dir/error.log" >&2
 rm -rf -- "$dir"
}
trap cleanup EXIT
export PHP83_HTTP_NONCE=$(openssl rand -hex 16)
export PHP83_EXPECTED_RUNTIME=$1 PHP83_EXPECTED_MODE=$2
export PHP83_CACHE_DIR="$dir/cache/"
mkdir "$dir/empty" "$dir/cache"
export PHP83_EXPECTED_INI="$dir/php.ini"
export PHP_INI_SCAN_DIR="$dir/empty"
cat > "$dir/php.ini" <<INI
error_reporting=32767
display_errors=0
log_errors=1
error_log=/dev/stderr
allow_url_fopen=0
allow_url_include=0
apc.enabled=1
apc.use_request_time=0
extension=$extensions/apcu.so
INI
[[ $1 != 74 ]] || echo "extension=$extensions/json.so" >> "$dir/php.ini"
cat > "$dir/apache.conf" <<CONF
ServerRoot "$dir"
DefaultRuntimeDir "$dir"
PidFile "$dir/pid"
ServerName 127.0.0.1
Listen 127.0.0.1:18383
LoadModule mpm_prefork_module /usr/lib/apache2/modules/mod_mpm_prefork.so
LoadModule authz_core_module /usr/lib/apache2/modules/mod_authz_core.so
LoadModule alias_module /usr/lib/apache2/modules/mod_alias.so
LoadModule $module_name $module
PHPIniDir "$dir"
User vagrant
Group vagrant
StartServers 1
MinSpareServers 1
MaxSpareServers 1
MaxRequestWorkers 1
ServerLimit 1
MaxConnectionsPerChild 0
ErrorLog "$dir/error.log"
LogLevel warn
DocumentRoot /audit/tests
Alias /probe /audit/tests/endpoint.php
<Directory /audit/tests>
 Require all denied
</Directory>
<Location /probe>
 Require all granted
 SetHandler application/x-httpd-php
</Location>
CONF
/usr/sbin/apache2 -f "$dir/apache.conf" -t
/usr/sbin/apache2 -f "$dir/apache.conf" -DFOREGROUND & server=$!
# Readiness opens a TCP connection only, not a synthetic cache request.
python3 - <<'PY'
import socket,time
for _ in range(100):
 try:
  with socket.create_connection(('127.0.0.1',18383),timeout=.1):break
 except OSError:time.sleep(.05)
else:raise RuntimeError('Apache did not start')
PY
kill -0 "$server"
python3 /audit/tests/client.py
