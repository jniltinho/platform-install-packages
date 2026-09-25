# Three-class behavior regression for the held curly-offset batch

Primary execution passes nine real PHP processes and **204 strict case rows**:
Google_Utils (old and 1.1.2 versions, separate processes) each has 20 cases;
HTMLPurifier_Encoder has 28. Each corpus runs on original PHP 7.4, candidate
PHP 7.4 and candidate PHP 8.3. Complete hash-verified class files execute, not
extracted snippets, rewritten functions or dependency mocks. No SQL, application
bootstrap, HTTP requests or external services execute.

The actual methods include Google string length, URL-safe base64 encoding and
decoding, key normalization, HTMLPurifier UTF-8 cleaning (including changed-loop
invalid/control-byte inputs), Unicode encoding boundaries and ASCII entity
conversion. Empty, ASCII, NUL, binary, multi-byte, truncated, surrogate and
out-of-range codepoints are covered. Native array/string type and overread
controls are explicitly fixture-only, not runtime coverage of 43 application files.

Return values are hand-authored explicit expectations, not blind recorded golden
output. Original/candidate PHP 7.4 functional values and runtime diagnostics
match exactly. Candidate PHP 8.3 values match; diagnostic parity is **not** claimed:
original curly-syntax load deprecations disappear, and existing uninitialized
string-offset NOTICE diagnostics on PHP 7.4 become WARNING on PHP 8.3. Native
square-offset overread controls independently reproduce the latter change.

Google's existing `getStrLen` multibyte loop overreads: selected 2-byte/4-byte/mixed
inputs return 3/7/5 with 1/3/1 offset diagnostics. This is retained characterization,
not an endorsed correct byte-count algorithm or a new repair. Error handlers
record diagnostics and return false so PHP still emits them. Expected diagnostic
phase, severity, source basename and line are checked; no warning is suppressed.

The isolated baseline74 stage is `/home/vagrant/php-curly-behavior-r1`. The runner
binds the selected original/candidate source read-only, verifies the source mount,
hides production/configured-service paths, denies socket/socketpair with EPERM,
and uses private network/tmp/devices, no-new-privileges and resource/time limits.
PHP runs with `-n`, explicit E_ALL and only JSON added on 7.4. Interpreter,
linked-library, JSON-module, selected source and harness identities are checked
before/after; the full-file loaded class hash is verified through reflection.
The copied PHP 8.3 runtime is not installed as the baseline's system interpreter.

Eight local collector/fixture tests pass, and the PHP fixture lints on both actual
runtimes. Read-only graph/source inspection and exact three-file patch/ZIP
identities are retained in the `plan-*` files. Separate independent CLI evidence
must be evaluated independently; this note only attests the primary run.

Only **3 of 43 actual class files** are exercised behaviorally. The separate
43-file lexical/token/compiler proof is not a substitute for broader runtime,
application, generation-workflow, external-service or performance acceptance.
No held patch is promoted into an artifact or release by this probe.

## Independent repeat

Obtain exclusive baseline74 ownership; do not recreate/modify the frozen stage.
Use a new output filename and retain stdout/stderr/exit:

```sh
python3 tools/php83/curly-offsets/collect.py \
  doc/php83/evidence/curly-offsets/behavior-claude.json
python3 tools/php83/curly-offsets/test_probe.py
```

Reports with any nonzero process exit or validation error are not passing.
A transport/hash/identity failure can abort before the final report; missing
reports are incomplete, never successful. All source content is the reviewed
public artifact subset; SSH host-key policy remains inherited from the existing
lab rather than newly authenticated by this harness.
