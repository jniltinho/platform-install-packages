# Exp12 paired compile-only scan — Claude r2 independent repeat

- Case: exp12 paired compile-only nonregression (exp11 vs exp12), independent repeat r2.
- Executor: Claude Code CLI (claude-opus-5-5). Primary scan: pre-existing `primary.json`.
- Environment: exclusively granted native83 lab (`kaltura-php83-lab`) only; no baseline74, no `.20`.
- Prior attempts preserved untouched (`claude-scan.*`, `claude-native-*`); new r2 paths only, written with noclobber.

## Commands and exits

| Step | Command | Exit | Output |
|---|---|---|---|
| Harness pins | `sha256sum` of the 6 frozen files vs `frozen-tools.json` | 0 | 6/6 match |
| Native scan (2026-09-26T16:44:22Z → 16:44:52Z UTC, synchronous) | `ssh -T -F /tmp/kaltura-php83-ssh.conf php83 'bash /home/vagrant/php-candidate-syntax-exp12/tools/run.sh'` | 0 | `claude-r2-scan.json` (17916900 B, sha256 `8bf0b1d191671bfd264e658b43ecc9df0d3d90769b33eec5ccac23d2895ec846`), `.stderr` empty, `.exit`=0 |
| Comparator | `python3 tools/php83/exp12-syntax/compare.py doc/php83/evidence/exp12-syntax/primary.json doc/php83/evidence/exp12-syntax/claude-r2-scan.json doc/php83/evidence/exp12-syntax/claude-r2-compare.json` | 0 | `claude-r2-compare.json` (sha256 `739abe5198fc74e0f80f1492c9fec942d86889afa14487c33ae778113cd3dd13`), `.stdout`, `.stderr` empty, `.exit`=0 |
| Local tests | `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tools/php83/exp12-syntax -p 'test_*.py' -v` | 0 | `claude-r2-tests.log`: Ran 40 tests, OK |

Primary sha256 `ea9f5b6fb98677cd67e2b5c60504088b33c98607c737333fa360d4c8faf5bee1`; comparator sha256 `7519ec906412aa30a4afdc7e140c99b16209bbbf111259180e9ac5db9b38006a`.

## Result summary (from comparator output, not a dump of the 18 MB report)

- Reports equal except per-record `duration_ns`; 23568 logical rows (11784 per variant); `collection_complete`=true.
- ZIP pins verified in-scanner: exp11 `f2474f5b…44a7`, exp12 `de5e61a1…7e8b`; runtime `/usr/bin/php8.3` PHP 8.3.6 NTS, `-n` (no php.ini).
- Both variants: 11784 scanned, 7 rejected, 11777 accepted, 0 incomplete, 73 diagnostic files, 66 accepted with diagnostics.
- 7 → 7 rejections unchanged (same paths as `primary-summary.json`); 3 changed targets still accepted, target diagnostics unchanged.
- Unchanged-source outcome/diagnostic differences: none. Newly accepted with diagnostics: none.
- All 10 comparator checks true; `bounded_regression_pass`=true.

## Limitations

- Compile-only (`php -n -l`) nonregression for 3 runtime-repair targets; no includes, bootstrap, SQL, packages or application body executed.
- `candidate_all_files_compile`=false (7 rejections not waived); `application_acceptance`=false.
- Same lab VM and staged artifacts as the primary scan; repeat is independent in executor/time, not in host or staging.
- This is execution evidence by one executor; it is not an independent review of itself.
