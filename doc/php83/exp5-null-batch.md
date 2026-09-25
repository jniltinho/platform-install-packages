# exp5: five explicit-null repairs, integrated and edge-case checks

This is a separate **experimental** twelve-patch ZIP: exp4's seven patches plus
five one-line null-coalescing changes. No non-null rejection/cast, property
visibility, signature, authorization rule or serialized wire-format change is
selected. The earlier broad suggestions were not applied.

## Changes and identities

| File / line in exp4 | Change | API events removed on 8.3 |
| --- | --- | ---: |
| myCustomData.class.php:28 | `unserialize($str ?? '')` inside existing error-control expression | 22 |
| Partner.php:1431 | `trim($names ?? '')` for the existing default-name condition | 20 |
| PermissionPeer.php:329 | `trim(getDependsOnPermissionNames() ?? '')` | 32 |
| KalturaLog.php:122 | `strtr($value ?? '', ',', ' ')` | 54 |
| KalturaFrontController.php:76 | coalesce the **result** of the existing uid/ks_uid ternary | 14 |
| **Total** | **Five source lines; all non-null paths retained** | **142** |

The original `@unserialize` is retained, not newly added as a warning fix.
`PermissionPeer` has a second similar expression elsewhere; the generation guard
initially rejected a whole-file replacement because there were two matches.
The corrected patch explicitly targets the observed line 329 only. That initial
attempt produced no ZIP/manifest and is not counted as a build. Other reachable
null sites remain a wider-analysis obligation, not presumed fixed.

- exp5 ZIP SHA256: `ef4d3e67c077014ba4837c83eec57ee7e0bf3548e444337ee92b19dad27bbcf5`.
- Two independent builder invocations (`exp5/`, `exp5-repeat/` in the sibling
  artifacts directory) produced identical bytes.
- Twelve changed original files, fourteen metadata additions; all other original
  entry bytes preserved, verified independently by Cursor.
- [Ordered manifest](evidence/null-batch/manifest.json),
  [exact-delta verification](evidence/null-batch/verification.json),
  [Cursor verification](evidence/null-batch/cursor-verification.json).
- [Current patch identity audit](evidence/null-batch/patch-inventory.json):
  25 patches (3 in unchanged active exp2 manifest, 22 held). Explicit exp5
  selection does not silently promote the other held/rejected alternatives.

Original, exp2, exp3 and exp4 are preserved. No package metadata/CI, release,
installed application or `.20` change is made.

## Real API / SQL / HTTP / trusted HTTPS

The six-row matrix runs original, exp4 and exp5 on PHP 7.4/8.3 with a newly owned
private synthetic database. Original 8.3 remains the expected PDO declaration
fatal control. All four candidate rows match original-7.4 normalized functional
output: session start/get, GET/POST, user/admin kinds and the five denied cases,
both HTTP and trusted HTTPS, including untrusted-CA rejection.

Contemporaneous exp4→exp5 comparison on 8.3 removes exactly the five groups above:
**40 groups / 1,073 events → 35 groups / 931 events**. All other sanitized group
counts are unchanged. This is not a performance measurement, acceptance of the
remaining diagnostics or proof that different messages at the same location
cannot be conflated by sanitization.

[Primary API report](evidence/exp5-api/codex.json),
[independent Claude run](evidence/exp5-api/claude.json),
[diagnostic delta](evidence/exp5-api/diagnostic-delta.json).

## Focused actual-class edge cases

The `null-probe` harness loads the real application bootstrap, Partner,
myCustomData, KalturaLog and KalturaFrontController from the actual extracted ZIP.
Only the logger output sink is an in-memory fixture; no DB/network operation is
allowed in these processes. It compares **41 contract rows** per source/runtime:
null, empty string, false, numeric zero, zero string, whitespace, dummy name,
comma-containing string, array and object across four real class operations,
plus a serialized custom-data namespace/nested-data roundtrip.

All 41 outputs/errors match exp4 **within each runtime**, including non-null
invalid-input behavior. This does not claim that PHP 7.4 and 8.3 treat every
invalid input identically. Explicit assertions preserve the default permission
name and the dummy-name override. Front-controller testing invokes the real
end-logging method without singleton construction/dispatch; only the deterministic
user field is compared, not request duration. No real KS is created or retained.
Runtime diagnostics remain recorded separately and are not hidden as success.

[Focused primary evidence](evidence/null-probe/codex.json). The initial collector
was hardened to pin the reused bootstrap fixture hash before final execution;
its earlier report is retained under `attempts/`.

## Real PermissionPeer dependency filtering over SQL

A separate private-DB collector runs the real `PermissionPeer::filterDependencies`
with actual KalturaPDO queries. **Ten cases** cover empty permissions, null/empty/
zero dependency strings, satisfied dependency, missing dependency, transitive
removal, whitespace/CSV, an active partner-specific plugin permission and wrong
partner denial. All ten expectations pass on exp4 and exp5 under both runtimes.
The fixture bootstrap also retains its native-vs-KalturaPDO query controls.

[Dependency primary evidence](evidence/null-probe/codex-dependencies.json).
Each collector owns a new random unit/datadir, validates exact `@@datadir` before
schema writes, and stops its service in a finally block. Synthetic directories
are retained for diagnosis; service stop is not a claim of disk deletion.

## Boundaries and reproduction

All tests use the already approved isolated labs, hostname guards, read-only
application/fixture binds and private cache/config overlays. The SQL/API 8.3
runtime is the copied bundle on baseline74, not full AIO installation. Full distro,
media/browser, cache, benchmark and recovery obligations remain open. Existing
SSH settings do not pin host keys. Original baseline/runtime binaries are not
rehashed by this cycle's collector. The new focused collectors have real runtime
execution but no added mocked unit-test coverage; the existing local suite is
122 tests. Focused output parity is not a whole-app or release decision.

```sh
# Stage exp5 only once per owned lab; existing directories are refused.
bash tools/php83/exp5-api/stage.sh 74
bash tools/php83/exp5-api/stage.sh 83
# Stage null-probe separately in each exp5 lab root, preserving source artifacts.
python3 tools/php83/exp5-api/collect.py /path/to/new-api-report.json
python3 tools/php83/null-probe/collect.py /path/to/new-focused-report.json
python3 tools/php83/null-probe/collect-dependencies.py /path/to/new-sql-report.json
```

Do not run competing writers on baseline74. New reports cannot overwrite old
evidence. API/SQL logs are sanitized; do not persist raw token-bearing stderr.
The parser/JSON/export focused CLI matrix was rerun on actual exp5 bytes:
48 rows, 44 zero exits and four expected original-8.3 syntax-fatal controls;
all 24 candidate rows exit zero. Twenty typed-output/serialized-entry comparisons
match original 7.4. Claude independently repeats both runtimes; Codex verifies
normalized reports and all recorded local fixture hashes. See
[`exp5-runtime/parity.json`](evidence/exp5-runtime/parity.json).
No acceptance checkbox closes.

## Independent review and explicit limitations

Claude independently repeated the API, all four actual-class rows, all four
dependency SQL rows and both CLI batches. Cursor independently verified the ZIP
and reviewed primary/independent focused reports. Grok timed out (124); OpenCode
Muse Spark Free ran 122 local tests and reviewed the API/patch/focused evidence.
All actual CLI outcomes are retained separately; a timeout is not approval.

Three absolute assertions exist in the actual-class fixture: default permission,
dummy permission and serialized namespace conversion. Other rows are differential
contracts, not proof the old behavior was correct. The SQL fixture has ten
absolute expectations, including denial; it does not exercise false/array/object
dependency values. Real invalid-input errors remain errors, while fixture
RuntimeExceptions abort instead of being counted as expected application errors.

The class-only collector retains raw **synthetic** bootstrap stderr and diagnostic
messages (no KS, users or production config); it must not be reused with live
data. SQL/API collectors retain only sanitized locations/counts and hashes.
Exceptions before completion may leave no structured partial report, although
the SQL finally block still stops the known owned unit. No diagnostic group is
accepted merely because output comparison passes.

Reviewer corrections: the early API review preceded the added focused fixtures;
its coverage gaps are partly addressed by these later results. The author counted
only two absolute class assertions, corrected to three by Cursor. The CLI author
said the local exp5 `run-one.sh` was missing; Codex verified that it exists and
its hash, along with every other fixture, matches both independent VM reports.
Raw advisory responses are retained without promoting those statements to facts.
