# Exp10: pure offset batch integrated into the experimental source ZIP

**Experimental, not an accepted release.** This cycle adds the reviewed43-file
curly-offset-only repair to exp9's unchanged16-target selection. No production,
`.20`, package/CI, main-merge or release operation is part of this experiment.
Original acceptance remains0/24 and detailed cases3/27.

## Artifact identity

[Selection and assembly](exp10-candidate.md) record two identical builds:

```text
Rigel-18.20.0-php83-experimental.exp10.zip
de177e6cbaedf3a3207661c2325f466cce37febb73190f3a49d31f24b740c053
```

The ZIP changes59 unique source files relative to the pinned original, adds61
metadata members and preserves all other upstream entry bytes. Against exp9,
exactly43 application files change; all previous16 results remain identical.
Actual Cursor independently verifies the archive and delta. No mixed held Spyc
`each()` repair is included. Existing artifacts and active exp2 manifest remain
unchanged; exp10 is a separate PHP8.3-only experiment, not supported on PHP7.4.

## Whole-source compiler result

The fresh paired scan uses PHP8.3.6 CLI, `-n`, short tags enabled and diagnostics
on, four workers with per-file timeouts. All ZIP/extracted-source bytes and
runtime/harness identities are checked before and after in a read-only,
network-denied transient service. No application bodies are executed by lint.

| Metric | exp9 | exp10 |
|---|---:|---:|
| PHP-family files scanned | 11,784 | 11,784 |
| Accepted | 11,730 | 11,773 |
| Rejected | 54 | 11 |
| Accepted with diagnostics | 64 | 66 |
| Files with diagnostics, including rejected | 118 | 77 |
| Incomplete subprocesses | 0 | 0 |

All43 targeted files change from expected compiler rejection to acceptance.
Every unchanged source file retains identical compiler outcome and diagnostic
content. Two newly parsable files expose existing diagnostics: final/private
`CvsPassTask.php:141` and three optional-before-required declarations in
`FileUtils.php:74`. Those warnings are retained, not hidden or waived.

The remaining11 rejections are still open: three removed `__autoload`
declarations, one unparenthesized nested ternary, six unexpanded generator
skeletons and the reserved Riak `Object` alias. Positive template-consumer
analysis does not prove valid generated output and is not permission to remove
those rows. `candidate_all_files_compile` stays **false**.

See [primary scan](evidence/exp10-syntax/primary.json) and
[primary summary](evidence/exp10-syntax/primary-summary.json). Independent full
scan repetition is a separate execution phase, not implied by preparatory tests.

## Actual extracted-artifact regression

The isolated baseline74 lab runs a fresh synthetic MariaDB fixture and transient
Apache for original74, original83, exp9/83 and exp10/83, serially. Each positive
row checks the existing11 HTTP assertions, untrusted-CA rejection and11
trusted-HTTPS assertions. The original83 PDO signature failure remains an
expected negative control. Both candidate contracts match original74 exactly.

**API diagnostics remain18 groups /503 events**, identical for exp9 and exp10.
This syntax batch does not resolve them. One baseline diagnostic group/six
events and the original83 signature failure remain visible separately.
The owned synthetic DB unit is confirmed inactive after execution.

The two labs together execute48 focused CLI rows across standard/minimal INI:
44 successful rows plus four expected original83 JSON compiler failures. All12
exp10 rows and all12 exp9 rows succeed;20 JSON-type-preserving candidate-to-
original74 comparisons pass. Environment rows have runtime-specific values and
are not incorrectly treated as behavior-equal across PHP versions.

Three actual exp10 class files are additionally loaded in separate PHP8.3
processes: two Google utility versions and HTMLPurifier Encoder. All68 cases
match the prior source-pinned candidate83 corpus exactly, linking this ZIP to
the earlier original74/candidate74/candidate83 experiment. This is selected-method
coverage of three files, not full behavior coverage of the59 changed files.
Retained Google multibyte overreads and NOTICE-to-WARNING differences still need
application error-handler analysis.

Actual Claude independently repeats the baseline74 API,12 CLI and68 class rows.
See [primary runtime summary](evidence/exp10-runtime/primary-summary.json) and
[Claude baseline execution](evidence/exp10-runtime/claude.json).

## Runtime identities and scope

Fresh baseline74 snapshots hash55 PHP/Apache binaries/modules, linked libraries
and41 PHP7.4 CLI INI files; before/after identity records match. Native php83lab
snapshots cover39 binary/module objects, linked libraries and standard/minimal
INI configuration around the36-row CLI sequence. The syntax scanner separately
attests its minimal runtime and15 linked libraries.

These are byte-identity observations, not a new package-signature or copied-
runtime provenance audit. They do not continuously attest executing memory,
SSH host authentication, the kernel/systemd/MariaDB binaries or all host Apache
configuration. Fixture configuration and source hashes are recorded separately.
No secrets or configuration values are copied into identity evidence.

## Review and local tests

Actual CLI roles are recorded separately:

- Claude: strict selection replay/13 builder tests; independent actual API,
  CLI and class execution with review.
- Cursor Agent:10 selection,28 syntax and15 API local tests plus shell syntax;
  independent actual archive verification/delta and review.
- Grok: bounded120-second timeout, exit124; not a passing test.
- OpenCode Muse Spark1.3 Contributor Free: authorized fallback,13 builder and10
  selection tests plus independent selection review.
- Coordinator: existing146-test root suite and OpenSpec strict validation pass.

Mocked guard tests do not execute the application. Each runtime report names its
source/harness identities and captures actual exits; no report absence or timeout
is converted into a pass. Prep-phase missing-pin reports remain historical
records; later verified pins and runs are separate evidence.

## Remaining gates

Full static-finding, dependency/license and entrypoint attribution; the complete
frozen PHP7.4 baseline; remaining compiler/runtime defects; real application/UI/
worker/cache/media coverage; three-distribution provider and installation
acceptance; performance and matched-state recovery all remain open. Feasibility,
production-package/CI, release and live-cutover approvals are not bypassed.

## Completed independent scan/CLI repetition

Actual Claude now repeats all23,568 compiler rows, the36 native PHP8.3 CLI rows,
and fresh native83 runtime snapshots. The full paired reports match exactly
except each lint row's `duration_ns`; all source, diagnostic, exit, runtime,
harness and contract fields match. Its35 local syntax/comparator tests pass.
See [independent scan comparison](evidence/exp10-syntax/claude-compare.json) and
[executor report](evidence/exp10-syntax/claude-agent.json). Combined with its
baseline74 phase, all48 CLI rows have independent execution.

The coordinator's snapshot command in the prompt incorrectly proposed piping a
local SSH wrapper into remote Python. Claude inspected it and invoked the local
wrapper correctly **before attempting the invalid command**; no failed snapshot
or overwritten evidence is claimed. The actual command and all per-step exits
are recorded separately in its report/sidecars. Snapshot identity records match
between all primary and independent before/after observations.

JSON `doc-comment-export` comparisons intentionally compare typed entry payloads,
not the runtime/source provenance envelope. Runtime environment rows likewise
remain version-specific. Cross-runtime stderr is not declared equal; remaining
8.3 deprecations persist. Independent same-runtime CLI stderr is exact.

The [strict runtime reconciliation](evidence/exp10-candidate/comparison-runtime.json)
joins16 primary/independent reports and both labs' four snapshots each. API
comparison preserves exact collected stdout, diagnostic groups/events, runtime
observations and expected failures; fresh DB UUIDs are distinct and each owned
unit's cleanup is checked. Raw API stderr was not retained because it can contain
session credentials: opaque stderr hashes remain evidence, but equality is **not**
claimed for unretained raw stderr. No assumption that its differences contain
only timestamps/UUIDs is made. The earlier12-report comparison is retained as a
narrower phase; the final one additionally verifies native83 snapshots.

Actual Cursor subsequently executes the final16-input runtime comparator and35
syntax/comparator tests, independently produces a byte-identical reconciliation
report, and confirms the no-overwrite guard. Its [final review](evidence/exp10-candidate/cursor-reconcile.json)
checks this document against the actual evidence and retains all open gates.
