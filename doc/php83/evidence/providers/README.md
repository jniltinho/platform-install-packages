# Disposable provider probes — 2026-09-25

These are package/runtime probes, **not Kaltura acceptance or provider selection**.
Containers were removed after testing, with no bind mounts or production data.
No host/VM package repositories were changed. APT/RPM signature verification
remained enabled. Repo signing keys were bootstrapped from the providers' HTTPS
URLs; fingerprints are recorded, not independently authenticated out of band.

Images (amd64, Docker):

- `ubuntu:26.04`: `ubuntu@sha256:da6fc2be547864451aa253836dd926da33623312df4a9a243e35dc877c378a78`
- `rockylinux:9`: `rockylinux@sha256:d7be1c094cc5845ee815d4632fe377514ee6ebcf8efaed6892889657e5ddaaa6`

## Results and limitations

| Image/provider | Observation | Exit |
|---|---|---|
| Ubuntu 26.04 native | PHP 8.3 requested packages not found; simulation fails | 100 |
| Ubuntu 26.04 Sury `resolute` | Signed APT metadata accepted; requested packages installed; CLI PHP 8.3.35 and modules printed | 0 |
| Rocky 9 AppStream `php:8.3` | Stream enabled; listing contains PHP 8.3.33 and several extensions, but not memcache/ssh2 | 0 |
| Rocky 9 Remi `php:remi-8.3` | Requested packages installed; PHP 8.3.35 CLI and FPM module lists printed | 0 |

An AppStream partial `dnf list` result can exit zero: it does **not** establish
resolution of the complete dependency set. Ubuntu's Apache module package was
installed, but no Apache request was exercised in this container. FPM `-m` is
module discovery, not FastCGI request acceptance. EL9's probe does not cover all
application extension requirements (for example bcmath was not requested).
Final extension/ABI/provider matrix and unattended application tests remain open.

At probe time, the Ondrej PPA `dists/resolute/Release` returned HTTP 404, while
Sury's matching `resolute` Release returned HTTP 200. More importantly, the latter
passed signed APT metadata validation and dependency installation below. No
Debian suite or insecure APT override was used. Availability is time-dependent.

## Reproduction

Run each block in a separate disposable container of the image above, e.g.
`docker run --rm ubuntu:26.04 bash -c '...'`. Full output is in adjacent logs.

Native Ubuntu:

```sh
apt-get update -qq
apt-cache policy php-cli php8.3-cli libapache2-mod-php8.3 php8.3-mysql php8.3-memcache php8.3-ssh2
apt-get install --simulate php8.3-cli libapache2-mod-php8.3 php8.3-mysql php8.3-memcache php8.3-ssh2
```

Ubuntu Sury (container only; not an installation recommendation):

```sh
set -eu
apt-get update -qq
apt-get install -y ca-certificates curl gnupg
curl -fsSL https://packages.sury.org/php/apt.gpg | gpg --dearmor -o /usr/share/keyrings/sury-php.gpg
gpg --show-keys --with-fingerprint /usr/share/keyrings/sury-php.gpg
echo 'deb [signed-by=/usr/share/keyrings/sury-php.gpg] https://packages.sury.org/php/ resolute main' > /etc/apt/sources.list.d/sury-php.list
apt-get update
apt-cache policy php8.3-cli libapache2-mod-php8.3 php8.3-memcache php8.3-ssh2
apt-get install -y php8.3-cli libapache2-mod-php8.3 php8.3-mysql php8.3-xml php8.3-mbstring php8.3-gd php8.3-gmp php8.3-ldap php8.3-intl php8.3-zip php8.3-apcu php8.3-memcache php8.3-ssh2 php8.3-curl php8.3-bcmath
php8.3 -v
php8.3 -m
```

Native Rocky:

```sh
set -eu
dnf -q module list php --all
dnf -y module enable php:8.3
dnf list --available php-cli php-fpm php-mysqlnd php-xml php-mbstring php-gd php-gmp php-ldap php-intl php-pecl-zip php-pecl-apcu php-pecl-memcache php-pecl-ssh2
```

Rocky Remi, following its [repository prerequisites](https://blog.remirepo.net/pages/Config-en):

```sh
set -eu
dnf -y install epel-release dnf-plugins-core
dnf config-manager --set-enabled crb
dnf -y install https://rpms.remirepo.net/enterprise/remi-release-9.rpm
dnf -y module reset php
dnf -y module enable php:remi-8.3
dnf -y install php-cli php-fpm php-mysqlnd php-xml php-mbstring php-gd php-gmp php-ldap php-intl php-pecl-zip php-pecl-apcu php-pecl-memcache php-pecl-ssh2
php -v
php -m
php-fpm -m
rpm -qa 'php*' | sort
```
