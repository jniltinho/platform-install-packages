# exp12-syntax — Cursor local harness readiness review

- Case: `exp12-syntax` paired compile-only nonregression harness (prep / readiness only)
- Executor/reviewer: Cursor Agent (local, repository-only)
- Environment: repo checkout `/home/nilton/Projetos/nilton/NOVOS/platform-install-packages-php83`; no VM/SSH/network; no artifact-directory access; no PHP native scan
- Date (UTC): `2026-09-26T16:37:51Z`
- Prior OpenCode result preserved: `doc/php83/evidence/exp12-syntax/opencode-prep-outcome.json` → `INCOMPLETE_PERMISSION_DENIAL`, `final_review_written: false`. That denied external-artifact call was **not** retried here.

## Scope (this review)

In scope:

- `tools/php83/exp12-syntax/{README.md,input-contract.json,run.sh,scan.py,stage.py,compare.py,test_scan.py,test_compare.py}`
- Committed provenance reports: `doc/php83/evidence/exp12-candidate/{delta.json,verification.json}`
- Local commands: 40 unit tests + `bash -n run.sh`
- Static adaptation check vs frozen `tools/php83/exp11-syntax` (read-only diff)

Out of scope / not performed:

- Reading ZIP bytes or any path outside this repository
- Staging, `scan.py` main, `compare.py` main, php83lab, native PHP 8.3 `-l`
- Acceptance, compilation, or release claims from the synthetic suite

## Commands and exits

| Step | Command | Exit | Result |
|---|---|---|---|
| 1 | `python3 -m unittest test_scan test_compare -v` (cwd `tools/php83/exp12-syntax`) | 0 | Ran **40** tests, OK (~2.6s) |
| 2 | `bash -n run.sh` (same cwd) | 0 | Syntax OK |

No other executors. Harness unit tests are **not** whole-artifact compiler evidence.

## Identities observed (repo files only)

| Path | sha256 |
|---|---|
| `tools/php83/exp12-syntax/README.md` | `64b19f5498ecd9ccf59c50e23a57344a796db1a3ed3d0b5d190a64de412c1507` |
| `tools/php83/exp12-syntax/compare.py` | `d643f104993e02325ebbd82887a59be353e6d8c2315e76de7402d93c36e18e1e` |
| `tools/php83/exp12-syntax/input-contract.json` | `f1fb66181fd74120e102eb8c227d8b89fb0592dfa5070e4771bc350b455d32b4` |
| `tools/php83/exp12-syntax/run.sh` | `bcbeb6f3b11e10bace34d9971f16b1e18981a9906a78f342411c0380b271e1d3` |
| `tools/php83/exp12-syntax/scan.py` | `fd98fdb419679017363cdb4fe6fc2f0db0dfcbbe5ee84d3055f79e4260e48f3e` |
| `tools/php83/exp12-syntax/stage.py` | `b9b9d5ce9f56183560576d90c6b4a6a2fd1da1988f724dd7ff6c0cc95c37bd5f` |
| `tools/php83/exp12-syntax/test_compare.py` | `19944365cc43c3fe5cde996036805bfff1bafbc8e4e4014e3469522ca6c1fa2c` |
| `tools/php83/exp12-syntax/test_scan.py` | `f9b4dd59ef8c83ab680fd78a21c1b4cafb9c55c72aeb3811b728f94f22d6e3da` |

Contract pins (provenance — not re-hashed from ZIP bytes):

- exp11: `f2474f5b951bfd2d121291025c8dd4554697fb5bb4024e132987643dab6144a7`
- exp12: `de5e61a1b54f472e605ef2e87669302a3915616fd85378e0f05706fcb06a7e8b`

Cross-check vs allowed reports:

- `delta.json`: same exp11/exp12 ZIP hashes; `changed_application_paths` equals the three contract target paths (order match); `application_acceptance: false`; status `PASS_LAB_ARTIFACT_DELTA_ONLY`
- `verification.json`: `zip_sha256` and `repeat_build_sha256` equal exp12 pin; the three targets appear under `changed_files` with `server-Rigel-18.20.0/` prefix

Per-file `exp11_sha256` / `exp12_sha256` values in `input-contract.json` do **not** appear in `delta.json` or `verification.json`. They are treated as contract-declared provenance only; this review did not independently corroborate those six digests.

## Adaptation review (exp11 → exp12)

Structural remapping is consistent across scanner, contract, stage, sandbox, tests:

| Concern | exp11 | exp12 adaptation |
|---|---|---|
| Variants | exp10 / exp11 | exp11 / exp12 |
| Baseline pin constant | `EXP10_PIN` | `EXP11_PIN` (= prior candidate pin) |
| Reviewed targets | 4 previously **rejected** | 3 previously **accepted** |
| Rejection check | `new == old - targets` (11→7) | `new == old` (7→7) |
| Diagnostics | unchanged non-targets | + `target_diagnostics_unchanged` for all three targets |
| Corpus | 11784 PHP-like each | same encoding / same unit fixture size |
| Stage root | `php-candidate-syntax-exp11` | `php-candidate-syntax-exp12` |
| Sandbox binds | exp10/exp11 zip+trees | exp11/exp12 zip+trees; same PrivateNetwork / socket deny / RO binds / `-n -l` only |
| Over-acceptance guards | `candidate_all_files_compile` false; `application_acceptance` false | preserved |

Old “4 newly accepted repairs” assumption is removed from `scan.py` checks and from `test_scan.py` fixtures (`all_targets_previously_accepted`, diagnostic-drift and “old rejection is not assumed repair” tests added). Sandbox and syntax-only flags match exp11 machinery.

## Bugs / defects

1. **MEDIUM — stale comparator success stdout (`compare.py:74`)**  
   Still prints: `23568 independent logical rows equal; 4 repairs compile; 7 rejections remain`.  
   For exp12 the logical row count (23568) remains correct if both variants scan 11784 files, but **“4 repairs compile” is false for this experiment**: three targets are already-accepted runtime-repair nonregression targets, not four newly accepted repairs. This does not fail unit tests (print is untested) and does not alter pass/fail logic, but it is operator-facing overclaim if a future lab compare exits 0.

2. **LOW — comparator result `scope` string still says “compiler repair”** (`compare.py` return payload). Wording mismatch with nonregression semantics; not a gate-logic bug.

No other leftover `exp10` / `Expected 4` / `previously_rejected` / old stage-path constants found under `tools/php83/exp12-syntax`.

No gate-logic defect found in `compare_reports` for the stated exp12 policy (3 accepted targets, identical residual rejection set of size 7, unchanged-source exit+diagnostics identity, target diagnostics unchanged, incomplete exits fail).

## Exact unverified scope

Unverified by this review (and not claimed):

1. Actual ZIP / extracted tree bytes for either pin (no archive access by design).
2. Exact six per-file target digests in `input-contract.json` (absent from the two allowed candidate reports).
3. Native paired scan over 11784 PHP-like files per variant on php83lab.
4. That residual compiler rejects are the same **paths** as exp11’s seven (harness asserts count equality of rejection sets between variants only; paths are produced at scan time).
5. That native diagnostics on unchanged and changed targets are byte-identical to a prior run (encoded policy + unit tests only).
6. Independent dual-scan comparator run against real primary/independent reports.
7. Fresh `stage.py` extraction under lab hostname/uid guards.
8. Application runtime behavior, SOAP/includes, package/CI/release cutover.

## Verdict

**PASS_LOCAL_HARNESS_READINESS** — with one non-blocking medium defect (stale “4 repairs compile” stdout).

Meaning: repository harness + contract adaptation are ready for a later, separately authorized staged native scanner. This is **not** syntax acceptance, not compilation proof, and not application acceptance. Forty synthetic tests do not verify archive pins or the live 11784-file corpus.

## Not claimed

- exp12 ZIP identity verified from bytes
- php83lab syntax scan executed
- independent dual scan comparison
- seven residual rejects path-listed
- application acceptance / release readiness
- OpenCode prep review completed (remains `INCOMPLETE_PERMISSION_DENIAL`)
