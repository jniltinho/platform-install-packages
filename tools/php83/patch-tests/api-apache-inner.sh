#!/usr/bin/env bash
# Separate unprivileged Apache; no installed config/service is touched.
set -euo pipefail
umask 077
[[ $(id -u) == 1000 ]] || exit 64
export PHP83_HTTP_NONCE=$(openssl rand -hex 16)
: >/audit/app/cache/probe-diagnostics.log
dir=$(mktemp -d)
server=
cleanup() {
 if [[ -n "$server" ]]; then kill "$server" 2>/dev/null || true; wait "$server" 2>/dev/null || true; fi
 [[ ! -f "$dir/error.log" ]] || cat "$dir/error.log" >&2
 [[ ! -f /audit/app/cache/probe-diagnostics.log ]] || cat /audit/app/cache/probe-diagnostics.log >&2
 rm -rf -- "$dir"
}
trap cleanup EXIT
case "$1" in
 74) module=/usr/lib/apache2/modules/libphp7.4.so; module_name=php7_module; extensions=/usr/lib/php/20190902 ;;
 83) module=/audit/runtime83/libphp8.3.so; module_name=php_module; extensions=/audit/runtime83 ;;
 *) exit 64 ;;
esac
mkdir "$dir/empty"
export PHP83_EXPECTED_INI="$dir/php.ini"
export PHP_INI_SCAN_DIR="$dir/empty"
cat >"$dir/php.ini" <<EOF
error_reporting=32767
display_errors=0
log_errors=1
error_log=/dev/stderr
date.timezone=UTC
allow_url_fopen=0
allow_url_include=0
EOF
for extension in mysqlnd pdo pdo_mysql posix ctype iconv; do echo "extension=$extensions/$extension.so" >>"$dir/php.ini"; done
[[ "$1" != 74 ]] || echo "extension=$extensions/json.so" >>"$dir/php.ini"
openssl req -x509 -newkey rsa:2048 -nodes -days 1 -subj '/CN=Synthetic PHP probe CA' -addext 'basicConstraints=critical,CA:TRUE' -keyout "$dir/ca.key" -out "$dir/ca.crt" >/dev/null 2>&1
openssl req -newkey rsa:2048 -nodes -subj '/CN=127.0.0.1' -keyout "$dir/server.key" -out "$dir/server.csr" >/dev/null 2>&1
printf 'subjectAltName=IP:127.0.0.1,DNS:localhost\nbasicConstraints=critical,CA:FALSE\nkeyUsage=digitalSignature,keyEncipherment\nextendedKeyUsage=serverAuth\n' >"$dir/extensions"
openssl x509 -req -in "$dir/server.csr" -CA "$dir/ca.crt" -CAkey "$dir/ca.key" -CAcreateserial -days 1 -extfile "$dir/extensions" -out "$dir/server.crt" >/dev/null 2>&1
cat >"$dir/apache.conf" <<EOF
ServerRoot "$dir"
DefaultRuntimeDir "$dir"
PidFile "$dir/pid"
ServerName 127.0.0.1
Listen 127.0.0.1:18383
Listen 127.0.0.1:18443
LoadModule mpm_prefork_module /usr/lib/apache2/modules/mod_mpm_prefork.so
LoadModule authz_core_module /usr/lib/apache2/modules/mod_authz_core.so
LoadModule alias_module /usr/lib/apache2/modules/mod_alias.so
LoadModule ssl_module /usr/lib/apache2/modules/mod_ssl.so
LoadModule socache_shmcb_module /usr/lib/apache2/modules/mod_socache_shmcb.so
LoadModule $module_name $module
PHPIniDir "$dir"
User vagrant
Group vagrant
StartServers 1
MinSpareServers 1
MaxSpareServers 1
MaxRequestWorkers 1
ServerLimit 1
ErrorLog "$dir/error.log"
LogLevel warn
SSLSessionCache shmcb:$dir/ssl-cache(512000)
DocumentRoot /audit/tests
Alias /probe /audit/tests/api-web-router.php
<Directory /audit/tests>
 Require all denied
</Directory>
<Location /probe>
 Require all granted
 SetHandler application/x-httpd-php
</Location>
<VirtualHost 127.0.0.1:18443>
 ServerName localhost
 SSLEngine on
 SSLCertificateFile "$dir/server.crt"
 SSLCertificateKeyFile "$dir/server.key"
</VirtualHost>
EOF
/usr/sbin/apache2 -f "$dir/apache.conf" -t
setsid /usr/sbin/apache2 -f "$dir/apache.conf" -DFOREGROUND &
server=$!
python3 - <<'PY'
import socket,time
for _ in range(100):
 try:
  with socket.create_connection(('127.0.0.1',18383),timeout=.1): break
 except OSError: time.sleep(.05)
else: raise RuntimeError('Apache probe did not start')
PY
kill -0 "$server"
export PHP83_EXPECTED_SAPI=apache2handler
PHP83_HTTP_TLS=0 python3 /audit/tests/api-http-client.py
# A client without the synthetic CA must reject the certificate.
python3 - <<'PY'
import socket,ssl
try:
 with socket.create_connection(('127.0.0.1',18443),timeout=5) as sock:
  with ssl.create_default_context().wrap_socket(sock,server_hostname='127.0.0.1'):
   raise RuntimeError('Untrusted certificate accepted')
except ssl.SSLCertVerificationError:
 print('["untrusted-ca-rejected", true]')
PY
PHP83_HTTP_TLS=1 PHP83_HTTP_CA="$dir/ca.crt" python3 /audit/tests/api-http-client.py
