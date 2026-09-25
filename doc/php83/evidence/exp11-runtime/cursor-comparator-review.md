# Cursor independent comparator review — exp11-runtime

Scope: read-only local review of `compare-runtime.py` / `test_compare.py` against
predecessor `doc/php83/evidence/exp10-candidate/compare-runtime.py`, current
primary reports, `doc/php83/evidence/exp11-candidate/selected-manifest.json`, and
actual Claude repeat JSON inputs. No SSH/VM, no source edits, no `.env` /
credentials / `/tmp` / agent-stream reads. Bounded lab evidence only.

Executor: Cursor Agent. Reviewer role: independent comparator semantics.
Frozen pins: `comparator-frozen.json` matches live
`compare-runtime.py` / `test_compare.py`
(`7f6ea173…e8b7` / `e47b23e8…33ef`).

## Executed evidence

| Step | Command / artifact | Exit |
|---|---|---|
| Unit tests | `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s doc/php83/evidence/exp11-runtime -p test_compare.py -v` → `cursor-comparator-tests.{stdout,stderr,exit}` | **0** (18 tests OK; unittest verbose on stderr) |
| Comparator (final) | `compare-runtime.py --output …/cursor-comparison-runtime.json` → `cursor-comparison.{stdout,stderr,exit}` | **0** |
| Comparison report | `cursor-comparison-runtime.json` | status `PASS_BOUNDED_RUNTIME_COMPARISON`, `application_acceptance: false` |

Note: a first comparator attempt during concurrent Claude baseline arrival returned
exit **2** / `PENDING` with `missing_inputs: ["claude-runtime-after.json"]` only.
After all 18 INPUTS were present on disk (Claude baseline collectors exit 0),
the comparator was re-run; that final run is the retained `cursor-comparison.*`.
No runtime reports were synthesized by this review.

## Verdict

Comparator logic is a faithful exp11 port of the exp10 strict reconciler: pending
inputs cannot become PASS, matrices/controls/pins match the primary corpus, and
the final bounded comparison PASSed with `application_acceptance: false`.
Unit tests are local duplicated-fixture guards only — not independent application
execution. No release or application acceptance is claimed.

## Checks

### Exact matrix

- API: `74/original`, `83/original`, `83/exp10`, `83/exp11` (4 rows).
- CLI: 74 → 12 (`original` × 2 ini × 6 cases); 83 → 36
  (`original|exp10|exp11` × 2 ini × 6 cases); totals 48 / 44 positive / 4 fatals.
- Curly classes: `google-old`, `google-new`, `purifier` → 20+20+28 = 68 cases;
  `all63_source_runtime_coverage: false` (honest; selected-manifest has 63 patches).
- Additions: exact ordered 17 processes via `collect-additions.reference_records()` /
  `validate()` (1 ternary + 6 autoload + 10 composition); summary
  16 positive + 1 expected duplicate-include fatal; 147 ternary functional rows.

### Typed comparison

- CLI: exp10/exp11 non-`environment` stdout JSON compared to original74 for same
  ini/case; `doc-comment-export` compares `entries` only → 20 typed equals.
- API: golden stdout / signature_failure / observation counts; exp10 vs exp11
  diagnostics exact 18 groups / 503 events vs historical
  `exp10-runtime/api-primary.json`.
- Additions: full `{exit,stdout,stderr}` byte equality to reviewed candidate83
  corpus (no independent normalization).

### original83 failure controls

- CLI: exactly 4 rows `original` × {standard,minimal} × {legacy-json,zend-json}
  exit **255** with curly-brace fatal text.
- API: `83/original` returncode 1, `signature_failure` true, empty stdout,
  1 runtime observation; non-control rows exit 0 with golden stdout.

### Source / harness pins

- Artifact CURRENT `f2474f5b…44a7` / 15240; PRIOR exp10 `de177e6c…c053` / 15236.
- Collectors pinned to `tools/php83/exp11-api/*` (and native83 snapshot pin to
  `exp10-runtime/snapshot-php83.py`); harness paths remapped under
  `php-exp11-regression` / `exp11-api` / `exp11-regression`.
- Curly source hashes match `exp11-candidate/selected-manifest.json` `after_sha256`
  for the three class paths.
- Additions pins go through `collect-additions.fixtures()` / corpus contract, not
  `verify_harness()` path aliases (by design).

### Native vs copied interpreter equality

- `native83_runtime_identity.copied_and_native83_interpreter_hash_equal: true`
- `/usr/bin/php8.3` == baseline copied
  `/home/vagrant/php-mysql-probe/runtime83/php8.3`
  sha256 `1c564e6b…c7d8`.
- Four native83 snapshots byte-equal; four baseline74 snapshots byte-equal;
  baseline74 scope remains native74 + copied83 (not a fresh php83lab module set).

### API stderr hash limitation and DB cleanup identity

- Normalization excludes only `duration_ns` and opaque `stderr_sha256`; policy
  documents that raw KS-bearing logs were not retained, so differing stderr hashes
  are not attributed solely to timestamps/UUIDs.
- Observed: all four API row stderr hashes differ across primary vs Claude; DB
  tokens distinct
  (`…001aa375…` vs `…9280ef72…`); unit/cleanup identity
  `php83-exp11-api-<token>`, `stopped: true`, `is_active_output: inactive`.

### New 17-addition process contract

- Comparator loads live `collect-additions.py`, recomputes corpus/fixtures/summary,
  requires primary≡Claude report equality, `status==PASS`,
  `application_acceptance is False`, and summary constants above.
- Claude `claude-additions.json` is byte-identical to primary (deterministic
  collector; baseline collector stdout `{"status":"PASS","processes":17}`, exit 0).

### Predecessor delta (exp10 → exp11)

- Inputs add additions pair; rename Claude CLI/runtime83 files to `claude-native83-*`;
  trees/sources `exp9/exp10` → `exp10/exp11`; prior API baseline
  `exp9-api/codex.json` → `exp10-runtime/api-primary.json`; manifest
  `exp10-candidate/manifest.json` → `exp11-candidate/selected-manifest.json`;
  new `additions_comparison` + policy entry. Core fail-closed / pending / typed /
  control / pin structure preserved.

## Independence signals (content)

| Pair | Byte-identical? | Independent signal |
|---|---|---|
| API primary ↔ Claude | No | Distinct DB tokens; stderr/duration differ; normalized rows equal |
| CLI74 / CLI83 ↔ Claude | No | `recorded_at_utc` + all `duration_ns` differ; normalized equal |
| Additions / curly / runtime snapshots ↔ Claude | Yes | Deterministic collectors; process provenance outside comparator (`claude-baseline-*.exit` 0 / native83 public review) |

## Defects / limits (concrete)

1. **Unit tests ≠ application proof.** `test_compare.py` docstring is correct:
   duplicated local fixtures only. 18 OK does not prove VM/lab independence.
2. **No full selected-manifest runtime coverage.** Classes assert 3 probes / 68
   cases; `all63_source_runtime_coverage` remains false.
3. **Comparator does not bind Claude process provenance.** It only reconciles
   report JSON. Byte-identical deterministic reports (additions/curly/runtime)
   would also PASS if files were copied; anti-copy relies on external baseline
   exit/stdout and native83 review artifacts, not on `compare-runtime.py` itself.
4. **Unit coverage gaps vs comparator surface.** No tests for
   `native83_runtime_comparison`, interpreter-hash equality, `main()` PENDING
   path, or typed CLI count 20 — only fixture positive/negative guards.
5. **API stderr opacity is a real equality limit** (acknowledged in
   `normalization_policy.api_stderr_limit`): sanitized-field equality only.
6. **Shared lab/harness with primary.** Fresh execution + separate reports; not a
   separate environment (same limitation recorded in native83 public review).
7. **`primary-summary.json` still labels** `independent_baseline_repeat: "pending"`
   while Claude baseline INPUTS and this comparison now exist — summary drift,
   not a comparator logic bug.
8. **`claude-baseline-cli74.stdout` empty** (exit 0); weaker stdout provenance for
   that one collector versus additions/api/curly/runtime-after one-line summaries.

## Non-claims

- Not application acceptance, release readiness, production parity, or complete
  63-patch behavioral coverage.
- Not a re-execution of collectors by Cursor; only local unittest + comparator
  over already-written reports.
