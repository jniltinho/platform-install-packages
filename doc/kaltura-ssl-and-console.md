# HTTPS for Kaltura and the Kaltura Console at /console

This guide serves everything over HTTPS from one host name, for a Single-server All-In-One:

| URL | Served by |
|---|---|
| `https://media.example.com/` (API, KMC, Admin Console) | Apache, port 443 |
| `https://media.example.com:8443/hls/...` (VOD/HLS) | kaltura-nginx, port 8443 |
| `https://media.example.com/console/` | Kaltura Console (Go), proxied by Apache to `127.0.0.1:8080` |

Validated on Ubuntu 24.04 with the `aiossl` Vagrant VM (`deb/noble`, 192.168.56.21, self-signed certificate): `sanity.sh` passes over `https://` (API, KMC, upload, transcoding, HLS manifest and segment). The Rocky Linux 9 steps follow the same answers, but they have not been run in a VM yet.

## 1. Certificate

Apache and nginx use the same files:

- `/etc/ssl/certs/kaltura.crt`: certificate. With Let's Encrypt, use the full chain.
- `/etc/ssl/private/kaltura.key`: private key, mode `0600`.
- An optional chain file, only for Apache.

The certificate must cover the host name users type (the `CN`/`subjectAltName`). Use an IP only in test setups (`subjectAltName=IP:...`).

### Let's Encrypt (certbot)

Requirements: the host name resolves to the server, and ports 80 and 443 are reachable from the Internet. On an SSL install, port 80 is Apache's default site (`/var/www/html`), so the HTTP-01 webroot challenge works without touching the Kaltura vhosts.

```bash
# Ubuntu: apt install certbot     Rocky 9: dnf install epel-release && dnf install certbot
certbot certonly --webroot -w /var/www/html -d media.example.com -m admin@example.com --agree-tos -n
ln -sf /etc/letsencrypt/live/media.example.com/fullchain.pem /etc/ssl/certs/kaltura.crt
ln -sf /etc/letsencrypt/live/media.example.com/privkey.pem   /etc/ssl/private/kaltura.key
```

Reload both servers after each renewal:

```bash
cat > /etc/letsencrypt/renewal-hooks/deploy/kaltura.sh <<'EOF'
#!/bin/sh
systemctl reload apache2 2>/dev/null || systemctl reload httpd
systemctl restart kaltura-nginx
EOF
chmod 755 /etc/letsencrypt/renewal-hooks/deploy/kaltura.sh
certbot renew --dry-run
```

Get the certificate **before** configuring Kaltura, so the host name is the final one: Kaltura writes it into the DB, the delivery profiles and the UI confs.

### A certificate from a CA

Copy the certificate (plus any intermediates, appended to it) and the key to the paths above. For Apache, you can also pass the intermediates as a separate chain file (`apache_ssl_chain` / `CHAIN_FILE`).

## 2. Install Kaltura with SSL

### Ubuntu 24.04 / 26.04 (debconf)

`deb/noble/install-aio.sh` takes `SSL=1` (see its `SSL_CERT`, `SSL_KEY` and `SSL_CHAIN` variables). Without them, it creates a self-signed certificate for `HOST_IP`. For your own server, preseed these values before `apt install kaltura-server`:

```
kaltura-base    kaltura-base/vhost_port        string  443
kaltura-base    kaltura-base/vod_packager_port string  8443
kaltura-front   kaltura-front/is_apache_ssl    boolean true
kaltura-front   kaltura-front/apache_ssl_cert  string  /etc/ssl/certs/kaltura.crt
kaltura-front   kaltura-front/apache_ssl_key   string  /etc/ssl/private/kaltura.key
kaltura-front   kaltura-front/apache_ssl_chain string  NONE
kaltura-front   kaltura-front/vhost_port       string  443
kaltura-nginx   kaltura-nginx/is_ssl           boolean true
kaltura-nginx   kaltura-nginx/ssl_cert         string  /etc/ssl/certs/kaltura.crt
kaltura-nginx   kaltura-nginx/ssl_key          string  /etc/ssl/private/kaltura.key
```

### Rocky Linux 9 (answers file)

In the answers file passed to `kaltura-config-all.sh`:

```
PROTOCOL="https"
IS_SSL="y"
KALTURA_VIRTUAL_HOST_PORT="443"
CRT_FILE=/etc/ssl/certs/kaltura.crt
KEY_FILE=/etc/ssl/private/kaltura.key
CHAIN_FILE=NONE
IS_NGINX_SSL="Y"
SSL_CERT=/etc/ssl/certs/kaltura.crt
SSL_KEY=/etc/ssl/private/kaltura.key
VOD_PACKAGER_SSL_PORT=8443
VOD_PACKAGER_PORT="8443"
```

### Why the VOD port is 8443

The playManifest builds segment URLs as `<scheme of the request>://<delivery profile host:port>`. If the delivery profiles keep port `88` (plain HTTP), an HTTPS player gets `https://host:88/...`, which fails. A new install with the settings above creates the profiles on port 8443. To fix an existing install, see [nginx-ssl-config.md](nginx-ssl-config.md):

```sql
UPDATE delivery_profile SET url = REPLACE(url, 'media.example.com:88', 'media.example.com:8443')
 WHERE url LIKE 'media.example.com:88%';
```

After the update, clear the cache with `rm -rf /opt/kaltura/app/cache/*`, then restore its owner and restart memcached and Apache.

The nginx `kalapi` upstream must point at the HTTPS API port (`media.example.com:443`); the packages set it when SSL is enabled.

## 3. Kaltura Console at /console

Configure the console to listen only on localhost under the prefix. In `config.toml`:

```toml
[server]
host = "127.0.0.1"
port = 8080
base_path = "/console"
trusted_proxies = ["127.0.0.1/32", "::1/128"]

[kaltura]
service_url   = "https://media.example.com/api_v3"
playback_host = "https://media.example.com"
```

The prefix reaches the console unchanged. Behind a trusted proxy, the console reads `X-Forwarded-Proto`. It then marks its cookies `Secure` and scopes them to `Path=/console`.

The Kaltura vhosts include `/opt/kaltura/app/configurations/apache/conf.d/enabled.*.conf`, so a drop-in file publishes the console without editing the packaged vhost. Create `/opt/kaltura/app/configurations/apache/conf.d/enabled.console.conf`:

```apache
# Kaltura Console behind the Kaltura vhost at /console
# mod_rewrite (not RedirectMatch): the Kaltura catch-all rewrite would win otherwise
RewriteEngine On
RewriteRule ^/console$ /console/ [R=301,L]
ProxyPreserveHost On
RequestHeader set X-Forwarded-Proto "expr=%{REQUEST_SCHEME}"
ProxyPass        /console/ http://127.0.0.1:8080/console/
ProxyPassReverse /console/ http://127.0.0.1:8080/console/
```

```bash
# Ubuntu
a2enmod proxy_http headers rewrite && apache2ctl configtest && systemctl reload apache2
# Rocky 9 (the modules are loaded by default)
apachectl configtest && systemctl reload httpd
setsebool -P httpd_can_network_connect 1   # only with SELinux enforcing
```

Check it:

```bash
curl -sI https://media.example.com/console           # 301 -> /console/
curl -s  https://media.example.com/console/healthz    # 200
```

### Console standalone over HTTPS

Without Apache in front, the console can serve TLS itself: set `https = true` with `tls_cert` and `tls_key` in `[server]`, or pass `--https --tls-cert ... --tls-key ...`. If both paths are empty, the console creates a self-signed certificate once in `tls_dir` (default `/var/lib/kaltura-console/tls`). It reuses that certificate on later starts. See the console README for details.

## Troubleshooting

| Symptom | Cause |
|---|---|
| Player loads the manifest, but segments fail over https | Delivery profiles still on `:88`: run the UPDATE above |
| `/console` redirects to the Kaltura home page or `@CORP_REDIRECT@` | A `RedirectMatch` was used instead of the `RewriteRule` above |
| `/console/` returns 503 | The console is not running on `127.0.0.1:8080` |
| The console reports TLS errors calling the API | The certificate does not cover `service_url`'s host name, or its issuing CA is not trusted by the system |
