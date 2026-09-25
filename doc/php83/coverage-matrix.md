# PHP 8.3 original-task coverage matrix (T0-03)

Snapshot: 2026-09-25. This is an evidence reconciliation, **not acceptance of the
24 original tasks**. The detailed cases are defined in
[the task list](../../openspec/changes/migrate-kaltura-php83/tasks.md).
T0-03 itself audits this mapping; it is not a functional substitute for each row.

OpenCode with Zen Muse Spark 1.3 Contributor Free produced the initial read-only
inventory after Grok exited at its turn limit without a completed report. The
[raw advisory audit](evidence/batch2-inventory/opencode-coverage.txt) is retained.
The table below corrects overbroad negative statements in that draft: many focused
repairs/tests and some diagnostic triage already exist; the missing item is full
coverage, not absence of any tests. Decision 7 already specifies the benchmark
protocol; frozen fixture/run evidence and measurements remain outstanding.
Evidence paths below are relative to `doc/php83/`. NONE means no completion
artifact identified for that gate, not proof that no related file exists anywhere.

| Original task | Detailed execution cases (excluding mapping case T0-03) | Existing bounded evidence | What remains to satisfy the original task |
|---|---|---|---|
| 1.1 Inventory | T0-02, T0-04 | `source-graph.md`, `feasibility-status.md`, `patch-inventory.md`, `inventory-ledger.md`, `package-identities.md`, `evidence/source-audit/source-to-package-map.json` | Complete dependency/license/revision attribution; active versus historical overlays and generated/web/CLI/cron/install/plugin entrypoints. |
| 1.2 Baseline | T0-05, T5-01 | `feasibility-status.md`, `evidence/noble-baseline/` | Full frozen fixture workload, repeated timings, browser/TLS/media/job coverage and comparable baseline reports beyond `.74` HTTP smoke. |
| 1.3 Static/syntax | T0-04, T1-04 | `feasibility-status.md`, `runtime-triage.md`, `candidate-syntax.md`, `compiler-triage.md`, `evidence/source-audit/` | Classify every finding and manual analyzer blind spot; map remaining findings to active entrypoints. Static counts are not confirmed incident counts. |
| 1.4 Providers | T4-01 | `evidence/noble-runtime/`, `evidence/providers/README.md` and probe outputs | Complete signed suite-compatible package resolution and loaded mandatory modules/ABIs in clean environments for all targets, not just probes. |
| 1.5 Feasibility approval | T0-06 | `feasibility-status.md` is partial; final approved report NONE | Consolidated bounded repairs/blockers/provider results and explicit go/no-go before production package/CI integration. |
| 1.6 Experimental repairs | T0-01 (harness support), T0-02, T1-01 | `experimental-zip.md`, `patch-inventory.md`, `exp9-pdo-integration.md`, held repair documents | Full selected repair coverage and combined candidate validation; exp9 integrates sixteen targets with bounded API/CLI/SQL evidence, but is not an accepted complete application. Original exp2 remains unchanged. |
| 1.7 Optional upgrades | T0-06 | Final per-component decision report NONE | Pinned versions, license/support/benefit/regression/revert analysis or explicit reviewed deferral. No component upgrade inferred from compatibility fixes. |
| 2.1 Core/API | T1-01, T1-02, T1-03 | `registry-investigation.md`, `symfony-bootstrap.md`, `api-mysql.md`, `doc-comment-property.md`, `doc-comment-consumer.md`, `patch-inventory.md` | Resolve known semantic/diagnostic gaps and select an integrated reviewed series. Focused parity and isolated strict application already exist, not full acceptance. |
| 2.2 Worker/CLI/libs/clients | T1-01, T1-02, T1-04, T3-02 | `runtime-triage.md`, `mysql-type-experiment.md`, `propel-init-hydration.md`, held patch documents | Full active worker/CLI/cron/install/plugin/generated-client execution; per-change attribution and regression/failure coverage. |
| 2.3 Shared package patching | T4-02, T4-06 | NONE for integrated packaging; `experimental-zip.md` is a lab builder only | After go/no-go, shared DEB/RPM transformation, identical accepted source payloads, drift-fails-build checks. |
| 2.4 Ubuntu dependencies | T4-03, T4-04 | NONE for migrated package integration | After go/no-go, coherent 8.3 dependencies/configuration and data/config-preserving upgrade on both Ubuntu targets. |
| 2.5 Rocky dependencies | T4-05 | Provider probes only; integration NONE | After go/no-go, coherent FPM/CLI stream, pools/services/extensions and no old workers after restart. |
| 2.6 CI guards | T4-06 | NONE for migrated CI | After go/no-go, exact-family/module/ABI positive and negative fixtures, including misleading RPM strings. |
| 3.1 Noble acceptance | T4-03 | `.74` baseline smoke; `.83` runtime and bounded probes only | Complete candidate clean install, reprovision, reboot, preserved data/configuration and full sanity. |
| 3.2 Ubuntu 26.04 acceptance | T4-04 | Provider probes only | Full isolated 8.3 application install/provision/reboot and runtime suite with verified suite-compatible provider. |
| 3.3 Rocky acceptance | T2-03, T4-05 | Provider probes only | Full isolated FPM application acceptance, request bodies, jobs/modules and restarts; dependency simulation is insufficient. |
| 3.4 API/UI/search | T1-02, T1-03, T2-01, T2-02, T2-03 | `api-bootstrap.md`, `api-mysql.md`, `api-session.md`, `api-auth-dispatch.md`, `api-http.md`, `api-web.md`, `analytics-partner-probe.md`, `exp9-pdo-integration.md` | Real full-service auth/contracts/cache/search/browser regression across distros; remaining KS/crypto/XML/locale negatives and diagnostic triage. Existing synthetic Apache HTTP/trusted HTTPS evidence is retained, not dismissed. |
| 3.5 Media | T2-02, T3-01, T3-02 | `.74` HTTP smoke; complete candidate evidence NONE | Frozen short/1080p60 fixtures, HTTP/trusted HTTPS READY/flavors/thumbnails/HLS/206/stream properties, Go console E2E, corrupt inputs/job retry. |
| 3.6 Performance | T5-01 | Protocol in design Decision 7; full measurement report NONE | Comparable repeated baseline/candidate workload, median/p95/conversion/queue/dispersion and 20% review threshold; comprehensive diagnostics, separate optional upgrades. |
| 4.1 Upgrade | T1-03, T6-01 | Rehearsal NONE; narrow legacy parser cache transfer documented | Full synthetic 7.4→8.3 state preservation and accepted runtime, without schema/engine changes. |
| 4.2 Recovery | T6-02 | Rehearsal NONE; planned boundary in design | Matched application/runtime/config/DB/media restoration after failed synthetic cutover, baseline login/playback and write-freeze verification. |
| 4.3 Operator docs | T6-03 | Experiment docs and design exist; accepted migration guide NONE | Tested migration/provider/rollback commands, linked full evidence matrix, limitations and fresh support-horizon check before release. |
| 4.4 Release gate | T6-04 | Approval/completed gate audit NONE | All mandatory acceptance/recovery rows, unique accepted packages/checksums and explicit release approval. `.20` remains separately gated. |
| 4.5 Publication | T6-05 | Local experimental ZIP only | After 4.4 approval, accepted ZIP+manifest+instructions and DEB/RPM bundles in one release; downloaded identity verification, preserve old artifacts, then spec sync/archive. |

## Uncovered scope stays visible

- Complete active-path and dependency/license classification is unknown. A large
  graph or static scan is not runtime reachability proof; unexercised code is not
  automatically inactive. Use graph freshness/coverage checks for future
  structural conclusions and read source for gaps.
- No full integrated runtime candidate is accepted. Held alternatives and known
  Registry/DB semantic differences cannot be silently combined or waived.
- Clean provider/application acceptance on the additional distros, real browser
  and production-topology cache/search/media/jobs, repeated performance and
  upgrade/recovery remain open. Existing support/provider statements need fresh
  evidence when their respective release gates are executed.
- Complete task mapping is not complete implementation. New findings must extend
  case rows and evidence accounting rather than disappear from the denominator.

## Latest bounded inventory/compiler refinement

The original T0-03 mapping audit is retained; the evidence column now includes
subsequent exp9 and inventory work rather than implying exp2 is the latest
experiment. All 792 missing packaged file identities are resolved through exact
payload bytes, while component/license/entrypoint attribution remains open.

The latest whole-ZIP compiler matrix retains 54 rejected files. Exact-source
historical 7.4 comparisons classify 47 as new 8.3 language incompatibilities and
seven as retained baseline rejections (six generator skeletons plus one reserved
Object import). Six positive generation-consumer chains establish template
purpose, not valid generated output or complete workflow execution. No compiler
row is removed or waived, and the 4,711 historical static report rows are not
automatically adjudicated from these 54 compiler classifications. See
[compiler triage](compiler-triage.md) for identities and limitations.

## Held curly-offset batch

[Curly-offset evidence](curly-offsets.md) now records 43 isolated source repairs:
153 paired delimiters, 306 changed bytes and no other token/byte changes. Actual
Claude repeats the 43 PHP8.3 compiler controls and native negative controls;
204 standalone behavior rows cover three source files on original74/candidate74/
candidate83 with exact independent results. Cursor executes/reviews the behavior
validator; OpenCode executes23 tests and an independent byte audit after Grok's
bounded timeout. Broader runtime effects and integration remain open; patches
stay held, exp9 remains unchanged. Original tasks0/24 and detailed3/27 are not
advanced by this partial T0-04/T1-01 evidence.

## Exp10 artifact integration

[Exp10 integration](exp10-integration.md) adds the43 pure curly-offset repairs to
all16 preserved exp9 targets in a separately named, twice-identical experimental
ZIP. Actual archive verification and exp9 delta independently match. Whole-source
PHP8.3 compiler rejections decrease54→11 across11,784 files per artifact, with no
incomplete rows; unchanged-source outcomes/diagnostics are identical. Two newly
parsable files expose existing declaration diagnostics, not accepted exceptions.
Actual API contracts and48 CLI rows retain prior behavior;18 API diagnostic
groups/503events remain unchanged. The actual ZIP passes68 selected-method cases
across three additional class files. No aggregate task closes: original0/24,
detailed3/27; remaining language failures, full runtime/distro/performance/recovery
and release gates stay open.
