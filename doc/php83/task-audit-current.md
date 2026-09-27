# PHP 8.3 task audit — current acceptance, not a progress percentage

Snapshot: 2026-09-26. Read-only audit of `migrate-kaltura-php83`; only this report
is authored here. No task checkbox, status board, application, VM or package changed.
Using change: `migrate-kaltura-php83` (repo-local, spec-driven).

## Authority and verification

Read the [proposal](../../openspec/changes/migrate-kaltura-php83/proposal.md),
[design](../../openspec/changes/migrate-kaltura-php83/design.md), all four delta
specifications and all 51 [tasks](../../openspec/changes/migrate-kaltura-php83/tasks.md).
Actual `openspec status --change migrate-kaltura-php83 --json` and
`openspec instructions apply --change migrate-kaltura-php83 --json` report
**51 tasks, 3 complete, 48 remaining**, ready to apply. `status.isComplete=true`
means planning artifacts exist, NOT implementation acceptance. Actual
`openspec validate migrate-kaltura-php83 --strict --no-interactive` exited 0;
that validates planning, not PHP behavior. Required artifact language is English.
Canonical AGENTS prefers actual Claude/Cursor/OpenCode with bounded attempts;
older design reviewer assignments do not turn unavailable CLIs into executions.

This audit reads retained execution records and authoritative current documents;
it does not rerun PHP, attest every historical report independently, or treat
mock-test counts as runtime coverage. A missing completion record means an open
criterion, not proof that no related experiment exists. Historical sections of
coverage/status documents sometimes describe older candidates: current pinned
reports take precedence over those chronological statements.

## Evidence key (links are part of each matrix row)

- **I**: [inventory ledger](inventory-ledger.md), [payload identities](package-identities.md),
  [attribution](dependency-attribution-followup.md), [actual entrypoint census](entrypoint-inventory.md).
  All 792 missing payload hashes resolved; 4,711 overlapping static rows are not
  4,711 adjudicated defects. Twenty vendor scopes still lack complete attribution.
  Actual entrypoint report has 18,336 candidates and 5,489 invocation rows (5,481
  unresolved), not that many active entrypoints; original ZIP supplies a count only.
- **A**: [exp14 artifact](exp14-candidate.md),
  [selected manifest](evidence/exp14-candidate/selected-r1/manifest.json),
  [compiler comparison](evidence/exp14-syntax/comparison.json),
  [API/CLI report](evidence/exp14-runtime/README.md).
  Twice-identical ZIP `459feaf9caf2abe55963dce0cac51b8b593e4ff1b46d2eaf9cb7d5c3f13f62a1`,
  76 source targets. API4/CLI48 independently repeated, zero sanitized API groups;
  API raw stderr is UNCOMPARED. Compiler OpenCode/Codex: 11,785 files per artifact,
  7 unchanged rejects, 72→71 diagnostic files; not all-files compile PASS.
- **B**: [baseline protocol](baseline-protocol-plan.md), [fixtures](baseline-media.md),
  [guarded transport](baseline-transport.md), [rehearsal history](baseline-rehearsal.md),
  [application-overlay plan](baseline-privacy-application-plan.md).
  Current [nonce V2](evidence/baseline-rehearsal/privacy/nonce-overlay-v2/primary.json)
  passes bounded USER/negative controls on PHP7.4 with approved privacy overlay,
  **not unchanged published source**. Historical smoke is not Decision7 acceptance.
- **M**: Separate real [media V1](evidence/baseline-rehearsal/privacy/media-overlay-v1/primary.json)
  and [media V2](evidence/baseline-rehearsal/privacy/media-overlay-v2/primary.json).
  Both reach READY, owned list and HTTP source delivery with the pinned short-file
  SHA. V1 then fails final privacy with `Incomplete`; V2 fails
  `PRIVATE_MARKER_LOGGED`, with full KS/prefix counts 3/3. Do not combine them into
  PASS, call delivery unexecuted, or infer candidate PHP8.3 functionality.
- **P**: [provider runtime](provider-runtime.md), [decision draft](provider-decision-draft.md).
  Real signed-container CLI/web GET/POST evidence exists on all three distro
  candidates. Mandatory application SOAP/APC semantics and final origin/ABI/SAPI
  matrix remain unresolved; native EL9 transaction failed missing probe packages.
- **S**: [real PDO SQL composition](return-contracts-sql.md),
  [AWS/cache](exp13-serialization.md), [serialization contracts](serialization-contracts.md),
  [XML](exp13-xml.md), [rank](rank-signature-repair.md), [generator](template-generation.md).
  SQL two cohorts ×91 typed rows independently repeated; XML40 and AWS88 native
  artifact processes independently repeated. Legacy readers reject new O wire;
  rollback compatibility is false. Exp14 XML/AWS are source-join NOT_RERUN.
  Rank omission/reflection is tested, positive rank-body persistence is not.
- **F**: [feasibility](feasibility-status.md), [provider decisions](provider-decision-draft.md),
  [seven-rejection plan](remaining-baseline-syntax-plan.md), [Riak](riak-provider.md).
  Bounded source experiments authorized; final package-integration go/no-go absent.
- **H**: [coverage mapping](coverage-matrix.md), [test board](test-status.md),
  [patch inventory](patch-inventory.md). Three completed detailed support cases
  are retained as such, not credited as original functional tasks.

## All 24 original obligations

Status PARTIAL means useful evidence exists but the full criterion is not met.
WAIT means a specified prerequisite has not passed; it is not N/A.

| Task | Required acceptance criterion | Executed evidence / status | Smallest remaining action, not a waiver |
|---|---|---|---|
| 1.1 | Exact dependency/revision/license/entrypoint/overlay inventory | I — PARTIAL | Classify active launch chains and all component scopes; join source/package owners and resolve exclusions. |
| 1.2 | Frozen published74 API/UI/worker/media baseline plus timings | B,M — PARTIAL/FAIL privacy | Fix observed KS emitter under approved policy; rerun failed privacy on owned media, then full frozen baseline. Label overlay explicitly and apply matching policy to candidate. |
| 1.3 | Exact packaged app/client/installer syntax+static findings all classified | I,A — PARTIAL | Adjudicate 4,711 source-hash-bound report rows/manual blind spots; retain seven rejects and generated/provider obligations. |
| 1.4 | Signed coherent provider/extensions/SAPI on three distros | P — PARTIAL | Resolve application-use SOAP/APC and mandatory module matrix; reconcile each exact package/ABI and worker/web/CLI. |
| 1.5 | Bounded final feasibility and explicit production-integration approval | F — WAIT | Consolidate actual blockers/repair scope and obtain go/no-go; lab permission is not that approval. |
| 1.6 | Minimal differential repairs plus reproducible experimental ZIP/provenance | A,S — closest to closure, PARTIAL | One 76-row selected-source→focused-proof join, described below; no full-AIO requirement added to this task. |
| 1.7 | Explicit per-component upgrade or deferral decisions, attribution/revert | F,I — PARTIAL | Write finite component decision records with old/new pins or explicit deferral; no need to implement optional upgrades just to finish migration. |
| 2.1 | Reviewed core/API repairs with changed-behavior tests and strict application | A,S — PARTIAL | Resolve known integrated behavioral gaps, including cache/callers and current privacy policy; join selected repairs to actual behavior. |
| 2.2 | Worker/CLI/library/generated-client fixes with execution and attribution | I,A,S — PARTIAL | Execute identified active entrypoints/jobs and failure paths; compiler/task-list output is not task-body acceptance. |
| 2.3 | Shared patch transformation in all DEB/RPM builds, drift refusal | A only lab builder — WAIT | After 1.5, integrate common transformation and compare ZIP/all payload identities; exercise deliberate mismatches. |
| 2.4 | Ubuntu dependencies/configuration, resolution and preserving upgrades | P only providers — WAIT | After approval, update both Ubuntu packages and prove CLI/Apache plus config/data preservation. |
| 2.5 | EL9 coherent runtime/FPM/CLI/extensions and old-worker removal | P only providers — WAIT | Select reviewed stream/dependencies, test pools/service policy and replacement of running old workers. |
| 2.6 | Positive exact8.3 CI/module/ABI assertions and negative fixtures | P probe guards not package CI — WAIT | Integrate and test wrong-minor, missing-module/ABI/hash/RPM-string controls after 1.5. |
| 3.1 | Noble fresh install, reprovision, reboot, full sanity/preservation | A isolated corpus, not full AIO — WAIT | Run selected application on isolated full Noble stack, then package-install lifecycle after integration. |
| 3.2 | Same full acceptance on Ubuntu26.04, no provider fallback | P — WAIT | Use verified suite-compatible provider in full lab and repeat lifecycle/runtime matrix. |
| 3.3 | Same Rocky9/FPM acceptance with body/jobs/modules | P,S narrow body/provider — WAIT | Full Rocky application/runtime/lifecycle checks, not a container dependency simulation. |
| 3.4 | API/auth/JSON/eSearch/Admin/KMC across targets, no untriaged failures | A,S,B — PARTIAL | Full application HTTP/trustedTLS auth matrix, search and browser sessions/ACL; resolve observed privacy. |
| 3.5 | Short+1080p60 HTTP/TLS READY/flavors/thumbnails/HLS/Range/Go E2E | B,M — PARTIAL/FAIL privacy | First complete short baseline privacy; then both fixtures/delivery protocols/profile outputs and candidate/distro matrix. |
| 3.6 | Comparable repetitions/errors/performance within reviewed20% boundary | Protocol+fixtures only B — NOT_RUN measurements | Exclusive matched labs, 2 warmups+5 measured rounds,100 calls/round and both uploads; no timing claim from smoke. |
| 4.1 | Synthetic-state74→83 upgrade preserving accounts/secrets/media/jobs | S identifies wire risk — NOT_RUN upgrade | Document cache namespace/invalidation, drain old workers, snapshot and execute full upgrade on lab clones. |
| 4.2 | Failed-cutover matched-state restoration and login/playback | Overlay rollback is not full rollback — NOT_RUN | Rehearse app/runtime/config/DB/media restore after controlled candidate writes; account for discarded writes. |
| 4.3 | Tested migration/provider/rollback docs and fresh support check | F experiment docs — PARTIAL | Derive operator commands from actual lifecycle/recovery runs, validate links and recheck support before RC. |
| 4.4 | All required gates plus release approval/unique packages | No accepted packages or release approval — WAIT | Audit completed matrix and obtain explicit release authorization; no tag/spec sync/archive earlier. |
| 4.5 | One release containing accepted ZIP/manifest/instructions/DEB/RPM/checksums | Local experimental artifacts only — WAIT | After4.4 publish new assets, redownload/verify accepted identities; preserve all prior releases. |

## All 27 detailed cases

| Task / case | Required criterion | Actual bounded evidence / status | Missing case / next step |
|---|---|---|---|
| 5.1 T0-01 | Frozen local suite, actual independent executors | H — COMPLETE,68 distinct tests historical | Keep support scope; do not reclose/count every subsequent harness. |
| 5.2 T0-02 | Immutable source/held/selected/exp2 identity review | H — COMPLETE, historical exp2 audit | Preserve history; current manifest coverage is separate1.6 work. |
| 5.3 T0-03 | Every original task mapped without hidden coverage gaps | H — COMPLETE mapping | This current audit updates visibility, not functional acceptance. |
| 5.4 T0-04 | Whole inventory/attribution/entrypoint/finding classification | I,A — PARTIAL | Semantic classification and original-tree launch chains; exact identities already solved must not be recounted as new coverage. |
| 5.5 T0-05 | Full frozen baseline/resources/fixtures/guards/UI/jobs/media/timings | B,M — PARTIAL/FAIL | Correct observed KS emitter and repeat privacy; full baseline workload/browser/TLS remains. |
| 5.6 T0-06 | Feasibility plus upgrades/deferrals and go/no-go | F,P — WAIT | Finish decisions, then explicit approval; no package integration by inference. |
| 5.7 T1-01 | Every selected repair focused then combined-manifest behavior | A,S — PARTIAL | Build76-row proof join; rerun only uncovered changed behavior/necessary composition, not all old mocks. |
| 5.8 T1-02 | PDO/DB errors and JSON/XML/generated-client typed contracts | A,S — PARTIAL | Extend real configured caller/client contracts beyond named SQL side-effect seams and offline XML lifecycle. |
| 5.9 T1-03 | Legacy serialization, configured caches/restart/invalidation, dates/locales | S — PARTIAL, rollback false | Select/test cache transition policy and real configured cold/warm restart; complete timezone/locale contracts. |
| 5.10 T1-04 | Actual active worker/cron/install/plugin/generated entrypoints | I,A,S — PARTIAL | Derive runnable active rows and test task bodies/jobs/errors; retain unresolved paths. |
| 5.11 T2-01 | HTTP/trustedTLS auth/security/crypto on each target without leaks | A,B,M — PARTIAL/FAIL privacy | Fix KS logging, full-app cross-partner/tamper/expiry/skew/privilege/crypto corpus across SAPIs. |
| 5.12 T2-02 | Real browser Admin/KMC/ACL/eSearch and Go E2E | No complete browser/search report — NOT_RUN aggregate | Start baseline real login/session plus one index/query, then candidate and required matrix. |
| 5.13 T2-03 | XXE/malformed negatives and real Apache/FPM body handling | S,P — PARTIAL | Join lifecycle safety to full HTTP application handlers on both required web topologies; no outside-network access. |
| 5.14 T3-01 | Both frozen fixtures/protocols/distros and delivered profiles/Range | B,M — PARTIAL/FAIL privacy | Complete short case before1080p60, HLS/thumbnail/flavors/206 and trustedTLS; inspect delivered streams. |
| 5.15 T3-02 | Corrupt/empty uploads, worker failure/retry/terminal cleanup | No full negative job matrix — NOT_RUN | Owned synthetic negative fixtures with exact job/flavor terminal expectations; no indefinite retries. |
| 5.16 T4-01 | Mandatory provider/module/SAPI matrix in clean targets | P — PARTIAL | Resolve SOAP/APC/application-use and signed per-package/module identities. |
| 5.17 T4-02 | ZIP/all packages same selected sources plus mismatch rejection | A builder only — WAIT | After feasibility, one shared DEB/RPM patch pipeline and payload join. |
| 5.18 T4-03 | Noble install/reprovision/reboot/preservation/full runtime | Runtime-only lab and synthetic API — WAIT | Full approved migrated package installation/lifecycle acceptance. |
| 5.19 T4-04 | Ubuntu26.04 same lifecycle with correct provider | P fixture — WAIT | Full application lab and package lifecycle, no cross-suite fallback. |
| 5.20 T4-05 | Rocky FPM/CLI/services/security-policy/body/jobs/no old workers | P fixture — WAIT | Full approved Rocky package/lifecycle runtime matrix. |
| 5.21 T4-06 | Package/CI version/module/ABI/hash/string fail-closed fixtures | Runtime probe guards only — WAIT | Integrate fixtures into actual package CI after feasibility. |
| 5.22 T5-01 | Matched labs, warmups/repetitions/API p95/media/dispersion | B protocol only — NOT_RUN measurements | Run without competing host workload after functional/privacy gates; retain INCONCLUSIVE contention. |
| 5.23 T6-01 | Per-target synthetic upgrade and exact state preservation | No full rehearsal — NOT_RUN | Implement approved cache policy and coherent clone upgrade, then full candidate suite. |
| 5.24 T6-02 | Failed cutover after writes, matched restore and baseline service | No full rehearsal — NOT_RUN | Restore coherent snapshot with explicit write-freeze/discard boundary and login/playback proof. |
| 5.25 T6-03 | Verified instructions/links/limitations/security support | F draft documents — PARTIAL | Verify commands against completed labs, not guessed installation steps. |
| 5.26 T6-04 | All gates/independent reviews/critical defects/artifacts/release approval | No final accepted matrix — WAIT | Gate audit after functional/distro/performance/recovery evidence. |
| 5.27 T6-05 | Approved source+packages release/download verification then archive | No migration release — WAIT | Publish only after5.26/4.4; never relabel experimental ZIP. |

## The smallest legitimate task closure: 1.6, not full-AIO acceptance

No currently unchecked task can be marked complete solely from the inspected
aggregate reports. This is not a claim that another huge runtime project must
precede 1.6. Its ZIP identity/reproducibility/original-preservation clauses already
have strong executed evidence. Its remaining audit should be **one finite join**:

1. Use the selected exp14 manifest as denominator: exactly **76 unique paths**,
   **43 pure-curly targets +33 other targets**. Ten source-patch location groups
   occur in that manifest; location alone is not a behavior classification.
2. For each path, record upstream hash, final hash, ordered cumulative patch
   provenance, changed behavior, focused original74/original83/candidate83 case
   identifiers, actual executor/reviewer and explicit intentional differences.
   Candidate74 execution is not required for intentionally PHP8.3-only native
   signatures; original74 is the behavioral reference, with original83 failures
   retained as controls. The rank reflection-default74 difference is intentional
   and must remain visible, not normalized away.
3. Link the exact compiler/token proof for all43 curly files. The dedicated
   behavioral corpus covers three files/204 observations; **40 files are outside
   that dedicated three-file corpus**, NOT a claim that all40 were never loaded
   by subsequent generator/autoload/API tests. Reconcile those later actual
   loaded-source maps before declaring any new missing execution. A pure-token
   substitution proof is useful evidence, not fabricated method execution.
4. Join the33 non-curly targets to existing JSON/reflection/PDO/config/Criteria,
   ternary/autoload/generator, XML, AWS/cache, dispatcher and rank records.
   Cumulative targets need proof of both prior retained edits and added edits;
   paths must match actual loaded after-hashes, not similar filenames or held
   alternatives. Preserve named fixture seams and behavior exceptions.
5. Link combined actual-artifact API4/CLI48, compiler23,570 and exact two-build
   verification. XML/AWS exp14 joins remain NOT_RERUN_SOURCE_JOIN_ONLY; explicitly
   decide the sufficiency of a no-source-change impact review for this bounded
   repair task, never convert it into fresh execution. No new compiler replay
   is necessary just to generate this documentary join.

The deliverable is **76 rows**, not 11,785 new behavioral tests or a fourth
framework. The precise unresolved-row count is not yet computed; do not claim
76/76 focused behavioral acceptance merely because all76 patches apply. Once
this join has no unexplained changed-behavior gaps and independent review accepts
its evidence, **1.6 can close without packages, full AIO, performance or release**.
T1-01/5.7 has the stronger explicit each-repair/combined contract; assess it from
the same rows rather than attaching unrelated release criteria. Rank positive
persistence remains a real broader API obligation, but do not demand execution
of its unchanged full database body solely to prove a seven-byte signature fix.

A second bounded closure opportunity is **1.7**: explicitly defer optional
upgrades component by component with pinned current identities and rationale.
No approved task requires upgrading every library. Deferral is not permission
to leave unknown compatibility/licensing or provider obligations unresolved.

## Critical path and work that actually advances gates

1. **Privacy first, one owned fixture.** Preserve V1/V2 failures and locate the
   actual full-KS emitter; repair narrowly, independently review and replay the
   existing owned short-media flow. Do not upload repeatedly just to accumulate
   successful READY counts. Success must include finite file/journal privacy and
   correct cleanup; it is still published74-with-overlay, not PHP8.3 acceptance.
2. **Full application on Noble candidate.** Reuse the frozen short fixture,
   guarded transport and approved privacy policy on a fresh isolated selected
   PHP8.3 application stack, first auth→upload→worker→READY→delivery. This is the
   highest-value runtime step beyond zero diagnostics in the bounded API corpus.
   Do not silently install migration packages/alter CI before the feasibility
   gate; distinguish a lab experiment from production packaging integration.
3. **Close the finite evidence/decision joins in parallel, locally.** The76-row
   repair join above, active entrypoint/finding classification, provider/APC/SOAP
   and optional-upgrade decisions should yield concrete runnable rows and a
   consolidated go/no-go. The remaining six raw templates and Riak reject keep
   their denominator: complete real generation contracts/provider disposition,
   not arbitrary raw-template deletion or a compiler suppression rule.
4. **Finish functional baseline/candidate coverage before benchmarking.** Real
   browser/search, trustedTLS,1080p60/HLS/Range/flavors/thumbnails and job negative
   cases are still required. Freeze matching privacy policy/resources/config;
   then Decision7 measurements become meaningful. A single untimed READY result
   cannot close performance or transcode-profile preservation.
5. **After explicit feasibility approval:** shared source/package pipeline,
   three distro install/reprovision/reboot suites, upgrade and coherent recovery.
   Resolve AWS old-reader/O-wire incompatibility through an explicit tested
   deployment/cache policy; do not claim mixed-runtime compatibility.
6. **Only then:** release documentation/support recheck, final approval, one
   uniquely versioned ZIP+DEB/RPM release, downloaded verification, spec sync and
   archive. `.20` cutover remains a separate explicit approval.

## Avoid further harness-only churn

- Another broad local unit-test count or independent re-run of unchanged mock
  tests will not close T0-04/T0-05/T0-06 or any full runtime gate. Reuse frozen
  guard suites; add tests only for a reproduced defect/new behavioral boundary.
- Do not clone entire API/CLI/compiler harnesses for a doc/manifest-only change.
  Thin pinned adapters and impact joins are already sufficient patterns.
- Stop repeated one-warning experiments when a cohesive family/whole-source
  corpus exists. New work should cover an unresolved selected behavior, real
  configured subsystem, active entrypoint or deployment/recovery obligation.
- Do not turn this audit into a new prerequisite framework. It reconciles the
  existing51 tasks and prioritizes their original criteria. Three completed
  support cases remain3; full original acceptance remains0/24 until real closure.

## Audit limitations

No live service, external provider support date or release state was queried in
this read-only task. Support dates above are not freshly revalidated claims;
task4.3/5.25 requires that check before an RC. The execution evidence cited is a
snapshot while other agents continue work; later results must be linked as new
phases. No raw log lines, credentials, KS values or hashes of secrets are included.
