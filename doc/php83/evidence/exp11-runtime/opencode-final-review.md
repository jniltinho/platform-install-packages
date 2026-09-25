# OpenCode final semantic review — exp11 preparation (repo-only)

Scope: `tools/php83/exp11-api/{collect-additions.py,run-additions.sh,stage.sh}`, other exp11-api/regression collectors and tests, and `doc/php83/evidence/exp11-runtime/addition-corpus.json` (in-repo; `tools/php83/exp11-api/addition-corpus.json` does not exist and was not used). No VM/SSH/runtime execution, no pin/source changes, no `/tmp` or external reads. Preserved execution (`25` unit tests OK, `6` per-file `bash -n` PASS) was not re-run; this is semantic review only.

## Verdict

No blocking defect in inspected scope. Preparation harnesses are fail-closed, contained, and correctly scoped as bounded-corpus evidence, not application acceptance.

## Source/artifact binding — PASS

- `collect-additions.py:9` binds to in-repo `doc/php83/evidence/exp11-runtime/addition-corpus.json`.
- `reference_records()` (`collect-additions.py:18-32`): enforces family inventory, `is_relative_to(REPO)` path guard, per-report `sha256` drift check, and corpus identities (ternary `441` positive rows, autoload `FAIL/3`, composition `PASS/30`), then selects exactly one reference process per `(family,case)`.
- `fixtures()`/`verify_fixtures()` (`:42-63`): local `sha256` inventory of `run-additions.sh`, `verify-source.py`, `artifact.py`, all three `probe.php`, and every `fixtures/**/*.php`; non-`api/` entries cross-checked against `fixture_sha256`. Repo inventory reconciles: 3 api + 3 probes + 8 fixture files = 14 pins; contract holds 11 (3 probes + 8 fixtures). No missing entry.
- `main()` (`:67-71,:80`): `read_pin()` first, remote `verify-source.py`, `zip_sha256 == pinned` before and `source()==before` plus fixture re-verify after the 17 runs. Same before/after pattern in `collect.py:40-44,62-64` (exp11 + exp10 reference) and `collect-curly.py:31-41`.

## Missing-pin fail-closed — PASS

- `artifact.py:5-10` accepts only `[0-9a-f]{64}`; missing/malformed raises before any staging or VM contact. `artifact-sha256.txt` is absent in `exp11-api/` (confirmed by repo listing) — intended preparation state, not a defect.
- `stage.sh:11-12` derives the pin via `artifact.py` and `sha256sum --check --strict` before any `ssh`. `collect.py:31-32` refuses existing output. `collect-additions.py:67` refuses existing report. No placeholder hash or exp10 fallback; `README.md:3-6` states this explicitly.

## Side-effect containment — PASS

- `run-additions.sh:4,12-20`: hostname/uid/argc gate (`exit 64`), closed `case` allowlist, `systemd-run` with `PrivateNetwork=yes`, `SystemCallFilter=~socket socketpair`, `ProtectSystem=strict`, `ProtectHome=yes`, `PrivateTmp=yes`, `NoNewPrivileges=yes`, `MemoryMax=512M`, `RuntimeMaxSec=60`, `InaccessiblePaths`, read-only binds, `env -i`, `php8.3 -n` with `allow_url_*=0`, `display_errors=stderr`, `log_errors=0`.
- `run-apache.sh`, `run-curly.sh`, `exp11-regression/run-one.sh` follow the same pattern (host/case gates, read-only binds, ephemeral cache overlays, no network).
- `stage.sh:13` uses `mkdir` without `-p`, so re-staging fails rather than replacing an earlier stage; remote hostname assertions precede writes; extraction verifies zip-against-pin and zip-slip guards (`:17-30`).

## DB-unit cleanup and KS privacy — PASS

- `collect.py:48-61`: per-run `uuid` token, `start-db.sh` identity echo check, `try/finally` stopping only the known `php83-exp11-api-<token>` unit; `cleanup.stopped` is a pass criterion (`:68`). `test_collector.py:16-55` covers malformed startup, untrusted identity (`/var/lib/mysql`/`mysql` cannot steer cleanup), and startup timeout — each still stops the known unit and writes no report.
- `start-db.sh:5` restricts token to `^[a-f0-9]{32}$`; socket path validated in `run-apache.sh:19-20` (regex, `-S`, `realpath`, no symlink).
- KS privacy: `collect.py:58` persists `stdout` only when `== ''` or `== EXPECTED_STDOUT`, else `''`, while always storing `stdout_sha256`/`stderr_sha256`; `test_unexpected_stdout_is_rejected_and_not_persisted` proves marker exclusion. Additions collector stores full `stdout/stderr` verbatim, which is acceptable here because the pinned corpora are synthetic/public (probes hash messages/loaded files; `autoload83/probe.php:28-32`, `autoload83-composition/probe.php:21,26`).

## 17-addition matrix and stdout/stderr contract — PASS

- `CASES` (`collect-additions.py:12-14`): 1 ternary `matrix` + 6 autoload (`hp`, `core-simple`, `core-full`, `cli-version`, `cli-version-queue`, `cli-tasks-configured`) + 10 composition (`hp-append/prepend/throw/repeat`, `core-repeat`, `cli-append/prepend/throw-front/throw-tail/repeat`) = 17 ordered processes.
- `validate()` (`:34-40`): exact order, strict `type(...) is int` (rejects `bool`/`float`), exact `{exit,stdout,stderr}` byte equality against the reviewed candidate83 reference. `test_additions.py:10-33` covers ordered-17, duplicate, missing, extra, bool/float status, extra-stdout, emptied-stderr, and fatal-must-remain-fatal (the expected duplicate-include fatal, `cli-repeat`, 16 positive + 1 fatal).
- Summary constants (`16` positive, `1` fatal, `147` ternary rows) are consistent with probe structure (10×13 matrix + 5 + 12 = 147; byte equality enforces the count). No 74-parity claim is made for additions — correctly scoped as candidate83 replay.

## Original83 fatal and original74 parity — PASS

- API matrix `collect.py:26-27` is exactly `[74/original, 83/original, 83/exp10, 83/exp11]`; `(74,exp11)` excluded, `(74,exp10/exp11)` listed as unsupported with reason (`:70`).
- Pass requires baseline `stdout==EXPECTED_STDOUT`, all `stdout_whitelisted`, `83/original` nonzero exit with `KalturaPDO::query()` signature failure, both candidates matching baseline, and cleanup stopped (`:65-68`). Fault-injection tests cover baseline failure, candidate failure, wrong failure string, unexpected stdout, and active-unit cleanup.

## Non-blocking notes (not defects)

- `collect-additions.py:67-68`: `read_pin()` failure happens before the `INCOMPLETE` report is written, so a missing pin leaves no file. Fail-closed is preserved; only the artifact-reporting path differs from post-write failures.
- `collect-additions.py:40`: `ternary_functional_rows:147` is a summary constant implied by whole-stdout byte equality, not independently recomputed. Adequate for a byte-replay harness.
- `fixtures()` calls `rglob('*.php')` on `base-object-ternary/fixtures`, which does not exist in-repo; the call yields zero entries (total still 14, `>10` test passes). Tolerant, not blocking.

## Limitations / not claimed

- Repo-only review; collectors were not executed here (pin absent by design). Preserved `25`-test and `6`-file syntax evidence is harness-only.
- Bounded corpora only (4 API rows, 48 CLI rows per prompt context, 68 class cases, 17 addition processes). No full-application, FPM/AIO, services, performance, package, or release acceptance. `application_acceptance:False` is explicit in collectors.
- One denied-tempfile read from a prior review was not retried or worked around; no gap in the owned in-repo scope resulted.

No concrete blocking defect found in the inspected files and lines above.
