## Context

Baseline: main `3bd3b189`, Kaltura CE Rigel-18.20.0. Only packaging/configuration evidence was inspected for this proposal; the full downloaded PHP application has NOT yet undergone a compatibility audit or a PHP 8.3 execution test.

### Verified repository evidence

| Area | Evidence | Consequence |
|---|---|---|
| Source provenance | `build/sources.rc`, `build/package_kaltura_core.sh`, `deb/kaltura-base/debian/rules`; mirrored archive with SHA-256; main `noble-deb-build` pins server commit `29cf45469c1e210498087942f5b76b5c706e4cda` | Audit the extracted exact tree plus packaging overlays/generated client libraries, not arbitrary upstream HEAD. |
| Ubuntu runtime | `deb/kaltura-{base,front,batch}/debian/control` explicitly requires `php7.4-*`; front/batch require `libapache2-mod-php7.4` | Dependencies, enabled Apache module and CLI invocation must move together. |
| Ubuntu 26.04 provider | `deb/ubuntu-26.04/install-aio.sh` configures packages.sury.org using the distro codename | Verify target-suite PHP 8.3 packages and extensions; do not assume an earlier provider or another distro's binaries are suitable. |
| Rocky runtime | `rpm/el9/install-aio.sh` selects `php:remi-7.4`; EL9 branch of `RPM/SPECS/kaltura-front.spec` requires `php-fpm` | Switch and validate web FPM and CLI together; generic RPM dependency names alone do not enforce the right minor version. |
| Extension surface | Base/front/batch package metadata includes MySQL/PDO, XML/XSL, curl, mbstring, GD, GMP, LDAP, zip/intl, APCu/memcache/SSH2 and process support, varying by distro | Reconcile a mandatory extension/SAPI matrix; memcache and memcached, or APC and APCu, are not interchangeable merely by package name. |
| CI guard | `.github/workflows/kaltura-server-packages.yml` rejects PHP 8 and enables Remi 7.4 | Replace the guard with exact 8.3 family checks and positive runtime/module verification, not removal of the guard. |

Historical `build/sources.rc` also contains legacy PHP 5.3/7.0 source definitions. Do not mechanically replace every PHP string: classify active AIO paths versus historical recipes before editing.

## Goals / Non-Goals

Preserve CE behavior, API shapes, data and operator configuration while moving supported AIO deployments to a coherent PHP 8.3 stack. This is a staged migration, not a declaration that CE already supports 8.3.

Non-goals: wholesale Kaltura/framework replacement; changing DB engine/schema; DWH enablement; changing ffmpeg/nginx/Elasticsearch versions without a proven blocker and a separate approved scope; PHP in the Go console; production experiments; permanent support for both PHP lines. HTTP/HTTPS behavior and current SAPI topology are retained to avoid combining unrelated migrations.

## Decisions

1. **Feasibility before runtime substitution.** Inventory exact source revisions, bundled Symfony/Zend/Propel-style or other legacy libraries if present, generated clients, package hooks, cron and batch entrypoints. Run syntax checks with PHP 8.3, pinned PHPCompatibility tooling and targeted runtime probes. Static checks are incomplete by design and never replace real API/UI/worker tests. Record each finding as confirmed, false positive with evidence, or unverified. Do not invent incompatibility counts.

2. **Bounded patch ownership.** Keep the pinned source archive immutable and apply an ordered, version-controlled compatibility patch series through a shared packaging step used by DEB and RPM. Verify archive/patch hashes and fail on patch drift or rejected hunks. Prefer small upstream fixes with attribution. If a framework replacement or upstream Kaltura upgrade is required, stop at the feasibility gate and request a revised proposal; do not smuggle it into this migration. Do not perform unpinned Composer updates during package installation.

3. **Audit the entire 7.4 → 8.3 path.** Candidate risks include removed functions/curly-brace offsets and stricter signatures/types in 8.0, optional-before-required parameters/internal interface return types/resource-to-object assumptions in 8.1, and dynamic-property deprecations in 8.2; review 8.3 changes too. These are language-level audit targets, NOT confirmed findings in Kaltura. Treat date/time, XML, serialization/session/KS cryptography, DB error semantics, callable behavior and extension-specific resources as regression surfaces. Do not hide failures by disabling all warnings or scattering compatibility attributes globally.

4. **Coherent, maintained runtime providers.** Prefer distro-native 8.3 where available; otherwise require a maintained, signed, suite-compatible provider with pinned package constraints and documented update policy. Rocky's Remi 8.3 stream is a candidate to verify, not a tested result. For Ubuntu 26.04, inability to resolve native/suite-compatible 8.3 and every mandatory extension is a blocker, not permission to mix incompatible distro packages or select 8.4/8.5 silently. Reusing an arbitrary 7.4 extension binary is forbidden. Freeze exact versions/repository origins in the test report, while allowing reviewed security updates within 8.3.

5. **Preserve SAPI topology.** Ubuntu retains its tested Apache module arrangement, updated to 8.3; Rocky retains FPM, updated to 8.3. Verify loaded INI paths/extensions independently for CLI and web, worker interpreter paths, OPcache, timeouts, permissions and service restarts. Avoid system-wide alternatives changes that affect unrelated applications. Restart long-running workers during controlled cutover so no old interpreter remains processing jobs.

6. **Isolated acceptance matrix.** Separate clones/labs for Ubuntu 24.04, Ubuntu 26.04 and Rocky 9; never use `.20` as an experiment. Record OS, PHP/SAPI/module versions, package revisions and source/patch hashes. For each distro validate fresh install, repeated provisioning, restart/reboot, controlled upgrade from the 7.4 baseline and rollback rehearsal. Containers cover builds/dependency checks; disposable full-service labs cover runtime behavior. HTTP and HTTPS API/delivery must both be exercised, including a trusted CA rather than bypassed TLS validation. Upload both a short deterministic MP4 and a Full HD/60 fps fixture; verify READY, flavors, thumbnails, HLS segments and actual progressive stream properties/Range.

7. **Failure and release gates.** Capture baseline warnings/performance and run the same bounded workload on 8.3. Block on fatal/type errors, worker/job failures, authentication/permission regressions, missing extensions, changed API contracts or untriaged warnings in exercised paths. The same workload's median and p95 API latency and transcode wall time must not regress more than 20% without explicit review; use multiple repetitions and preserve reports, not a one-off benchmark. Scope exclusions and nonfatal accepted deprecations require named rationale/tests, not blanket ignore rules. Publish no migration release until all distro/runtime and rollback gates pass.

## Risks / Trade-offs

- **PHP 8.3 support horizon** → the user specifically requested 8.3; reassess security-support dates before implementation/release. A later minor target needs an explicit updated proposal, not an automatic substitution.
- **Bundled legacy dependencies may be the dominant work** → Stage 1 produces a go/no-go report before package/runtime work; unsupported dependencies are blockers requiring a bounded repair plan.
- **Warnings may become fatal through application error handlers** → test handlers with realistic calls and background jobs; suppressing output is not compatibility.
- **Cache/session serialization may differ** → quiesce workers and invalidate only documented disposable caches; preserve secrets/data. Rehearse login/session behavior and rollback rather than assuming drop-in equivalence.
- **Rollback after new writes can lose data** → require a maintenance/read-only window until acceptance and recover a matched application/config/DB/media snapshot if needed; package downgrade alone is not a recovery plan.

## Migration Plan

1. After separate implementation approval, prepare isolated baseline and compatibility reports; obtain go/no-go approval on blockers/provider matrix.
2. Develop audited source patches, runtime metadata/config changes and CI assertions on a migration branch. Keep published 7.4 releases untouched.
3. Complete the three-distro test matrix and a consistent backup/restore rehearsal. Archive sanitized evidence, not secrets/KS/cookies/user media.
4. Produce a release candidate with documented upgrade commands, maintenance steps, known limitations and rollback instructions. Any live target, window and backups require explicit operator confirmation.
5. At an approved cutover, stop new uploads and drain/stop workers, snapshot configuration/database/media coherently, install matching packages, restart all PHP processes, validate before reopening intake. On failure, stop writes and restore the matched baseline; do not merely flip `/usr/bin/php`.

## Reference sources (checked 2026-09-25)

- [PHP supported versions](https://www.php.net/supported-versions.php): 8.3 active support ended 2025-12-31; security support ends 2027-12-31.
- [PHP 8.0 incompatible changes](https://www.php.net/manual/en/migration80.incompatible.php).
- [PHP 8.1 incompatible changes](https://www.php.net/manual/en/migration81.incompatible.php).
- [PHP 8.2 deprecations](https://www.php.net/manual/en/migration82.deprecated.php).
- [PHP 8.3 incompatible changes](https://www.php.net/manual/en/migration83.incompatible.php).
- [PHPCompatibility project](https://github.com/PHPCompatibility/PHPCompatibility): static compatibility checks have incomplete coverage; pin the chosen analyzer and its dependencies during implementation.
