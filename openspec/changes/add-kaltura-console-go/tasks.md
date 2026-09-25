## 1. Skills and scaffolding

- [x] 1.1 Copy the `golang-*` skills and `create-release` from go-ispconfig/painel-golang into `.claude/skills/` and `.agents/skills/`. Adapt `create-release` to tags `kaltura-console/v*` and paths under `kaltura-console/`. Verify the files exist and the skill text has no go-imapsync/painel leftovers.
- [x] 1.2 Scaffold `kaltura-console/`:
  - `go.mod` (Go 1.27), `main.go`, `cmd/` (root, serve, migrate, user, config, version);
  - `internal/buildinfo`, `Makefile`, `.golangci.yml`, `config.toml.example`, `CHANGELOG.md`;
  - `web/web.go` with the embed, plus a stub `dist`.
  Verify with `go build ./...` and `kaltura-console version`.

## 2. Backend

- [x] 2.1 `internal/config` (Viper, defaults, validation, `KCONSOLE_` env). Verify with table-driven tests: missing secret, env override, search order.
- [x] 2.2 `internal/database` and `models`: GORM with SQLite (glebarez: WAL, busy_timeout, foreign keys) or MySQL, gormigrate versioned migrations (`users`, `sessions`, `login_attempts`). Verify with `CGO_ENABLED=0 go test`, and with `migrate` twice against MariaDB on the AIO (idempotent).
- [x] 2.3 `internal/auth`: bcrypt, DB sessions (rotation, idle and absolute expiry, remember-me), CSRF token, lockout, roles, return URL; user management rules; CLI `user add|passwd|list|delete`. Verify with tests: login, wrong password, lockout, CSRF missing or invalid, revocation on password or role change, last-admin protection.
- [x] 2.4 `internal/kaltura`: client, KS cache with retry, media, upload token, flavors, ping, typed errors, streaming upload. Verify with an `httptest` fake `api_v3`: expired KS and `INVALID_SESSION_ID` retry rebuilding the body, streaming multipart, and an early upstream response without goroutine leaks (goleak).
- [x] 2.5 `internal/server` and `handlers`: Echo v5, middleware (recover, request id, slog, security headers, trusted proxies), JSON API, SPA fallback, media proxy with Range, health, upload limits. Also covers upload staging (MaxBytesReader, semaphore, free space, ftyp sniff, cleanup, orphan entry delete). Verify with httptest tests: 401, 403 (CSRF and role), 413, 429, and the proxy matrix (200, 206, 416, HEAD, redirect allowlist, error before and after headers, client disconnect).

## 3. Frontend

- [x] 3.1 `frontend/`: Vite + Vue 3.5 + TypeScript + Tailwind v4 + Pinia + vue-router + lucide, self-hosted Inter, pt-BR/en i18n. The `@theme` tokens copy the painel-golang `criarenet` variables, with every radius set to 0, plus a lint check that forbids `rounded-`. `make frontend` builds `web/dist`. Verify with `npm run build`, Vitest and the lint check.
- [x] 3.2 Chrome in the painel-golang style: tabs, navy sub-menu band, info bar, content card with a version footer, and the Ajuda column. Screens: login, dashboard, media library, upload with progress, entry details (player, polling, edit, delete, flavors), users, health. All screens must be responsive. Verify with E2E (4.2): computed `border-radius` is 0 on every element, and screenshots are compared with `painel-golang/docs/prints`.

## 4. Packaging, release and validation

- [x] 4.1 nfpm `.deb`/`.rpm`: preinst creates the user; hardened unit with ReadWritePaths; config `root:kaltura-console 0640` noreplace; postinst migrate and hint; upgrade restart; purge. Version from `git describe --match 'kaltura-console/v*'`. Verify by installing on the noble `aio` VM (`systemctl is-active`), upgrading with data kept, and installing the `.rpm` on Rocky 9 `el9aio` when available.
- [x] 4.2 E2E on the noble `aio` VM:
  - install the `.deb` and configure partner 102;
  - use `agent-browser` to log in, upload an MP4, wait for READY, play (check the 206 Range), edit and delete;
  - save screenshots to `doc/prints/kaltura-console-go/`.
  Verify that the script exits 0.
- [x] 4.3 `.github/workflows/kaltura-console-release.yml` on tags `kaltura-console/v*`: lint gates (golangci-lint, vue-tsc, eslint, radius check), `go test -race`, Vitest, build, and publish the tar.gz, `.deb`, `.rpm` and SHA256SUMS. Verify on a fork or with `act`, or by pushing a pre-release tag `kaltura-console/v0.1.0-rc1`.
- [x] 4.4 Docs:
  - `kaltura-console/README.md` (install, config, CLI);
  - a link from the root `README.md`;
  - a note in `doc/validation-noble.md`.
  Verify the links.
- [x] 4.5 Review the proposal and the implementation with the `codex` CLI and apply the relevant fixes.

### Validation evidence (2026-09-25 UTC)

- Console DEB install and rc1 → rc2 upgrade passed on noble aio; config, users and a live session were preserved. RPM construction passed; real Rocky 9 installation remains pending coordination with the packaging agent (4.1).
- The workflow build job passed under act v0.2.89 with the Ubuntu 24.04 image: frontend build/lint/Vitest, Go lint/static tests/race tests, binary/DEB/RPM/archive/checksums and local artifact upload. GitHub-hosted publication was not performed.
- Documentation relative links and Archify diagram schema/render/layout/SVG checks passed.
- Codex reviewed the proposal and implementation in this CLI session, applying fixes for transactional last-admin protection, logout/login-attempt DB failures, API cache policy, proxy truncation/cancellation, configuration validation and upstream error-log redaction. No separate automated codex review process is claimed.

## 5. HTTPS and reverse-proxy refinement

- [ ] 5.1 Implement/validate canonical server.base_path across routes, assets, cookies and frontend; test deep links, login, upload and media URLs at root and /console.
- [x] 5.2 Implement standalone TLS flags/env and persistent self-signed certificate fallback; test permissions, reuse, explicit pair, invalid material and real HTTPS.
- [ ] 5.3 Document Apache prefix-preserving proxy/TLS settings; validate HTTPS proxy E2E with a trusted local proxy and standalone TLS smoke test.

### HTTPS refinement evidence (2026-09-25 UTC)

- rc6 RPM installed on Rocky 9 el9aio; service active as kaltura-console. Noble/26.04 DEB upgrades kept operator configs using dpkg --force-confold.
- Standalone HTTPS on el9aio:8443/console/healthz returned200 with curl --cacert; key0600, identical certificate SHA256 before/after restart.
- Go tests (CGO0 and race), lint and13Vitest tests passed. Tests cover prefix route isolation, SPA base/deep-link redirects, cookie path, trusted/untrusted forwarding, CSRF, prefixed media URLs and certificate generation/reuse/permissions/invalid material.
- rc6 Noble browser E2E passed; Rocky/26.04/prefixed HTTPS E2E are still in progress.
