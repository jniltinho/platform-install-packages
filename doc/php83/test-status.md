# PHP 8.3 test status

Snapshot: 2026-09-26, migration branch. This is a scoped evidence board, not a
release estimate. [Detailed plan](../../openspec/changes/migrate-kaltura-php83/tasks.md)
and [execution contract](../../openspec/changes/migrate-kaltura-php83/design.md).

## Counts and boundaries

- Original acceptance obligations: **0 of 24 complete**.
- Detailed cases: **3 of 27 complete; 24 remain open**. Several open cases now
  contain actual partial lab evidence; they must not be called wholly NOT_RUN or
  fully accepted. Consult each case's scoped evidence in the detailed task list.
- T0-01: **68 distinct local Python tests passed**, independently executed by
  Claude and Grok, with a Codex cross-check. Do not sum repeated runs into 204
  distinct tests. These include mocks and do not establish PHP runtime acceptance.
- The initial T0 batch below was local-only. Subsequent bounded application tests
  ran in the isolated labs; no production/package/release acceptance follows.
  No release ETA or application completion percentage is inferred.

## Renewed operator authorization — current work in progress

The operator subsequently confirmed both previously requested items explicitly
("Autorizar 1,2"): read-only checksum verification and the narrow logging/privacy
correction. The source-stage privacy repair in `privacy/trace-policy-v1` now has primary
and actual OpenCode independent native results (`5e45a074`): four PHP processes
and 52 lints per run, with identical raw channels and typed reports. All 23 local
guard tests pass. This is not an installed-application result. Published
artifacts and production remain unchanged.

A new OpenCode checksum-verification attempt under that authorization again
received a permission rejection before staging/native execution (`bb710cf5`).
It is retained separately from the historical denial. Read-only diagnosis found
OpenCode 1.18.32 with no global permission overrides; its
[documented external-path approval default](https://dev.opencode.ai/docs/permissions/)
suggests a noninteractive approval boundary. No permission was
changed and no rejected read was retried by another executor. A separate request
for temporary CLI permission was subsequently approved: the operator explicitly
authorized OpenCode permissions needed for the laboratory tests. The new isolated
compiler attempt completed on `.83` with actual OpenCode and a Codex repeat
(`23d52765`); the historical denials remain intact. No global permission
change, production access or release acceptance follows from this authorization.

## Current built candidate: exp14 — API/CLI and bounded compiler repeated

[exp14](exp14-candidate.md), committed in `0c152ce1`, was built by Codex and
independently rebuilt by actual Claude with identical ZIP bytes:
`459feaf9caf2abe55963dce0cac51b8b593e4ff1b46d2eaf9cb7d5c3f13f62a1`
(91,210,691 bytes). It preserves all75 exp13 results and adds one rank-signature
repair:76 targets total, one seven-byte source delta,11,785 PHP-family files.
The original and prior archives remain unchanged. The source-stage
[signature proof](rank-signature-repair.md) preserves effective omission behavior
and PHP8.3 metadata, but records a PHP7.4 reflection-default difference explicitly;
positive rank-body execution and persistence remain unverified.

[Actual-artifact API/CLI evidence](evidence/exp14-runtime/README.md) has Codex
primary and actual OpenCode independent repetitions (`bd39e7bf`). Claude's session-limit
failure is preserved as NOT_EXECUTED, not credited with this runtime repeat.
Four API modes retain the bounded logical contract: exp13 has one sanitized
diagnostic group/event, exp14 has **zero sanitized groups/events**. This is not
an unrestricted raw-log or full-application claim. Raw API stderr remains
**UNCOMPARED**. CLI48 has44 successful processes and four original fatal controls,
with exact repeated stdout/stderr. Source/runtime checks and owned DB cleanup
are retained. XML/AWS on exp14 are **NOT_RERUN_SOURCE_JOIN_ONLY**; their unchanged
source identities do not become fresh runtime passes.

[Whole-artifact compiler](exp14-syntax.md) now has actual OpenCode primary and
Codex independent repetition (`23d52765`): 23,570 rows per run, 11,785 files per
artifact. Both retain 11,778 accepted and seven rejected files; zero incomplete
rows. Diagnostic files decrease 72→71, only the rank declaration warning.
The strict comparison preserves raw channels, source/harness/runtime identities
and diagnostics, excluding only per-row duration. The seven historical rejects
remain open: **not all candidate files compile**, and full application acceptance
is still false. Earlier quota and permission failures remain historical evidence;
the renewed user authorization enabled this separate successful attempt. `.83`
is released with no pending compiler process.

The [real logging-pipeline observation](evidence/baseline-rehearsal/privacy/pipeline/README.md)
was independently repeated by actual Claude (`8f6d39a0`). Throwable reaches the
writer/formatter in the applicable cases, but intrinsic messages, extras.message
and pre-rendered strings remain separate exposure paths. Expected synthetic leaks
and six ZendConfig diagnostics remain visible. That observation alone did not authorize a logging fix or valid USER rehearsal.
The subsequent operator approval and source-stage repair supersede the historical
pending policy decision, but installed-route checks are still required before
valid USER authentication/upload. Full application, provider,
performance, recovery and release gates are unchanged.

The final API/CLI checkpoint and the two outstanding operator decisions were
sent by verified-TLS SMTP on 2026-09-26 at18:40:18 America/Sao_Paulo. SMTP
accepted the message; inbox delivery is not confirmed. Both lab slots are
released and no fixture process is pending at this checkpoint. The task board
remains3/51: these bounded improvements do not close full acceptance obligations.

## Approved privacy correction — source proof, installed acceptance pending

[Trace-policy evidence](evidence/baseline-rehearsal/privacy/trace-policy-v1/README.md)
preserves an initially failed host validator and its narrowly reviewed correction;
no failed result was overwritten. The patch masks exception argument values while
retaining structural information and Throwable identity. Intrinsic-message,
pre-rendered-string and extras.message controls still leak by design: this is not
a universal sanitizer. The repeat has an additional 55-file/library/INI identity
snapshot, not a retroactive claim about the primary interval.

The append-window scanner now passes 23 tests and independent review, including
the previously failing truncate-after-growth and processing-deadline cases
(`6f9c20bc`). Installed read-only auditing and the application/rollback recipe
are committed in `14265040`: six audit tests and 14 recipe tests pass, with an
independent 14-test/frozen-source review. The reviewed recipe includes post-start
and rollback source/configuration checks. Controlled application is now assigned
exclusively to `.74`, separately from the `.83` compiler run. No installed overlay
or new valid USER/upload acceptance is claimed until execution evidence arrives.
Any subsequent overlay must be labelled a modified lab baseline, not unchanged
published packages; benchmark acceptance remains separate.

A status email about the independently repeated privacy probe was accepted over
verified-TLS SMTP at 20:20:25 America/Sao_Paulo on 2026-09-26. Inbox delivery was
not confirmed. The detailed task count remains **3/51**.

## Prior candidate: exp13 — compiler and bounded runtime repeated

[exp13](exp13-candidate.md) was built by Codex and independently rebuilt by actual
Claude (`4c5e058f`), producing identical91,210,445-byte ZIPs with SHA256
`6d0bc4947207e6c5457b7843948d263aa8d5f251480e58cbf9086c0add79a944`.
The original and exp12 archives are unchanged. All75 targets are verified;
62 prior results remain identical, and the exp12→13 delta is12 modified files
plus one added XML helper. Privacy patches remain excluded. [Whole-artifact compiler validation](exp13-syntax.md) now has primary and actual
Claude repetition (`4eee520f`):11,785 files,11,778 accepted, the same seven
historical rejects, zero incomplete rows. Diagnostic files decrease73→72, solely
removing KalturaAPIException::__wakeup's warning. Raw channels and source/runtime
identities agree. [API/CLI artifact evidence](evidence/exp13-runtime/README.md)
now includes primary and actual Claude repetitions (`030c2831`): four API modes,
48 CLI rows (44 successful and four original fatal controls),20 typed contract
comparisons. API diagnostics decrease **17 groups/371 events →1 group/1 event**;
CLI raw channels agree. Raw API stderr is explicitly **UNCOMPARED**, not assumed
equal or known to differ only by temporary paths. Source-stage results are not
relabelled as fresh artifact execution. There is no accepted release.

This build milestone was accepted by verified-TLS SMTP on2026-09-26 at17:39:06
America/Sao_Paulo; inbox delivery is not confirmed.

[Actual-artifact XML contracts](exp13-xml.md) now have40 primary processes and40
actual Claude repetitions (`b4360935`), with identical complete reports and four
matching runtime snapshots. Source files, including the added helper, come from
the verified ZIP. Expected rejection/SoapFault controls remain explicit; this is
not full web-SAPI, application or release acceptance. XML status email was
accepted by verified-TLS SMTP at17:52:50 America/Sao_Paulo; inbox unconfirmed.

[Actual-artifact credentials/cache](exp13-serialization.md) adds88 native83
processes and88 actual Claude repetitions (`56edfd53`), with complete reports,
source identities and four runtime snapshots identical. The46 historical R3
observations used for analysis are explicitly NOT_RERUN, not additional native
passes. Old readers still reject candidate O-format records; application and
rollback acceptance remain false. The API/cache milestone email was accepted
by verified-TLS SMTP at18:05:37 America/Sao_Paulo; inbox delivery unconfirmed.

Independent review found a comparator-only gap in API ledger validation when an
output hash is null. Actual retained reports have the expected hashes/paths;
the narrow validator correction (`e213aaed`) now passes16 tests and independent
Codex review, reproduces the original bypass rejection and reconciles unchanged
native reports. No native replay or changed acceptance scope follows. Full AIO, privacy, distro/provider,
performance and recovery gates remain open.

## Historical checkpoint and baseline preparation: exp12

[exp12](exp12-candidate.md) was built twice with identical SHA256
`de5e61a1b54f472e605ef2e87669302a3915616fd85378e0f05706fcb06a7e8b`.
It has65 source targets:62 exp11 entries preserved, one cumulative Criteria
replacement and two generator helper additions. Exactly three application files
differ from exp11. Source-stage Criteria/generator behavior was independently
repeated; these results do **not** transfer automatically to the new ZIP.
[Paired whole-artifact compilation](exp12-syntax.md) now has primary and actual
Claude repetition:7→7 residual rejects, no outcome/diagnostic drift and no
incomplete files. [Actual-artifact runtime evidence](evidence/exp12-runtime/README.md)
now also has primary and actual Claude repetitions, reconciled by the strict
comparator and independent Cursor review. API diagnostics decreased from
**18 groups / 503 events to 17 groups / 371 events**: exactly the 132-event
Criteria marker group disappeared; other groups remain visible. This is bounded
synthetic SQL/Apache HTTP/trusted-HTTPS evidence, not complete AIO acceptance.

The checkpoint includes 48 CLI rows (44 successful processes and 4 expected
original83 failures), 20 typed baseline comparisons, 68 curly-offset class cases,
17 additional repair processes, 72 generator rows and 4 Criteria processes.
The initial loaded-source metadata mismatch and interrupted independent generator
attempt remain preserved; narrow hash-bound revalidation and a completed fresh
repeat are separately identified. Both runtime identities remained unchanged.
The historical exp11 checkpoint below is retained, not the current candidate.

[Criteria](criteria-marker.md) preserves same-runtime state in its bounded corpus,
but three pre-existing74/83 subclass serialization-order differences remain a
strict layout FAIL; no cache/backend/invalidation acceptance is claimed.
[XML policies](xml-loader.md) reject a no-op security-call removal: enabled/default
read local canaries, while legacy block and denying callback do not in the corpus.
The [held XML lifecycle repair](xml-lifecycle-fix.md) now has independently
repeated 38-process observations, a two-process causal follow-up and a reviewed
bounded contract; old expectation failures remain visible. The separately
versioned [ZIP builder v2](zip-builder-v2.md) supports the new helper with 24
independently executed synthetic tests. Neither is integrated into exp12 or an
approved production release.

[Source media](baseline-media.md) now includes independently validated10s360p25
and60s1080p60 H.264/AAC fixtures; no application upload/delivery claim follows.
[Deadline transport](baseline-transport.md) has19 independently executed local
tests including real synthetic TLS and cleanup. [API protocol](baseline-api.md)
has 36 independently executed local tests. The subsequent untimed baseline
rehearsal reached the actual PHP7.4 Apache provider and wrong-secret rejection,
but stopped before valid authentication or upload: its synthetic invalid secret
was found in two DEBUG log emissions. No real USER secret was sent by that run.
The earlier log-size guard failure is preserved; no logs were erased or diagnostic
levels lowered. A narrowly scoped privacy repair and an explicitly revised lab
baseline policy need review before retry. Measured rounds remain pending.
[Provider decision draft](provider-decision-draft.md)
reconciles historical provider probes with SOAP/APC gaps, without selecting a
production provider. No broad task checkbox closes from these
supporting results, and there is still no final release or production cutover.

## Historical held investigations — superseded by access-confirmed follow-up

- Dispatcher/rank checkpoint `30c397af`: four native83 primary processes with
  unchanged runtime/source identities. The targeted dynamic-property attribute
  preserves serialization in eight states; a public declaration changes seven.
  The attribute also exempts descendants/future dynamic names, an explicit policy
  cost, while an unrelated-class diagnostic remains. Original rank reflection
  requires all three arguments and five omission controls fail before the body.
  No rank repair, positive persistence test or independent native repetition is
  claimed at this checkpoint. [Evidence](dispatch-rank.md).
- AWS credential serialization: 60 native83 observations independently repeated
  by actual OpenCode, with identical results and runtime snapshots. The first
  bridge is **rejected**: invalid UTF-8 can be written and fails only on reading,
  unlike the original write-time failure. Original readers also reject the new O
  format. A corrected candidate, original74 comparison, actual cache boundary
  and recovery policy remain pending. No accepted warning reduction or new ZIP
  follows from this rejected experiment. [Evidence](serialization-contracts.md).

The subsequent repository-local report-consumer repair now checks all38 baseline
records, binds collector/module identities and records the exact consumed input
hash. Actual Claude completed two source-only reviews; the second approved the
two provenance fixes. Codex cross-checked34 synthetic tests and six file hashes.
This is harness integrity only: native R2 remains unexecuted and old stage
validation remains stale. See [serialization evidence](serialization-contracts.md).

### Historical execution restrictions, superseded by explicit access confirmation

The subsequent dispatcher repeat/PHP74 attempt did not execute PHP: Claude hit
its quota and OpenCode rejected reading the two lab SSH configuration files.
OpenCode did complete 12 local tests and two separate shell syntax checks; those
are not native repetition. Checkpoint `e1411647` preserves the exact denied
operation. Both lab reservations were released. Await explicit operator access
authorization; do not repeat the denied operation through another executor.
Baseline privacy changes also await the separately presented policy approval.
No release, package integration, task completion or production change follows.

### Access-confirmed follow-up

The operator subsequently confirmed the requested audit/SSH/temporary/lab
accesses. New executions are separate phases; prior denials remain recorded and
any new denial must still stop the affected operation. Production/release gates
are unchanged. The actual [entrypoint-candidate inventory](entrypoint-inventory.md)
now covers17 published packages/43,782 payload members with primary and actual
Claude repeat byte-identical. Original-tree discovery, source-owner reconciliation
and active-path classification remain open; no broad task checkbox closes.

The held [return-contract family](return-contracts.md) also now has an authorized
actual Claude repeat of all nine native83 observations, strict record/source/runtime
comparison and preserved original hierarchy failure. SQL/API/constructor effects
remain untested by that corpus; no new artifact or release approval follows.

### Latest reviewed source batches and remaining privacy gate

- [Dispatcher](dispatch-rank.md): actual Claude native83 repetition and the
  original74 comparison are complete (`31ddd27c`). Eight serialized states
  retain bounded parity with the targeted attribute; its inheritance/future-name
  exemption remains explicit. Rank persistence remains untested.
- [Credential/cache R3](serialization-contracts.md):38 original74 and96 native83
  observations are independently repeated by actual Claude (`db4cd39d`). The
  repaired candidate rejects invalid UTF-8 before writing a cache record.
  Original readers reject the candidate O wire format: rollback compatibility
  and application acceptance remain false. The earlier rejected60-record phase
  above is historical, not the latest candidate result.
- [Real SQL return contracts](return-contracts-sql.md):91 typed rows per cohort,
  primary and actual Claude repeat, match the explicit oracle (`004b75da`).
  Declaration diagnostics decrease15 to4 without suppression;38 local tests and
  independent OpenCode review pass. Four fresh private database services are
  stopped; source/runtime identities are unchanged. Logging/monitor/cache seams,
  MSSQL and full API acceptance remain outside this fixture.
- [Privacy observations](baseline-rehearsal-privacy-proposal.md): four native
  probes and12 lints complete on74/83 (`58bd0d1c`). Parameter-copy behavior passes,
  but native exception traces still expose a15-character synthetic-secret prefix.
  Full privacy is **FAIL**; no valid USER authentication/upload or installed-app
  patch follows. The [trace proposal](baseline-rehearsal-trace-proposal.md) awaits
  policy confirmation and full-pipeline validation, not just formatter tests.
- [exp13 proposal](exp13-candidate.md) freezes75 targets, preserving62 prior
  results with three cumulative replacements and ten new targets. The SQL gate
  is now recorded; selection and two identical experimental builds completed
  in `4c5e058f`, without production promotion. Previous source-stage passes do not establish acceptance
  of the eventual ZIP. Privacy changes are excluded from this candidate.

Status email for the SQL milestone was accepted by verified-TLS SMTP on
2026-09-26 at17:33:32 America/Sao_Paulo; inbox delivery is not confirmed.
No parent/detailed task count changes from these bounded results.

## Historical artifact-runtime checkpoint: exp11 real-artifact regression

Two identical exp11 ZIP builds select 63 source repairs. Codex and actual Claude
independently compile all 11,784 PHP-family files per artifact: exp10 rejects11,
exp11 rejects7; 66 accepted files still have diagnostics. The seven remaining
rejections are not waived. [Build](exp11-candidate.md), [compiler evidence](exp11-syntax.md).

The actual extracted artifact passes the bounded synthetic SQL/Apache HTTP and
trusted-HTTPS contract against original74; the original83 PDO failure remains
an expected control. API diagnostics remain **18 groups / 503 events**. Across
the two labs,48 CLI rows comprise44 successful processes and4 expected original
JSON compiler failures;20 typed candidate/baseline comparisons agree.68 class
cases and17 additional repair processes also meet their exact contracts, including
one expected duplicate-include fatal. Actual Claude repetitions reconcile; Cursor
executes18 local guards and independent report comparison. Its outer CLI timeout
after writing its checks/review is retained. [Runtime evidence](exp11-integration.md).

## Current limits and negative findings

- Riak alias-only repair is rejected: actual74/83 source execution still fails
  at the resolved reserved parameter type; Cursor repeats the83 failure.
  [Failed experiment](riak-alias.md). This does not change exp11 or remove Riak.
- [Dependency attribution](dependency-attribution-followup.md) adds12 scoped
  version declarations and14 partial license-evidence rows, not20 resolved bundles.
- Full application/UI/media/worker acceptance, all-distro installation, extension
  policy, cold/warm cache compatibility, performance and upgrade/recovery remain
  open. Broad tasks are not closed by these bounded corpora.
- Feasibility approval precedes production package/CI integration; release and
  `.20` cutover have separate gates. No accepted PHP8.3 release exists from this work.

## Historical evidence below

The following snapshots preserve the state and counts at their recorded phase;
they are not the current artifact, current test totals, or fresh authorization.

## Historical checkpoint: held reflection compatibility repair

Native controls caught two pitfalls: class-plus-scalar unions retain a class
component, and SELF/PARENT matching is case-insensitive. The corrected resolver
matches 15/22 native cases and 17/24 real API-metadata cases on PHP 7.4/8.3,
preserving same-runtime serialized parameter hashes. [Evidence and limits](reflection-parameter-repair.md).
Not yet selected into a new ZIP or real SQL/HTTP/TLS matrix; no 84-event API reduction claimed.

## Historical checkpoint: exp5 null-only batch

Five one-line null-only repairs were integrated in a reproducible twelve-patch
ZIP. Actual API/SQL/HTTP/trusted-HTTPS comparison removes exactly five groups /
142 events (35 groups / 931 remain), preserving functional contracts. Added
41 actual-class edge cases and ten real SQL dependency cases pass before/after
on both runtimes. [Evidence and limits](exp5-null-batch.md). No full acceptance.

## Historical checkpoint: remaining exp4 diagnostic triage

All 40 observed groups / 1,073 events now have source-pinned candidate-cause
accounting across seven categories. A read-only native reflection probe records
22 contracts on PHP 7.4/8.3. This is bounded triage, not a complete static audit
or acceptance of any warning. [Repair batches and required tests](exp4-diagnostic-triage.md).

## Historical checkpoint: exp4 actual ZIP integration

A separately built seven-patch ZIP now runs the synthetic SQL/HTTP/trusted-HTTPS
matrix alongside exp3. All candidate outputs match original 7.4; the 694 Criteria
null-alias events disappear while the other 40 groups / 1,073 events remain
unchanged. Two builds are identical. [Artifact and integration evidence](exp4-candidate.md).
This is not full application, distro, performance or release acceptance.

## Historical checkpoint: Criteria null-alias repair (held)

A new one-line explicit-null repair preserves eight alias contracts on real
Criteria/Criterion classes under PHP 7.4/8.3. Four source/runtime rows agree;
three original-8.3 null-to-strlen diagnostics disappear while other warnings
remain recorded. This is a fixture-boundary probe, not integrated SQL acceptance.
[Patch, exact scope and next integration check](criteria-null-alias.md).

## Historical checkpoint: exp3 SQL / Apache / trusted TLS

The actual ZIP now passes the bounded synthetic SQL/session HTTP + trusted HTTPS
matrix on PHP 7.4 and 8.3; original 8.3 fails at the expected PDO declaration.
Claude independently executes the same matrix. Candidate 8.3 still has 41
sanitized diagnostic groups / 1,767 events, so no full-case acceptance follows.
[Results, isolation and remaining scope](exp3-api.md). Local suite: 122 tests.

## Historical checkpoint: actual exp3 runtime regression

The built ZIP now ran in both isolated labs: 48 rows, 44 zero exits and four
expected original-8.3 JSON syntax controls. All 24 candidate rows exit zero;
20 typed-output/serialized-entry comparisons match original PHP 7.4. Claude and
Cursor independently reran the corrected harness. PHP deprecations remain open,
so no full acceptance checkbox is closed. [Evidence and diagnostic gaps](exp3-runtime.md).

## Historical checkpoint: integrated experimental source artifact

The separate six-patch **exp3** ZIP was built twice with identical hashes and
verified exact delta (six source changes, eight metadata additions). It preserves
the original archive and exp2. Selection includes the demonstrated JSON/PDO/date/
parser repairs; Symfony, Registry, DebugPDO alternatives and APCu remain explicit
separate work. [Selection, artifact and remaining tests](exp3-candidate.md).

The built ZIP has completed the first focused CLI matrix above. Bounded SQL/HTTP/TLS
regression is now recorded above; full application regression remains pending; no original or detailed
acceptance checkbox is closed.

## Historical checkpoint: configuration cache over Apache

Four original-source HTTP rows passed (7.4/8.3 × original/test-only aliases),
independently rerun by Claude and Cursor. The alias fixture demonstrates real
same-worker persistence across requests, version mismatch, deletion and replacement.
The original controls remain disabled under the explicit minimal test INI.
This does not approve production cache activation or resolve counter failures.

[Apache cache evidence and boundaries](apcu-web.md). Ten additional mocked client
tests pass; full local suite is **119 tests**. Case/parent counts remain unchanged.
The next integrated experiment is a six-patch exp3 ZIP; no release claim.

## Historical checkpoint: APC/APCu application cache

Original wrapper controls reproduce `init=false` on both 7.4 and 8.3 CLI: an
existing baseline gap, not a newly proven migration regression. A fixture-only
direct alias experiment fails four native missing-counter assertions on both
runtimes (59/63 pass); Claude and Cursor independently reproduced the results.
The failures remain visible; no adapter or source patch was promoted. Upstream
APCu-BC source supports the missing-counter guard, but concurrency and actual
web/application cache acceptance remain untested. Grok hit its turn limit;
OpenCode reviewed and ran the 109-test local suite successfully.

[Cache investigation, evidence and next actions](apcu-cache.md). These are partial
T1-03/T4-01 findings; detailed and original completion counts are unchanged.

## Historical checkpoint: real provider SAPIs (partial T4-01)

CLI and real HTTP GET/POST/invalid-POST probes passed for Noble native 8.3.6,
Resolute Sury 8.3.35 and Rocky Remi 8.3.35. Claude independently reran Noble/Remi;
Cursor reran Resolute. Strict evidence collection agrees across primary and
independent runs, with fresh nonces. Full local harness: **109 tests pass**.

The native Rocky transaction cannot resolve memcache/ssh2 in its configured
repositories. The tested Remi stack does not provide the legacy `php-pecl-apc`
capability still required by current RPM metadata. Cache API compatibility and
final provider/ABI policy must be reconciled: **5.16 and original 1.4 remain open**.
No Kaltura install/media/upgrade acceptance, package/CI integration or `.20` change.

[Provider evidence and limitations](provider-runtime.md),
[structured audit record](evidence/provider-runtime/result.json).
Grok timed out; OpenCode reviewed scripts but could not perform the independent
Remi rerun because its CLI denied `/tmp` access. Claude completed that rerun;
no tool denial is counted as PASS. All owned containers were removed.

## Latest batch: inventory and coverage

- **T0-02 / 5.2 PASS:** all 19 current patches (3 active / 16 held), 15,175 raw
  source files, 17 Noble baseline DEBs and the exp2 archive verified. Explicit
  selected/deferred/rejected ledger; no patch promotion. Cursor executed and
  Claude independently reran the audits.
- **T0-03 / 5.3 PASS:** all 24 parent tasks reconciled to case IDs, bounded
  evidence and remaining gaps. OpenCode Muse Spark executed the audit after
  Grok hit its turn limit; Cursor verified the corrected matrix.
- New offline auditor has 12 unit tests; **80 local tests** pass in Codex and
  Claude runs. This is not a new PHP/application runtime acceptance result.

[Inventory](patch-inventory.md), [coverage matrix](coverage-matrix.md),
[batch results and identities](evidence/batch2-inventory/result.json).

## First batch (historical, before the completed audit above)

| Case | State | Executor / independent review | Evidence / remaining work |
|---|---|---|---|
| T0-01 / 5.1 | PASS | Claude execution; Grok independent rerun and review; Cursor additional review | 68 tests, exit 0 for both executions and Codex cross-check. Frozen harness identity verified. |
| T0-02 / 5.2 | PARTIAL | Cursor execution; Claude independent rerun and review | Three held patch/original-source hash checks and exp2 ZIP hash agree. All other patches, active series payload transformations, published baseline and complete selection decisions remain unverified by this case. |
| T0-03 / 5.3 | NOT_RUN | Assigned Grok; Cursor reviewer | Full original-task/evidence/uncovered-entrypoint reconciliation still required; prior planning mapping checks do not close this execution case. |

[Machine-readable results](evidence/batch1-local/result.json),
[frozen identities](evidence/batch1-local/identities.json),
[raw primary test output](evidence/batch1-local/codex-tests.txt),
[Claude execution](evidence/batch1-local/claude-execution.txt),
[Grok execution](evidence/batch1-local/grok-execution.txt),
[Cursor execution](evidence/batch1-local/cursor-execution.txt),
[Claude review](evidence/batch1-local/claude-review.txt),
[Grok review](evidence/batch1-local/grok-review.txt), and
[Cursor review](evidence/batch1-local/cursor-review.txt).

## Reproduction and identity

Input commit: `e93dc4cfd77c4be65ab117cc24999a925a5108cd`.
Host: Ubuntu 24.04.5 LTS, Python 3.12.3. CLI execution reports are retained as
reported, not a source of verified model/version claims. All six CLI processes
(execution and review) returned exit 0. Test commands themselves returned exit 0.

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tools/php83 -p 'test_*.py'
```

The 107 tracked harness/patch files were hashed during the read-only batch,
compared to the frozen commit and checked again after execution. No such file
changed; the only pre-execution repository edit was the AGENTS.md fallback rule.
Reports/docs were added during coordination without changing the tested inputs.
Tests own temporary fixtures; no lab target or PHP SAPI is exercised by this
command. Existing target guards and mock HTTP tests are not real TLS acceptance.

For the bounded integrity check, both CLIs inspected and executed
`PYTHONDONTWRITEBYTECODE=1 python3 /tmp/php83-independent-integrity.py`.
Its exact [read-only source](evidence/batch1-local/integrity-verifier.txt) is retained
with its hash; reproduction requires the documented local source/artifact paths.
It checks doc-comment-property, dateUtils-ternary and KalturaPDO-query, plus
exp2 SHA256 `99233ac6638f02072b3394159340edd1e2388b243bafadca3fe33b6bbafa97a0`.
It does not apply patches, check their resulting bytes, or audit all held files.
The active manifest remains JSON-only; no held patch was promoted.

## CLI fallback

AGENTS.md records the operator-approved fallback from slow/failed Grok attempts
to OpenCode with Zen Muse Spark 1.3 Free. Local model discovery returned
`opencode/muse-spark-1.3-contributor-free`. Grok completed execution and review
within their 120-second deadlines, so **the fallback was not invoked**.
In the second batch, Grok exited 1 at its turn limit. OpenCode with that model
then executed the local coverage audit successfully (exit 0); its result is
attributed to OpenCode and independently reviewed by Cursor. Model discovery
alone was not counted as execution success.
If needed, record the stopped/failed Grok attempt separately and report the actual
OpenCode executor and model, never attribute its result to Grok.

## Remaining gates and next three cases

All seven aggregate gates T0–T6 remain open. Major unknowns include complete
static/reachable-path triage, a reviewed integrated candidate, the two additional
provider/distros, full browser/media/job regression, benchmark acceptance and
upgrade/recovery rehearsal. Small passing probes do not close these gaps.

1. Investigate the confirmed **APC/APCu source-cache dependency gap**, then
   reconcile T4-01 provider/ABI requirements without changing production packages.
2. Execute **T0-04**: complete dependency/license/active-entrypoint and static
   finding classification, retaining unknown reachability rather than assuming
   unused code.
3. Execute **T0-05**: finish comparable baseline fixture/run evidence and the
   frozen workload. VM ownership and existing isolation/approval gates apply.

## exp6 reflection integration (partial)

Separate reproducible thirteen-patch ZIP integrates the parameter reflection
repair. Actual API/SQL/HTTP/trusted-HTTPS contracts are preserved; diagnostics
fall from 35 groups/931 events to 33 groups/847 events, with only the two
reflection locations removed. Focused CLI candidate rows preserve baseline
outputs. See [exp6 evidence](exp6-reflection-integration.md). Aggregate acceptance
remains 0/24, detailed tasks 3/27; this bounded integration closes no full case.

## Held Zend_Config native return declarations

Six explicit return contracts pass 16 actual-class rows against original7.4 and
original8.3; candidate8.3 has no captured warnings. The held patch intentionally
uses native `mixed` and is not a candidate7.4 support claim. Full integration is
pending; see [configuration return evidence](config-return-contracts.md).
No full acceptance task is closed.

## exp7 PHP 8.3-only configuration return integration

Reproducible fourteen-patch ZIP; actual API/SQL/HTTP/trusted-TLS parity retained
and six Zend_Config diagnostic locations removed (144 events). Remaining bounded
API diagnostics: 27 groups/703 events. CLI: 60 rows including original7.4 baseline
and exp6 counterfactual; all 12 exp7 rows pass. Local suite: 126 tests.
See [exp7 evidence](exp7-config-integration.md). Acceptance remains 0/24 and
3/27 detailed tasks; no release or production change is approved by this cycle.

## Held Criteria iterator native returns

Sixteen actual-class state/alias rows and two invalid-access controls pass with
independent reruns after correcting a fixture filename mismatch. Cumulative patch
preserves the null-alias repair and must replace its old manifest entry, not be
stacked. See [Criteria evidence](criteria-return-contracts.md). No API diagnostic
reduction or full-case completion is claimed before artifact integration.

## exp8 cumulative Criteria artifact integration

Reproducible fourteen-patch ZIP preserves the alias guard and changes only six
Criteria declarations relative to exp7. Actual API/SQL/HTTP/trusted-TLS parity
retained; diagnostics reduce by 132 events to 21 groups/571. Forty-eight CLI rows
retain original74 reference and exp7 comparison; all 12 exp8 rows exit 0. Local
suite 136 tests includes ten new collector cases. See
[exp8 evidence](exp8-criteria-integration.md); acceptance remains 0/24 and 3/27.

## PDO return-loss diagnosis on real synthetic SQL

Codex/Claude independently reproduce nineteen rows per runtime: attributes and
statement execution discard native success/failure booleans, while transaction,
cache and dry-run effects remain intact. No repair or warning reduction claimed.
See [PDO return audit](pdo-return-audit.md). Exp8 residual remains 21 groups/571;
full acceptance stays 0/24 and 3/27 detailed tasks.

## Held PDO boolean repair

Twenty-nine real SQL cases across previous/candidate74/83 confirm native boolean
success/failure restoration without changing observed transaction/cache/dry-run
data effects. Three load warnings removed in this focused fixture only; artifact
API count remains unchanged until integration. See
[boolean repair](pdo-boolean-repair.md). Full acceptance tasks remain open.

## exp9 PDO boolean artifact and real-bootstrap integration

The separate reproducible sixteen-patch ZIP passes four API rows and 48 CLI rows,
independently repeated by Claude. The API removes exactly 68 events, leaving
18 groups / 503. A new real KalturaPDO/bootstrap probe (no dependency stubs) passes
23 typed rows per exp8/exp9 independently; nine public null-to-bool corrections
are explicit. First named-binding fixture failure is retained and corrected.
Root harness 146 plus separate bootstrap 11 local tests pass; Grok timeout and
OpenCode's initial denied report-write remain visible, with a completed read-only
fallback review. See [exp9 evidence](exp9-pdo-integration.md). Original acceptance
remains 0/24 and detailed 3/27, not a percentage or release date.

Next aggregate progress must include inventory/classification and the frozen
full-service 7.4 baseline, not only individual diagnostic repairs. Do not reuse
`/tmp/php74-baseline-sanity.sh` unmodified: its default target is protected `.20`
and `curl -L` does not enforce per-hop lab destinations. Historical network-guard
removal means prior temporary protection cannot be assumed active.

## Inventory accounting prerequisite

A reproducible, independently Cursor-rebuilt ledger now links 4,711 overlapping
static-report rows, 275 syntax records, 79 compiler comparisons and exp9 runtime
locations to available source identities. Eight additional nested local tests
pass. It explicitly exposes 792 missing packaged-file hashes and 20 unresolved
dependency version/license attributions; it resolves zero semantic findings.
See [inventory ledger](inventory-ledger.md). T0-04 remains open; next is read-only
identity extraction from the already checksum-verified published DEB payloads.

## Published payload identities and whole-exp9 syntax

All 792 previously missing packaged hashes are now recovered from exact payload
bytes across 17 checksum-verified DEBs; 149 known hashes remain equal. Claude's
independent build and the primary/repeat reports are byte-identical, covering
13,454 PHP-family files. Cursor reviews the joins and tests; orchestration
negative controls expand the nested package suite to 25. See
[package identities](package-identities.md). This closes the missing-hash
subcase, not T0-04's semantic/license/entrypoint obligations.

A fresh original/exp9 compiler matrix on one isolated PHP 8.3 runtime scans
11,784 files per artifact, with full ZIP/source/runtime identities. Claude
independently repeats all 23,568 logical rows. Rejections decrease 58→54;
64 accepted-with-diagnostics files remain per artifact and no new rejection
appears. The initial syscall-action harness failure is retained; corrected
collection completes but `candidate_all_files_compile` remains false. See
[paired syntax](candidate-syntax.md). Static finding attribution, remaining
compiler failures and full runtime coverage remain open; acceptance stays
0/24 original and 3/27 detailed cases.

## Source-supported compiler classification

All 54 exp9 compiler-rejected files now have exact ZIP/local/published-payload
and historical runtime identity joins plus diagnostic/source classification.
The result is 47 new PHP 8.3 language incompatibilities (43 curly offsets,
three autoload declarations, one ternary) and seven retained baseline rejections
(six unexpanded templates, one reserved Object alias). Six positive template
consumer chains do not prove valid generated output. No rejection is waived.
Claude independently rebuilds identical classification reports; Cursor verifies
13 template/consumer source identities; OpenCode executes the bounded fallback
after Grok times out. Final 19-test status guards reject timeout/signal/noninteger
values instead of misclassifying them as compiler failures. See
[compiler triage](compiler-triage.md). No application patch is promoted and no
aggregate acceptance checkbox closes.

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

## Additional inventory progress

[Prepared entrypoint collector](entrypoint-inventory.md): 17 synthetic tests and
actual Claude independent review after fixing real daemon-launch matching gaps.
Real archive input execution remains unperformed after an external-directory
permission denial, with operator confirmation requested before any retry.
[Packaging repository literal inventory](packaging-launchers.md) separately
scans 1,045 text members out of 1,085 tracked paths, with all exclusions visible.
Its 909 regex candidate rows (many changelog/comment false positives) repeat
byte-identically under actual OpenCode; they are not 909 active entrypoints.
[Diagnostic families](exp12-diagnostic-families.md) organizes the remaining
17 groups / 371 events; unimplemented families and inheritance constraints stay
open. No original task or detailed acceptance checkbox closes from this work.

## Held return-contract batch

[Return contracts](return-contracts.md) records 11 native declarations and three
narrowly justified transaction attributes, with DebugPDO query v3 an explicit
prerequisite. The nine-process native primary confirms class loading and bounded
configuration/wakeup behavior, with four unrelated hierarchy warnings retained.
26 local tests and an actual OpenCode preparation review passed. The attempted
independent native repeat was **NOT_EXECUTED** after a permission denial reading
its external staging identities; no alternative tool retried that denied action.
Real SQL/API parity and independent runtime repetition remain open. This batch
is held, not selected into exp12 or accepted for release.
