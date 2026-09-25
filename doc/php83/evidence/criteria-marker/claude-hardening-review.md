# Claude hardening follow-up review: criteria-marker

This review follows up on `claude-review.md`. Executor/reviewer: Claude CLI (Opus 5.5). The work was repository-only.
The following were not done: prepare `main`, `run.sh` execution, PHP, VM or SSH access, and source changes.
The parent freezes `run.sh`/`verify.py` at staging. The local `verify.py` is therefore **not** claimed to protect against malicious self-replacement.

## Executed (actual output kept)
- `TMPDIR=<repo>/doc/php83/evidence/criteria-marker/claude-hardening-tmpdir PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tools/php83/criteria-marker -p 'test_*.py' -v`
  → exit 0, `Ran 22 tests ... OK` (4 prepare, 13 compare, 5 verify). Files: `claude-hardening-tests.{stdout,stderr,exit}`.
  TMPDIR pointed to an owned directory inside the repo so the tests did not use /tmp. The directory was empty afterwards and was removed.
- `bash -n tools/php83/criteria-marker/run.sh` → exit 0, empty stdout/stderr. Files: `claude-hardening-bash.{stdout,stderr,exit}`.
- Current SHA-256 of `probe.php`, `run.sh` and `verify.py` = the values in `hardening-identities.json` (c1870d3f…, 13378241…, 9b8e7479…).

## Earlier findings: status
| # | Earlier finding | Status | Evidence |
|---|---|---|---|
| 1 | json74 with `-n` | RESOLVED in code (not observed at runtime) | run.sh:5 `extra=(-d extension=json)` for 7.4 only. compare.py:38 requires the `7.4.`/`8.3.` prefix |
| 2 | Unrelated diagnostics ignored | RESOLVED | compare.py:47-70 compares non-marker events per runtime, fails on mismatch and keeps raw `original`/`declaration` in `deltas` |
| 3 | line 51 / `any()` | PARTIAL | compare.py:43 still uses a fixed line 51, not checked locally against pin fc4cefcb…. `any()` accepts extra marker events in original83 (they are reported in `target_events`, not rejected) |
| 4 | Unpinned identities / TOCTOU | MOSTLY RESOLVED | verify.py:7-17: the manifest pin comes from the parent (run.sh:3,9). It checks the exact 6-file inventory, and symlinks on the base path, the manifest and each file. run.sh:11-13 verifies before and after (trap → exit 70). What remains is below |
| 5 | stdout/body | RESOLVED (semantic) | compare.py:36 `json.loads(stdout)==body`. test_stdout_body_binding |
| 6-7 | shallow `public_vars`, Throwable message | UNCHANGED (LOW, fails closed) | probe.php:23, 38 |
| 8 | test gaps | PARTIAL | 22 tests. Gaps listed below |

## Checked, no defect found
- 15 cases: probe.php:27-39 == compare.py:8 (order), required by compare.py:39.
- Native stderr is kept: probe.php:8 `return false`, run.sh:20 `display_errors=stderr`. compare.py:44 requires the native text for original83. compare.py:77 keeps the stderr hash for all 4 modes.
- Serialization: compare.py:13-15 validates base64/length/sha/roundtrip. compare.py:53 checks the inventory of the 4 paths. compare.py:72-76 reports `serialized_byte_delta` against original74, separately from parity. `exact_representation_parity`, `patch_selected=False` and `application_acceptance=False` are set.
- Line mapping: compare.py:57-65 only moves events from the `declaration.php` file with line ≥40, by −1. `probe.php`/`criteriaFilter.php` events are unchanged. test_unrelated_exact_source_line_mapping (99↔100).

## Remaining blockers and limits
1. **MEDIUM**: compare.py:54-65 hard-codes "anchor on original line 38 → skip at ≥40". This was not verified locally against Criteria.php pin 0626bb5b…, and prepare.py:14 does not record or check the anchor line. If the anchor is on another line, the mapping is wrong. That fails closed (false regression), unless mismatches cancel out. Add an assertion on the anchor line to `prepare`.
2. **MEDIUM**: compare.py:43 has a fixed `criteriaFilter.php:51` that was not verified locally. The `any()` check does not reject additional marker events in original83.
3. **LOW**: compare.py compares **events** between original and declaration, but only hashes native **stderr** (compare.py:77). It does not compare stderr text between variants. Output that skips the handler (for example, a startup or engine message) is not checked for regressions if exit==0.
4. **LOW**: The stdout/body binding is semantic (`json.loads`), not byte-exact, and has no stdout hash. The record producer (collector) is not in this directory, so it was not reviewed.
5. **LOW (TOCTOU / scope)**: between run.sh:11 and the `exec` at 14-21, the vagrant-writable directory can change. The post-run check (13) only detects a change that persists. `verify.py` runs from the stage itself (10). Both depend on the parent freezing the stage, as declared. verify.py:14 raises `KeyError`/`JSONDecodeError`, not `ValueError`, on a malformed manifest (still fails closed).
6. **LOW (test gaps)**: there are no tests for the following: an unexpected marker in declaration/74 (compare.py:45), a PHP prefix mismatch (38), a broken roundtrip (15), a missing representation path (53), a mapping boundary at line 39/40, an extra or missing file in the verify inventory (14), a symlink on the base or on `identities.json` (8,10), or `prepare()` ZIP/pin/existing-output.

## Not executed / release gates
No PHP runtime, sandbox (`systemd-run`), native json74 load, native observation of the line-51 marker or cross-version unserialize was executed. The 22 tests are synthetic local guards and are not execution evidence. There is **no** application acceptance and no patch selection.
