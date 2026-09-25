# Quick install — Ubuntu 26.04 (amd64)

Install Kaltura CE **18.20.0-1** and the optional Go Console **0.1.0** from
published packages. No local compilation, Go or Node installation is needed.

> Use a **fresh, dedicated Ubuntu 26.04 amd64 machine** on a trusted private
> network. This installer changes MariaDB authentication, Apache and package
> repositories; do not run it on an existing shared database/web server.
> The server still requires **PHP 7.4** and third-party repositories. PHP 8.3
> migration is only a proposal. This is not an Internet-facing hardening guide.

The project's AIO lab uses 4 CPUs and 8 GiB RAM. Allow additional disk space for
packages, uploaded originals and transcoded media. Choose a stable server IP.
Permit web access only from trusted clients; do not expose MariaDB or Elasticsearch.

## 1. Prepare the machine

Open a root Bash shell and keep using it for the server steps:

```bash
sudo -i
set -euo pipefail
. /etc/os-release
test "$ID" = ubuntu && test "$VERSION_ID" = 26.04
test "$(dpkg --print-architecture)" = amd64
apt-get update
apt-get install -y ca-certificates curl git openssl

# Replace with this machine's stable private IP, reachable by your browser.
export HOST_IP=192.168.56.40
mkdir -p /opt/kaltura-downloads/server
cd /opt/kaltura-downloads/server
```

## 2. Download and verify the server repository

```bash
BASE=https://github.com/jniltinho/platform-install-packages/releases/download/kaltura-server/v18.20.0-1
curl -fL --retry 3 "$BASE/kaltura-server-ubuntu-26.04-repo.tar.gz" -o kaltura-server-ubuntu-26.04-repo.tar.gz
curl -fL --retry 3 "$BASE/SHA256SUMS" -o SHA256SUMS
grep '  kaltura-server-ubuntu-26.04-repo.tar.gz$' SHA256SUMS | sha256sum -c -
mkdir -p /opt/kaltura-repo/ubuntu-26.04
tar -xzf kaltura-server-ubuntu-26.04-repo.tar.gz -C /opt/kaltura-repo/ubuntu-26.04
```

Expect `OK`. Stop if verification fails. The archive contains a **flat apt
repository**, including `Packages.gz`; the GitHub download URL itself is **not**
an apt repository. The installer trusts the verified local packages with
`[trusted=yes]`; these archives are not a signed distribution repository.

## 3. Install Kaltura

Fetch the installer from the same immutable server release tag:

```bash
git clone --depth 1 --branch kaltura-server/v18.20.0-1 \
  https://github.com/jniltinho/platform-install-packages.git /opt/kaltura-install

read -r -p 'Kaltura administrator email: ' ADMIN_EMAIL
export ADMIN_EMAIL
read -r -s -p 'Kaltura administrator password: ' ADMIN_PASSWD
printf '\n'
export ADMIN_PASSWD
# Generated SQL-safe database password; no literal secret in shell history.
export MYSQL_ROOT_PASSWD="$(openssl rand -hex 24)"
umask 077
printf '%s\n' "$MYSQL_ROOT_PASSWD" > /root/kaltura-mariadb-root-password

export KALTURA_APT=file:/opt/kaltura-repo/ubuntu-26.04
bash /opt/kaltura-install/deb/ubuntu-26.04/install-aio.sh
unset ADMIN_PASSWD MYSQL_ROOT_PASSWD
```

The Kaltura administrator password must be 8–14 characters with a digit,
lowercase letter and symbol, and must not contain parts of the administrator's
name/email. Keep it in your password manager. The database password file is
root-only; back it up securely, never commit or publish it. Do not run the
installer with shell tracing (`bash -x`).

The script configures PHP, Elasticsearch and the local apt repository, then
installs services in dependency order. If the PHP repository does not provide
packages for `resolute`, **stop**: do not substitute Debian/another Ubuntu suite
or PHP 8.x to get past dependency errors.

## 4. Check the server

```bash
systemctl is-active mariadb apache2 memcached elasticsearch \
  kaltura-nginx kaltura-sphinx kaltura-batch kaltura-populate kaltura-elastic-populate
curl -fsS "http://$HOST_IP/api_v3/index.php?service=system&action=ping"
```

Expect active services and an API result containing `1` or `true`.

- Admin Console: `http://YOUR_SERVER_IP/admin_console/`
- KMC: `http://YOUR_SERVER_IP/index.php/kmcng/`
- Delivery service: TCP 88; keep access restricted to the intended network.

Log into Admin Console with the email/password chosen above. Create or select a
**regular publisher partner**, and obtain its positive partner ID and admin
secret for the Go Console. Do not configure the console with system partner `-2`.
Publisher/KMC credentials and Go Console local accounts are separate.

For an optional upload/transcode/HLS smoke test **on a disposable lab only**,
see [`sanity.sh`](../deb/ubuntu-26.04/sanity.sh). It creates a test partner and
media; it is not a read-only production health check.

## 5. Install the Go Console (optional)

Still in the root shell:

```bash
mkdir -p /opt/kaltura-downloads/console
cd /opt/kaltura-downloads/console
BASE=https://github.com/jniltinho/platform-install-packages/releases/download/kaltura-console/v0.1.0
curl -fL --retry 3 "$BASE/kaltura-console_0.1.0_amd64.deb" -o kaltura-console_0.1.0_amd64.deb
curl -fL --retry 3 "$BASE/SHA256SUMS" -o SHA256SUMS
grep '  kaltura-console_0.1.0_amd64.deb$' SHA256SUMS | sha256sum -c -
apt-get install -y ./kaltura-console_0.1.0_amd64.deb
sudoedit /etc/kaltura-console/config.toml
```

Edit the existing sections (do not duplicate TOML sections):

| Setting | Value to configure |
|---|---|
| `server.host` | The server's stable private IP |
| `server.port` | `8080` |
| `server.https` | `true` |
| `server.base_path` | `""` for root, or `"/console"` for the prefix |
| `kaltura.service_url` | `"http://YOUR_SERVER_IP/api_v3"` |
| `kaltura.playback_host` | `"http://YOUR_SERVER_IP"` |
| `kaltura.extra_media_hosts` | `["YOUR_SERVER_IP:88"]` if delivery redirects there |
| `kaltura.partner_id` | Your positive publisher partner ID |
| `kaltura.admin_secret` | That publisher's admin secret, entered only in this protected file |

With both TLS certificate paths empty, the console creates a persistent
self-signed certificate for lab use. Verify/trust it on your client before
logging in. For production use a CA-issued certificate/key or a TLS reverse
proxy; follow the [TLS guide](../kaltura-console/docs/operations.md#standalone-https).
Console HTTPS does **not** enable HTTPS for the Kaltura server API/KMC.

Create an independent local console administrator using the hidden prompt:

```bash
sudo -u kaltura-console /usr/bin/kaltura-console \
  --config /etc/kaltura-console/config.toml \
  user add --email admin@example.com --name Administrator --role admin
systemctl enable --now kaltura-console
systemctl status kaltura-console --no-pager
kaltura-console version
```

Replace the example email. Open `https://YOUR_SERVER_IP:8080/`, or
`https://YOUR_SERVER_IP:8080/console/` if you selected that prefix. Log in with
this local account: **there is no default console username/password**.

## Troubleshooting and next steps

- Installer failure: inspect the first apt/debconf error. Do not purge packages
  or recreate the database to retry. Preserve configuration and data first.
- Console won't start: `journalctl -u kaltura-console -n 100 --no-pager`.
- Empty media/authorization errors: check the publisher ID, its admin secret
  and the configured API URL; never share the secret in diagnostic output.
- Playback returns 502: check delivery reachability and the exact allow-listed
  hostname/port. Never use wildcard allowlists or disable TLS verification.
- Back up MariaDB, `/opt/kaltura` configuration/media, console configuration
  and SQLite state before upgrades. Debian console **purge deletes its state**.

More detail: [Ubuntu 26.04 build/install](install-kaltura-ubuntu-26.04.md),
[console operations](../kaltura-console/docs/operations.md),
[architecture](../kaltura-console/docs/architecture.md),
[validation matrix](../kaltura-console/docs/validation.md).

This quick guide was checked against the release assets and repository scripts;
writing it did not provision another Ubuntu 26.04 machine.
