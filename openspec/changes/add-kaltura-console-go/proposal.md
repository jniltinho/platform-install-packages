## Why

`criare/kaltura-console` is a Laravel 13 / PHP 8.3 app. It needs a PHP runtime, Composer, Node and a web server next to Kaltura, which itself runs PHP 7.4, so two PHP stacks end up on one host. It was also built around the legacy `kaltura-legacy-gateway` URLs. It already works against the Kaltura CE 18.20 AIO built in this repository (see `doc/validation-noble.md`).

A single static Go binary, packaged as `.deb`/`.rpm` next to the Kaltura packages, removes that extra stack and the gateway. It also follows the owner's house pattern for Go services (go-ispconfig, painel-golang).

## What Changes

- New project `kaltura-console/` in this repository: a Go rewrite of `criare/kaltura-console` with feature parity. The UI uses the painel-golang `criarenet` layout and theme (square corners, navy/orange palette, tabs plus sub-menu band, help column) with modern interactions.
  - **Backend**: Go 1.27, Echo v5, Cobra CLI, Viper `config.toml`, GORM. Database: SQLite (pure Go, `CGO_ENABLED=0`) or MariaDB, chosen in config.
  - **Frontend**: Vue 3 + Vite + TypeScript + Tailwind CSS v4 SPA, embedded in the binary with `go:embed`.
  - **Kaltura access**: talks to `api_v3` directly (`session.start` admin KS cache with retry, `media.*`, `uploadToken.*`, `flavorAsset.list`, `system.ping`). No `kaltura-legacy-gateway`.
  - **Features**:
    - login;
    - dashboard with counters and recent entries;
    - media library with search and pagination;
    - upload with a real progress bar;
    - entry details with player, edit, delete, live status polling and a flavors table;
    - system health page;
    - local user management.
  - **Media proxy**: playback and thumbnails go through the console, with HTTP Range support, so browsers never need direct access to the Kaltura delivery host.
  - **CLI**: `serve`, `migrate`, `user` (add/passwd/list/delete), `config init`, `version`.
- Packaging and release:
  - `kaltura-console` `.deb` and `.rpm` built with nfpm, with a systemd unit.
  - A GitHub Actions release workflow on tags `kaltura-console/v*`.
  - The `create-release` skill adapted to this monorepo.
- The owner's Go skills (`golang-*`) and the `create-release` skill are added to `.claude/skills/` and `.agents/skills/`.
- Validation on the noble AIO Vagrant VM:
  - an E2E run with `agent-browser`;
  - screenshots in `doc/prints/kaltura-console-go/`.

## Capabilities

### New Capabilities
- `kaltura-console-web`: the web console. Covers authentication, dashboard, media library, upload, entry management, playback proxy and health. Behavior must match the Laravel app.
- `kaltura-console-ops`: operations. Covers the CLI, configuration file, database backends, packaging, release and the Kaltura API client contract.

### Modified Capabilities
<!-- none -->

## Impact

- New directory `kaltura-console/` (Go module `kaltura-console`), its CI workflow `.github/workflows/kaltura-console-release.yml`, and new skills under `.claude/skills/` and `.agents/skills/`.
- There is no change to the Kaltura server packages. Optionally, `deb/noble/install-aio.sh` can install the console on the `aio` VM for validation.
- `criare/kaltura-console` and `criare/kaltura-legacy-gateway` are superseded once this ships. They are not modified.
