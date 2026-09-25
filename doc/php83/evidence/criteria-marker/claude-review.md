# Claude independent preparation review — criteria-marker

Executor/reviewer: Claude CLI (Opus 5.5), repository-only. Author: another provider.
Scope: `tools/php83/criteria-marker/{prepare.py,probe.php,run.sh,compare.py,test_prepare.py,test_compare.py,source-pins.json}`, `doc/php83/criteria-marker.md`.
Not done: prepare main (original ZIP is external), run.sh runtime, PHP/VM/SSH, /tmp, retries of another provider's denied read.

## Executed
- `python3 -m unittest discover -s tools/php83/criteria-marker -p 'test_*.py' -v` → exit 0, 14 tests OK (`claude-tests.{stdout,stderr,exit}`).
- `bash -n tools/php83/criteria-marker/run.sh` → exit 0, no output (`claude-bash.{stdout,stderr,exit}`).

The 14 tests are local synthetic guard tests only (4 for `propose`, 10 for `validate` on fabricated bodies). They exercise no PHP, `prepare()`/ZIP/pin logic, probe.php, run.sh sandbox or cross-version serialization. The source pins and line 51 were not verified against the original ZIP.

## Checked, no defect found
- Case inventory: probe.php:27-39 records exactly 15 cases in the same order as compare.py:7. Representation paths (probe 27,29,33,39) match compare.py:48.
- Native warnings: probe.php:8 returns false and run.sh:21 sets `display_errors=stderr`, so native output is kept. compare.py:42 requires the native stderr text for original83.
- 4-mode comparator: exact order (31), int exit==0 (34), runtime prefix/variant (36), source identity (38). Functional parity is checked separately from representation deltas (44-55). Deltas never set parity/selection (55).
- `propose` fails closed on 0 or 2+ anchors and on an already-present property (prepare.py:14).

## Findings
1. **HIGH (probable, runtime-unverified)** — run.sh:21 `php -n` loads no ini files. On Debian/Ubuntu PHP 7.4, `json` is a shared module loaded via ini, so probe.php:42 `json_encode`/`JSON_THROW_ON_ERROR` may be undefined on the 7.4 baseline. That fails closed (non-zero exit) but would block the 74 modes. Before scheduling, confirm `php7.4 -n -m | grep json` on the VM (read-only), or load the module explicitly.
2. **MEDIUM** — compare.py:39-43 only filters marker events. Every other event/stderr difference between original and declaration (for example, new warnings in declaration83) is collected (47) but never compared or rejected. That means "functional parity" can pass even though the declaration variant has new diagnostics. Compare the non-marker event sets per runtime, or at least report their deltas.
3. **MEDIUM** — compare.py:41 hard-codes `criteriaFilter.php` line 51 as the marker assignment. This was not verified locally against the pinned source (fc4cefcb…). Also, `any()` accepts extra marker events in other phases/files (for example, probe.php:31 presets) without listing them.
4. **MEDIUM** — run.sh:10-14 verifies the files listed in `identities.json`, but `identities.json` itself is not pinned: the files dict (prepare.py:29) does not include it. The directory is writable by vagrant, and there is a TOCTOU window between the hash check and `exec` at line 15. Also, `is_symlink` only checks the final path component. The doc (line 18-19) delegates before/after verification to the parent. That requirement should be enforced, not just described.
5. **LOW** — compare.py has no check that `body` came from the raw stdout (no stdout bytes/hash in the record). "Decoded exact stdout" (doc:28) cannot be verified.
6. **LOW** — probe.php:23 `get_object_vars` → json_encode only serializes public props of nested Criterion objects, so `public_vars` is a shallow representation. The serialized bytes cover the full representation.
7. **LOW** — probe.php:38 embeds the `Throwable` message in the functional result. Engine message wording differences between 7.4 and 8.3 would appear as a behavior difference (a false negative that fails closed).
8. **LOW** — Test gaps: nothing covers compare.py:43 (unexpected marker diagnostic in declaration/74), the php version mismatch (36), a broken roundtrip (15), a missing representation path (48), or `prepare()` drift/duplicate/existing-output. prepare.py:10 `PINS={}` is dead code. prepare.py:23 raises KeyError, not ValueError, when a member is missing (still fails closed).

## Status
Preparation review complete. No runtime, PHP lint, cross-version serialization import or descendant collision test was executed; the doc (35-38, 42) correctly says these are pending. This is not execution evidence and not application acceptance. Finding 1 should be resolved before VM scheduling.
