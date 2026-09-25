## Why

The released Kaltura CE Rigel-18.20.0 packaging deliberately selects PHP 7.4; it cannot be moved to PHP 8.3 by changing package names alone. The user has approved phase-1 feasibility, an isolated Ubuntu 24.04 laboratory, and minimal experimental application patches with a separate PHP 8.3 source ZIP. The existing `.20` application/runtime and original PHP 7.4 artifacts remain preserved.

PHP 8.3 is the requested target, not a claim of current Kaltura compatibility. As of 2026-09-25 it receives security fixes through 2027-12-31; its limited remaining support window must be reviewed before shipping (see design.md sources).

## What Changes

- Inventory the pinned Kaltura source, bundled libraries/generated clients, installer scripts, CLI workers, web SAPIs and extensions; establish a reproducible PHP 7.4 baseline and PHP 8.3 compatibility report.
- Develop and test minimal, reviewed compatibility patches in isolated lab source trees during feasibility, producing a clearly experimental PHP 8.3 ZIP with an ordered patch manifest and checksums. Production packaging integration still requires the feasibility go/no-go decision. Do not silently replace CE with a different upstream release or broadly rewrite frameworks.
- Evaluate beneficial dependency updates separately from required compatibility repairs, with pinned versions, license/security review and focused regression tests. Measure performance against the unchanged baseline; do not assume an upgrade is faster or bundle unrelated features into this change.
- **BREAKING**: the eventual migration release requires PHP 8.3 for Kaltura web and CLI processes; package dependency/CI rules that currently reject PHP 8 must explicitly change. Existing published 7.4 releases remain immutable recovery artifacts, not a promise of continued PHP 7.4 support.
- Build and validate coherent PHP 8.3 extension sets and AIO packages on Ubuntu 24.04, Ubuntu 26.04 and Rocky Linux 9; fail closed when a supported provider is unavailable.
- After acceptance and final release approval, publish the versioned PHP 8.3 source ZIP alongside the DEB/RPM repository bundles in the same GitHub release, with a source/patch manifest, installation instructions and SHA256SUMS; preserve the upstream ZIP and prior releases.
- Test API/session semantics, Admin Console/KMC, uploads, background processing, eSearch, HTTP/HTTPS HLS and Full HD progressive playback, plus upgrade and recovery in isolated environments.
- Require staged cutover, restricted backups and a rehearsed full-state rollback before any live migration. No manual package, configuration, database or media changes to `.20` during feasibility; the expressly authorized boot/read-only inspection and normal service-startup writes are allowed.

## Capabilities

### New Capabilities

- `kaltura-php83-runtime`: a consistent runtime, extension and compatibility contract, with isolated acceptance and safe migration/recovery gates.

### Modified Capabilities

- `noble-deb-build`: replace the package-quality requirement pinning PHP 7.4 with an explicit coherent 8.3 runtime for the migration release.
- `ubuntu-2604-deb`: update unattended runtime requirements and the three-distribution CI version gate.
- `el9-rpm`: update unattended installation from the 7.4 runtime to a verified 8.3 stack, preserving re-provisioning guarantees.

## Impact

`deb/kaltura-{base,front,batch}/debian/control`, relevant package hooks/configuration templates, `deb/{noble,ubuntu-26.04}/`, `rpm/el9/`, `RPM/SPECS/kaltura-{base,front,batch}.spec`, shared source packaging, PHP sanity scripts and `.github/workflows/kaltura-server-packages.yml`. The actual server tree is downloaded by the build; it must be audited after extraction, including vendor/generated code, not inferred from this packaging repository alone.

The Go console has no PHP runtime dependency. Its existing E2E suite is a downstream compatibility gate; MCP implementation, DWH enablement, DB engine upgrades and unrelated UI changes are out of scope. Current authorization covers phase-1 investigations and isolated Noble candidate/baseline labs and disposable provider-resolution environments. Minimal experimental source patches and an isolated PHP 8.3 ZIP are authorized by the operator confirmation. Production package/CI changes still require the later go/no-go decision; release and live cutover retain their separate acceptance and operator approvals. Dependency upgrades require an explicit reviewed per-component decision; wholesale application/framework replacement or unrelated additions need a revised scope. The MODIFIED specs describe the eventual migration branch/release; do not synchronize them into main or archive this change before release acceptance.
