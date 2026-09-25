# Claude native PHP 8.3 runtime repeat — exp11 regression batch

- Case: independent fresh execution of the 36-row exp11 native CLI regression batch plus before/after runtime snapshots on `kaltura-php83-lab` (alias `php83`, port 2200).
- Executor/reconciler: actual Claude CLI (claude-opus-5-5). Primary reviewed: `cli83-primary.json`, `runtime83-before.json`, `runtime83-after.json`.
- Nothing restaged; no source/tool/patch/package/git/service/.20/SQL edits.

## Commands and exits (local wall clock of batch: 2026-09-25T21:48:44Z–21:48:51Z)

| Step | Command | Exit |
|---|---|---|
| 1 | `python3 doc/php83/evidence/exp10-runtime/snapshot-php83.py …/claude-native83-runtime-before.json` | 0 (39 files, 2 modes, empty stderr) |
| 2 | `ssh -T -F /tmp/kaltura-php83-ssh.conf php83 'python3 /home/vagrant/php-exp11-regression/exp11-regression/batch.py'` | 0 (empty stderr) |
| 3 | same snapshot wrapper → `…/claude-native83-runtime-after.json` | 0 (39 files, 2 modes, empty stderr) |

## Reconciliation (`claude-native83-comparison.json`, verdict PASS)

- Both primary and fresh: exact ordered 36 unique triples (original, exp10, exp11) × (standard, minimal) × 6 cases; every `exit` is `int`.
- 32 rows exit 0; exactly 4 exit 255: `original` × {standard, minimal} × {legacy-json, zend-json}, empty stdout, stderr carries the concrete PHP 8.3 compiler fatal
  "Array and string offset access syntax with curly braces is no longer supported" (`Services_JSON.class.php:176`, `Zend/Json/Encoder.php:557`), identical to primary.
- All 36 rows: native stdout/stderr/exit match primary byte-for-byte; only `duration_ns` differs.
- Batch metadata (schema, host, zip_sha256 `f2474f5b…44a7`, 15240 verified files, harness hashes, previous_artifact exp10 `de177e6c…c053`/15236, unsupported_cases `[]`, application_acceptance `false`) strictly equal; `recorded_at_utc` new (VM clock `2026-09-25T22:03:41Z`, ahead of local clock).
- Remote `batch.py`/`run-one.sh` hashes equal the local frozen pins.
- Runtime identity (PHP 8.3.6 NTS, php8.3 sha256 `1c564e6b…c7d8`, 39 files, linked libraries, modules and INI configs for both modes) identical across primary before/after and fresh before/after; canonical identity sha256 `4d94383a…5975`. Snapshot files are byte-identical to primary (`83b656a2…9491`), expected because the collector emits no timestamp.
- All 22 pinned local inputs (`claude-native83-input-identities.json`) unchanged after the run.
- Fresh CLI JSON sha256 `f556b3c5…3358`.

## Limitations

- Covers only these 36 native PHP 8.3 CLI cases. Not PHP 7.4 baseline semantics, not HTTP/API/DB, not full application acceptance.
- Same VM, staged artifacts and harness as primary: independence is fresh execution plus separate reconciliation, not a separate environment.
- No release, parity or completion claim.
