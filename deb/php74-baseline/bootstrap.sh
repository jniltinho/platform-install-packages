#!/usr/bin/env bash
# Fresh isolated reference; never used against .20 or a production clone.
set +x
set -euo pipefail
export DEBIAN_FRONTEND=noninteractive
. /etc/os-release
[[ $ID == ubuntu && $VERSION_ID == 24.04 ]]
[[ $(hostname) == kaltura-php74-baseline ]]
ip -4 -o addr show | grep -q '192\.168\.56\.74/24'
[[ ! -d /opt/kaltura && ! -d /var/lib/mysql ]]
apt-get update -q
apt-get install -y ca-certificates curl openssl python3 iptables
# Defense in depth: the lab cannot contact the protected .20 guest.
iptables -C OUTPUT -d 192.168.56.20 -j REJECT 2>/dev/null ||
    iptables -I OUTPUT -d 192.168.56.20 -j REJECT
install -d -m 0755 /opt/kaltura-baseline/repo
cd /opt/kaltura-baseline
curl -fL --retry 3 --proto '=https' --proto-redir '=https' \
    https://github.com/jniltinho/platform-install-packages/releases/download/kaltura-server/v18.20.0-1/kaltura-server-noble-repo.tar.gz -o repo.tar.gz
printf '%s  %s\n' 91629580441f6a896ebf9e51f0256532221715bee57a3e5a64c66ff0c4e3127b repo.tar.gz | sha256sum -c -
tar -xzf repo.tar.gz -C repo
curl -fL --retry 3 --proto '=https' --proto-redir '=https' \
    https://raw.githubusercontent.com/jniltinho/platform-install-packages/c9b93424aa57b88164084ba78b336664c299a8d0/deb/noble/install-aio.sh -o install-aio.sh
printf '%s  %s\n' 3888f90a295f03421ea54c5055aad978cefb7121428941880ee0e787b38f30a5 install-aio.sh | sha256sum -c -
umask 077
export HOST_IP=192.168.56.74 KALTURA_APT=file:/opt/kaltura-baseline/repo
export ADMIN_EMAIL=baseline@lab.invalid
ADMIN_PASSWD="Aa1!$(openssl rand -hex 4)"
MYSQL_ROOT_PASSWD=$(openssl rand -hex 24)
export ADMIN_PASSWD MYSQL_ROOT_PASSWD
install -d -m 0700 /root/kaltura-baseline-private
printf '%s\n' "$ADMIN_PASSWD" > /root/kaltura-baseline-private/admin-password
printf '%s\n' "$MYSQL_ROOT_PASSWD" > /root/kaltura-baseline-private/mysql-password
umask 022 # Package/install-created runtime files must retain normal service readability.
bash ./install-aio.sh
unset ADMIN_PASSWD MYSQL_ROOT_PASSWD
php7.4 -r 'exit(PHP_MAJOR_VERSION === 7 && PHP_MINOR_VERSION === 4 ? 0 : 1);'
systemctl is-active apache2 mariadb kaltura-batch kaltura-nginx
curl --max-time 30 -fsS 'http://192.168.56.74/api_v3/index.php?service=system&action=ping' |
    grep -Eq '<result>(1|true)</result>'
printf 'PHP 7.4 synthetic baseline installed. Full workload acceptance is pending.\n'
