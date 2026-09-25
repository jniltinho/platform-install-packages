# Claude review — criteria-marker/attribute (repository-only)

- Case: independent static review of `tools/php83/criteria-marker/attribute/` + `doc/php83/criteria-marker.md` §"Attribute follow-up v1 preparation" (lines ~209-236).
- Executor/reviewer: Claude CLI (Opus 5.5). Author: not Claude. Repo-only; no VM/SSH/PHP, no collect.py/prepare main, no /tmp reads.
- Commands: `python3 -m unittest discover -s tools/php83/criteria-marker/attribute -p 'test_*.py' -v` → exit 0, 14 tests OK (`claude-tests.{stdout,stderr,exit}`); `bash -n tools/php83/criteria-marker/attribute/run.sh` → exit 0 (`claude-bash.{stdout,stderr,exit}`).

## Verdict
No blocking defect found in probe/collector/compare logic. Release gate unchanged: nothing executed on labs; attribute74 parse/behavior and all 83 byte-exact imports remain UNPROVEN until native runs.

## Checked (holds)
- Full originals: 5 sources ZIP+hash pinned (`prepare.py:9,21-22`, `source-pins.json`); only DBAdapter/Propel stubbed (`probe.php:10-11`).
- Attribute transform: single anchor, must be exact line 38, no pre-existing attribute (`prepare.py:12-14`); compare remaps attribute lines >=39 by -1 (`compare.py:69`) — consistent with the insertion.
- 19-case matrix: probe `recordCase` order == `compare.CASES` (`probe.php:31-47`, `compare.py:5,35`).
- attribute74 must execute: required ordered mode, exit 0, 7.4.x, rows identical to original74 (`compare.py:27-37`); no dynamic-property events allowed on 74 (`compare.py:44`).
- myCriteria hint + KalturaCriteria inheritance: original83 must emit both real warnings (`compare.py:45-47`); attribute83 must emit no hierarchy target (`compare.py:49`) — tests inherited attribute.
- Unrelated control: exactly one E_DEPRECATED (8192) handler event plus native stderr in both 83 modes (`compare.py:41-43`).
- Legacy payloads: derived from recorded original74 rows only (`collect.py:65`), 7 exact paths (`compare.py:6,23`), bound to original74 again in compare (`compare.py:58`); 83 re-serialization must be byte-identical to 74 bytes (`compare.py:57`) and original83/attribute83 imports equal (`compare.py:59`); unserialize class allow-list (`probe.php:53`).
- Fresh immutable stage: `mkdir` (fails if exists) + root-owned + a-w (`collect.py:46`); parent-supplied manifest pin, verify pre/post in run.sh (`run.sh:10-13`); parent source hashes before/after, runtime before/after compared (`collect.py:48-61`).

## Non-blocking findings
1. `compare.validate` never checks that `identities83.files['legacy.json']` == sha256 of the canonical `payloads` JSON (nor that 74 legacy.json is `{}`); binding currently relies on collector code path, not the comparator (`compare.py:26-58`, `prepare.py:30`). Suggest one assert.
2. Runtime identity is before/after only, not pinned to an expected value (`collect.py:59-61`); acceptable for drift, not for provenance across cycles.
3. Stage extra-file check absent: `source()`/verify.py hash only manifest names, not directory listing (`collect.py:48`, `verify.py:14-17`). Low risk given fresh mkdir.
4. Probe correctness depends on real KalturaCriteria/myCriteria loading with only the stubs listed; not verifiable repo-only (pinned sources live in the forbidden ZIP). A load-time dependency would surface as nonzero exit, not a false pass.
5. `attribute74_executed: True` / `hierarchy_exemption_broader_than_marker: True` are hard-coded constants (`compare.py:74`); fine since reached only after checks, but the second is an assertion of design, not evidence.

## Untested scope
All lab execution (4 processes), PHP 7.4 attribute-as-comment parse, 8.3 unserialize deprecation behavior, byte-exact 74→83 serialization. No patch/attribute selection; no application acceptance.
