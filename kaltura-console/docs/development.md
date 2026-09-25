# Development, testing and delivery

[Architecture](architecture.md) · [Operations](operations.md) · [API](api.md)

## Build locally

Work from `kaltura-console/`. Toolchain versions are declared in [`go.mod`](../go.mod) (Go 1.27), frontend lockfile and workflow (Node 24). Use the lockfile rather than updating dependencies while reproducing a build.

```sh
make build                 # npm ci, typecheck, Vite, then CGO_ENABLED=0 go build
./bin/kaltura-console version
make lint                  # golangci-lint, TS/ESLint, square-corner check, example parity
make test                  # pure-Go tests, race tests, frontend tests
```

Production builds disable CGO; SQLite is pure Go. The **race detector** is a separate developer/CI build and requires a C toolchain/CGO support. Do not interpret its requirement as a runtime libc dependency of the release executable. golangci-lint and nFPM are external development tools, not runtime requirements.

For an isolated development config, use `config init`, set a development partner and writable DB/staging paths, then create a local admin. Do not reuse production secrets. Prefer `make build` + the embedded UI when checking complete same-origin behavior. `npm run dev` starts Vite with proxy entries from `frontend/vite.config.ts`; check Host/Origin and proxy routing when testing authentication or `/media/...` paths. No production CORS workaround is needed. Test `base_path` against the built embedded UI: runtime base injection is performed by the Go server, not by the default Vite development server. Relative Vite assets plus `frontend/src/base.ts` avoid separate per-prefix builds.

## Validation layers

- `internal/config`: configuration/defaults/env validation, canonical base paths.
- `internal/tlsconfig`: self-signed generation/reuse, pair validation, permissions and TLS listener behavior.
- `internal/database`: migration idempotency and pure-Go SQLite behavior.
- `internal/auth`: local accounts, sessions, password/role revocation and last-admin invariants.
- `internal/kaltura`: fake upstream API, session retry, multipart streaming, errors and ownership checks.
- `internal/server`: route/role/CSRF, multipart limits, proxy Range/redirects and SPA behavior.
- `cmd`: command validation and configuration/account operations.
- `frontend/src/api.test.ts`: API helper and safe redirect behavior.
- `tests/e2e.py`: browser workflow against a **real configured console/Kaltura instance**.

Tests using a fake upstream do not prove real Kaltura conversion or target-OS package behavior. Review test names and assertions rather than treating a green unit suite as complete parity evidence.

### Real browser acceptance

Prerequisites: a disposable configured console/partner, an admin account, `agent-browser`, Python 3 and a valid short MP4. The test creates uniquely named media and a user, performs mutations, and attempts cleanup. Run only where that is authorized.

```sh
export E2E_BASE_URL='https://test-console.example.invalid/console'
export E2E_EMAIL='test-admin@example.invalid'
export E2E_PASSWORD_FILE='/protected/path/test-password'
export E2E_VIDEO='/path/to/short-valid.mp4'
./tests/e2e.sh
```

Include the configured prefix in `E2E_BASE_URL` (omit `/console` for root deployments). Lab self-signed trust is an explicit test-client setup step, not a production verification bypass.

Keep the password file out of Git and restrict permissions. Screenshots default to `doc/prints/kaltura-console-go` at repository root; override with `E2E_SCREENSHOTS`. Screenshots may contain account/media metadata: review before publication. Headless-browser flags are optional via `E2E_CHROME_ARGS`; do not disable browser sandboxing in ordinary desktop use.

## GitHub delivery

![Console build and release workflow](diagrams/release.svg)

[Open the interactive release workflow diagram](diagrams/release.html).

The workflow source is [`.github/workflows/kaltura-console-release.yml`](../../.github/workflows/kaltura-console-release.yml). Tags use the module namespace `kaltura-console/v<version>`, separate from other packages in this monorepo. Path-filtered pushes and pull requests, plus manual dispatch, build artifacts; publishing a GitHub Release is tag-gated. The build job has read-only repository permissions. A separate release job downloads its artifacts and receives `contents: write` only for module tags. Read the workflow for exact runner/version/matrix values; those are not inferred from the target package's distribution name.

The delivery path builds embedded assets, runs quality checks, compiles the static Linux executable, packages `.deb` and `.rpm` with nFPM, creates a `.tar.gz`, computes `SHA256SUMS`, and uploads artifacts. Tagged releases attach artifacts and release notes. The tarball is not a service installer: apply the configuration/account/service setup from [operations](operations.md) when deploying it manually.

Local package reproduction:

```sh
go install github.com/goreleaser/nfpm/v2/cmd/nfpm@v2.47.0
make package VERSION=0.1.0-dev
```

Artifacts land in `dist/`. Keep that directory clean of obsolete build artifacts before preparing a release so checksum/release globs do not pick up older versions. Package scripts and service paths are defined in [`packaging/nfpm.yaml`](../packaging/nfpm.yaml). Package construction alone does not establish that install/upgrade/remove/purge work on every distribution. In particular, Ubuntu 26.04 acceptance requires a real 26.04 environment, distinct from building on a GitHub Ubuntu runner.

Release preparation should review CHANGELOG, run the checks, inspect archive/package contents, install on isolated target systems, smoke-test login/upload/playback, test upgrades with preserved configuration/state, and only then push the release tag. A workflow file existing in Git is not evidence that GitHub has executed it or published artifacts.

## Validation evidence

Implementation-session checks reported on 2026-09-25:

- Local rc1/rc2 package generation; `.deb` installation on the Ubuntu Noble AIO test host.
- Real Kaltura upload reaching READY, playback, HTTP 206 range response and metadata editing on that host.
- Isolated MariaDB last-administrator concurrency test repeated five times successfully.
- Complete scripted browser E2E exited successfully, including account management, mobile layout, localization and zero-border-radius checks.

See the [integration validation report](validation.md) for the subsequent rc3 Ubuntu 26.04 installation, Noble retest, GitHub run and outstanding Rocky/upgrade/removal gates. These are bounded observations, not a blanket distribution compatibility claim. No credentials are included here.

### TLS and prefix acceptance scope

The earlier rc3/root-deployment evidence is not evidence for the subsequent native-TLS/base-path changes. Re-run acceptance at root and `/console`, checking refresh/deep links, assets, login/logout, cookie Path/Secure, CSRF, upload, playback Range and prefixed health probes. Check self-signed reuse across restarts, explicit CA pair loading and rejected partial/expired material. A real Apache HTTPS deployment must preserve the prefix and overwrite forwarding protocol. Target-host HTTPS results remain pending until recorded separately; implementation and local test code are not a claim of a completed deployment run.

## Diagrams and documentation maintenance

[`diagrams/`](diagrams/) contains editable Archify JSON sources, standalone dual-theme SVGs for inline Markdown display, and generated standalone HTML with inline SVG, theme toggle and exports. Download/open HTML in a browser to use the interactive viewer. SVG/PNG/JPEG/WebP export is available in its toolbar. These files do not execute application code or contain deployment secrets.

With the Archify skill installed, regenerate from the repository root:

```sh
ARCHIFY="$HOME/.agents/skills/archify/bin/archify.mjs"
for pair in 'architecture architecture' 'upload sequence' 'release workflow'; do
  set -- $pair
  node "$ARCHIFY" render "$2" "kaltura-console/docs/diagrams/$1.$2.json" "kaltura-console/docs/diagrams/$1.html"
  node "$ARCHIFY" validate "$2" "kaltura-console/docs/diagrams/$1.$2.json" --json
  node "$ARCHIFY" check "kaltura-console/docs/diagrams/$1.html"
done
```

After regeneration, use each HTML viewer’s Export → SVG action to refresh its matching standalone `.svg`. This uses Archify’s dual-theme export, including semantic CSS, local font fallbacks and `prefers-color-scheme` handling. Do not extract raw inline SVG without its required styles.

The renderer is a development aid; generated diagrams are usable without it. When routes, config keys, source layout or packaging change, update the related guide and diagram JSON together. [OpenSpec artifacts](../../openspec/changes/archive/2026-09-25-add-kaltura-console-go/) document the proposal; [Kaltura API notes](../../doc/kaltura-api-noble.md) document the validated upstream contract. Do not copy secrets, local session state or `.env` files into examples.

### Page transitions

The routed content uses the same out-in transition as painel-golang: 150 ms
opacity easing and a 6 px entrance translation. Header and navigation remain
mounted. Like painel-golang, the card has a stable 720 px height and internal
scrolling (viewport-bounded on mobile), avoiding footer jumps during fade or
API loading. New pages start at the top of the card; the route path keys a wrapper so multi-root views animate correctly.
Query-only updates do not remount the view. Reduced-motion users get no animation.

Run `python3 tests/navigation.py` from `kaltura-console/` with the same
`E2E_BASE_URL`, `E2E_EMAIL`, `E2E_PASSWORD_FILE` and optional `E2E_CHROME_ARGS`
as the full E2E script. It checks actual transition classes/timing, stable
navigation, rapid route changes, reduced-motion emulation and logout.
