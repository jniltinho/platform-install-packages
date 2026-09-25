# PHP 8.3 test status

Snapshot: 2026-09-25, migration branch. This is a scoped evidence board, not a
release estimate. [Detailed plan](../../openspec/changes/migrate-kaltura-php83/tasks.md)
and [execution contract](../../openspec/changes/migrate-kaltura-php83/design.md).

## Counts and boundaries

- Original acceptance obligations: **0 of 24 complete**.
- Detailed cases: **3 of 27 complete**, **1 partial (T4-01)**, **23 not yet executed under
  the new case contract**. Older evidence is retained; NOT_RUN here does not mean
  no historical investigation exists.
- T0-01: **68 distinct local Python tests passed**, independently executed by
  Claude and Grok, with a Codex cross-check. Do not sum repeated runs into 204
  distinct tests. These include mocks and do not establish PHP runtime acceptance.
- No new VM/application test, release, package integration or `.20` mutation in
  this batch. No release ETA or application completion percentage is inferred.

## Latest progress: held reflection compatibility repair

Native controls caught two pitfalls: class-plus-scalar unions retain a class
component, and SELF/PARENT matching is case-insensitive. The corrected resolver
matches 15/22 native cases and 17/24 real API-metadata cases on PHP 7.4/8.3,
preserving same-runtime serialized parameter hashes. [Evidence and limits](reflection-parameter-repair.md).
Not yet selected into a new ZIP or real SQL/HTTP/TLS matrix; no 84-event API reduction claimed.

## Latest progress: exp5 null-only batch

Five one-line null-only repairs were integrated in a reproducible twelve-patch
ZIP. Actual API/SQL/HTTP/trusted-HTTPS comparison removes exactly five groups /
142 events (35 groups / 931 remain), preserving functional contracts. Added
41 actual-class edge cases and ten real SQL dependency cases pass before/after
on both runtimes. [Evidence and limits](exp5-null-batch.md). No full acceptance.

## Latest progress: remaining exp4 diagnostic triage

All 40 observed groups / 1,073 events now have source-pinned candidate-cause
accounting across seven categories. A read-only native reflection probe records
22 contracts on PHP 7.4/8.3. This is bounded triage, not a complete static audit
or acceptance of any warning. [Repair batches and required tests](exp4-diagnostic-triage.md).

## Latest progress: exp4 actual ZIP integration

A separately built seven-patch ZIP now runs the synthetic SQL/HTTP/trusted-HTTPS
matrix alongside exp3. All candidate outputs match original 7.4; the 694 Criteria
null-alias events disappear while the other 40 groups / 1,073 events remain
unchanged. Two builds are identical. [Artifact and integration evidence](exp4-candidate.md).
This is not full application, distro, performance or release acceptance.

## Latest progress: Criteria null-alias repair (held)

A new one-line explicit-null repair preserves eight alias contracts on real
Criteria/Criterion classes under PHP 7.4/8.3. Four source/runtime rows agree;
three original-8.3 null-to-strlen diagnostics disappear while other warnings
remain recorded. This is a fixture-boundary probe, not integrated SQL acceptance.
[Patch, exact scope and next integration check](criteria-null-alias.md).

## Latest progress: exp3 SQL / Apache / trusted TLS

The actual ZIP now passes the bounded synthetic SQL/session HTTP + trusted HTTPS
matrix on PHP 7.4 and 8.3; original 8.3 fails at the expected PDO declaration.
Claude independently executes the same matrix. Candidate 8.3 still has 41
sanitized diagnostic groups / 1,767 events, so no full-case acceptance follows.
[Results, isolation and remaining scope](exp3-api.md). Local suite: 122 tests.

## Latest progress: actual exp3 runtime regression

The built ZIP now ran in both isolated labs: 48 rows, 44 zero exits and four
expected original-8.3 JSON syntax controls. All 24 candidate rows exit zero;
20 typed-output/serialized-entry comparisons match original PHP 7.4. Claude and
Cursor independently reran the corrected harness. PHP deprecations remain open,
so no full acceptance checkbox is closed. [Evidence and diagnostic gaps](exp3-runtime.md).

## Latest progress: integrated experimental source artifact

The separate six-patch **exp3** ZIP was built twice with identical hashes and
verified exact delta (six source changes, eight metadata additions). It preserves
the original archive and exp2. Selection includes the demonstrated JSON/PDO/date/
parser repairs; Symfony, Registry, DebugPDO alternatives and APCu remain explicit
separate work. [Selection, artifact and remaining tests](exp3-candidate.md).

The built ZIP has completed the first focused CLI matrix above. Bounded SQL/HTTP/TLS
regression is now recorded above; full application regression remains pending; no original or detailed
acceptance checkbox is closed.

## Latest progress: configuration cache over Apache

Four original-source HTTP rows passed (7.4/8.3 × original/test-only aliases),
independently rerun by Claude and Cursor. The alias fixture demonstrates real
same-worker persistence across requests, version mismatch, deletion and replacement.
The original controls remain disabled under the explicit minimal test INI.
This does not approve production cache activation or resolve counter failures.

[Apache cache evidence and boundaries](apcu-web.md). Ten additional mocked client
tests pass; full local suite is **119 tests**. Case/parent counts remain unchanged.
The next integrated experiment is a six-patch exp3 ZIP; no release claim.

## Latest progress: APC/APCu application cache

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

## Latest progress: real provider SAPIs (partial T4-01)

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

## exp7 PHP8.3-only configuration return integration

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
