## Why

The released Kaltura CE Rigel-18.20.0 packaging deliberately selects PHP 7.4; it cannot be moved to PHP 8.3 by changing package names alone. The user requests a migration proposal while the current release CI runs, with the remaining `.20` installation preserved.

PHP 8.3 is the requested target, not a claim of current Kaltura compatibility. As of 2026-09-25 it receives security fixes through 2027-12-31; its limited remaining support window must be reviewed before shipping (see design.md sources).

## What Changes

- Inventory the pinned Kaltura source, bundled libraries/generated clients, installer scripts, CLI workers, web SAPIs and extensions; establish a reproducible PHP 7.4 baseline and PHP 8.3 compatibility report.
- Apply reviewed, reproducible compatibility patches against the pinned CE source only after feasibility gates pass. Do not silently replace CE with a different upstream release or broadly rewrite frameworks.
- **BREAKING**: the eventual migration release requires PHP 8.3 for Kaltura web and CLI processes; package dependency/CI rules that currently reject PHP 8 must explicitly change. Existing published 7.4 releases remain immutable recovery artifacts, not a promise of continued PHP 7.4 support.
- Build and validate coherent PHP 8.3 extension sets and AIO packages on Ubuntu 24.04, Ubuntu 26.04 and Rocky Linux 9; fail closed when a supported provider is unavailable.
- Test API/session semantics, Admin Console/KMC, uploads, background processing, eSearch, HTTP/HTTPS HLS and Full HD progressive playback, plus upgrade and recovery in isolated environments.
- Require staged cutover, restricted backups and a rehearsed full-state rollback before any live migration. No changes to `.20` during proposal work or feasibility experiments.

## Capabilities

### New Capabilities

- `kaltura-php83-runtime`: a consistent runtime, extension and compatibility contract, with isolated acceptance and safe migration/recovery gates.

### Modified Capabilities

- `noble-deb-build`: replace the package-quality requirement pinning PHP 7.4 with an explicit coherent 8.3 runtime for the migration release.
- `ubuntu-2604-deb`: update unattended runtime requirements and the three-distribution CI version gate.
- `el9-rpm`: update unattended installation from the 7.4 runtime to a verified 8.3 stack, preserving re-provisioning guarantees.

## Impact

`deb/kaltura-{base,front,batch}/debian/control`, relevant package hooks/configuration templates, `deb/{noble,ubuntu-26.04}/`, `rpm/el9/`, `RPM/SPECS/kaltura-{base,front,batch}.spec`, shared source packaging, PHP sanity scripts and `.github/workflows/kaltura-server-packages.yml`. The actual server tree is downloaded by the build; it must be audited after extraction, including vendor/generated code, not inferred from this packaging repository alone.

The Go console has no PHP runtime dependency. Its existing E2E suite is a downstream compatibility gate; MCP implementation, DWH enablement, DB engine upgrades and unrelated UI changes are out of scope. This proposal authorizes no implementation or server changes.
