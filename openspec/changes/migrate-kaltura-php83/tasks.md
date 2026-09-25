## 1. Baseline and feasibility gate

- [ ] 1.1 Extract the checksum-verified pinned Kaltura archive and enumerate bundled dependencies, generated clients, packaging overlays and PHP entrypoints; verify a reproducible inventory records revisions, licenses and active versus historical build paths.
- [ ] 1.2 Reproduce the PHP 7.4 baseline from checksum-verified published packages in a fresh isolated lab, never `.20`; freeze the design's VM/fixture/API/repetition protocol first, enforce target/DNS/redirect guards, and use synthetic data only; verify API/UI/upload/worker/playback checks and save sanitized runtime, extension and timing reports.
- [ ] 1.3 Run PHP 8.3 syntax checks and a PHP-8.3-capable pinned PHPCompatibility/PHPCS analyzer with testVersion=7.4-8.3 against the exact packaged application, clients and installer PHP; verify every reported finding is classified with a source location and evidence, including manual checks the analyzer cannot cover.
- [ ] 1.4 Produce the three-distro provider/extension/SAPI matrix (native Noble pinned origins; EL9 AppStream versus Remi evaluation); verify signed suite-compatible PHP 8.3 package resolution and loaded modules in clean test environments, without mixing unsupported distro packages or extension ABIs.
- [ ] 1.5 Write a go/no-go feasibility report with bounded repairs, upstream references and blockers; verify operator approval before production runtime/package integration (lab-only source experiments in 1.6 are already authorized), stopping for a revised proposal if a framework/Kaltura upgrade is needed.

- [ ] 1.6 Develop minimal experimental source patches for confirmed failures in disposable lab trees; verify focused before/after behavior on PHP 7.4 and PHP 8.3, then generate the separately named experimental ZIP twice and compare hashes; record original archive, ordered patch, changed-file and ZIP identities, retaining the original 7.4 artifacts and excluding secrets/runtime data.
- [ ] 1.7 Evaluate dependency upgrade candidates independently from compatibility fixes; record pinned old/new versions, support/license evidence, expected benefit, regression/revert tests and the explicit per-component selection or deferral decision; verify no upgrade is silently bundled or performance gain asserted without comparable measurements.

## 2. Compatibility patches and packaging

- [ ] 2.1 Fix confirmed core/API compatibility issues in a reviewed patch series; verify focused PHP 8.3 tests cover each changed behavior and the patch series applies to the pinned archive without fuzz or rejected hunks.
- [ ] 2.2 Fix confirmed worker/CLI, bundled-library and generated-client issues without an unpinned dependency upgrade; verify focused execution tests, attribution and hashes for every dependency/source change.
- [ ] 2.3 Wire a common reproducible patch application step into DEB/RPM builds; verify identical patched PHP sources are packaged on all three targets and a deliberate source/patch mismatch fails the build.
- [ ] 2.4 Update Ubuntu package dependencies and web/CLI configuration to the verified 8.3 stack; verify clean dependency resolution, matching CLI/Apache modules and configuration-preserving upgrade behavior on both Ubuntu versions.
- [ ] 2.5 Update EL9 dependencies, runtime stream and FPM/CLI configuration; verify 8.3 version-family selection, mandatory extensions, pool/service configuration and no old-runtime Kaltura workers after restart.
- [ ] 2.6 Replace PHP-8-rejection CI checks with positive exact-family and extension assertions; verify fixtures reject 7.4, 8.2/8.4, absent modules and misleading RPM release strings, while accepting the intended 8.3 transaction.

## 3. Isolated runtime acceptance

- [ ] 3.1 Run fresh install, repeated provisioning and reboot acceptance on an isolated Ubuntu 24.04 lab; verify no data/secret reset and zero functional sanity failures with web/CLI PHP 8.3 evidence.
- [ ] 3.2 Repeat the same acceptance on isolated Ubuntu 26.04 and save provider/module evidence; verify no fallback to another PHP minor or unsupported distro packages.
- [ ] 3.3 Repeat the same acceptance on isolated Rocky 9 with FPM; verify request-body handling, worker processing and modules rather than relying on dependency simulation alone.
- [ ] 3.4 Run API authentication/permission/JSON-contract, eSearch and Admin Console/KMC browser regression tests across the matrix; verify unauthorized calls still fail, UI flows succeed and logs contain no untriaged runtime failures.
- [ ] 3.5 Run short deterministic and Full HD/60 fps upload fixtures across HTTP and trusted HTTPS API/delivery; verify READY, thumbnails/flavors, HLS manifest/segment, progressive resolution/frame rate/Range and existing Go console E2E behavior.
- [ ] 3.6 Compare repeated unchanged-baseline/candidate workload timings and error logs, separating compatibility-only patches from any selected component upgrade; verify the design's performance gate and triage all exercised-path warnings without blanket suppression.

## 4. Upgrade, recovery and release gate

- [ ] 4.1 Rehearse 7.4-to-8.3 upgrade with representative synthetic existing data in an isolated lab clone; verify accounts, partner secrets, media, configuration and job state are preserved without schema/engine changes.
- [ ] 4.2 Rehearse failed-cutover recovery from a coherent restricted snapshot; verify matched application/runtime/config/DB/media restoration and baseline login/playback, documenting the maintenance/write-freeze boundary.
- [ ] 4.3 Write migration, provider-update, rollback and limitations documentation with the evidence matrix; verify commands/links and re-check PHP 8.3 security-support dates before proposing a release candidate.
- [ ] 4.4 Obtain release approval only after all distro, runtime and recovery gates pass; verify uniquely versioned DEB/RPM artifacts and checksums, leaving old releases unchanged; synchronize main specs/archive only after this gate and the publication checks in 4.5, and create no migration tag earlier. Any actual `.20` cutover requires separate explicit target/window/backup approval.

- [ ] 4.5 After task 4.4 approval, publish the versioned PHP 8.3 source ZIP as an asset of the same GitHub release as the Ubuntu DEB and Rocky Linux RPM repository bundles; include its source/patch manifest and installation instructions, and cover the ZIP, manifest and package bundles in SHA256SUMS. Verify downloaded release assets against their checksums and the accepted source/patch identities; preserve the original upstream ZIP and all existing releases, and never relabel the incomplete experimental ZIP as an accepted release.

## Partial phase-1 evidence (2026-09-25)

See `doc/php83/feasibility-status.md` and `doc/php83/evidence/`. Planning corrections
are approved and strict validation passes. Noble candidate runtime/modules and
package origins are verified; raw-source and published-payload syntax/static
scans are recorded, including identical-file PHP 7.4/8.3 comparison. The isolated
`.74` baseline is provisioned and passed the HTTP upload-to-READY/HLS smoke suite. The operator subsequently confirmed lab-only minimal patches and a separate experimental PHP 8.3 ZIP (tasks 1.6–1.7); production/release gates remain unchanged. No checkbox above is complete yet: full
inventory/license/entrypoint review, runtime reachability, synthetic workload,
provider matrix and go/no-go decision remain open.

## 5. Approved detailed test cases

These cases refine, rather than replace, the original 24 acceptance tasks.
All start NOT_RUN under the new evidence contract; existing limited evidence
remains PARTIAL pending identity/coverage reconciliation. The added checkboxes
must not be interpreted as increased implementation progress or a new release
scope. Expand applicable distro/SAPI/transport rows before execution. Use the
owners/reviewer rotation and result contract in design.md. Closing a detailed
case does not automatically close its original parent.

- [x] 5.1 T0-01 — Claude executes the existing local Python harness suite on a frozen commit; Grok reviews and independently reruns it. Record command, test count, exit, harness hashes and sanitized results, with mocks explicitly excluded from runtime acceptance; this is harness support, not baseline acceptance (parent 1.6).
- [x] 5.2 T0-02 — Cursor audits immutable baseline/source, held patch metadata, selected/rejected/deferred patch decisions and exp2 ZIP identities; Claude verifies hashes and the held-versus-exp2 gap. No selected patch may silently disappear from a proposed candidate (parents 1.1, 1.6).
- [x] 5.3 T0-03 — Grok reconciles all original 24 tasks with these cases and existing evidence; Cursor verifies every parent is mapped, partial evidence is bounded and untested entrypoints/findings remain visible (parents 1.1–1.7, 2.1–2.6, 3.1–3.6, 4.1–4.5).
- [ ] 5.4 T0-04 — Inventory dependencies/licenses, active packaging overlays, generated clients, web/CLI/cron/install/plugin entrypoints and syntax/static findings; verify exact identities, analyzer pins and classification of every finding, with uncovered paths listed (parents 1.1, 1.3).
- [ ] 5.5 T0-05 — Freeze the full published-7.4 synthetic baseline, VM resources, fixture hashes, expected outputs and guarded target protocol; verify API/UI/worker/media smoke evidence, runtime/extension reports and baseline timings using Decision 7, including rejected targets/redirects (parent 1.2).
- [ ] 5.6 T0-06 — Produce the feasibility and optional dependency decision records; verify each proposed upgrade has old/new pins, attribution, regression/revert evidence or explicit deferral, and obtain go/no-go before production packaging integration (parents 1.5, 1.7).
- [ ] 5.7 T1-01 — Run focused original/candidate 7.4/8.3 cases for each selected repair, then the combined manifest; verify expected control failures, preserved behavior, diagnostics, strict patch application and two identical experimental ZIP builds (parents 1.6, 2.1, 2.2).
- [ ] 5.8 T1-02 — Exercise PDO/database error paths and JSON/XML/generated-client contracts with numeric, string, NULL and false fixtures; verify explicit type/value comparisons and no broad normalization of differences (parents 2.1, 2.2, 3.4).
- [ ] 5.9 T1-03 — Exercise complete legacy serialized objects, actual configured cache backends, cold/warm restart and documented invalidation; verify dates/relative time in selected timezones/locales and preserved API semantics (parents 2.1, 3.4, 4.1).
- [ ] 5.10 T1-04 — Run active worker/CLI/cron/install/plugin entrypoints and bundled/generated code cases from the inventory; verify interpreter, diagnostics, jobs and failure handling, recording any excluded inactive paths (parents 1.3, 2.2).
- [ ] 5.11 T2-01 — Run real HTTP and trusted-HTTPS API authentication/authorization on each target, including cross-partner denial, tampered/expired/skewed KS, privilege edits and legacy crypto fixtures; verify exact error/response contracts and no secret leakage (parent 3.4).
- [ ] 5.12 T2-02 — Run Admin Console/KMC browser login/session/ACL and eSearch index/query regression plus Go console E2E; verify real service/browser evidence rather than HTTP mocks or page reachability alone (parents 3.4, 3.5).
- [ ] 5.13 T2-03 — Test XML external-entity rejection without external network access, malformed requests and real Apache/FPM body handling; verify no unauthorized data exposure and explicit negative outcomes (parents 3.3, 3.4).
- [ ] 5.14 T3-01 — Upload the frozen 10-second 360p25 and 60-second 1080p60 fixtures through HTTP and trusted HTTPS across the distro matrix; verify READY, each required flavor/thumbnail, HLS manifest/segments and progressive 206/Content-Range using delivered-stream inspection and predeclared tolerances/timeouts (parent 3.5).
- [ ] 5.15 T3-02 — Exercise empty/corrupt uploads and worker failure/retry in disposable fixtures; verify rejected input, explicit terminal job/flavor states, no duplicate or indefinitely stuck processing and cleanup (parents 2.2, 3.5).
- [ ] 5.16 T4-01 — Resolve the provider/extension/SAPI matrix on clean Ubuntu 24.04, Ubuntu 26.04 and Rocky 9 environments; verify signed suite-compatible origins and loaded 8.3 modules, recording unavailable providers as BLOCKED rather than fallback (parent 1.4).
- [ ] 5.17 T4-02 — After the feasibility approval, verify shared patch integration yields identical selected PHP source identities in ZIP and all DEB/RPM payloads; deliberate source/patch drift must fail the build (parent 2.3).
- [ ] 5.18 T4-03 — After the feasibility approval, run Ubuntu 24.04 clean install, repeated provisioning and reboot; verify exact web/CLI 8.3, services/modules, preserved configuration/data and the full applicable runtime suite (parents 2.4, 3.1).
- [ ] 5.19 T4-04 — After the feasibility approval, repeat the same installation/preservation/runtime cases on Ubuntu 26.04 with its verified provider; verify no wrong-minor or cross-suite fallback (parents 2.4, 3.2).
- [ ] 5.20 T4-05 — After the feasibility approval, repeat on Rocky 9 with coherent FPM/CLI and reviewed service/security-policy configuration; verify required modules, request bodies, jobs and no old-runtime workers after restart (parents 2.5, 3.3).
- [ ] 5.21 T4-06 — After the feasibility approval, exercise package/CI negative fixtures for PHP 7.4, 8.2/8.4, missing extensions, mismatched ABI, misleading RPM strings and bad hashes; verify fail-closed behavior and correct 8.3 acceptance (parents 2.3, 2.6).
- [ ] 5.22 T5-01 — Compare unchanged 7.4 baseline and 8.3 candidate in matching labs, separating compatibility-only patches from any selected component upgrade. Run the frozen Decision 7 workload without competing host workloads, recording two warmups, at least five measured rounds, API median/p95, transcode/queue times, dispersion and diagnostic causes/events; verify the 20% review threshold and repeat INCONCLUSIVE measurements (parents 1.2, 3.6).
- [ ] 5.23 T6-01 — Rehearse each target's upgrade from a synthetic 7.4 baseline, drain/stop old workers and compare accounts/secrets/configuration/media/jobs before and after; verify preserved state and full candidate acceptance without schema/engine changes (parent 4.1).
- [ ] 5.24 T6-02 — Rehearse failed cutover after controlled synthetic candidate writes and restore a matched app/runtime/config/DB/media snapshot; verify baseline authentication/playback, state consistency and explicit handling of discarded candidate writes before reopening intake (parent 4.2).
- [ ] 5.25 T6-03 — Validate migration/provider/rollback instructions and evidence links, known limitations and current PHP security-support information; verify documentation against lab commands and the complete coverage board (parent 4.3).
- [ ] 5.26 T6-04 — Audit all required distro/runtime/performance/recovery rows, independent reviews and critical defects; verify uniquely versioned artifacts and explicit operator release approval, without implying `.20` cutover approval (parent 4.4).
- [ ] 5.27 T6-05 — Only after T6-04, publish the accepted versioned ZIP, manifest, instructions and DEB/RPM bundles in one release; verify downloaded SHA256SUMS and accepted identities, preservation of existing releases, then synchronize/archive only when all original gates are satisfied (parent 4.5).

## Detailed-case execution evidence

T0-01 / 5.1 is complete for frozen commit `e93dc4cf`: Claude executed the
68-test local harness, Grok independently reran and reviewed it, and Cursor
reviewed the result. Codex also reran the suite and verified all 107 tracked
harness/patch file hashes against that commit. This does not close parent 1.6.
T0-02 / 5.2 now has complete current-inventory identity/disposition evidence: 19
patches, original source tree, Noble baseline and exp2 archive verified with
Cursor execution and Claude independent reruns. T0-03 / 5.3 is complete for the
24-parent coverage reconciliation: OpenCode Muse Spark executed the local audit
after Grok exited at its turn limit; Cursor reviewed the corrected matrix.
See `doc/php83/patch-inventory.md`, `doc/php83/coverage-matrix.md` and
`doc/php83/evidence/batch2-inventory/`. No held patch was promoted.
See `doc/php83/test-status.md` and `doc/php83/evidence/batch1-local/`.
The original 24 acceptance tasks remain unchecked.

T4-01 / 5.16 now has partial real CLI/Apache/FPM provider evidence on all three
targets and independent reruns (`doc/php83/provider-runtime.md`). It remains
unchecked: legacy APC dependency/use and full extension/ABI/provider policy
reconciliation are still open. No package/CI or VM changes were made.

T1-03 / 5.9 and T4-01 / 5.16 have additional bounded APC/APCu evidence
(`doc/php83/apcu-cache.md`): original CLI cache initialization is disabled on
both 7.4 and 8.3; a fixture-only direct alias experiment fails missing-counter
semantics on both. Claude/Cursor independently reproduced the results. No
application adapter was selected and no checkbox is closed by these probes.

Additional T1-03/5.9 evidence: original `kApcConf` exercised across real Apache
requests under an explicit minimal INI on PHP 7.4/8.3; disabled-cache controls
and test-only fetch/store/delete alias persistence/version/delete/replacement
rows passed with independent Claude/Cursor reruns. This is not full bootstrap,
reflection, concurrency/restart or an approved adapter. See `doc/php83/apcu-web.md`.

For T1-01/5.7 and original 1.6, a separately reviewed six-patch exp3 experiment
selects the existing JSON repairs plus KalturaPDO query, date ternary and parser
property repairs. The original exp2 selection/artifact is preserved. Actual ZIP
construction and regression on its extracted bytes are tracked separately in
`doc/php83/exp3-candidate.md`; no full-case completion is inferred from selection.

T1-01/5.7 now has focused execution of the actual extracted exp3 ZIP: 48 CLI rows,
20 candidate functional comparisons, independent Claude/Cursor reruns, and four
expected original-8.3 syntax controls. Diagnostics remain open and SQL/HTTP/TLS
artifact regression is pending, so the case remains unchecked. The initial
minimal-consumer harness failure is retained with its guarded correction. See
`doc/php83/exp3-runtime.md`.

Additional T1-01/T1-02 partial evidence: actual exp3 ZIP synthetic SQL + Apache
HTTP/trusted-HTTPS session/auth matrix matches original 7.4; expected original
8.3 PDO signature failure retained. Codex and Claude execute independently.
41 candidate-8.3 diagnostic groups / 1,767 events remain unresolved; this is
not full AIO/FPM/session-persistence/media acceptance. See `doc/php83/exp3-api.md`.
No checkbox is closed by the bounded matrix.

T1-01 partial follow-up: held `Criteria-null-alias.patch` explicitly handles the
missing-alias null before strlen. Eight real-class contracts agree on PHP 7.4
and 8.3; three focused null deprecations disappear, other diagnostics remain.
DB adapter is a fixture; real SQL/API integration remains pending. See
`doc/php83/criteria-null-alias.md`; no acceptance checkbox is closed.

T1-01/T1-02 partial integration: separate seven-patch exp4 ZIP built twice with
identical bytes and exact source delta. Actual extracted ZIP runs alongside exp3
in the synthetic SQL/Apache/HTTP/trusted-TLS matrix; normalized contracts match
original 7.4. The 694 Criteria1375 events disappear, while all other 40 groups /
1,073 events remain unchanged. Full acceptance stays open. See
`doc/php83/exp4-candidate.md`; original/exp2/exp3 preserved.

Partial diagnostic triage for T0-04/T1-01: all 40 groups / 1,073 events from the
exp4 API fixture accounted for in seven source-supported categories, with
artifact-pinned excerpts and 22 native runtime return contracts on 7.4/8.3.
This is not global static-finding/reachability coverage or accepted exceptions.
See `doc/php83/exp4-diagnostic-triage.md`; all relevant acceptance tasks stay open.

T1-01/T1-02 partial: exp5 integrates five explicit-null input guards in a separate
reproducible twelve-patch ZIP. Real SQL/HTTP/trusted-TLS contract remains equal;
exactly 142 events removed, 35 groups/931 remain. Forty-one actual-class cases
and ten real PermissionPeer SQL dependency cases pass on exp4/exp5 × 7.4/8.3;
no full acceptance inferred. See `doc/php83/exp5-null-batch.md`.

T1-01/T1-03 partial: held ActionReflector parameter-class resolver matches native
15/22 cases and real metadata17/24 cases across 7.4/8.3, retaining errors/options
and same-runtime serialized hashes. Uppercase SELF failure was corrected with
the control retained; class-plus-scalar unions handled as native. ZIP/API/shared
cache integration remains pending. See `doc/php83/reflection-parameter-repair.md`.

T1-01/T1-02 partial integration: separate thirteen-patch exp6 ZIP adds the tested
parameter-reflection repair. Actual SQL/HTTP/trusted-TLS and focused CLI parity
remain equal to baseline; exactly 84 reflection events disappear, leaving 33
groups/847 events. Independent reruns and byte identities are recorded in
`doc/php83/exp6-reflection-integration.md`. Full acceptance remains open.

T1-01 partial return-contract repair: held Zend_Config patch adds six explicit
native return declarations for the PHP 8.3-only target. Sixteen actual-class rows
match original7.4/original8.3/candidate8.3; six observed return warnings disappear
without suppression. Combined ZIP/API and broader configuration/scheduler/cache
coverage remain open. See `doc/php83/config-return-contracts.md`.

T1-01/T1-02 partial integration: separate PHP 8.3-only exp7 ZIP integrates the
Zend_Config native return declarations. Five API rows and 60 CLI rows retain
original7.4 functional comparisons plus exp6 counterfactuals. Exactly 144 events
are removed; 27 groups/703 events remain. Four local fault-injection/matrix tests
raise the suite to 126. See `doc/php83/exp7-config-integration.md`; no full-case
checkbox closes and candidate7.4 support is explicitly not claimed.

T1-01 partial: cumulative held Criteria-native-returns retains the prior alias
fix and adds six native return declarations for 8.3. Sixteen state/alias rows and
two invalid iterator controls match; the first fixture-filename equality failure
is retained and corrected through a canonical read-only mount, not suppression.
See `doc/php83/criteria-return-contracts.md`; combined ZIP/SQL/API remains pending.

T1-01/T1-02 partial integration: exp8 replaces the Criteria alias entry with its
cumulative native-return patch (same 14 unique source targets). Exact exp7-to-exp8
application delta is only six declarations; alias guard retained. Four API and
48 CLI rows preserve the original74 reference. Exactly 132 events disappear;
21 groups/571 remain. Local suite now 136 with ten new collector tests.
See `doc/php83/exp8-criteria-integration.md`; no full acceptance checkbox closes.

T1-01/T1-02 additional actual SQL evidence: nineteen rows per runtime confirm
PropelPDO::setAttribute and KalturaStatement::execute discard native booleans on
both 7.4/8.3; nested transaction/cache/dry-run data effects are separately asserted.
This is a reproduced defect, not a corrected candidate or accepted exception.
See `doc/php83/pdo-return-audit.md`; native-bool propagation and caller integration
remain required before return declarations or release.

T1-01/T1-02 partial repair: held PropelPDO setter and KalturaStatement result
patches intentionally restore native boolean success/failure, preserving nested
transactions/cache/dry-run effects in 29 SQL cases × 4 variants. EOF patch serialization
and fixture-only reflection deprecations were corrected with attempts retained.
See `doc/php83/pdo-boolean-repair.md`; real callers/bootstrap/artifact integration
remain pending and public null→bool behavior is explicitly documented.

T1-01/T1-02 partial integration: exp9 retains prior 14 patches and adds the two
boolean-result repairs, with reproducible 16-target ZIP. Four API / 48 CLI rows match
baseline contracts; exactly 68 diagnostic events disappear,18 groups / 503 remain.
Actual KalturaPDO/bootstrap without dependency stubs independently passes 23 rows
per prior/candidate artifact; nine intentional null-to-bool slots are checked.
First fixture named-input failure is retained and corrected. See
`doc/php83/exp9-pdo-integration.md`; no aggregate acceptance checkbox closes.
