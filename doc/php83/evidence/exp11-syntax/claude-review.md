# exp11 paired compiler repeat — Claude (actual CLI) independent execution + review

- Case: exp11 paired whole-artifact PHP 8.3 `-n -l` compiler audit, fresh repeat (not a replay).
- Executor/reviewer: Claude (Opus 5.5) CLI, sole php83lab user for this repeat. No baseline74, no .20.
- Environment: SSH alias `php83` (`/tmp/kaltura-php83-ssh.conf`), host guard `kaltura-php83-lab`, uid 1000;
  systemd-run sandbox (PrivateNetwork, socket syscalls denied, ProtectSystem=strict, ProtectHome,
  read-only binds of tools/ZIPs/trees, /opt/kaltura + MySQL paths inaccessible). Only `php8.3 -n -l`.

## Commands and exits
| Step | Command | Exit |
|---|---|---|
| 1 | `ssh -T -F /tmp/kaltura-php83-ssh.conf php83 'bash /home/vagrant/php-candidate-syntax-exp11/tools/run.sh'` (21:38:11Z–21:38:41Z) | 0, stderr empty |
| 2 | `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tools/php83/exp11-syntax -p 'test_*.py' -v` | 0, Ran 38, OK |
| 3 | `python3 tools/php83/exp11-syntax/compare.py primary.json claude-scan.json claude-compare.json` | 0 |

## Identities
- claude-scan.json sha256 `69163332de53dba8fddb30d698d043b73349f92974f01178ec240e2cba5c4edd`; primary.json `e6c11b07…bff7`.
- Pins inside scan: exp10 `de177e6c…c053`, exp11 `f2474f5b…44a7` (match task-stated pins).
- Harness in-report: run.sh `c5d257ca…`, scan.py `b6dd5359…`, stage.py `761f70f4…`, input-contract.json `5a8e3999…`,
  compare.py `c2910c60…` — equal to local files. Runtime `/usr/bin/php8.3` 8.3.6 NTS, sha256 `1c564e6b…d7`, no ini loaded.
- Frozen local inputs (primary.json, frozen-tools.json, tools/php83/exp11-syntax/*) re-hashed after run: unchanged.

## Results (targeted fields)
- compare stdout: "23568 independent logical rows equal; 4 repairs compile; 7 rejections remain";
  `reports_equal_except_record_duration_ns: true`, all 9 checks true, `bounded_regression_pass: true`.
- exp10: 11784 scanned, 11 rejected, 11773 accepted, 0 incomplete, 77 diagnostic files, 66 accepted-with-diagnostics.
- exp11: 11784 scanned, 7 rejected, 11777 accepted, 0 incomplete, 73 diagnostic files, 66 accepted-with-diagnostics.
- delta = exactly 4 (all source_changed, 255→0, empty exp11 diagnostics): baseObjectUtils.class.php,
  HTMLPurifier.autoload.php, symfony-data/bin/symfony.php, symfony/util/sfCore.class.php.
- No unchanged-source outcome/diagnostic differences; no newly accepted-with-diagnostics.
- 7 remaining rejects retained, NOT waived: 6 symfony-data raw templates/skeletons + vendor/aws/Doctrine/Common/Cache/RiakCache.php.
- Scanner guards reviewed in source: contract pin check, read-only mount assertion, archive inventory pre/post
  (drift fails), runtime identity + harness hash pre/post, identical pathset. Guards are self-enforced by scan.py;
  exit 0 implies they passed.

## Limitations
- Compiler/syntax only (`-n`, no extensions beyond built-ins): no includes, autoload, runtime, SQL, or application acceptance.
  `candidate_all_files_compile: false`, `application_acceptance: false`.
- exp11 ZIP has 4 more non-selected files than exp10 (15240 vs 15236; excluded 3452→3456): the four `.php83-experimental/*.patch` provenance files; not compiled by design.
- Same lab/VM/runtime as primary: repeat proves determinism of this environment, not cross-environment parity.
- No parity, release, or cutover endorsement.
