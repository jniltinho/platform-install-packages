# exp12-runtime — Cursor independent LOCAL comparator review

- Case: bounded `exp12-runtime` comparator / retained reports (repository-only)
- Executor/reviewer: Cursor Agent
- Environment: `/home/nilton/Projetos/nilton/NOVOS/platform-install-packages-php83`; no VM/SSH/network; no external-artifact directory; no complete comparator run; no ZIP join
- Date (UTC): `2026-09-26T17:02:39Z`
- Final comparison artifact read: `comparison-runtime.json` (repo name; prompt alias `finalcomparison-runtime.json`)

## Verdict

Filtered **18**/22 local guard tests **PASS** (exit 0). Frozen comparator pins verify. Retained `comparison-runtime.json` status is `PASS_BOUNDED_RUNTIME_COMPARISON` with `application_acceptance: false`. Strict matrix and exact API diagnostic drop **18/503 → 17/371** (only the reviewed 132-count Criteria marker group) hold against repo reports. This is **not** full-application or release acceptance.

## Executed by this review

| Step | Command / check | Exit | Result |
|---|---|---|---|
| 1 | `sha256sum -c doc/php83/evidence/exp12-runtime/comparator-frozen.sha256` | **0** | All 6 listed paths OK (`compare-runtime.py`, `test_compare.py`, `comparison-runtime.json`, `criteria-source-identities.json`, `tools/php83/exp12-api/validate-additions.py`, `tools/php83/exp12-api/compare-identities.py`) |
| 2 | Python `unittest` load of `doc/php83/evidence/exp12-runtime/test_compare.py`; suite filtered to names **not** starting with `test_additions_` | **0** | **Ran 18 tests … OK** (~0.07s); failures=0 errors=0 |

### 18 tests executed (all ok)

`test_api_active_cleanup`, `test_api_bool_exit`, `test_api_control_removed`, `test_api_diagnostic_loss`, `test_api_fixture_positive`, `test_api_missing_row`, `test_api_response_drift`, `test_api_same_db`, `test_classes_fixture_positive`, `test_cli_bool_exit`, `test_cli_duplicate`, `test_cli_fixture_positive`, `test_cli_stderr_drift`, `test_criteria_native_noise`, `test_criteria_positive`, `test_generator_drop_row`, `test_generator_positive`, `test_runtime_drift`

### Explicitly not executed by this review

- Four unit cases: `test_additions_fixture_positive`, `test_additions_missing`, `test_additions_wrong_control`, `test_additions_bad_summary` (they invoke `additions_comparison` → live `validate-additions.py` → **external ZIP** joins)
- Full/complete `compare-runtime.py` main reconciliation
- Any external ZIP open / source-join rehash outside committed manifests
- Parent recorded **22**/22 comparator unit suite / full run (`comparator-tests.exit` 0, log “Ran 22 tests … OK”) — prior evidence only; **not** this reviewer’s execution

## Matrix review (read-only vs `compare-runtime.py` + `comparison-runtime.json` + retained primaries)

| Scope | Claim reviewed | Local finding |
|---|---|---|
| API 4 | rows `74/original`, `83/original`, `83/exp11`, `83/exp12` | Matches `api-primary.json` / comparison `logical_rows: 4` |
| CLI 48 / typed 20 | 48 logical; 44 positive; 4 original83 JSON fatals; 20 typed equals | Matches comparison + `cli_comparison` totals |
| Curly 68 | 3 classes → 20+20+28 | Matches; `all65_source_runtime_coverage: false` retained |
| Additions 17 | processes 17; historical collector `FAIL` retained; app acceptance false | Matches comparison summary; allowance adapter separate |
| Generator 72 | 72 rows; 12 changed debug / 60 unchanged | Matches `generator-primary.json` ≡ `claude-generator-r2.json` (same sha256) |
| Criteria 4 | 4 modes `prior-filter` / `candidate-filter` / `prior-returns` / `candidate-returns`; 19 filter + 16 return + 2 invalid controls | Matches; `strict_cross_engine_layout: FAIL_RETAINED`; `application_acceptance: false` |

### Exact diagnostic group drop

From retained `exp11-runtime/api-primary.json` (83/exp11) vs `api-primary.json` (83/exp12):

- Prior: **18** groups / **503** events
- Candidate: **17** groups / **371** events
- Removed exactly one group: `ApplicationDiagnostic` @ `/audit/app/alpha/apps/kaltura/lib/criteriaFilter.class.php:51` count **132**
- `503 − 132 = 371`; `prior_diagnostics without that group == candidate diagnostics` (**no other loss**)

### Additions allowances (9 source-hash fields only)

- `comparison-runtime.json` lists exactly **9** `allowed_loaded_field_changes`; `all_other_stdout_stderr_exit_bytes_exact: true`
- Case/path set matches `validate-additions.py` contract (8× `pakeApp.class.php` across autoload/composition + 1× `sfPakeGenerator.php` on `cli-tasks-configured`)
- Committed manifests only (no ZIP): `exp12-candidate/selected-manifest.json` pin `593ff6e8…74d6` and `exp11-candidate/selected-manifest.json` pin `99f87bf7…f2ff` match live files; both TARGET paths present with before/after hashes cited by the allowance list
- Historical additions status `FAIL` / error string preserved in comparator policy; `application_acceptance: false`

## Ledger freshness binding

- `primary-execution-ledger.jsonl`: **17** ordered phase lines
- `primary-ledger-binding.json`: **17** entries, every `sha256_matches: true`, phase list identical to ledger
- `freshness_scope`: actual collector invocations recorded in order by owner, bound to output hashes — **not** inferred from identical snapshot bytes
- `compare-identities.py` documents the same gap: distinct paths alone are not freshness proof without the ledger

Independent Claude r2 ledger `claude74-r2-execution-ledger.jsonl` records UTC start/end, process exits, and output sha256 for runtime-before → generator-r2 (exit 2) → validation (exit 0) → runtime-after; orchestrator terminal with `stopped_at_unexpected_exit: null`.

## Interrupted generator SIGTERM preserved; r2 completed

- Preserved: `claude-generator.json` sha256 `e1231601…0b92`, status `FAILED_OBSERVATION_VALIDATION`, failures `Unknown lint status` on row `74/prerequisite/generate/rotate-false`
- Concrete signal: lint for `batch/rotate_log_auditapp_prod.php` has `"exit": -15` (SIGTERM); file remains distinct from successful r2 output
- Incomplete original `claude74-execution-ledger.jsonl` stops after additions-revalidated (no generator completion) — preserved as historical interruption context
- Independent r2: `claude-generator-r2.json` sha256 `c6cbdeb9…40da` (= `generator-primary.json`); collect exit **2** (expected observation); validation exit **0**; used as comparison input

## New source harness review (static only; no runtime execution)

- Harness maps in `api-primary`, `cli74-primary`, `cli83-primary`, `curly-primary`, `additions-primary`: **0** local hash mismatches vs `tools/php83/**`
- Collector pins match live tools for API/curly/additions/runtime74/runtime83 collectors
- Generator `harness_sha256` (7 tool files under `tools/php83/exp12-api/generator/`): **0** mismatches
- Criteria: `identities` byte-equal to `criteria-source-identities.json`; `identities_sha256` matches that file
- No collector/stage/SSH/runtime re-execution in this review

## Findings

1. Filtered 18-case local guards pass; frozen pins intact; retained comparison status consistent with reviewed matrices.
2. Exact API diagnostic delta is only the 132-count Criteria marker group (18/503 → 17/371).
3. Additions nine-field loaded-hash allowance is pinned in committed comparison + validator source; ZIP byte re-proof was **not** redone here by design.
4. Ledger binding and interrupted SIGTERM-15 generator report are present; r2 generator path completed independently and matches primary generator bytes.

No comparator gate-logic defect found within the reviewed local scope.

## Limitations (untested / not claimed)

1. Four `test_additions_*` cases and any live external ZIP join — **not executed by this reviewer**.
2. Complete `compare-runtime.py` write/reconcile — **not re-run** (existing `comparison-runtime.json` read only; refuse-overwrite design).
3. Parent 22-test / full comparator PASS is prior evidence, not this execution.
4. No VM/SSH collector freshness re-proof; ledger binding reviewed as committed text only.
5. Criteria cross-engine cache layout remains `FAIL_RETAINED` — not waived.
6. Generator `native_contract_independent_oracle: false`; no generated-application semantic acceptance.
7. No full application acceptance, package/CI integration, `.20` cutover, or release claim.

`application_acceptance: false` everywhere reviewed.
