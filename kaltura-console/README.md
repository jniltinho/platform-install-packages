# Kaltura Console (Go)

A single Linux binary with an embedded Vue 3 UI for one Kaltura CE 18.20 partner.
It does not replace KMC or Admin Console. Local users are separate from Kaltura
users; Laravel accounts are not imported.

## Build

Requires Go 1.27, Node 24, npm and (for packages) nfpm. From this directory:

```sh
make build
make lint test
make package VERSION=0.1.0-rc1
bin/kaltura-console version
```

`make frontend` must run before a direct `go build`; the generated `web/dist`
assets are ignored in Git and embedded with `go:embed`. The release workflow
builds them before Go tests. Node and PHP are **not** required at runtime.

## Install

```sh
sudo apt install ./dist/kaltura-console_*.deb
# Rocky Linux 9:
sudo dnf install ./dist/kaltura-console-*.rpm
sudoedit /etc/kaltura-console/config.toml
sudo -u kaltura-console kaltura-console --config /etc/kaltura-console/config.toml user add --email admin@example.com --role admin
sudo systemctl start kaltura-console
```

Set `kaltura.service_url` to `http://KALTURA/api_v3`, `playback_host` to the
HTTP(S) delivery origin, `partner_id` to a regular publisher (not -2), and
`admin_secret` to that publisher's admin secret. The package starts no service
until configured. Port 8080 is the default. Configure TLS or put the console
behind a TLS reverse proxy before exposing credentials outside a trusted lab.

The service runs as `kaltura-console`; configuration is `root:kaltura-console`
0640 and state is in `/var/lib/kaltura-console`. Upgrades preserve configuration
and data and restart a running service. Debian **purge deletes local state**;
regular removal and RPM removal keep it. Back up config and the database first.

## Configuration

See [config.toml.example](config.toml.example) for all options. Lookup order is
`--config`, `./config.toml`, `/etc/kaltura-console/config.toml`. Environment
variables override file values, and explicitly supplied `serve` flags override both, e.g. `KCONSOLE_KALTURA_ADMIN_SECRET` and
`KCONSOLE_SERVER_PORT`. `config init --output config.toml` writes a new file
with mode 0600 and never overwrites an existing file.

SQLite is the pure-Go default (WAL, foreign keys, one writer, 5s busy timeout).
For MariaDB use `driver = "mysql"` and a DSN such as
`console:REPLACE@tcp(127.0.0.1:3306)/console?charset=utf8mb4&parseTime=true&loc=UTC`.
Create the database and grant access beforehand. `migrate` records versioned
migrations and `serve` applies them at startup. MariaDB DDL may implicitly
commit; back up before schema upgrades even though the migration runner uses
transactions.

Only list actual reverse proxy CIDRs in `server.trusted_proxies`; forwarded
client IP and HTTPS are ignored from other peers. The service cannot bind
privileged ports.

### HTTPS and /console deployment

Set `server.base_path = "/console"` to mount UI, assets, API, media and health
under that prefix. Keep it canonical without a trailing slash; empty means root.
Open `https://HOST/console/` and preserve `/console/` in reverse-proxy forwarding.
The same embedded frontend build works at either prefix. Session cookie Path
follows the prefix; direct TLS or a trusted HTTPS proxy sets Secure.

For standalone TLS, set `server.https = true` and supply both `tls_cert` and
`tls_key` for a production CA-issued pair. If both paths are empty, the console
creates/reuses a ten-year self-signed pair in `server.tls_dir` (default
`/var/lib/kaltura-console/tls`), with a 0600 private key. Self-signed certificates
are not automatically trusted by browsers. Invalid, expired or incomplete
material fails startup; certificates are not silently renewed. Rotate explicitly
and restart. Outbound Kaltura TLS verification is unchanged.

```sh
# Isolated lab: persistent self-signed HTTPS using configured host/port.
kaltura-console --config /etc/kaltura-console/config.toml serve --https --base-path /console
```

`serve --https --tls-cert ... --tls-key ... --tls-dir ... --base-path ...`
flags override matching environment/file settings when supplied. HTTP at root
remains the default. For Apache TLS termination, use backend HTTP on loopback,
trust only the proxy CIDR, and preserve Host/protocol and the prefix.
See [operations](docs/operations.md#standalone-https) for exact configuration,
Apache rules, certificate handling and migration steps. When moving from root,
log out/clear old root and prefix cookies before logging in again.

The proxy follows redirects only to configured service/playback origins and
`extra_media_hosts` (exact `host[:port]` entries). Add the actual Kaltura CDN
host when it differs; never use wildcards. Cookies and browser Authorization
are not forwarded upstream. Media URLs exposed to the browser contain no KS.

Uploads are staged to private disk files, capped by `upload.max_mb`, checked
for an ISO-BMFF `ftyp` header, and streamed to Kaltura. `allowed_ext` opts in
additional ISO-BMFF extensions; it does not enable arbitrary containers.
Concurrent uploads and minimum free space are configurable. Temporary files
are removed on completion/failure and abandoned files older than an hour are
removed at startup. Leave sufficient disk space for concurrent uploads.

## CLI

```sh
kaltura-console --config /etc/kaltura-console/config.toml migrate
kaltura-console --config /etc/kaltura-console/config.toml serve
kaltura-console user add --email user@example.com --role viewer
kaltura-console user passwd --email user@example.com
kaltura-console user list
kaltura-console user delete --email user@example.com
```

Passwords are read without echo from the terminal. Automation can pipe a
password to `--password-stdin`; do not put passwords in command-line arguments.
An administrator cannot remove/demote the last admin. Resetting passwords or
changing roles revokes that user's sessions. Only admins can mutate media.

## Verification

Unit tests use an in-process fake Kaltura API. `tests/e2e.sh` exercises a
configured console through a named agent-browser session, using an MP4 file
supplied by the operator. Never point it at production: it creates and deletes
test media. Screenshots belong in `../doc/prints/kaltura-console-go/`.

See [OpenSpec](../openspec/changes/add-kaltura-console-go/tasks.md) for exact
completion/validation status; unmarked tasks are not claimed complete.

## Release

Tags use `kaltura-console/vX.Y.Z`. The dedicated GitHub workflow runs lint,
tests and builds the tarball, DEB, RPM and SHA256SUMS. The `create-release` skill
contains the release procedure. No release tag is created by a local build.

## Documentation map

- [Architecture and trust boundaries](docs/architecture.md)
- [Installation, configuration and operations](docs/operations.md)
- [HTTP routes and CLI reference](docs/api.md)
- [Development, tests and release](docs/development.md)
- [Interactive diagrams and their sources](docs/diagrams/)
- [Noble VM validation evidence](../doc/validation-noble.md)

## License

GNU Affero General Public License v3; see the repository [LICENSE](../LICENSE).
