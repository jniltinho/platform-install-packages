#!/bin/bash
# Installs and configures a Kaltura CE 18.20.0 All-In-One on Ubuntu 24.04 from the local repo.
# Idempotent: re-running only ensures packages and services; the DB and secrets are never recreated.
set -euo pipefail
export DEBIAN_FRONTEND=noninteractive NEEDRESTART_MODE=a

HOST_IP=${HOST_IP:-192.168.56.20}
# SSL=1: Apache on 443 and the nginx VOD packager on 8443 (see doc/kaltura-ssl-and-console.md).
# Without SSL_CERT/SSL_KEY a self-signed certificate for HOST_IP is generated and trusted
# locally (test VMs only; use a real certificate in production).
SSL=${SSL:-0}
SSL_CERT=${SSL_CERT:-/etc/ssl/certs/kaltura.crt}
SSL_KEY=${SSL_KEY:-/etc/ssl/private/kaltura.key}
SSL_CHAIN=${SSL_CHAIN:-}
# with SSL the delivery profiles must point at the nginx SSL port (doc/nginx-ssl-config.md)
if [ "$SSL" = 1 ]; then PROTO=https; VHOST_PORT=443; VOD_PORT=8443; else PROTO=http; VHOST_PORT=80; VOD_PORT=88; fi
SERVICE_URL=$PROTO://$HOST_IP
MYSQL_ROOT_PASSWD=${MYSQL_ROOT_PASSWD:-kaltura-root}
ADMIN_EMAIL=${ADMIN_EMAIL:-admin@kaltura.local}
ADMIN_PASSWD=${ADMIN_PASSWD:-Adm1n#Video}
# apt source for the Kaltura packages: the local build, or the GitHub release
# e.g. KALTURA_APT=https://github.com/jniltinho/platform-install-packages/releases/download/noble-deb-18.20.0-1
KALTURA_APT=${KALTURA_APT:-file:/vagrant/deb/noble/repo}
APT="apt-get install -y -q -o Dpkg::Options::=--force-confold"

# --- repositories ---
if [ ! -f /etc/apt/sources.list.d/kaltura-local.list ]; then
	apt-get update -q
	apt-get install -y -q software-properties-common curl gnupg
	add-apt-repository -y multiverse
	add-apt-repository -y ppa:ondrej/php
	curl -fsSL https://artifacts.elastic.co/GPG-KEY-elasticsearch | gpg --dearmor -o /usr/share/keyrings/elastic.gpg
	echo "deb [signed-by=/usr/share/keyrings/elastic.gpg] https://artifacts.elastic.co/packages/7.x/apt stable main" > /etc/apt/sources.list.d/elastic-7.x.list
	echo "deb [trusted=yes] $KALTURA_APT ./" > /etc/apt/sources.list.d/kaltura-local.list
fi
apt-get update -q

# --- MariaDB with the settings Kaltura requires ---
mkdir -p /etc/mysql/mariadb.conf.d
cat > /etc/mysql/mariadb.conf.d/99-kaltura.cnf <<EOF
[mysqld]
lower_case_table_names = 1
innodb_file_per_table
innodb_log_file_size = 32M
open_files_limit = 20000
max_allowed_packet = 16M
sql_mode = NO_ENGINE_SUBSTITUTION
EOF
$APT mariadb-server
systemctl restart mariadb
if mysql -uroot -e 'select 1' >/dev/null 2>&1; then
	mysql -uroot <<EOF
ALTER USER root@localhost IDENTIFIED VIA mysql_native_password USING PASSWORD('$MYSQL_ROOT_PASSWD');
CREATE USER IF NOT EXISTS root@'127.0.0.1' IDENTIFIED BY '$MYSQL_ROOT_PASSWD';
GRANT ALL ON *.* TO root@'127.0.0.1' WITH GRANT OPTION;
FLUSH PRIVILEGES;
EOF
fi

# --- self-signed certificate for SSL=1 test installs ---
if [ "$SSL" = 1 ] && [ ! -r "$SSL_CERT" ]; then
	openssl req -x509 -newkey rsa:2048 -nodes -days 3650 -subj "/CN=$HOST_IP" \
		-addext "subjectAltName=IP:$HOST_IP" -keyout "$SSL_KEY" -out "$SSL_CERT" 2>/dev/null
	chmod 640 "$SSL_KEY"
	cp "$SSL_CERT" /usr/local/share/ca-certificates/kaltura-selfsigned.crt && update-ca-certificates >/dev/null
fi
IS_SSL=false; [ "$SSL" = 1 ] && IS_SSL=true

# --- debconf answers (postfix + Kaltura) ---
debconf-set-selections <<EOF
postfix postfix/main_mailer_type select Local only
postfix postfix/mailname string $HOST_IP
kaltura-base kaltura-base/admin_console_email string $ADMIN_EMAIL
kaltura-base kaltura-base/admin_console_passwd password $ADMIN_PASSWD
kaltura-base kaltura-base/admin_console_passwd_again password $ADMIN_PASSWD
kaltura-base kaltura-base/apache_hostname string $HOST_IP
kaltura-base kaltura-base/cdn_hostname string $HOST_IP
kaltura-base kaltura-base/contact_phone string +1 800 871 5224
kaltura-base kaltura-base/contact_url string http://corp.kaltura.com/company/contact-us
kaltura-base kaltura-base/db_hostname string 127.0.0.1
kaltura-base kaltura-base/db_port string 3306
kaltura-base kaltura-base/dwh_db_hostname string 127.0.0.1
kaltura-base kaltura-base/dwh_db_port string 3306
kaltura-base kaltura-base/env_name string Kaltura CE noble
kaltura-base kaltura-base/install_analytics_consent boolean false
kaltura-base kaltura-base/ip_range string 0.0.0.0-255.255.255.255
kaltura-base kaltura-base/mysql_super_user string root
kaltura-base kaltura-base/mysql_super_passwd password $MYSQL_ROOT_PASSWD
kaltura-base kaltura-base/auto_generate_kaltura_mysql_passwd boolean true
kaltura-base kaltura-base/sphinx_hostname string 127.0.0.1
kaltura-base kaltura-base/second_sphinx_hostname string 127.0.0.1
kaltura-base kaltura-base/service_url string $SERVICE_URL
kaltura-base kaltura-base/time_zone string UTC
kaltura-base kaltura-base/vhost_port string $VHOST_PORT
kaltura-base kaltura-base/vod_packager_hostname string $HOST_IP
kaltura-base kaltura-base/vod_packager_port string $VOD_PORT
kaltura-db kaltura-db/db_already_installed boolean false
kaltura-db kaltura-db/db_hostname string 127.0.0.1
kaltura-db kaltura-db/db_port string 3306
kaltura-db kaltura-db/fix_mysql_settings boolean true
kaltura-db kaltura-db/mysql_super_user string root
kaltura-db kaltura-db/mysql_super_passwd password $MYSQL_ROOT_PASSWD
kaltura-db kaltura-db/remove_db boolean false
kaltura-front kaltura-front/is_apache_ssl boolean $IS_SSL
kaltura-front kaltura-front/apache_ssl_cert string $SSL_CERT
kaltura-front kaltura-front/apache_ssl_key string $SSL_KEY
kaltura-front kaltura-front/apache_ssl_chain string $SSL_CHAIN
kaltura-front kaltura-front/service_url string $SERVICE_URL
kaltura-front kaltura-front/vhost_port string $VHOST_PORT
kaltura-front kaltura-front/disable_default_vhost boolean true
kaltura-nginx kaltura-nginx/is_kaltura_server boolean true
kaltura-nginx kaltura-nginx/kaltura_service_url string $SERVICE_URL
kaltura-nginx kaltura-nginx/nginx_hostname string $HOST_IP
kaltura-nginx kaltura-nginx/nginx_port string 88
kaltura-nginx kaltura-nginx/nginx_ssl_port string 8443
kaltura-nginx kaltura-nginx/rtmp_port string 1935
kaltura-nginx kaltura-nginx/is_ssl boolean $IS_SSL
kaltura-nginx kaltura-nginx/ssl_cert string $SSL_CERT
kaltura-nginx kaltura-nginx/ssl_key string $SSL_KEY
EOF

# --- Kaltura: same order as the legacy all-in-1 installer (kaltura-db needs front and sphinx up) ---
for step in "kaltura-postinst kaltura-base" \
	"kaltura-kmcng kaltura-html5lib kaltura-html5lib3 kaltura-html5-studio kaltura-html5-studio3 kaltura-html5-analytics" \
	kaltura-front kaltura-sphinx kaltura-db kaltura-batch kaltura-nginx kaltura-elasticsearch kaltura-server; do
	echo "===== apt install $step"
	$APT $step
done

systemctl is-active --quiet apache2 && echo "Kaltura AIO: $SERVICE_URL (admin: $ADMIN_EMAIL)"
