# Feasibility gap audit — original 1.1–1.5 and detailed 5.4–5.6

Scope: read-only repo-local planning audit. No VM, network, source change,
production package/CI integration, or task-checkbox edit was performed for
this review. Inputs read: `AGENTS.md`,
`openspec/changes/migrate-kaltura-php83/{proposal,design,tasks}.md`,
`doc/php83/{inventory-ledger,dependency-attribution-followup,feasibility-status,test-status,baseline-protocol-plan}.md`,
plus linked local summaries `coverage-matrix.md`, `patch-inventory.md`,
`package-identities.md`, `candidate-syntax.md`, `compiler-triage.md`,
`provider-runtime.md`. Large scan JSON files were not inspected; identities
below cite their deterministic summary documents only.

Original scope and named gates are preserved. Nothing unknown is marked
complete. No requirement stronger than the approved texts is added. This is
prioritization and evidence mapping, not execution proof and not a release
decision.

Named gates retained: design Decisions 1–9, seven test gates T0–T6,
case/result contract in `design.md` (NOT_RUN / RUNNING / PASS / FAIL /
BLOCKED / INCONCLUSIVE, PARTIAL as aggregate or older limited evidence only,
justified N/A only with named scope rationale and reviewer, mandatory distro
or functional requirements cannot be waived this way), parallel execution and
independent-review rotation in `AGENTS.md` and `design.md`, and tasks 4.4 / 4.5
release and publication boundaries. Passing harness tests do not prove full
application acceptance. A review is not execution evidence.

## Requirement → current authoritative evidence → missing proof

Quoted requirement text is verbatim from `tasks.md`. Evidence column cites
only the authoritative local document that actually records the observation.
Missing-proof column states what the original text still requires before the
parent or detailed case can close. PARTIAL means useful bounded evidence for
its exact tested scope; it never closes full-case acceptance.

### Original 1.1

Requirement:

> 1.1 Extract the checksum-verified pinned Kaltura archive and enumerate
> bundled dependencies, generated clients, packaging overlays and PHP
> entrypoints; verify a reproducible inventory records revisions, licenses
> and active versus historical build paths.

Current authoritative evidence (PARTIAL, case remains open):

- Pinned content identity: original Rigel ZIP SHA-256
  `58d534d09b3b75c9a8333957268c884f79032638b2d44a278b1992fda1b0ab28`,
  verified before/after in `inventory-ledger.md`,
  `dependency-attribution-followup.md`, `package-identities.md`,
  `patch-inventory.md`. Immutable local source-tree check records all files
  in `server-Rigel-18.20.0` matching archive bytes
  (`patch-inventory.md`). This is content identity only.
- Published Noble bundle SHA-256
  `91629580441f6a896ebf9e51f0256532221715bee57a3e5a64c66ff0c4e3127b`
  with 17 embedded DEB hashes verified as stream reads, no hook execution
  (`patch-inventory.md`).
- Deterministic accounting join of raw and packaged static rows plus syntax
  records, without claiming distinct defects (`inventory-ledger.md`). Zero
  semantic findings resolved by that join.
- Exact packaged payload identities: all ledger packaged-file hash gaps
  closed through verified DEB payload bytes, known hashes preserved, two
  changed upstream files identified by before/after identity
  (`package-identities.md`). Explicitly not semantic classification,
  attribution, or T0-04 completion.
- Bounded vendor metadata delta for the 20 historical vendor directories:
  scoped version declarations and partial license notices recorded per
  directory with excerpts and manifests; zero directories claimed completely
  attributed (`dependency-attribution-followup.md`).
- Historical source-to-package map: 11,782 byte-identical upstream files,
  two overlay-changed files, 1,670 additional packaged PHP files grouped by
  path (`feasibility-status.md`, `package-identities.md`).

Missing proof for 1.1 full acceptance:

- Upstream revision-to-byte closure: comparison of the pinned server commit
  named in `design.md` (`29cf45469c1e210498087942f5b76b5c706e4cda` via
  `build/sources.rc` and `noble-deb-build`) against the mirrored archive
  bytes, including local modifications. See upstream-revision section below.
- Complete component version and license attribution: transitive scopes,
  nested vendors, fonts, AWS dependencies, metadata-only Avro entries,
  MaxMind Db, Akamai, mantis wrapper, phpGangsta variant, Symfony and
  symfony-data rights, Webex provenance, Propel/tFPDF LGPL version
  resolution, and the 1,670 package-only overlays
  (`dependency-attribution-followup.md`, `inventory-ledger.md`).
- Active versus historical build-path classification: `design.md` warns that
  `build/sources.rc` retains legacy PHP 5.3/7.0 recipes; mechanical string
  replacement is forbidden. No accepted active/historical ledger exists.
- Generated clients, web/CLI/cron/install/plugin entrypoints, executable
  reachability, and PHP embedded outside the selected suffix scope
  (extensionless/shebang launchers, shell/Python launchers, generated
  runtime files, active configuration). `package-identities.md` scope
  section explicitly lists these as separate work.
- Analyzer pins with checksums/lockfile and manual blind spots recorded per
  `design.md` phase-1 boundary; whole-tree rerun joined to identities.

### Original 1.2

Requirement:

> 1.2 Reproduce the PHP 7.4 baseline from checksum-verified published
> packages in a fresh isolated lab, never `.20`; freeze the design's
> VM/fixture/API/repetition protocol first, enforce target/DNS/redirect
> guards, and use synthetic data only; verify API/UI/upload/worker/playback
> checks and save sanitized runtime, extension and timing reports.

Current authoritative evidence (PARTIAL, case remains open):

- Isolated `.74` baseline provisioned from published 7.4 artifacts with
  matching box/CPU/RAM settings, no production data or host shared folders,
  and bootstrap-time `.20` blocking (`feasibility-status.md`).
- Historical HTTP smoke: zero failures across services, searchd, API ping,
  Admin Console/KMC HTTP responses, admin session, synthetic partner
  creation, upload-to-READY, HLS manifest and segment retrieval
  (`feasibility-status.md`, `evidence/noble-baseline/`). Explicitly not
  browser interaction, final benchmark, TLS, or rollback acceptance.
- Draft protocol plan only: `baseline-protocol-plan.md` is marked
  PLAN, NOT_EXECUTED. It records reuse boundaries, guard gaps in the legacy
  sanity script, and a proposed freeze manifest. It claims no measured
  baseline.
- Supporting local-only assets: independently validated synthetic fixtures
  exist as files but carry no application upload/delivery claim
  (`test-status.md` references `baseline-media.md`); transport guards have
  local tests but no API POST/workload integration
  (`test-status.md` references `baseline-transport.md`).

Missing proof for 1.2 full acceptance:

- Frozen manifest before timing: case/run IDs, published 7.4 release and
  installer SHAs, installed `dpkg` inventory, source-to-package and
  overlay hashes, VM UUID/box/checksum/disk/controller/cache/filesystem,
  host CPU/hypervisor/load, PHP CLI/web binaries/modules/INI/Apache/FPM,
  OPcache/JIT/timezone/locale, ffmpeg/ffprobe/worker/DB/cache/search
  versions, synthetic partner/user/permission IDs, seeded media entry,
  conversion profiles, queue/worker concurrency, literal target/port/CA
  allowlist, encoder commands and actual fixture hashes, request sequence,
  cache-state policy, sample/statistic definitions, warmup/round counts,
  timeout/retry/size policy, cleanup IDs (`baseline-protocol-plan.md`).
- Guarded-target protocol wired into the real client: literal-IP allowlist,
  per-hop redirect/DNS validation, private-CA context, nested
  manifest/segment URL re-entry. Legacy sanity script must not be invoked
  bare or unmodified; its protected `.20` default and `curl -L` behavior
  without per-hop validation are retained warnings
  (`inventory-ledger.md`, `baseline-protocol-plan.md`,
  `package-identities.md`).
- Full API/UI/worker/media smoke with runtime/extension reports: real
  browser login/session/ACL, trusted HTTPS, short deterministic MP4 and
  Full HD fixture upload-to-READY with flavors/thumbnails/HLS/progressive
  Range and stream-property inspection, worker processing, eSearch where
  applicable. Historical `.74` HTTP smoke does not satisfy this.
- Repeated timings per Decision 7: same pinned OS box, 4 vCPU, 8 GiB RAM,
  matching disk/controller, identical fixture bytes, two warmups plus at
  least five measured rounds, each with 100 sequential authenticated API
  calls recorded separately plus upload-to-READY per fixture, median and
  nearest-rank p95, transcode wall time, sample counts, dispersion,
  environment details. No timing collection before protocol freeze.

### Original 1.3

Requirement:

> 1.3 Run PHP 8.3 syntax checks and a PHP-8.3-capable pinned
> PHPCompatibility/PHPCS analyzer with testVersion=7.4-8.3 against the
> exact packaged application, clients and installer PHP; verify every
> reported finding is classified with a source location and evidence,
> including manual checks the analyzer cannot cover.

Current authoritative evidence (PARTIAL, case remains open):

- Whole-source compiler evidence on the exact packaged scope:
  original 58 rejected files versus exp9 54 rejected files across 11,784
  files each, zero incomplete rows, no new rejections in that paired run
  (`candidate-syntax.md`). Later bounded checkpoints reduce rejections
  further (exp10, exp11, exp12) but retain residual rejections and accepted
  files with diagnostics; compiler success never closes runtime or release
  gates (`test-status.md`, `tasks.md` detailed-case notes).
- Source-supported classification for the 54-file exp9 cohort: 47 new 8.3
  language failures and seven retained baseline rejections, with exact
  source/history/package identity joins, six template sources distinguished
  from removed failures, and no row waived (`compiler-triage.md`).
- Historical static candidates: raw 1,256 errors and 645 warnings;
  packaged 2,025 errors and 785 warnings; joined ledger of overlapping
  report rows explicitly not distinct defects and all rows unverified
  (`feasibility-status.md`, `inventory-ledger.md`).
- Analyzer identity cited in history: PHPCompatibility 10.0.0-alpha2 /
  PHPCS 4.0.4 with `testVersion=7.4-8.3` (`feasibility-status.md`).
  `design.md` still requires pins with checksums/lockfile, coverage check,
  and separation of syntax versus E_ALL runtime probes.

Missing proof for 1.3 full acceptance:

- Classification of every reported finding with source location and
  evidence, including the full static rows beyond the compiler-classified
  cohort, and manual checks the analyzer cannot cover. The ledger and
  triage documents state this explicitly.
- Exact packaged application, clients, and installer PHP coverage:
  generated clients, packaging overlays, installer PHP, and active
  entrypoint mapping to findings. Static counts must not be presented as
  confirmed incident counts (`design.md`, `coverage-matrix.md`).
- Pinned analyzer provenance with checksums/lockfile and PHP 8.3 coverage
  evidence, run with `testVersion=7.4-8.3`, with syntax checks and E_ALL
  runtime probes recorded as separate evidence (`design.md` phase-1
  boundary).
- Reachability adjudication: compiler/static location alone does not prove
  reachability or inactivity. Unexercised code is not automatically
  inactive; graph or runtime reachability must be evidenced per finding
  before any inactive-path exclusion (`coverage-matrix.md`,
  `candidate-syntax.md`).

### Original 1.4

Requirement:

> 1.4 Produce the three-distro provider/extension/SAPI matrix (native Noble
> pinned origins; EL9 AppStream versus Remi evaluation); verify signed
> suite-compatible PHP 8.3 package resolution and loaded modules in clean
> test environments, without mixing unsupported distro packages or
> extension ABIs.

Current authoritative evidence (PARTIAL, case remains open):

- Real CLI plus Apache/FPM HTTP GET/POST/invalid-POST probes in disposable
  containers: Noble native 8.3.6, Resolute Sury 8.3.35, Rocky Remi 8.3.35
  each pass the bounded fixture; Rocky native AppStream alone fails to
  resolve the requested memcache/ssh2 set (`provider-runtime.md`).
- Noble candidate runtime/modules and package origins verified for the
  initial lab scope (`tasks.md` partial-evidence note,
  `feasibility-status.md`).
- Bounded APC/APCu probes: original CLI cache initialization disabled on
  both runtimes; fixture-only alias experiment fails missing-counter
  semantics on both; real Apache rows under explicit minimal INI pass
  bounded persistence/version/delete/replacement checks. No adapter
  selected (`tasks.md`, `test-status.md`).
- Explicit blockers retained: legacy RPM `php-pecl-apc` capability has no
  provider in the tested Remi set; APCu is not equated with APC;
  full extension/ABI/provider policy reconciliation open
  (`provider-runtime.md`).

Missing proof for 1.4 full acceptance:

- Final coherent provider selection in a reviewed manifest: one provider
  per distro, with signed suite-compatible origins, pinned package
  constraints, and documented update policy (`design.md` Decision 4). Neither
  EL9 candidate is a tested result yet per that decision; Sury `resolute`
  and Remi 8.3 are probed candidates, not selections.
- Mandatory extension/SAPI matrix reconciled by use and ABI: MySQL/PDO,
  XML/XSL, curl, mbstring, GD, GMP, LDAP, zip/intl, APCu/memcache/SSH2,
  process support, varying by distro; memcache versus memcached and APC
  versus APCu are not interchangeable by name (`design.md`). Loaded INI
  paths and extensions verified independently for CLI and web, worker
  interpreter paths, OPcache, timeouts, permissions, restarts.
- Ubuntu 26.04 native/suite-compatible resolution: inability to resolve
  native 8.3 plus every mandatory extension is a blocker, not permission
  to mix cross-suite packages or silently select another minor
  (`design.md`).
- Clean-environment verification without unsupported mixing, frozen exact
  versions and repository origins in the test report, with reviewed
  security updates within 8.3 allowed (`design.md`).
- No production package/CI change before task 1.5 approval. Provider
  resolution in disposable environments is authorized; integration is not
  (`design.md`, `tasks.md`).

### Original 1.5

Requirement:

> 1.5 Write a go/no-go feasibility report with bounded repairs, upstream
> references and blockers; verify operator approval before production
> runtime/package integration (lab-only source experiments in 1.6 are
> already authorized), stopping for a revised proposal if a
> framework/Kaltura upgrade is needed.

Current authoritative evidence (no decision record; gate remains open):

- `feasibility-status.md` is explicitly partial evidence, not a
  compatibility or migration approval. `coverage-matrix.md` records final
  approved report as NONE.
- Bounded repair batches exist as lab experiments only (exp2 through exp12
  lineage, held patches with selected/rejected/deferred dispositions in
  `patch-inventory.md` and per-experiment documents). No integrated
  reviewed candidate is accepted as the feasibility selection.
- Provider, baseline, static, and runtime gaps above are the blocker inputs;
  they are not yet consolidated into a bounded go/no-go with upstream
  references.

Missing proof for 1.5 full acceptance:

- Consolidated go/no-go report: bounded repairs with upstream references,
  provider matrix outcome, blockers, unsupported-dependency repair plan if
  any, scope exclusions with named rationale, and explicit stop condition
  if a framework or Kaltura upgrade is required (`proposal.md`,
  `design.md` Decisions 2 and 8).
- Explicit operator approval before production runtime/package integration.
  Lab-only source experiments under 1.6 are already authorized; that
  authorization does not satisfy 1.5 and does not approve package/CI
  changes (`tasks.md` 1.5 parenthetical, `design.md` migration plan).

### Detailed 5.4 (T0-04)

Requirement:

> 5.4 T0-04 — Inventory dependencies/licenses, active packaging overlays,
> generated clients, web/CLI/cron/install/plugin entrypoints and
> syntax/static findings; verify exact identities, analyzer pins and
> classification of every finding, with uncovered paths listed (parents
> 1.1, 1.3).

Current authoritative evidence (PARTIAL, case remains open):

- Same ledger, package-identity, attribution-delta, paired-syntax, and
  compiler-triage evidence as 1.1/1.3 above. Hash-identity subcase is
  closed in the sense that missing packaged hashes are resolved; semantic,
  license, entrypoint, and full-finding classification obligations are not
  (`package-identities.md`, `inventory-ledger.md`, `compiler-triage.md`).
- Held repair batches (curly offsets, ternary, autoload) with token/byte/
  compile/behavior proofs remain held, not selected into the accepted
  lineage except where explicitly integrated in a named experiment
  (`tasks.md` notes, `test-status.md`). Riak alias-only patch is a recorded
  negative finding, not a selection (`tasks.md`).
- Task-to-case mapping and uncovered-path accounting exist via
  `coverage-matrix.md`, but uncovered scope stays visible by design.

Missing proof for 5.4: same as the missing items under 1.1 and 1.3,
plus explicit uncovered-path list maintained alongside the denominator,
with no shrinking of the denominator to conceal unknowns (`design.md`
evidence contract).

### Detailed 5.5 (T0-05)

Requirement:

> 5.5 T0-05 — Freeze the full published-7.4 synthetic baseline, VM
> resources, fixture hashes, expected outputs and guarded target protocol;
> verify API/UI/worker/media smoke evidence, runtime/extension reports and
> baseline timings using Decision 7, including rejected targets/redirects
> (parent 1.2).

Current authoritative evidence (PLAN plus PARTIAL smoke; case remains open):

- `baseline-protocol-plan.md` draft with freeze-manifest checklist,
  fixture/timeout/statistic proposals, recovery/boundary notes, and
  independent planning review. Not a frozen executable protocol and not
  execution evidence.
- Historical `.74` HTTP smoke and runtime/module reports as partial smoke
  only (`feasibility-status.md`).
- Local guard tests and synthetic fixture/transport groundwork that do not
  yet constitute the frozen workload (`baseline-protocol-plan.md`,
  `test-status.md`).

Missing proof for 5.5: identical to 1.2 missing items, with emphasis on
frozen expected outputs, rejected-target/redirect rows, full applicable
baseline API/UI/worker/media/TLS rows, resource/timing reports,
independent repetition, and documented gaps. Local tests alone do not close
1.2/5.5 (`baseline-protocol-plan.md`).

### Detailed 5.6 (T0-06)

Requirement:

> 5.6 T0-06 — Produce the feasibility and optional dependency decision
> records; verify each proposed upgrade has old/new pins, attribution,
> regression/revert evidence or explicit deferral, and obtain go/no-go
> before production packaging integration (parents 1.5, 1.7).

Current authoritative evidence (no decision record; case remains open):

- `coverage-matrix.md` records final per-component decision report as NONE.
- No component upgrade inferred or selected from compatibility fixes
  (`tasks.md`, `test-status.md`). Dependency evaluation remains a separate
  change with exact old/new versions, upstream support, license evidence,
  compatibility impact, focused tests, and revert path per `design.md`
  Decision 8.

Missing proof for 5.6: per-component old/new pins, support/license
evidence, expected benefit, regression/revert tests, explicit
selection-or-deferral decision for each candidate, plus the 1.5 go/no-go
and its operator approval before any production packaging integration.

## Full-case acceptance versus useful partial

Full-case acceptance requires the entire original acceptance text for the
parent, with all applicable distro/SAPI/transport/fixture rows executed and
independently reviewed per the evidence contract. Closing a detailed case
does not automatically close its parent (`tasks.md`). Syntax validation of
the plan, harness support passes, bounded SQL/HTTP matrices, paired
compiler scans, diagnostic triage, and fixture-level probes are useful
partial evidence for their exact scope only. They must retain their
identities, remain rerunnable after any source/harness/runtime/config
change, and never silently transfer PASS to a new candidate (`design.md`).

What is genuinely useful without closing gates:

- Paired whole-source compiler scans and source-supported triage focus
  repair selection and prevent silent exclusion of vendor or template paths.
- Bounded synthetic SQL/Apache HTTP plus trusted-HTTPS matrices preserve
  contract parity signals across experiments while diagnostics remain open.
- Disposable provider probes and APC/APCu narrow probes prevent premature
  provider selection or adapter claims.
- Deterministic ledger and payload-identity joins give later adjudication
  exact file keys instead of path-inferred assertions.
- The draft baseline protocol bounds the next freeze instead of allowing
  ad hoc timing collection.

## Actual must-blockers versus optional extra assurance

Must-blockers are those the approved texts name as blocking. They include:

- Upstream revision and inventory closure for 1.1: without byte-level
  revision and overlay/entrypoint attribution, patch applicability and
  support/license review have no anchor.
- Frozen baseline identity and guarded-target protocol before any timing
  comparison; more than 20 percent regression handling, INCONCLUSIVE on
  shared-host contention or unstable runs, and triage of all
  exercised-path warnings without blanket suppression (Decision 7).
- Signed suite-compatible provider with coherent extension/SAPI coverage
  on each target; missing providers are BLOCKED, not N/A (T4 gate).
- Reachable compiler/static failures adjudicated and repaired with
  focused before/after behavior on 7.4 and 8.3; expected original-8.3
  failures are controls, not candidate successes (T1 gate).
- Real HTTP plus trusted HTTPS auth/contracts, cross-partner denials, KS
  failures, real cache backends, eSearch, Admin Console/KMC and Go console
  behavior; mocks and isolated parser tests cannot substitute (T2 gate).
- Frozen fixtures with upload-to-READY, flavors/thumbnails, HLS segments,
  progressive properties/Range, corrupt/empty handling, worker
  failure/retry with terminal states (T3 gate).
- Upgrade, matched-state rollback, double-build ZIP reproducibility,
  downloaded-asset verification, and operator release approval before any
  publication; `.20` cutover has a separate approval boundary (T6 gate).
- Production package/CI integration only after 1.5/5.6 approval.

Optional extra assurance is anything beyond the approved text that would
increase confidence but cannot substitute for the above and cannot be
demanded as a new gate. Examples: repetitions beyond the frozen Decision 7
minimum once stability is demonstrated, additional locale or timezone
slices beyond the selected set, extended fuzz beyond the named negative
fixtures, or broader performance exploration beyond the frozen workload.
Record such work as additional evidence with its own identities; do not
present it as closing a parent, and do not invent new mandatory thresholds.

## Upstream-revision representation

The unresolved upstream revision should be represented as pinned content
identity plus unknown upstream revision mapping, as an inventory claim
only. It must not be represented as resolved revision attribution.

Reason, grounded in the approved texts rather than any legal judgment:

- Task 1.1 explicitly requires the reproducible inventory to record
  revisions, not merely archive hashes. `design.md` provenance evidence
  names `build/sources.rc`, `build/package_kaltura_core.sh`,
  `deb/kaltura-base/debian/rules`, the mirrored archive with SHA-256, and
  the main `noble-deb-build` pin to server commit
  `29cf45469c1e210498087942f5b76b5c706e4cda`, and directs the audit to the
  extracted exact tree plus packaging overlays and generated clients, not
  arbitrary upstream HEAD.
- Content identity (pinned ZIP SHA plus per-file hashes, now extended to
  packaged payload bytes) proves which bytes were audited. It does not
  prove which upstream commit those bytes correspond to, whether local or
  packaging modifications are present, or which upstream reference a patch
  or license notice should be attributed to.
- Byte closure is therefore required by the original task: a
  commit-to-byte comparison that either matches the pinned commit or
  records the exact delta, so later patch applicability checks, overlay
  accounting, and per-component support references have a verifiable base.
  Until that comparison exists, the correct ledger state is exact content
  identity with upstream mapping marked unknown, with no redistribution or
  compatibility conclusion drawn from it.
- No legal approval is offered here. License texts recorded in
  `dependency-attribution-followup.md` are scoped file evidence for later
  review, not compliance decisions or release gates.

## Three next executable bundles that best move go/no-go

No bundle mutates production packages, CI, release artifacts, `.20`, or
published 7.4 releases. All preserve independent review and frozen-input
reruns. Ownership follows `AGENTS.md`: use the actual Claude, Cursor, and
OpenCode CLIs with rotating reviewers; record BLOCKED or NOT_EXECUTED on
tool failure rather than counting it as a pass; keep Grok deprioritized as
directed and do not require a Grok retry to proceed. Parallel bundles must
use separate disposable clones and exclusive VM/DB/worktree owners; never
run competing writers, destructive fixtures, or benchmark workloads against
the same target.

Bundle A — T0-04 inventory closure path (local-only, no VM):

- Join exact package/file identities to dependency/version/license rows
  and to active entrypoint evidence, starting with compiler-rejected files
  over repeated single-warning fixes. Extend literal-target and manifest
  validation tests, analyzer-pin provenance, and the uncovered-path list
  without inventing classifications.
- Why it moves go/no-go: it turns hash closure into adjudicable units and
  exposes the true blocker set for the feasibility report.
- Parallel ownership: one CLI owns ledger/entrypoint join, another
  independently rebuilds and reviews identical bytes. No shared mutable
  state.

Bundle B — T0-05 frozen baseline without timing first (exclusive baseline
owner):

- Attest the existing published-7.4 lab against recorded post-bootstrap
  identities, restore and verify guards, install lab-only trusted TLS
  identity, seed scoped synthetic data, and run one untimed guarded
  HTTP/HTTPS API/media/browser smoke with cleanup verification. Freeze the
  manifest, fixture bytes/hashes, expected outputs, and Decision 7
  workload before any measured round. Obtain coordinator approval for a
  fresh isolated published-7.4 clone if drift or contamination cannot be
  excluded, rather than silently reprovisioning shared research state.
- Why it moves go/no-go: without a frozen comparable baseline, later
  candidate timings and contract comparisons have no anchor, and T5/T6
  cannot be evaluated.
- Parallel ownership: baseline VM has a single exclusive owner; Bundle A
  and Bundle C run in disposable local or container scope concurrently.
  No candidate timing runs during baseline rehearsal.

Bundle C — provider/ABI and decision-record skeleton (disposable scope,
no integration):

- Reconcile final mandatory-extension use and ABI requirements against the
  three probed stacks, resolve the legacy APC capability versus APCu API
  question as investigation only, record provider support/update policy
  evidence, and draft the T0-06 decision-record structure with
  selected/rejected/deferred dispositions and per-component old/new pin
  placeholders left explicitly empty until evidence exists.
- Why it moves go/no-go: it forces the provider and dependency decisions
  into reviewable form and prevents silent fallback, cross-suite mixing,
  or minor-version substitution.
- Parallel ownership: disposable containers only, one owner per target,
  independent rerun by a different CLI. No package/CI file change, no
  release step, no `.20` contact.

After these three, the remaining path is the consolidated 1.5/5.6 go/no-go
with upstream references and blockers, then — only after explicit approval
— production packaging integration, full distro acceptance, performance
comparison, and upgrade/recovery rehearsal under T1–T6.
