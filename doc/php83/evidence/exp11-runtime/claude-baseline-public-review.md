# Claude baseline74 exp11 runtime repeat — public review

Executor/reviewer: actual Claude CLI (claude-opus-5-5), exclusive `baseline74` alias via `/tmp/kaltura-php74-ssh.conf`.
Each step wrapped as `timeout -s INT -k 30 300 ...` (SIGINT so the API collector `finally` cleanup would run); Python steps with `PYTHONDONTWRITEBYTECODE=1`. Observed host command bounds do not overlap: fresh stdout redirection precedes each invocation and .exit creation follows completion. See claude-baseline-serialization.json. Tool-call grouping alone does not prove serial execution; no process-level monotonic trace was captured.

| Step | Command | Exit | stderr bytes |
|---|---|---|---|
| runtime-before | `runtime-identity.py claude-runtime-before.json` | 0 | 0 |
| api | `collect.py claude-api.json` | 0 | 0 |
| cli74 | `ssh ... baseline74 'python3 .../exp11-regression/batch.py' > claude-cli74.json` | 0 | 0 |
| curly | `collect-curly.py claude-curly.json` | 0 | 0 |
| additions | `collect-additions.py claude-additions.json` | 0 | 0 |
| runtime-after | `runtime-identity.py claude-runtime-after.json` | 0 | 0 |

`claude-baseline-cli74.stdout` is an empty placeholder: step 3 stdout is `claude-cli74.json`.

## Results
- Runtime: 55 files, 3 runtime modes; before == after == primary runtime-before/after (byte-identical, sha256 a7c9a22f…).
- API: 4 rows — 74/original rc0; 83/original rc1 with KalturaPDO::query() signature failure (15 diagnostic groups); 83/exp10 rc0 (18); 83/exp11 rc0 (18). functional_checks_passed=true. Own synthetic DB unit `php83-exp11-api-9280ef72…` stopped (`inactive`).
- CLI74: 12 original rows (standard+minimal INI x 6 cases), all exit 0.
- Curly: 3 class files, 68 cases, all match prior candidate83; report byte-identical to curly-primary.json.
- Additions: 17 processes PASS (16 positive + 1 expected duplicate-include fatal, 147 ternary rows); byte-identical to additions-primary.json.
- Frozen inputs (24 entries in claude-baseline-input-identities.json): unchanged after run.

## Differences vs primary
- Excluded as legitimate: API per-record duration_ns, db.unit/db.datadir/cleanup.unit (UUID); CLI per-row duration_ns, recorded_at_utc.
- NOT excluded, disclosed: API `stderr_sha256` differs for all 4 records (see claude-baseline-comparison.json). Raw stderr is not persisted by the collector, so the cause was not determined here. Diagnostics, runtime observations, stdout, return codes, signature control, artifact/harness identities all identical.

## Limits
No application/release acceptance. exp11 is PHP 8.3-only: no original74 exp11 support claim. Not AIO/FPM. Single repeat on one lab VM.
