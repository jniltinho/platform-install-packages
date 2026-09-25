# exp11 preflight — Claude CLI executor/reviewer (claude-opus-5-5)

Status: PREPARED_NOT_SELECTED. Not selection, ZIP, runtime or application approval.
Env: local worktree, Python 3.12.3, GNU patch 2.7.6 (/usr/bin/patch). No VM/SSH/SQL/network/git.
Inputs: all 72 pins in review-input-identities.json re-hashed, 0 mismatches.
Original ZIP sha256 unchanged before/after (58d534d0…b0ab28).

| Case | Command | Exit | Result |
|---|---|---|---|
| preflight | stage.py --check-only --report claude-preflight.json | 0 | 63 replays, all exit 0, diagnostics only "patching file"; report byte-identical to preflight-final.json (sha256 7a05c7dd…3048); stdout identical; stderr empty |
| unittest | unittest discover tools/php83/exp11-candidate | 0 | Ran 23, OK (synthetic fixtures only) |

Note: both commands ran concurrently; tests use private temp fixtures, not the ZIP or evidence paths.

## Observed
- manifest[:59] == exp10 patches (fields+order); +4 = ternary, HTMLPurifier, CLI, sfCore; 63 unique paths/leaves.
- sfCore not in prior 59; taken once from symfony-bootstrap.json. Other bootstrap rows (sfRouting/UrlHelper/sfFinder/Spyc via curly-offset variants in prior; sfToolkit/sfConfigHandler) not selected.
- Ternary manifest: 1 changed target, 7 unchanged helpers verified against ZIP bytes.
- Four held patches: exactly 2 header lines, 0 git metadata lines.

## Advisory findings (no defect blocking preflight)
1. Header check scans every line starting "--- "/"+++ "; hunk content removing "-- x" or adding "++ x" would false-reject (fail-closed). `diff --git`/mode lines are not rejected; mode changes would pass undetected (none present).
2. Post-replay file-set check uses rglob is_file: empty dirs / dangling symlinks not detected. Low risk with -p1 + header check.
3. manifest.json itself is not hash-pinned by stage.py (reported only); non-selection fields (known_limitations, extra keys) are unvalidated. Covered externally by review-input-identities pin.
4. Untested branches: fuzz and reversed specifically (only offset tested), unexpected replay output files, cumulative drift, ternary helper byte drift, nonregular/duplicate ZIP members, main() --report/--output refusal and mutual exclusion.
5. Report does not record patch/python version or test_stage.py hash; `preflight_sha256` is stage.py hash (naming).
6. Textual disjointness is proven; behavioral composition of sfCore (throws when SPL absent) with curly-offset Symfony variants and the new autoload patches is not. Composition qualification remains pending.

Limits: preflight success != PHP 8.3 application compatibility; no PHP executed.
