## Context

- **Source app.** The source is `criare/kaltura-console`, a Laravel app.
  - Routes: `/login`, `/dashboard`, `/media` (search, paginate, 20 per page), `/media/upload`, `/media/{id}` (show, PATCH, DELETE), `/media/{id}/status` (JSON used for polling), `/media/{id}/thumbnail`, `/media/{id}/stream` (proxy with Range), `/system/health`.
  - Users: one local users table, with no roles.
  - UI: pt-BR, with a dark top navbar (slate-900), white page header, `max-w-7xl` content and status badges (emerald ready, amber processing, red error, gray other).
- **Kaltura calls.** It uses `session.start` (type 2, cached for expiry − 300 s, retried once on `INVALID_KS`/`EXPIRED_KS`), `media.list/get/add/update/delete`, `uploadToken.add/upload`, `media.addContent` (`KalturaUploadedFileTokenResource`), `flavorAsset.list` and `system.ping`. Every call is a form POST to `{service_url}/` with `format=1` and flattened `obj:field` parameters.
- **House Go pattern.** It comes from go-ispconfig and painel-golang:
  - Root `main.go` calls `cmd.Execute`, with Cobra commands in `cmd/`.
  - Viper reads `config.toml`, and `config.toml.example` is committed.
  - Echo v5.3.x, GORM 1.31, Vue 3 + Vite in `frontend/` built to `web/dist` and embedded with `//go:embed all:dist`.
  - Builds use `CGO_ENABLED=0 -trimpath -ldflags "-s -w -X …Version/BuildDate/GitCommit"`, with the version taken from `git describe`.
  - Logging is `slog` JSON. Also: `.golangci.yml`, Keep a Changelog, nfpm packaging (painel-golang), a release workflow on tags, and the `create-release` skill.
- **Environment.** The host has Go 1.27.1 and Node 24. The noble AIO VM (192.168.56.20) is available for E2E.

## Goals / Non-Goals

**Goals:**
- Feature parity with the Laravel console, in one static binary with the UI embedded.
- SQLite by default, for a zero-dependency install next to the Kaltura AIO. MariaDB is optional and uses the same code.
- The UI reuses the painel-golang `criarenet` look: square corners, navy/orange palette, tabs plus sub-menu band, and a help column. It adds modern behaviors: toasts, upload progress, and responsive down to 360 px.

**Non-Goals:**
- Replacing the KMC or the Admin Console.
- Multi-partner support (one partner per console instance, as today).
- Live streaming, analytics, and roles beyond admin/viewer.
- A public REST API contract (the JSON API is internal to the SPA; there is no Swagger requirement).

## Decisions

1. **Location and module.** The project lives in `kaltura-console/` at the repo root, as Go module `kaltura-console`. The layout follows go-ispconfig:
   - `main.go` at the root;
   - `cmd/` for the Cobra commands;
   - `internal/{config,database,models,auth,kaltura,server,handlers,middleware,buildinfo}`;
   - `frontend/` for the Vue app;
   - `web/` with `web.go` holding the embed of `dist/`;
   - `packaging/`, `init/systemd/`, `Makefile`, `config.toml.example`, `CHANGELOG.md`.
2. **SQLite without CGO.**
   - **Pinned versions**: `github.com/glebarez/sqlite` pinned together with GORM 1.31.x. CI builds and runs the tests with `CGO_ENABLED=0`.
   - **Connection settings**: SQLite runs with `_pragma=busy_timeout(5000)`, `journal_mode(WAL)` and `foreign_keys(1)`, with one writer connection.
   - **Migrations**: versioned with `github.com/go-gormigrate/gormigrate/v2`, with IDs such as `202609250001_init`. They run inside a transaction and are recorded in a `migrations` table. The same code path is used for MariaDB.
   - **Details**: The build uses `github.com/glebarez/sqlite` (GORM dialector on modernc, pure Go), so `CGO_ENABLED=0` still works. MariaDB uses `gorm.io/driver/mysql`. Config `[database] driver = "sqlite" | "mysql"` plus `dsn`. Tables: `users` and `sessions` (and `login_attempts`). `migrate` applies pending migrations, and `serve` applies them at start. Alternative rejected: mattn/go-sqlite3, because it needs CGO.
3. **Auth.** Sessions are server-side and DB-backed, as in go-ispconfig.
   - **Cookie**: a random 32-byte ID, `HttpOnly`, `SameSite=Lax`, with `Secure` set when the request comes over HTTPS or a trusted proxy.
   - **Rotation and expiry**: the session ID is rotated on login. Sessions have an idle timeout (`session_ttl`) and an absolute cap (`session_max`). "Lembrar-me" extends the cap to 30 days.
   - **CSRF**: every mutating request (POST/PATCH/PUT/DELETE) must send `X-CSRF-Token`, which must equal the per-session token returned by `GET /api/session`. The go-ispconfig synchronizer pattern is used.
   - **Revocation**: all sessions of a user are revoked when their password or role changes or the user is deleted.
   - **Passwords and lockout**: passwords are hashed with bcrypt. Login lockout is 5 failures per 15 minutes per IP and e-mail.
   - **Return URL**: after login the user returns to the originally requested URL, validated to be a local path.
   - **Roles**: `admin` can upload, edit, delete and manage users; `viewer` is read-only.
   - **User management** (new compared to Laravel):
     - list, add, change role, reset password, delete;
     - unique e-mail;
     - the last admin cannot be deleted or demoted;
     - an admin cannot delete themselves.
   - **Bootstrap**: when there are no users, `serve` logs a hint to run `kaltura-console user add --role admin`. The package postinst prints the same hint.
4. **Kaltura client** in `internal/kaltura`.
   - Form-POSTs to `{service_url}/`, never to `index.php`.
   - KS cache guarded by a mutex. One retry after refreshing the KS on `INVALID_KS`, `EXPIRED_KS`, `KS_EXPIRED` or `INVALID_SESSION_ID`.
   - Error mapping: an `objectType` containing `Exception`, or `code`+`message`.
   - Uploads always come from a **staged file on disk**. Each attempt, including the KS retry, reopens the file and builds a new multipart body through `io.Pipe`. The writer goroutine is tied to the request `context`: on an early upstream response or on cancel, the pipe is closed with an error so no goroutine leaks. A test covers an upstream that answers before reading the body.
   - The client has `ResponseHeaderTimeout` and connect timeouts but no overall `Timeout`, so long uploads and streams are not cut. Uploads get `upload_timeout` through their context.
5. **Upload path.**
   1. The browser posts the file to `POST /api/media` (multipart). The body is capped with `http.MaxBytesReader` before any parsing, and the handler streams it to `upload_tmp_dir`, which defaults to `/var/lib/kaltura-console/tmp`.
   2. Concurrency is limited with a semaphore (`max_concurrent_uploads`, default 2; excess requests get 429). An upload is refused while the tmp dir has less free space than `min_free_mb`.
   3. Validation keeps Laravel parity: `.mp4` only by default, and the first bytes must sniff as an ISO-BMFF `ftyp` box. Extra extensions are opt-in through `allowed_ext`.
   4. The console then runs `media.add` → `uploadToken.add` → `uploadToken.upload` → `media.addContent`.
   5. On failure after `media.add`, the entry is deleted (best effort) and a distinct step error is returned.
   6. Temp files are removed on success, error or cancel, and older than 1 hour at startup.
   7. The UI shows three phases: "Enviando ao console" with byte progress from `XMLHttpRequest.upload.onprogress`, "Enviando ao Kaltura", then "Processando". Success is shown only after `addContent`.
6. **Media proxy.**
   - **Access control**: `GET|HEAD /media/{id}/stream` and `/thumbnail` require a session and an `entryId` matching `^[0-9]_[a-z0-9]{8}$`. The entry must belong to the configured partner (`media.get`, cached for 60 s).
   - **Upstream fetch**:
     - The console requests `playManifest …/format/url` and follows redirects itself, at most 5.
     - Each hop must match an **allowlist**: the hosts of `playback_host` and `service_url`, plus `extra_media_hosts`. Anything else returns 502, which protects against SSRF.
     - Only `Range` (and `If-Range`) are forwarded. Browser cookies and `Authorization` are never sent upstream.
   - **Response**: status (200, 206 or 416), `Content-Type`, `Content-Length`, `Content-Range`, `Accept-Ranges`, `ETag` and `Last-Modified` are relayed.
   - **Errors**: 502 is returned only while no bytes have been written. After that, the connection is aborted and logged.
   - **Timeouts**: the stream route clears its write deadline per request with `http.ResponseController.SetWriteDeadline(time.Time{})`. The server keeps `ReadHeaderTimeout` and idle timeouts, and other routes keep their write timeout. A client disconnect cancels the upstream request.
   - **Tests**: 200 without Range, 206, 416, HEAD, redirect chain, redirect to a host outside the allowlist, upstream error before and after the headers, client disconnect.
7. **Frontend and theme.**
   - **Stack**: Vue 3.5 + TypeScript + Vite + Tailwind v4 (`@tailwindcss/vite`), Pinia, vue-router and lucide icons.
   - **Font**: Inter, self-hosted (400/600) with a Tahoma/Verdana fallback, no CDN.
   - **Theme**: the layout and theme of **painel-golang** (the `criarenet` skin, `frontend/src/skins/criarenet/`), reproduced with Tailwind v4 `@theme` tokens that copy its CSS variables:
     - `--cn-primary #113058`, `--cn-primary-dark #0E172D`, `--cn-primary-alt #10315A`, `--cn-primary-light #1d4a7e`;
     - `--cn-accent #F58322`, `--cn-accent-strong #FE6101`;
     - `--cn-text-muted #69788B`, `--cn-text-soft #8B9AAD`;
     - `--cn-bg-light #E7ECEF`, `--cn-bg-blue #D9E6F3`, `--cn-bg-blue-soft #EAF0F6`, `--cn-border #b9c9dc`.
   - **Square corners everywhere**: every Tailwind `--radius-*` token is set to `0` and no `rounded-*` utility is used. A lint check fails the build if `rounded-` appears in `frontend/src`.
   - **Layout (the painel-golang chrome)**:
     - a centered fixed-width container over a dotted light-blue page background;
     - a light (`--cn-bg-light`) header with the logo and square top-level tabs (Dashboard, Mídia, Usuários, Health, Sair); the active tab is inverted;
     - an always-visible navy sub-menu band with the section's sub-tabs (for example Mídia → Biblioteca | Upload);
     - a navy info bar with "Partner: <id>" on the left and the user on the right, with the value text in orange;
     - a content card with a navy footer band showing the version;
     - a right "Ajuda" column with per-route help text;
     - tables with a navy header, zebra `--cn-bg-blue-soft` rows and `--cn-border` borders;
     - section boxes with an orange left border, as in `.cnSec`.
   - **Modern behaviors layered on that chrome, without changing its look**:
     - toasts;
     - upload progress bar;
     - live status polling;
     - an HTML5 `<video>` player;
     - responsive collapse under 768 px: tabs wrap, and the help column moves below the content.
   - **Language**: pt-BR by default, `en` through a small i18n map.
   - **Dev server**: proxies `/api` and `/media` to `:8080`.

8. **HTTP.**
   - Echo v5 with Recover, request ID, `slog` request logging, security headers (CSP allowing only self plus `blob:` for media), a body limit on non-upload routes, and a gzip skip for media routes.
   - `trusted_proxies` CIDRs control the real IP.
   - Explicit `http.Server` timeouts, without a write timeout on the stream route.
   - Optional TLS (`https`, `tls_cert`, `tls_key`).
9. **Config** (`config.toml`, search order `--config` → `./` → `/etc/kaltura-console/`, env prefix `KCONSOLE_`):
   ```toml
   [server]   host, port, https, tls_cert, tls_key, trusted_proxies, session_ttl
   [database] driver = "sqlite", dsn = "/var/lib/kaltura-console/console.db"
   [kaltura]  service_url, upload_service_url, partner_id, admin_secret, user_id,
              session_expiry, playback_host, http_timeout, connect_timeout, upload_timeout, max_upload_mb
   [log]      level
   ```
   `config init` writes the example with `0600` permissions. `serve` refuses to start when `admin_secret` is empty or `partner_id` is 0.
10. **Packaging and release.** nfpm builds `.deb` and `.rpm`.
    - **Package contents**:
      - a `kaltura-console` system user and group, created by preinst;
      - `/usr/bin/kaltura-console`;
      - `/etc/kaltura-console/config.toml`, a noreplace config file (`root:kaltura-console`, mode `0640`);
      - `/var/lib/kaltura-console`, with `tmp/` (`kaltura-console:kaltura-console`, mode `0750`).
    - **systemd unit**:
      - `User=kaltura-console`;
      - `ProtectSystem=strict`;
      - `ReadWritePaths=/var/lib/kaltura-console`;
      - `PrivateTmp=yes`;
      - `NoNewPrivileges=yes`.
    - **Maintainer scripts**:
      - postinst runs `migrate`, enables the unit but does not start it until the config is valid, and prints the `user add` hint;
      - upgrade restarts the unit;
      - purge removes `/var/lib/kaltura-console`.
    - **Version**: from `git describe --tags --match 'kaltura-console/v*'`. The prefix is stripped, and pre-releases are normalized to `~rc1` for packages.
    - **Release workflow**, on tags `kaltura-console/v*`:
      1. lint (`golangci-lint`, `vue-tsc`, `eslint`, radius check);
      2. `go test -race` and Vitest;
      3. build the frontend and the binary;
      4. build the `.deb` and `.rpm`;
      5. publish the tar.gz, `.deb`, `.rpm` and `SHA256SUMS` with `softprops/action-gh-release`.
    - **Skill**: `create-release` is copied from painel-golang and adapted: English CHANGELOG, the tag prefix above, and paths under `kaltura-console/`.
11. **Tests and status mapping.**
    - **Status groups**: entry statuses come from the 18.20 enum (`alpha/lib/enums/entryStatus.php`):
      - ready: 2;
      - processing: 0, 1, 4;
      - error: -2, -1;
      - other: 3, 5, 6, 7.
      This fixes the Laravel app, which treated 6 as "no content".
    - **Go tests**: table-driven with testify, covering config, the kaltura client (fake `api_v3`), handlers (httptest, including CSRF and authorization for every mutation), auth (rotation, revocation, lockout, last admin) and the proxy (matrix in item 6). The Echo v5 streaming path is tested through a real `httptest.Server`.
    - **Frontend**: Vitest for stores and utils.
    - **E2E** (`kaltura-console/tests/e2e.sh`):
      1. installs the `.deb` on the noble `aio` VM, or the `.rpm` on the Rocky 9 `el9aio` VM once it exists, and configures partner 102;
      2. uses `agent-browser` to go through login → upload (all three phases) → READY → play, checking that a 206 is seen → edit → delete → user management;
      3. checks that the computed `border-radius` is `0px` on every element;
      4. upgrades the package and checks that data and config are kept;
      5. saves screenshots at 1280×900.
    - **Visual baseline**: `painel-golang/docs/prints/novo-clients-list.png` (1280 px wide) for the chrome: header, tabs, sub-menu band, info bar, table and help column. Review is side by side, with no pixel diff.
## Risks / Trade-offs

- [Pure-Go SQLite is slower than CGO SQLite] → The console only stores users and sessions, so the load is negligible.
- [Echo v5 API churn] → Pin v5.3.x as in go-ispconfig, and follow the `golang-*` skills.
- [Large uploads through the console double the transfer] → Stream to disk and then to Kaltura, with a configurable limit. Direct browser-to-Kaltura upload with a KS is rejected, because it would expose the KS.
- [pt-BR-only UI today] → Keep pt-BR as the default and add `en` with the i18n map.
- [The painel-golang theme is table-based legacy CSS] → Recreate its look with Tailwind tokens and semantic markup (no `<table>` layout), and compare against `painel-golang/docs/prints` in review.

## Migration Plan

Deploy the new package side by side on a different port, then point users to it. Laravel users are not migrated; recreate them with `kaltura-console user add`. To roll back, stop the service and keep using the Laravel app.
