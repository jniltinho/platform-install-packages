#!/usr/bin/env bash
set -euo pipefail
source "$(dirname -- "$0")/common.sh"
source /etc/os-release
[[ $ID == rocky && $VERSION_ID == 9* ]] || exit 2
dnf -y install dnf-plugins-core ca-certificates gnupg2
if ! command -v curl >/dev/null; then dnf -y install curl-minimal; fi
dnf config-manager --set-enabled crb
dnf -y install epel-release
fingerprint=${PHP83_REMI_FINGERPRINT:-B1ABF71E14C9D74897E198A8B19527F1478F8947}
keyurl=${PHP83_REMI_KEY_URL:-https://rpms.remirepo.net/RPM-GPG-KEY-remi2021}
[[ $fingerprint =~ ^[A-F0-9]{40}$ && $keyurl =~ ^https://rpms.remirepo.net/RPM-GPG-KEY-remi[0-9]+$ ]] || exit 2
curl --proto '=https' --tlsv1.2 --fail --show-error --location --max-time 60 "$keyurl" -o /tmp/remi.asc
actual=$(gpg --batch --show-keys --with-colons /tmp/remi.asc | awk -F: '$1=="fpr"{print $10;exit}')
[[ $actual == "$fingerprint" ]] || exit 2
rpm --import /tmp/remi.asc
curl --proto '=https' --tlsv1.2 --fail --show-error --location --max-time 60 https://rpms.remirepo.net/enterprise/remi-release-9.rpm -o /tmp/remi-release.rpm
rpmkeys --checksig /tmp/remi-release.rpm
dnf -y --setopt=localpkg_gpgcheck=1 install /tmp/remi-release.rpm
dnf -y module reset php
dnf -y module enable php:remi-8.3
packages=(php-cli php-fpm php-common php-mysqlnd php-xml php-curl php-mbstring php-gd php-gmp php-ldap php-intl php-pecl-zip php-pecl-apcu php-pecl-memcache php-pecl-ssh2 php-process php-bcmath php-opcache httpd)
dnf -y --setopt=gpgcheck=1 install "${packages[@]}"
echo 'PHP83_PROVIDER_PACKAGES_BEGIN'
dnf module list php --enabled
dnf repolist -v
dnf list --installed 'php*' httpd
rpm -qa --qf '%{NAME}\t%{VERSION}-%{RELEASE}\t%{ARCH}\t%{RSAHEADER:pgpsig}\n' | sort
echo PHP83_PROVIDER_LEGACY_APC_CAPABILITY_BEGIN
rpm -q --whatprovides php-pecl-apc || echo LEGACY_APC_CAPABILITY_NOT_PROVIDED
echo PHP83_PROVIDER_LEGACY_APC_CAPABILITY_END
php --ini
php -v
cat /etc/os-release
echo 'PHP83_PROVIDER_PACKAGES_END'
mkdir -p /run/php-fpm /run/httpd
# Dedicated FPM config: no system pool, Unix socket, no external listener.
cat > /tmp/provider-fpm.conf <<'FPM'
[global]
pid = /run/php-fpm/provider.pid
error_log = /proc/self/fd/2
daemonize = no
[provider]
user = apache
group = apache
listen = /run/php-fpm/provider.sock
listen.owner = apache
listen.group = apache
listen.mode = 0600
pm = static
pm.max_children = 2
catch_workers_output = yes
FPM
# Retain packaged module loading but replace generic PHP proxy configuration.
rm -f /etc/httpd/conf.d/php.conf /etc/httpd/conf.d/welcome.conf
sed -i 's/^Listen .*/Listen 127.0.0.1:18083/' /etc/httpd/conf/httpd.conf
cat > /etc/httpd/conf.d/provider.conf <<APACHE
ServerName localhost
<VirtualHost 127.0.0.1:18083>
 DocumentRoot $webroot
 <Directory $webroot>
  Require all granted
 </Directory>
 <FilesMatch "\\.php$">
  SetHandler "proxy:unix:/run/php-fpm/provider.sock|fcgi://localhost"
 </FilesMatch>
</VirtualHost>
APACHE
printf 'fpm-fcgi\n' > "$webroot/expected-sapi"
php-fpm --test --fpm-config /tmp/provider-fpm.conf
httpd -t
php-fpm --nodaemonize --fpm-config /tmp/provider-fpm.conf > /tmp/provider-fpm.log 2>&1 & fpm_pid=$!
httpd -DFOREGROUND > /tmp/provider-httpd.log 2>&1 & http_pid=$!
run_requests fpm-fcgi
echo 'PHP83_PROVIDER_COMPLETE rocky'
