# Privacy trace policy v1 — scoped synthetic execution

Primary completed four PHP processes and52 lints, all native exit0. The first
host validator failed on the original Error instrumentation byte comparison;
`runner.exit=1`, runner.stderr and reviewed-r3-validate.py are retained. No PHP
product failure was hidden or overwritten. A narrowly reviewed r4 validator
classifies the three original Error wrappers separately; policy invariants remain
strict. 23 local tests pass. Actual OpenCode Muse independent repeat completed with the same4 processes and
52 lints: exact stdout/stderr and typed report equivalence; comparison.json.
Broad55-file/library/INI identity snapshots before/after repeat also match.
Both exact units inactive;74 released, no pending VM calls.

## Source sets (frozen labels are not renamed)

| Record label | Actual source/runtime |
|---|---|
| original74 | upstream original / PHP7.4.33 |
| policy74 | upstream + approved display-policy patch / PHP7.4.33 |
| original83 | exp14 **without** privacy overlay / copied PHP8.3.6 |
| policy83 | exp14 **with** privacy overlay / copied PHP8.3.6 |

Each source set is private root-owned readonly synthetic files. No application
installation, published artifact, logging configuration, USER/login/upload or
real credential was modified/accessed. An eventual installed overlay must be
labelled **modified laboratory baseline with approved privacy policy**, not
published packages intact. Both sides require the same audited policy; measured
benchmark/full baseline acceptance remains separate.

## What is demonstrated

11 cases per process: mixed six argument types (including object whose
__toString throws), serialize/unserialize writer then actual subsequent write,
Exception, previous chain, Error through err/alert/crit, intrinsic-message leak,
pre-rendered trace leak, extra.message leak, ordinary string. A separate rejecting
priority filter control verifies no writer observer/formatter call and empty sink.

Policy replaces only display Throwable.message in a copied event, retaining
actual Error/Exception identity/state, priority/context/filter behavior and
structural metadata. Safe getTrace projection (no argument values or object
serialization) must match the entire formatted structure exactly, including
frame locations/calls, argument counts and native types. Unknown strings are not
regex-redacted. Intrinsic messages and previous messages remain intact.

`legacy-error-classification.json` binds old guards and probe call sites:
original Error gets a new Exception per logging invocation, unlike policy's
identity-preserving Throwable guard. Only these three original cases require
observed_same_bytes=false, writer_same_message=false and formatter_type=object.
This is source-bound attribution, not a claim to know every raw differing byte.
Policy never gets that exclusion. `validation-complete-closure.json` additionally
replays the exact fixed11-source closure from the reviewed runner, not a subset
derived from the report. Negative controls remain explicit known leaks.

## Diagnostics and identities

Zero diagnostics observed in these four processes is consistent with actual
loaded bytes: original ZendConfig runs only on7.4; both8.3 sets use exp14's six
already typed return signatures. See zend-config-diagnostic-attribution.json
with both hashes and exact diff. Earlier original-source8.3 pipeline's six
ZendConfig warnings remain unchanged in its own evidence. E_ALL/-1,
display_errors=stderr and handler returnfalse remain; synthetic log_errors=0
prevents writing host logs, not diagnostic capture.

Primary pins cover all staged sources plus PHP binaries/json.so before/after.
They do not independently pin all linked libraries/INI in that primary interval.
The separately collected repeat-runtime-before/after helper snapshots cover55
files, linked libraries and configurations for the repeat only, never retroactive
primary attestation. Timeouts can lack partial output and remain INCOMPLETE.
Exact-unit stop/inactive evidence remains separate in cleanup files.

## Reviews and remaining limits

Actual Claude prep attempt hit quota (exit1, no test execution). Actual OpenCode
Muse source review executed17 tests and returned bounded no-blocker findings;
independent Codex pdo reviewed the subsequent typed/runner23-test delta and
retained-report classification. Reviews are not additional PHP execution.

Intrinsic-message/pre-rendered/extras leak controls must not be relabelled PASS.
Before synthetic lab USER/auth, audit effective logger writers/formatters,
extras.message and premature stringification in the exercised path; reject unsafe
configuration or repair the narrowly identified emitter. This is not a universal
sanitizer, full privacy acceptance, package selection or production authorization.
