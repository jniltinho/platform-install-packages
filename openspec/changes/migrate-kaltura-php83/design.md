## Context

Planning baseline: main `3bd3b189` (migration branch subsequently synchronized with main `1286d0f1`), Kaltura CE Rigel-18.20.0. At proposal creation only packaging/configuration evidence had been inspected. Phase-1 syntax/static evidence is now recorded in `doc/php83/feasibility-status.md`; application runtime acceptance is still pending.

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

2. **Bounded patch ownership and experimental ZIP.** The operator confirmed minimal experimental application repairs during feasibility. Keep the pinned source archive and published PHP 7.4 artifacts immutable. Apply an ordered, version-controlled patch series only to disposable source copies; generate a separately named `Rigel-18.20.0-php83-experimental.<revision>.zip`, not an overwrite of the upstream mirror. Record the upstream archive SHA-256, patch order/hashes, changed-file before/after hashes, license attribution and resulting ZIP SHA-256. Exclude credentials, runtime configuration, databases and media. Freeze archive entry order, timestamps and permissions and verify two builds from identical inputs produce identical hashes. The archive remains experimental, not an installable release or a claim of full compatibility. After go/no-go approval, integrate the same reviewed source transformation into the shared DEB/RPM build step. Verify archive/patch hashes and fail on patch drift or rejected hunks. Prefer small upstream fixes with attribution. If a framework replacement or upstream Kaltura upgrade is required, stop at the feasibility gate and request a revised proposal; do not smuggle it into this migration. Do not perform unpinned Composer updates during package installation.

3. **Audit the entire 7.4 → 8.3 path.** Candidate risks include removed functions/curly-brace offsets and stricter signatures/types in 8.0, optional-before-required parameters/internal interface return types/resource-to-object assumptions in 8.1, and dynamic-property deprecations in 8.2; review 8.3 changes too. These are language-level audit targets, NOT confirmed findings in Kaltura. Treat date/time, XML, serialization/session/KS cryptography, DB error semantics, callable behavior and extension-specific resources as regression surfaces. Do not hide failures by disabling all warnings or scattering compatibility attributes globally.

4. **Coherent, maintained runtime providers.** For Noble use native Ubuntu 8.3 and its native extensions, with package-origin pinning and per-extension policy/ABI evidence; keep the 7.4 baseline PPA in a separate VM. Elsewhere prefer distro-native 8.3 where available; otherwise require a maintained, signed, suite-compatible provider with pinned package constraints and documented update policy. Compare EL9 AppStream 8.3 and Remi 8.3 package/extension availability. Select one coherent provider in the reviewed manifest; neither is a tested result yet. For Ubuntu 26.04, inability to resolve native/suite-compatible 8.3 and every mandatory extension is a blocker, not permission to mix incompatible distro packages or select 8.4/8.5 silently. Reusing an arbitrary 7.4 extension binary is forbidden. Freeze exact versions/repository origins in the test report, while allowing reviewed security updates within 8.3.

5. **Preserve SAPI topology.** Ubuntu retains its tested Apache module arrangement, updated to 8.3; Rocky retains FPM, updated to 8.3. Verify loaded INI paths/extensions independently for CLI and web, worker interpreter paths, OPcache, timeouts, permissions and service restarts. Avoid system-wide alternatives changes that affect unrelated applications. Restart long-running workers during controlled cutover so no old interpreter remains processing jobs.

6. **Isolated acceptance matrix.** Begin with fresh Ubuntu 24.04 lab VMs, with distinct hostnames/IPs, no shared production storage, database, credentials or host source mounts. Never clone `.20` or use it as an experiment. Synthetic lab snapshots/clones are allowed. Test runners must reject `.20` and unexpected target addresses after DNS resolution, and refuse redirects to them; host-only/NAT alone does not enforce this boundary. Ubuntu 26.04 and Rocky 9 remain eventual acceptance targets. The expressly authorized `.20` boot and read-only package/service inspection are allowed; normal startup/log/worker writes are not manual migration changes. Do not install/update/remove packages, edit configuration, manually restart services, issue database/media writes, or export secrets there. Record OS, PHP/SAPI/module versions, package revisions and source/patch hashes. For each distro validate fresh install, repeated provisioning, restart/reboot, controlled upgrade from the 7.4 baseline and rollback rehearsal. Containers cover builds/dependency checks; disposable full-service labs cover runtime behavior. HTTP and HTTPS API/delivery must both be exercised, including a trusted CA rather than bypassed TLS validation. Upload both a short deterministic MP4 and a Full HD/60 fps fixture; verify READY, flavors, thumbnails, HLS segments and actual progressive stream properties/Range.

7. **Failure and release gates.** Before capturing measurements, freeze the baseline protocol: separate 7.4 and 8.3 labs use the same pinned OS box, 4 vCPU, 8 GiB RAM and matching virtual disk/controller settings. Use checksum-verified published 7.4 server packages, never `.20`, as the application baseline. Generate synthetic 10-second 640x360/25fps and 60-second 1920x1080/60fps H.264/AAC fixtures; record encoder settings and SHA-256 hashes and reuse identical bytes in both labs. After two warm-up rounds, run at least five measured rounds, each with 100 sequential authenticated API calls (session start, media list and media get recorded separately) plus upload-to-READY/stream verification for each fixture. Record sample counts, nearest-rank p95, median, conversion profile and environment details. Capture baseline warnings/performance and run this same bounded workload on 8.3. Block on fatal/type errors, worker/job failures, authentication/permission regressions, missing extensions, changed API contracts or untriaged warnings in exercised paths. The same workload's median and p95 API latency and transcode wall time must not regress more than 20% without explicit review; use multiple repetitions and preserve reports, not a one-off benchmark. Scope exclusions and nonfatal accepted deprecations require named rationale/tests, not blanket ignore rules. Publish no migration release until all distro/runtime and rollback gates pass.

8. **Separate improvements from compatibility fixes.** Prefer the smallest justified source change and test it against both the unpatched PHP 7.4 behavior and PHP 8.3 candidate. Evaluate component upgrades in separate changes with exact old/new versions, upstream support and license evidence, compatibility impact, focused tests and a revert path. An upgrade candidate is not automatically selected. Avoid bundling framework replacement, DB changes or unrelated application features. Record any accepted upgrade decision before adding it to the experimental ZIP; larger scope changes require a separately approved proposal. Measure API median/p95 and transcode timing with the frozen protocol before claiming performance improvement. Preserve functionality over speculative speed gains. No experiment authorizes a `.20` deploy, promises zero downtime or bypasses recovery rehearsal.

9. **One approved release for packages and source ZIP.** The operator confirmed publishing the accepted, versioned PHP 8.3 source ZIP as an asset of the same GitHub release as the Ubuntu DEB and Rocky Linux RPM repository bundles. Include the source/ordered-patch manifest and installation instructions; SHA256SUMS covers the ZIP, manifest and package bundles. Verify downloaded assets against the checksums and the accepted source/patch identities. Keep the original upstream ZIP and all existing releases unchanged. The current experimental ZIP is not promoted by this planning decision: the final release still requires all runtime/recovery gates and final operator approval.

## Risks / Trade-offs

- **PHP 8.3 support horizon** → the user specifically requested 8.3; reassess security-support dates before implementation/release. A later minor target needs an explicit updated proposal, not an automatic substitution.
- **Bundled legacy dependencies may be the dominant work** → Stage 1 produces a go/no-go report before package/runtime work; unsupported dependencies are blockers requiring a bounded repair plan.
- **Warnings may become fatal through application error handlers** → test handlers with realistic calls and background jobs; suppressing output is not compatibility.
- **Cache/session serialization may differ** → quiesce workers and invalidate only documented disposable caches; preserve secrets/data. Rehearse login/session behavior and rollback rather than assuming drop-in equivalence.
- **Rollback after new writes can lose data** → require a maintenance/read-only window until acceptance and recover a matched application/config/DB/media snapshot if needed; package downgrade alone is not a recovery plan.

## Migration Plan

1. Phase-1 preparation and minimal lab-only source repairs are approved. Prepare isolated baseline and compatibility reports, test individual repairs and build the separately named experimental PHP 8.3 ZIP; obtain go/no-go approval on blockers/provider matrix before production packaging integration.
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

## Phase-1 review boundary (2026-09-25)

Claude reviewed the planning artifacts without repository/tool access; its findings are advisory, not runtime evidence. The operator approved incorporating the corrections. Source inventory, syntax/static checks, synthetic probes and provider resolution may proceed. The subsequent operator confirmation also permits minimal lab-only source patches and the separate reproducible PHP 8.3 ZIP, without marking feasibility complete or approving package/CI changes. No migration tags, main-spec synchronization or archive before task 4.4. Production data extraction requires separate approval. PHPCompatibility and PHPCS versions plus dependencies must be pinned with checksums/lockfile, checked for PHP 8.3 coverage, and run with `testVersion=7.4-8.3`; syntax checks and E_ALL runtime probes remain separate evidence.

## Approved test execution plan (2026-09-25)

The operator approved this refinement after parallel planning reviews by the
Claude, Grok and Cursor CLIs. Those reviews are advisory, not test execution.
This section operationalizes Decisions 1–9 without changing the proposal or
specification gates. The original 24 tasks remain acceptance obligations;
the detailed cases in tasks.md are their execution breakdown, not extra release
scope or an estimate of work completed.

### Seven test gates

| Gate | Required evidence | Entry / exit boundary |
|---|---|---|
| T0 Inventory and coverage | Source, published baseline, ordered patches, harness and fixture hashes; dependency/license/entrypoint inventory; static findings; task-to-case mapping and uncovered paths | Freeze identities and expected results before execution. Unknown coverage is explicit, not PASS. |
| T1 PHP compatibility | Original/candidate differential tests on 7.4 and 8.3; individual fixes then the selected combined patch set; PDO types/errors, JSON/XML, dates/locales, serialization, cron/CLI/workers | Expected original-8.3 failures are controls, not candidate successes. Selected patch omissions or unexpected diagnostics block acceptance. |
| T2 API, security and UI | Real HTTP/trusted HTTPS authorization and response contracts, cross-partner denials, KS failures, real cache backends, eSearch, Admin Console/KMC and Go console | Mock-client and isolated parser tests cannot substitute for full-service or browser evidence. |
| T3 Media and jobs | Frozen short and Full HD/60 fps fixtures; upload-to-READY, flavors/thumbnails, HLS segments and progressive Range; corrupt/empty input and worker failure/retry | Assert actual delivered stream properties and terminal job states, not just status 200 or READY. |
| T4 Three distributions and packages | Ubuntu 24.04, Ubuntu 26.04, Rocky 9; coherent 8.3 provider/extensions/SAPI; fresh install, reprovision and reboot; build/CI rejection cases | Provider resolution may proceed in disposable environments; production package/CI integration still requires task 1.5 approval. Missing providers are BLOCKED, not N/A. |
| T5 Performance and diagnostics | Decision 7's identical-resource protocol, two warmups and at least five measured rounds; API median/p95, transcode and queue timings; classified diagnostics | More than 20% regression requires explicit review. Shared-host contention or unstable runs are INCONCLUSIVE and require repetition, not PASS. |
| T6 Upgrade, recovery and release | Synthetic-state upgrade, matched-state rollback, approved ZIP/DEB/RPM identities, double-build ZIP reproducibility and downloaded asset verification | Full distro/runtime/recovery acceptance plus operator release approval precede publication; `.20` cutover has a separate approval boundary. |

A candidate is an explicitly selected, reviewed patch manifest, not necessarily
all patches in `held/`. Record each held patch as selected, rejected or deferred
with its reason. The JSON-only exp2 ZIP is neither the complete candidate nor a
release. Its bounded evidence remains useful only for its exact tested scope.
Changing source, selected patches, harness, runtime or configuration makes
previous dependent results stale until rerun or a documented impact review;
retain their history, never silently transfer PASS to a new candidate.

### Case and evidence contract

Expand each case into applicable distro × SAPI × transport × fixture rows before
running it. Record a stable case/run ID, original parent task(s), executor and
independent reviewer, timestamp, commit and source/patch/harness/fixture hashes,
OS/runtime/module/INI/provider identities, target allowlist, preconditions,
exact command, expected result, observed result, exit code, duration, sanitized
log/report paths, defect IDs, cleanup and retest outcome. Do not record credentials,
KS values, cookies, private keys or production data. Commands, timeouts, profile
and stream tolerances must be reviewed before execution rather than inferred
from a successful output. Normalize only explicitly listed volatile fields;
never normalize away types, authorization failures or semantic changes.

Execution states are NOT_RUN, RUNNING, PASS, FAIL, BLOCKED and INCONCLUSIVE.
A justified N/A requires a named scope rationale and reviewer; mandatory distro
or functional requirements cannot be waived this way. PARTIAL describes aggregate
coverage or older limited evidence, never a passing execution. An unavailable CLI
is BLOCKED/NOT_EXECUTED, not application FAIL and never PASS. Track unknown paths
and new findings alongside the denominator; do not conceal them by shrinking it.

Report after each batch: planned applicable rows, executed rows, PASS/FAIL/
BLOCKED/INCONCLUSIVE/NOT_RUN counts, stale results, critical defects and release
prerequisites, new discoveries, and the next three runnable cases. Report the
original 24 acceptance tasks separately from detailed-case counts. Neither count
is a completion percentage or release ETA. All applicable rows and independent
review must pass before closing a case; close a parent only when its entire
original acceptance text is satisfied. Syntax validation of this plan does not
complete any application test.

### Parallel execution and independent review

Follow AGENTS.md: involve the actual Claude, Grok and Cursor (`agent`) CLIs in
execution and review over every validation cycle; Codex integrates results.
Default ownership is Claude for differential PHP/API, Grok for negative/security
cases, Cursor for coverage/artifact/distro checks. Rotate reviewers:
Claude → Grok, Grok → Cursor, Cursor → Claude. A blocked reviewer remains visible;
another independent authorized reviewer may provide additional evidence without
pretending that the blocked CLI ran. Review alone is not execution; arrange an
independent rerun of critical cases on the same frozen inputs.

Parallelize only independent read-only checks or tests in distinct disposable
clones. Reserve each VM/DB/worktree for one mutation owner and each benchmark host
for one workload; serialize if separate clones or an exclusive reservation are
unavailable. Protect `.20`, reject unexpected DNS/redirect targets, use synthetic
data and restore disposable state in cleanup. Do not bypass CLI protections.

### Specific regression boundaries

- Assert PDO numeric/string/NULL/false behavior through actual API contracts and
  generated clients, not just driver return values. Include negative DB paths.
- Exercise original 7.4 serialized objects with 8.3, cold/warm real caches and
  documented invalidation. A mixed 7.4/8.3 rollout is not approved: demonstrate
  that cutover drains/stops old workers. Do not add mixed-runtime support or claim
  arbitrary 8.3 writes can be read by 7.4; rollback restores a coherent snapshot.
- Include KS crypto interoperability, expiry/clock skew, privilege tampering,
  cross-partner denial, XML external-entity rejection without external network
  access, timezone/locale behavior, and active install/plugin/cron entrypoints.
  Optional capabilities are inventoried before inclusion; do not silently add
  DRM/live/DWH or DB/schema upgrades to this change.
- Test browser login/session/ACL behavior and search indexing/query parity. Check
  Apache/FPM body handling and OS service/security-policy behavior in the actual
  target topology. No bypass of TLS verification or SELinux/AppArmor to pass.
- Separate worker orchestration/queue latency from ffmpeg conversion time. Keep
  profiles and OPcache/JIT settings recorded and comparable; record sample counts
  and dispersion. Resolve unstable measurements before applying the 20% gate.
- Rehearse failure after synthetic candidate writes while intake is restricted;
  restore the matched baseline and explicitly account for discarded experimental
  writes. This is recovery rehearsal, not a promise of lossless post-cutover
  downgrade or permission to alter production.

### First execution batch

T0-01: Claude runs the existing local harness suite; Grok independently reviews
and reruns the bounded command. T0-02: Cursor audits source/patch/ZIP identities
and selection gaps; Claude reviews. T0-03: Grok maps each original task to cases,
existing evidence and uncovered scope; Cursor reviews. All are local-only; no
VM, package, CI or release mutation is authorized by this batch. Record tool
failures separately. Subsequent lab cases start only after target ownership,
commands and candidate identities are frozen. These are assignments, not claims
that execution has already happened.

### Refinement validation

All three actual CLIs returned planning reviews of the supplied proposal,
updated design/tasks and delta specs with no blocking planning findings. Claude
identified non-blocking baseline-timing and approval-boundary ambiguities;
the final case wording now explicitly covers baseline runtime/extension/timing
reports, baseline-versus-candidate measurements separated from optional upgrades,
and feasibility approval for both additional distro integrations. Cursor and
Grok confirmed the parent mapping and preserved gates. These were document-only
reviews, not independent runtime execution or release sign-off. Local strict
OpenSpec validation and checks for preserved original text, 24 mapped parents,
27 unique cases and zero completed checkboxes passed. Application execution
remains the next apply-phase activity.
