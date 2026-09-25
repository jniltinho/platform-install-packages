# exp3: first regression from the actual ZIP

2026-09-25. **PARTIAL T1-01/T1-03**, not clean application acceptance.
Unlike prior ad-hoc patch experiments, these runs load the extracted
[six-patch exp3 artifact](exp3-candidate.md), SHA256
`1c64edb5ff34308cedfcea3c7879187c21417b6bd1a8e083d70d580bedc985e3`.

## What ran

The same public ZIP was copied into a new `php-exp3-regression` directory in each
existing synthetic lab, verified before extraction, then checked byte-for-byte
against **every one of its 15,183 extracted regular files** before each batch.
No existing candidate, installed application, service or package was replaced.
The original control is the previously extracted published application tree.

Matrix: PHP 7.4.33 / 8.3.6 × original / exp3 × standard / minimal INI × six cases:
CLI environment, legacy JSON, Zend JSON, doc-comment parser, six full parser
object exports, and the real annotation/deserializer consumer with a synthetic
relative-time object. Each process runs as nobody, with network/socket denial,
read-only source and private cache/config overlays. See the
[runner](../../tools/php83/exp3-regression/README.md).

| Runtime | Rows | Exit zero | Original expected syntax fatals | Unexpected nonzero exits |
|---|---:|---:|---:|---:|
| PHP 7.4 | 24 | 24 | 0 | 0 |
| PHP 8.3 | 24 | 20 | 4 | 0 |

The four original 8.3 controls fail on removed curly-brace offsets in legacy/Zend
JSON. All **24 exp3 rows exit zero**, including four environment rows. Across
both INIs/runtimes, the other **20 candidate comparisons** preserve the original
7.4 typed JSON outputs or all six complete serialized parser entries. Export
producer-version/source-hash metadata is checked separately, not confused with
payload parity. Environment rows verify CLI/runtime and retain loaded modules.

Claude independently executed the 7.4 matrix; Cursor independently executed 8.3.
Codex reran both after the harness correction below. Reports agree exactly after
excluding only batch timestamps and per-row durations. Repeated runs are not
counted as additional distinct matrix rows.

## Harness failure preserved, then corrected

The initial minimal consumer failed before reaching application code: `-n`
omitted POSIX, which its euid guard requires. Both original and exp3 failed on
both PHP versions. Those attempts and the old runner are retained under
[evidence/exp3-runtime/attempts](evidence/exp3-runtime/attempts/).

The corrected minimal **consumer only** loads POSIX/ctype/iconv explicitly, as
required by the real guarded bootstrap. The user/namespace checks remain intact;
no application source or error handler was changed. JSON/parser-only minimal
cases remain `-n` (+ JSON on 7.4). Codex, Claude and Cursor reran the corrected
batch; all four consumer rows now execute successfully.

## Diagnostics remain open

Exit zero is not a diagnostic-clean PASS. Full stderr is retained per row:

- PHP 8.3 legacy JSON creates dynamic `Services_JSON::$use`.
- PHP 8.3 Zend decoder creates dynamic `Zend_Json_Decoder::$_tokenValue`.
- The real consumer still exercises deprecated libxml disabling, Zend_Config
  interface return signatures, an optional-before-required service parameter,
  ReflectionParameter::getClass and legacy Serializable implementations.
- PHP 7.4 still reports the legacy Services_JSON_Error constructors. Error paths
  with and without PEAR require separate checks; disappearing warnings in 8.3
  are not proof that historical constructor behavior is preserved.
- Standard consumer mode logs three missing cache host/port messages per run;
  the synthetic configuration does not establish actual cache-service acceptance.

[Candidate diagnostic lines](evidence/exp3-runtime/candidate-diagnostics.json)
are occurrence evidence, not a count of distinct bugs or approved exceptions.
The repaired exp3 **doc-comment and doc-comment-export have empty stderr** on
both runtimes/INIs. The original 8.3 parser still has dynamic-property notices.
No blanket suppression or production compatibility adapter was introduced.

## Independent review and limitations

Grok timed out at 120 seconds, exit 124, without final JSON. Authorized OpenCode
Muse Spark Free then executed the **119-test local suite** and independently
reviewed the runtime reports/value parity. Claude/Cursor also reviewed the
runner they executed; Codex reconciled their independent results.

The first OpenCode review confused its 2,000-character display excerpt with
stored evidence truncation and grouped exp3 parser with original warnings.
Authoritative reports store `run.stderr` in full and show the clean exp3 parser
rows. The original review is retained; the correction is recorded separately.

[Structured result](evidence/exp3-runtime/result.json) records hashes, row exits,
comparisons and remaining diagnostics. Per-row durations are operational
measurements, not the approved benchmark workload. The batch itself returns zero
after collecting rows, even when a row fails; it is **not an acceptance checker**.

This matrix does not exercise the patched PDO/date paths through SQL/session
requests, actual Apache HTTP/TLS, cross-runtime application object migration,
cache backends, workers/media/UI or recovery. Those remain required. Next, run
API/SQL/Apache from this same extracted artifact, then repair and independently
retest the confirmed JSON/consumer diagnostics. No task is checked complete and
no package/CI, release, main merge or `.20` cutover is authorized by this result.
