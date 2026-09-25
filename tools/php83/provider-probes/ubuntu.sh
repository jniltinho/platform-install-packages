#!/usr/bin/env bash
set -euo pipefail
source "$(dirname -- "$0")/common.sh"
source /etc/os-release
[[ $ID == ubuntu ]] || exit 2
case "$VERSION_ID:$VERSION_CODENAME" in
    24.04:noble) provider=native ;;
    26.04:resolute) provider=sury ;;
    *) echo 'Only noble24.04/resolute26.04 supported' >&2; exit 2 ;;
esac
export DEBIAN_FRONTEND=noninteractive
printf '#!/bin/sh\nexit 101\n' > /usr/sbin/policy-rc.d
chmod 755 /usr/sbin/policy-rc.d
apt-get update
apt-get install -y --no-install-recommends ca-certificates curl gnupg
if [[ $provider == sury ]]; then
    curl --proto '=https' --tlsv1.2 --fail --show-error --location --max-time 60 https://packages.sury.org/debsuryorg-archive-keyring.deb -o /tmp/debsuryorg-archive-keyring.deb
    # HTTPS bootstrap artifact pinned for this probe; updates require review.
    echo '7511384559c9ddf1d5ce5f60be429ae9d4e7d01d9480d6f1b7a30c0810cf8b60  /tmp/debsuryorg-archive-keyring.deb' | sha256sum --check --strict
    sha256sum /tmp/debsuryorg-archive-keyring.deb
    dpkg -i /tmp/debsuryorg-archive-keyring.deb
    gpg --batch --show-keys --with-colons /usr/share/keyrings/debsuryorg-archive-keyring.gpg
    printf 'deb [signed-by=/usr/share/keyrings/debsuryorg-archive-keyring.gpg] https://packages.sury.org/php resolute main\n' > /etc/apt/sources.list.d/php83-sury.list
    apt-get update
fi

packages=(php8.3-cli libapache2-mod-php8.3 php8.3-common php8.3-mysql php8.3-xml php8.3-xsl php8.3-curl php8.3-mbstring php8.3-gd php8.3-gmp php8.3-ldap php8.3-intl php8.3-zip php8.3-apcu php8.3-memcache php8.3-ssh2 php8.3-bcmath php8.3-opcache apache2)
echo 'PHP83_PROVIDER_POLICY_BEGIN'
apt-cache policy "${packages[@]}"
echo 'PHP83_PROVIDER_POLICY_END'
apt-get install -y --no-install-recommends "${packages[@]}"
echo 'PHP83_PROVIDER_PACKAGES_BEGIN'
dpkg-query -W -f='${binary:Package}\t${Version}\t${Architecture}\n' 'php*' 'libapache2-mod-php*' apache2
php --ini
php -v
cat /etc/os-release
echo 'PHP83_PROVIDER_PACKAGES_END'
# Start a single private loopback listener; no service manager or published ports.
printf 'Listen 127.0.0.1:18083\n' > /etc/apache2/ports.conf
rm -f /etc/apache2/sites-enabled/*
cat > /etc/apache2/sites-enabled/provider.conf <<APACHE
ServerName localhost
<VirtualHost 127.0.0.1:18083>
 DocumentRoot $webroot
 <Directory $webroot>
  Require all granted
 </Directory>
</VirtualHost>
APACHE
printf 'apache2handler\n' > "$webroot/expected-sapi"
# Packaged envvars intentionally reads optional unset variables.
set +u
source /etc/apache2/envvars
set -u
apache2 -t
apache2 -DFOREGROUND > /tmp/provider-httpd.log 2>&1 & http_pid=$!
run_requests apache2handler
echo 'PHP83_PROVIDER_COMPLETE ubuntu'
