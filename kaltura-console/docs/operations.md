# Installation and operations

[Architecture/source map](architecture.md) · [API](api.md) · [Build/release](development.md)

## Install and first login

Use an artifact for the host architecture and verify `SHA256SUMS` before installation. Current packaging targets Linux amd64. Examples assume the downloaded file is in the current directory:

```sh
sha256sum -c SHA256SUMS
sudo apt install ./kaltura-console_<version>_amd64.deb
# RPM-based host alternative:
# sudo dnf install ./kaltura-console-<version>-1.x86_64.rpm
```

Package installation creates the unprivileged `kaltura-console` system account, prepares state directories, migrates the database and enables the service when systemd is available. A fresh service is **not started** until configuration and initial-account setup are complete. Installation is not proof that a target distribution has passed runtime validation.

1. Edit `/etc/kaltura-console/config.toml` using a privileged editor. Set the partner ID, admin secret, API URL and playback host. Never commit this file or paste its contents into a ticket.
2. Configure HTTPS (direct TLS or a trusted reverse proxy) before using real credentials over a network. The default listener is all interfaces on port 8080 with HTTP.
3. Create your first admin using an interactive hidden password prompt:

   ```sh
   sudo -u kaltura-console /usr/bin/kaltura-console \
     --config /etc/kaltura-console/config.toml \
     user add --email admin@example.invalid --name Administrator --role admin
   sudo systemctl start kaltura-console
   sudo systemctl status kaltura-console --no-pager
   ```

4. Open your configured console URL and log in with that account. There is **no built-in/default username or password**. Console credentials are independent of the Kaltura partner secret.

For noninteractive provisioning, `--password-stdin` reads the first line from stdin. Obtain it from a protected secret source; avoid literal passwords in command arguments, shell history, repository files or logs. Use `user passwd --email ...` for recovery; it revokes all sessions for that user.

## Installed paths

| Path | Purpose / ownership |
|---|---|
| `/usr/bin/kaltura-console` | Executable, mode 0755 |
| `/etc/kaltura-console/config.toml` | Local secrets/settings; root:`kaltura-console`, 0640; preserved on upgrade |
| `/usr/lib/systemd/system/kaltura-console.service` | Packaged unit; customize with a systemd override, not by editing this file |
| `/var/lib/kaltura-console` | Service working directory/state; `kaltura-console`, 0750 |
| `/var/lib/kaltura-console/console.db` | Default SQLite database (plus WAL/SHM sidecars while running) |
| `/var/lib/kaltura-console/tmp` | Private upload staging; `kaltura-console`, 0750 |
| `/usr/share/doc/kaltura-console/README.md`, `CHANGELOG.md` | Packaged quick-start/release notes |
| system journal | Structured JSON stdout/stderr; no dedicated application log file |

The extended guides and diagrams are repository documents, not currently installed by the package manifest. The service has `ProtectSystem=strict`, `ProtectHome=yes`, `PrivateTmp=yes`, no capabilities and write access only beneath `/var/lib/kaltura-console`. Moving state outside this tree requires a reviewed unit override as well as filesystem permissions. A TLS key under a protected home directory will not be readable by the service.

## Configuration reference

Authority: [`config.toml.example`](../config.toml.example) and [`internal/config/config.go`](../internal/config/config.go). Precedence is `KCONSOLE_*` environment variables over TOML over defaults. Dot-separated keys map to underscores, e.g. `KCONSOLE_KALTURA_ADMIN_SECRET`. `--config` selects a specific file; a missing explicit file is an error. Without it, lookup checks `./config.toml`, then `/etc/kaltura-console/config.toml`; absent files permit defaults/environment loading.

| Section/key | Default | Meaning |
|---|---|---|
| `server.host`, `port` | `0.0.0.0`, `8080` | Bind address/port |
| `server.https` | `false` | Direct TLS; requires `tls_cert`, `tls_key` |
| `server.trusted_proxies` | `[]` | Exact trusted CIDRs for forwarded IP/protocol |
| `server.session_ttl`, `session_max` | `2h`, `12h` | Normal-session idle/absolute limits |
| `database.driver` | `sqlite` | `sqlite` or `mysql` (MariaDB) |
| `database.dsn` | `/var/lib/kaltura-console/console.db` | SQLite path or MySQL driver DSN |
| `database.debug` | `false` | SQL logging; avoid enabling with production secrets |
| `kaltura.service_url` | No usable built-in value | API base ending in `/api_v3`; required |
| `kaltura.upload_service_url` | empty | Optional dedicated API upload endpoint; otherwise service URL |
| `kaltura.playback_host` | No usable built-in value | Delivery base URL; required |
| `kaltura.extra_media_hosts` | `[]` | Additional exact `host[:port]` redirect destinations, not URLs/wildcards |
| `kaltura.partner_id`, `admin_secret` | unset | Required positive partner ID and its admin secret |
| `kaltura.user_id`, `session_expiry` | `kaltura-console`, `24h` | KS identity and requested lifetime |
| `kaltura.http_timeout`, `connect_timeout` | `15s`, `5s` | API operation/response-header and dial limits |
| `kaltura.upload_timeout` | `30m` | Upload budget; not a conversion deadline |
| `upload.tmp_dir` | `/var/lib/kaltura-console/tmp` | Staging filesystem |
| `upload.max_mb`, `max_concurrent` | `2048`, `2` | Per-file MiB limit; per-process slots |
| `upload.min_free_mb` | `1024` | Minimum free MiB at admission (not a reservation) |
| `upload.allowed_ext` | `[".mp4"]` | Lowercase extensions; BMFF header validation still applies |
| `log.level` | `info` | `debug`, `info`, `warn`, `error` |

The example file includes loopback Kaltura URLs but intentionally invalid partner credentials. Replace them. Duration values use Go duration strings. Restart after changing configuration; hot reload is not implemented.

### Reverse proxy

Bind the console to loopback when the proxy is on the same host. Trust only the proxy's actual CIDR (for example `127.0.0.1/32`), not all private networks. Preserve the external Host and set `X-Forwarded-Proto` and `X-Forwarded-For` correctly, replacing untrusted incoming forwarding values. Without a trusted TLS-terminating proxy, Secure cookies and same-origin checks will not reflect the external HTTPS scheme correctly.

Proxy request-body limits must allow the configured upload size **plus** its 64 KiB envelope. Timeouts must accommodate both browser intake and the upstream upload; avoid response buffering for media and preserve Range/HEAD. Disable upload request buffering if you want to avoid a second large staging copy at the reverse proxy. Secure proxy temporary storage too. These are deployment requirements, not a bundled proxy configuration.

### MariaDB instead of SQLite

Provision a separate console database/account and set `database.driver = "mysql"`. Example DSN shape (replace placeholders securely):

```text
console:<secret>@tcp(db.internal:3306)/kaltura_console?charset=utf8mb4&parseTime=true&loc=UTC
```

Use appropriate TLS for remote database traffic. The account needs schema migration privileges in **its console database**. Changing the driver does not migrate existing SQLite accounts/sessions; plan an explicit data migration or recreate accounts. Back up before migrations and never point this application at the Kaltura database.

## CLI and maintenance

```sh
kaltura-console version
kaltura-console config init --output /path/to/new-config.toml
kaltura-console --config /etc/kaltura-console/config.toml migrate
kaltura-console --config /etc/kaltura-console/config.toml user list
kaltura-console --config /etc/kaltura-console/config.toml user passwd --email admin@example.invalid
kaltura-console --config /etc/kaltura-console/config.toml user delete --email viewer@example.invalid
journalctl -u kaltura-console --since today
```

Run database commands as the service account when using package state. `config init` creates a new 0600 file and refuses to overwrite an existing one. CLI user creation defaults to `viewer`; initial administrators require `--role admin`. CLI and HTTP enforce last-admin protection; HTTP additionally prevents self-deletion.

### Backup, upgrade and restore

1. Schedule a maintenance window and stop intake; an active upload may exceed the 30-second shutdown window.
2. Stop the service. Back up `/etc/kaltura-console/config.toml` and console state with ownership/modes preserved to restricted storage. With SQLite, copying the whole stopped state directory also captures any WAL sidecars; do not copy only the live `.db` file. Use a database-aware backup for MariaDB.
3. Install the new verified package. Configuration is `noreplace`; migrations run during installation. Inspect package-manager `.rpmnew`/equivalent config artifacts before adopting new defaults.
4. Start the service; check liveness, authenticated diagnostics, login, list, upload and Range playback.
5. To roll back a schema-incompatible upgrade, stop the service, restore the matched pre-upgrade database/config and binary/package. There is no exposed CLI migration-down command. Avoid parallel migrations from multiple hosts.

Ordinary removal retains state. **Explicit Debian purge deletes `/var/lib/kaltura-console`**, including accounts/sessions/staging: back up first. A console backup does not back up Kaltura media; maintain Kaltura backups separately.

## Troubleshooting

| Symptom | Check |
|---|---|
| Service fails immediately | Journal, required partner settings, explicit config path, file permissions, certificate paths |
| Login unavailable after install | Initial admin must be created manually; verify the same database/config is used by CLI and service |
| Login 429 | Wait for the 15-minute failed-attempt window; inspect proxy IP attribution |
| Mutation 403 after HTTPS setup | Correct Origin/Host, trusted proxy CIDRs, forwarding protocol, current CSRF token |
| Media list 502 | Authenticated diagnostics; API URL, partner secret, endpoint connectivity |
| Thumbnail/stream 502 | Kaltura delivery health and redirect host:port allowlist; do not broaden it blindly |
| Upload 413/429/507 | Console and proxy limits, active upload slots, free staging space |
| Upload 422 | Extension, ISO-BMFF header, single file part, name/description lengths |
| Upload 502 | API/upload endpoint, chunked-body support, timeout and Kaltura logs; inspect orphan entry cleanup |
| Video never becomes READY | Kaltura conversion workers/flavors; console does not run transcoding |
| New database unexpectedly empty | Wrong `--config`/DSN or working directory; do not create replacement admins until scope is verified |
