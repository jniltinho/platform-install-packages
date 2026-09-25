# kaltura-console-ops Specification

## Purpose

Operational contract of the Go kaltura-console: command line, configuration, database backends, the Kaltura API client, packaging and release.

## Requirements

### Requirement: Single static binary
The console SHALL build with `CGO_ENABLED=0` into one binary that embeds the web UI. It SHALL NOT need PHP, Node or a separate web server at runtime.

#### Scenario: Run from a clean host
- **WHEN** the binary and a `config.toml` are copied to a clean Ubuntu 24.04 or Rocky Linux 9 host
- **THEN** `kaltura-console serve` starts and serves the UI and API

### Requirement: CLI
The binary SHALL provide these Cobra commands:
- `serve`;
- `migrate`;
- `user add|passwd|list|delete`;
- `config init`;
- `version`, which prints the version, commit and build date injected at build time.

#### Scenario: First admin
- **WHEN** the operator runs `kaltura-console user add --email a@b.c --role admin` and enters a password
- **THEN** the user can log in to the web console

### Requirement: Configuration file
Configuration SHALL be read from `config.toml`, looked up in this order: `--config`, the working directory, `/etc/kaltura-console/`. Environment variables prefixed `KCONSOLE_` SHALL override file values. `serve` SHALL fail fast with a clear message when `kaltura.partner_id` or `kaltura.admin_secret` is missing.

#### Scenario: Missing secret
- **WHEN** `admin_secret` is empty
- **THEN** `serve` exits non-zero with a message naming the missing key and prints no secret values

### Requirement: Database backends
The console SHALL support SQLite (default, pure Go) and MariaDB/MySQL through the same code, selected by `database.driver`. Schema migrations SHALL be versioned and recorded, and SHALL run inside a transaction. They SHALL run with `migrate` and automatically at `serve` start.

#### Scenario: MariaDB
- **WHEN** `driver = "mysql"` with a valid DSN
- **THEN** `migrate` creates the tables
- **AND** login works exactly as with SQLite

### Requirement: Kaltura API client
The client SHALL:
- call `api_v3` directly, with no gateway: form POST to `{service_url}/`, `format=1`, flattened `object:field` parameters;
- cache an admin KS until 5 minutes before it expires;
- retry a call exactly once after refreshing the KS on `INVALID_KS`, `EXPIRED_KS`, `KS_EXPIRED` or `INVALID_SESSION_ID`, rebuilding the upload body from the staged file on retry;
- map Kaltura exceptions to typed errors;
- stream uploads without buffering the whole file in memory.

#### Scenario: Expired KS
- **WHEN** a call returns `EXPIRED_KS`
- **THEN** the client starts a new session and repeats the call once
- **AND** it returns that call's result

#### Scenario: Compatibility
- **WHEN** the console runs against the Kaltura CE 18.20 noble AIO in `deb/noble`
- **THEN** list, upload, READY polling, playback, edit and delete all succeed

### Requirement: Packaging
The project SHALL produce `.deb` and `.rpm` packages that install:
- the binary to `/usr/bin/kaltura-console`;
- a config file to `/etc/kaltura-console/config.toml` (preserved on upgrade);
- a data directory `/var/lib/kaltura-console` owned by a dedicated system user;
- a hardened systemd unit `kaltura-console.service`.

#### Scenario: Upgrade keeps data
- **WHEN** a newer package is installed over an existing one
- **THEN** users, sessions and `/etc/kaltura-console/config.toml` are preserved
- **AND** the service is restarted

#### Scenario: Rocky Linux 9
- **WHEN** the `.rpm` is installed on a Rocky Linux 9 host
- **THEN** the service starts under the `kaltura-console` user with its hardened unit

#### Scenario: Install on the AIO
- **WHEN** the `.deb` is installed on the noble `aio` VM and the config points to 127.0.0.1
- **THEN** `systemctl is-active kaltura-console` is `active` and the login page answers HTTP 200

### Requirement: Release
A tag `kaltura-console/vX.Y.Z` SHALL trigger CI that builds the frontend, runs the Go tests and publishes a GitHub release with the tar.gz, `.deb` and `.rpm` assets. The CHANGELOG SHALL follow Keep a Changelog.

#### Scenario: Tag pushed
- **WHEN** `kaltura-console/v0.1.0` is pushed
- **THEN** the release `kaltura-console/v0.1.0` has release notes and the three assets

### Requirement: Standalone HTTPS
The console SHALL support HTTPS with an explicit certificate/key pair or, when
neither is provided, a persisted self-signed certificate in `server.tls_dir`.
It SHALL support equivalent serve flags and environment configuration.
Private keys SHALL be mode 0600 and existing material SHALL NOT be overwritten.

#### Scenario: First standalone TLS start
- **WHEN** HTTPS is enabled without explicit certificate paths
- **THEN** a ten-year self-signed certificate is created and HTTPS serves the console
- **AND** subsequent starts reuse the same certificate and private key

#### Scenario: Invalid certificate configuration
- **WHEN** only one explicit certificate path is configured or stored material is incomplete
- **THEN** startup fails without replacing existing certificate material
