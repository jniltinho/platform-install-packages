# PHP 8.3 test status

Snapshot: 2026-09-25, migration branch. This is a scoped evidence board, not a
release estimate. [Detailed plan](../../openspec/changes/migrate-kaltura-php83/tasks.md)
and [execution contract](../../openspec/changes/migrate-kaltura-php83/design.md).

## Counts and boundaries

- Original acceptance obligations: **0 of 24 complete**.
- Detailed cases: **1 of 27 complete**, **1 partial**, **25 not yet executed under
  the new case contract**. Older evidence is retained; NOT_RUN here does not mean
  no historical investigation exists.
- T0-01: **68 distinct local Python tests passed**, independently executed by
  Claude and Grok, with a Codex cross-check. Do not sum repeated runs into 204
  distinct tests. These include mocks and do not establish PHP runtime acceptance.
- No new VM/application test, release, package integration or `.20` mutation in
  this batch. No release ETA or application completion percentage is inferred.

## First batch

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
Availability in a model list is not proof of authentication or execution success.
If needed, record the stopped/failed Grok attempt separately and report the actual
OpenCode executor and model, never attribute its result to Grok.

## Remaining gates and next three cases

All seven aggregate gates T0–T6 remain open. Major unknowns include complete
static/reachable-path triage, a reviewed integrated candidate, the two additional
provider/distros, full browser/media/job regression, benchmark acceptance and
upgrade/recovery rehearsal. Small passing probes do not close these gaps.

1. Finish **T0-02**: complete immutable source/baseline/active/held identity and
   explicit selected/rejected/deferred inventory without promoting patches.
2. Execute **T0-03**: reconcile all 24 original tasks against actual evidence and
   uncovered scope, independently reviewed by Cursor.
3. Execute **T0-04**: prioritize remaining dependency/license/entrypoint and static
   finding classifications; retain unknown reachability instead of declaring it
   unused. Lab mutations remain subject to ownership and existing approval gates.
