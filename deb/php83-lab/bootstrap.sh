#!/usr/bin/env bash
# Provision only PHP 8.3 tooling, not the incompatible released Kaltura packages.
set -euo pipefail
export DEBIAN_FRONTEND=noninteractive
. /etc/os-release
[[ $ID == ubuntu && $VERSION_ID == 24.04 ]]
[[ $(hostname) == kaltura-php83-lab ]]
[[ ! -d /opt/kaltura && ! -d /var/lib/mysql ]]
# Keep the candidate on native Ubuntu packages, even if another repo is added.
cat > /etc/apt/preferences.d/kaltura-php83-native <<'PIN'
Package: php8.3* libapache2-mod-php8.3
Pin: release o=Ubuntu
Pin-Priority: 1001

Package: php8.3* libapache2-mod-php8.3
Pin: version *
Pin-Priority: -1
PIN
apt-get update -q
apt-get install -y ca-certificates curl unzip python3 apache2 \
    php8.3-cli libapache2-mod-php8.3 php8.3-xml php8.3-curl php8.3-mysql \
    php8.3-mbstring php8.3-gd php8.3-gmp php8.3-ldap php8.3-zip php8.3-intl \
    php8.3-apcu php8.3-memcache php8.3-ssh2
php8.3 -r 'exit(PHP_MAJOR_VERSION === 8 && PHP_MINOR_VERSION === 3 ? 0 : 1);'
php8.3 -r '
$required = ["curl", "pdo_mysql", "mysqli", "mbstring", "gd", "gmp", "ldap",
    "zip", "intl", "apcu", "memcache", "ssh2", "xml", "dom", "xsl", "pcntl", "posix"];
foreach ($required as $extension) {
    if (!extension_loaded($extension)) { fwrite(STDERR, "Missing: $extension\n"); exit(1); }
}'
# Keep diagnostic output loopback-only and remove it even on failure.
cat > /etc/apache2/conf-available/php83-lab-probe.conf <<'APACHE'
<Files "php83-lab-probe.php">
    Require local
</Files>
APACHE
cat > /var/www/html/php83-lab-probe.php <<'PHP'
<?php
header('Content-Type: application/json');
echo json_encode(['version' => PHP_VERSION, 'sapi' => PHP_SAPI,
    'extensions' => get_loaded_extensions()]);
PHP
trap 'rm -f /var/www/html/php83-lab-probe.php' EXIT
a2enconf php83-lab-probe
systemctl restart apache2
install -d -m 0755 /var/lib/kaltura-php83-lab
curl -fsS http://127.0.0.1/php83-lab-probe.php > /var/lib/kaltura-php83-lab/apache-runtime.json
python3 - <<'PY'
import json
from pathlib import Path
r = json.loads(Path('/var/lib/kaltura-php83-lab/apache-runtime.json').read_text())
assert r['version'].startswith('8.3.') and r['sapi'] == 'apache2handler', r
required = {'curl','pdo_mysql','mysqli','mbstring','gd','gmp','ldap','zip','intl',
            'apcu','memcache','ssh2','xml','dom','xsl'}
assert required <= set(r['extensions']), required - set(r['extensions'])
PY
php8.3 -v > /var/lib/kaltura-php83-lab/php-version.txt
php8.3 -m > /var/lib/kaltura-php83-lab/cli-modules.txt
php8.3 --ini > /var/lib/kaltura-php83-lab/cli-ini.txt
dpkg-query -W 'php8.3*' 'libapache2-mod-php8.3' > /var/lib/kaltura-php83-lab/packages.txt
apt-cache policy $(dpkg-query -W -f='${binary:Package}\n' 'php8.3*' 'libapache2-mod-php8.3') \
    > /var/lib/kaltura-php83-lab/provider-policy.txt
printf 'PHP 8.3 CLI/Apache lab ready; Kaltura compatibility is NOT established.\n'
