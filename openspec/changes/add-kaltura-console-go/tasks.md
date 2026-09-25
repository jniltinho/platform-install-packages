## 1. Skills and scaffolding

- [ ] 1.1 Copy the `golang-*` skills and `create-release` from go-ispconfig/painel-golang into `.claude/skills/` and `.agents/skills/`. Adapt `create-release` to tags `kaltura-console/v*` and paths under `kaltura-console/`. Verify the files exist and the skill text has no go-imapsync/painel leftovers.
- [ ] 1.2 Scaffold `kaltura-console/`:
  - `go.mod` (Go 1.27), `main.go`, `cmd/` (root, serve, migrate, user, config, version);
  - `internal/buildinfo`, `Makefile`, `.golangci.yml`, `config.toml.example`, `CHANGELOG.md`;
  - `web/web.go` with the embed, plus a stub `dist`.
  Verify with `go build ./...` and `kaltura-console version`.

## 2. Backend

- [ ] 2.1 `internal/config` (Viper, defaults, validation, `KCONSOLE_` env). Verify with table-driven tests: missing secret, env override, search order.
- [ ] 2.2 `internal/database` and `models`: GORM with SQLite (glebarez: WAL, busy_timeout, foreign keys) or MySQL, gormigrate versioned migrations (`users`, `sessions`, `login_attempts`). Verify with `CGO_ENABLED=0 go test`, and with `migrate` twice against MariaDB on the AIO (idempotent).
- [ ] 2.3 `internal/auth`: bcrypt, DB sessions (rotation, idle and absolute expiry, remember-me), CSRF token, lockout, roles, return URL; user management rules; CLI `user add|passwd|list|delete`. Verify with tests: login, wrong password, lockout, CSRF missing or invalid, revocation on password or role change, last-admin protection.
- [ ] 2.4 `internal/kaltura`: client, KS cache with retry, media, upload token, flavors, ping, typed errors, streaming upload. Verify with an `httptest` fake `api_v3`: expired KS and `INVALID_SESSION_ID` retry rebuilding the body, streaming multipart, and an early upstream response without goroutine leaks (goleak).
- [ ] 2.5 `internal/server` and `handlers`: Echo v5, middleware (recover, request id, slog, security headers, trusted proxies), JSON API, SPA fallback, media proxy with Range, health, upload limits. Also covers upload staging (MaxBytesReader, semaphore, free space, ftyp sniff, cleanup, orphan entry delete). Verify with httptest tests: 401, 403 (CSRF and role), 413, 429, and the proxy matrix (200, 206, 416, HEAD, redirect allowlist, error before and after headers, client disconnect).

## 3. Frontend

- [ ] 3.1 `frontend/`: Vite + Vue 3.5 + TypeScript + Tailwind v4 + Pinia + vue-router + lucide, self-hosted Inter, pt-BR/en i18n. The `@theme` tokens copy the painel-golang `criarenet` variables, with every radius set to 0, plus a lint check that forbids `rounded-`. `make frontend` builds `web/dist`. Verify with `npm run build`, Vitest and the lint check.
- [ ] 3.2 Chrome in the painel-golang style: tabs, navy sub-menu band, info bar, content card with a version footer, and the Ajuda column. Screens: login, dashboard, media library, upload with progress, entry details (player, polling, edit, delete, flavors), users, health. All screens must be responsive. Verify with E2E (4.2): computed `border-radius` is 0 on every element, and screenshots are compared with `painel-golang/docs/prints`.

## 4. Packaging, release and validation

- [ ] 4.1 nfpm `.deb`/`.rpm`: preinst creates the user; hardened unit with ReadWritePaths; config `root:kaltura-console 0640` noreplace; postinst migrate and hint; upgrade restart; purge. Version from `git describe --match 'kaltura-console/v*'`. Verify by installing on the noble `aio` VM (`systemctl is-active`), upgrading with data kept, and installing the `.rpm` on Rocky 9 `el9aio` when available.
- [ ] 4.2 E2E on the noble `aio` VM:
  - install the `.deb` and configure partner 102;
  - use `agent-browser` to log in, upload an MP4, wait for READY, play (check the 206 Range), edit and delete;
  - save screenshots to `doc/prints/kaltura-console-go/`.
  Verify that the script exits 0.
- [ ] 4.3 `.github/workflows/kaltura-console-release.yml` on tags `kaltura-console/v*`: lint gates (golangci-lint, vue-tsc, eslint, radius check), `go test -race`, Vitest, build, and publish the tar.gz, `.deb`, `.rpm` and SHA256SUMS. Verify on a fork or with `act`, or by pushing a pre-release tag `kaltura-console/v0.1.0-rc1`.
- [ ] 4.4 Docs:
  - `kaltura-console/README.md` (install, config, CLI);
  - a link from the root `README.md`;
  - a note in `doc/validation-noble.md`.
  Verify the links.
- [ ] 4.5 Review the proposal and the implementation with the `codex` CLI and apply the relevant fixes.
