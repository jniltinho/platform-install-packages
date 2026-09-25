#!/bin/bash
# Installs and configures a Kaltura CE 18.20.0 All-In-One on Rocky Linux 9 from the local RPM repo.
# Idempotent: re-running only ensures packages and services; the DB and secrets are never recreated.
set -euo pipefail

HOST_IP=${HOST_IP:-192.168.56.30}
MYSQL_ROOT_PASSWD=${MYSQL_ROOT_PASSWD:-kaltura-root}
ADMIN_EMAIL=${ADMIN_EMAIL:-admin@kaltura.local}
ADMIN_PASSWD=${ADMIN_PASSWD:-Adm1n#Video}
# yum baseurl of the Kaltura RPMs: the local build, or an extracted release tarball
KALTURA_REPO=${KALTURA_REPO:-file:///vagrant/rpm/el9/repo}
ANS=/root/kaltura.ans
# written only after kaltura-config-all.sh succeeds, so an interrupted configuration is retried
DONE=/opt/kaltura/app/configurations/.aio-configured
# Kaltura does not support SELinux enforcing (see doc/install-kaltura-redhat-based.md).
# RELAX_HOST_SECURITY=1 (set by the Vagrantfile) makes SELinux permissive and stops firewalld;
# on real servers do it yourself and open the ports in doc/kaltura-required-ports.md.
RELAX_HOST_SECURITY=${RELAX_HOST_SECURITY:-0}

if [ "$RELAX_HOST_SECURITY" = 1 ]; then
	setenforce 0 2>/dev/null || true
	sed -i 's/^SELINUX=enforcing/SELINUX=permissive/' /etc/selinux/config
	systemctl disable --now firewalld 2>/dev/null || true
elif [ "$(getenforce 2>/dev/null)" = Enforcing ]; then
	echo "ERROR: SELinux is enforcing; Kaltura needs permissive (or run with RELAX_HOST_SECURITY=1)" >&2
	exit 1
fi

# --- repositories ---
if [ ! -f /etc/yum.repos.d/kaltura-local.repo ]; then
	dnf -y -q install epel-release dnf-plugins-core
	dnf config-manager --set-enabled crb
	dnf -y -q install https://mirrors.rpmfusion.org/free/el/rpmfusion-free-release-9.noarch.rpm \
		https://rpms.remirepo.net/enterprise/remi-release-9.rpm
	dnf -y -q module reset php
	dnf -y -q module enable php:remi-7.4
	rpm --import https://artifacts.elastic.co/GPG-KEY-elasticsearch
	printf '[elastic-7.x]\nname=Elastic 7.x\nbaseurl=https://artifacts.elastic.co/packages/7.x/yum\ngpgcheck=1\nenabled=1\n' > /etc/yum.repos.d/elastic-7.x.repo
	printf '[kaltura-local]\nname=Kaltura local\nbaseurl=%s\ngpgcheck=0\nenabled=1\nmetadata_expire=0\n' "$KALTURA_REPO" > /etc/yum.repos.d/kaltura-local.repo
fi

# --- MariaDB with the settings Kaltura requires ---
dnf -y -q install mariadb-server
cat > /etc/my.cnf.d/99-kaltura.cnf <<EOF
[mysqld]
lower_case_table_names = 1
innodb_file_per_table
innodb_log_file_size = 32M
open_files_limit = 20000
max_allowed_packet = 16M
sql_mode = NO_ENGINE_SUBSTITUTION
EOF
systemctl enable --now mariadb
systemctl restart mariadb
if mysql -uroot -e 'select 1' >/dev/null 2>&1; then
	mysql -uroot <<EOF
ALTER USER root@localhost IDENTIFIED VIA mysql_native_password USING PASSWORD('$MYSQL_ROOT_PASSWD');
CREATE USER IF NOT EXISTS root@'127.0.0.1' IDENTIFIED BY '$MYSQL_ROOT_PASSWD';
GRANT ALL ON *.* TO root@'127.0.0.1' WITH GRANT OPTION;
FLUSH PRIVILEGES;
EOF
fi

# --- packages ---
dnf -y -q install kaltura-server memcached postfix
systemctl enable --now memcached postfix

# --- configuration (first run only) ---
if [ ! -f "$DONE" ]; then
	sed -e "s#@HOSTNAME@#$HOST_IP#g" -e "s#@MYSQL_HOST@#127.0.0.1#g" -e "s#@MYSQL_PORT@#3306#g" \
		-e "s#@KALT_DB_PASS@#$(tr -dc A-Za-z0-9 </dev/urandom | head -c16)#g" \
		-e "s#@MYSQL_SUPER_USER@#root#g" -e "s|@MYSQL_SUPER_USER_PASSWD@|$MYSQL_ROOT_PASSWD|g" \
		-e "s#@NGINX_HOST@#$HOST_IP#g" -e "s#@NGINX_PORT@#88#g" -e "s#@API_HOST_TO_USE_FOR_NGINX@#$HOST_IP#g" \
		-e 's#^TIME_ZONE=.*#TIME_ZONE="UTC"#' -e 's#^KALTURA_VIRTUAL_HOST_PORT=.*#KALTURA_VIRTUAL_HOST_PORT="80"#' \
		-e 's#^PROTOCOL=.*#PROTOCOL="http"#' -e 's#^IS_SSL=.*#IS_SSL="n"#' -e 's#^USER_CONSENT=.*#USER_CONSENT=0#' \
		-e "s#^ADMIN_CONSOLE_ADMIN_MAIL=.*#ADMIN_CONSOLE_ADMIN_MAIL=\"$ADMIN_EMAIL\"#" \
		-e "s|^ADMIN_CONSOLE_PASSWORD=.*|ADMIN_CONSOLE_PASSWORD=\"$ADMIN_PASSWD\"|" \
		-e 's#^KALTURA_FULL_VIRTUAL_HOST_NAME=.*#KALTURA_FULL_VIRTUAL_HOST_NAME="$KALTURA_VIRTUAL_HOST_NAME"#' \
		/vagrant/doc/kaltura.template.ans > $ANS
	echo 'CONTACT_URL="http://corp.kaltura.com/company/contact-us"' >> $ANS
	echo 'CONTACT_PHONE_NUMBER="+1 800 871 5224"' >> $ANS
	chmod 600 $ANS
	/opt/kaltura/bin/kaltura-config-all.sh $ANS
	# config-all starts the LSB daemons through their init scripts (systemd does not track them)
	# and configures Elasticsearch before the DB exists: restart them all through systemd
	systemctl restart kaltura-sphinx kaltura-populate kaltura-batch
	# ponytail: right after config-all the populate daemon sometimes exits within its 2 s start
	# check (no error logged); retry a few times, warn instead of failing the whole install
	started=
	for i in 1 2 3; do systemctl restart kaltura-elastic-populate && { started=1; break; }; sleep 10; done
	[ -n "$started" ] || echo "WARNING: kaltura-elastic-populate did not start; run: systemctl restart kaltura-elastic-populate"
	touch "$DONE"
fi

systemctl is-active --quiet httpd && echo "Kaltura AIO: http://$HOST_IP (admin: $ADMIN_EMAIL)"
