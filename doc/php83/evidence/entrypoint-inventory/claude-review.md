# Independent review — entrypoint-candidate inventory (Claude)

- Executor/reviewer: actual Claude CLI (Claude Opus 5.5), independent of the
  OpenCode author and the local author/repair.
- Scope: `tools/php83/entrypoint-inventory/*.py`, `doc/php83/entrypoint-inventory.md`.
  Repo-local, synthetic-only. No real archive/DEB/ZIP read, no `/tmp` use, no
  retry of the preserved OpenCode `/tmp` extraction denial or the local author
  `timeout 124`, no index/VM/network, no source edits.
- Reviewed identities (sha256):
  - `build.py` `85a4103d8c75f333dc211cbace20027f6451878106a9c8e33b3efe6ca5e62bf7`
  - `test_entrypoint_inventory.py` `375a7786ab683156c75996b90e8435833826992cac1f4a6062dcdedd3cc4938a`
  - `entrypoint-inventory.md` `bb1f5cd3b028db22737a77f942b10fa1ffa9baf7ec77525d240e481beb24b75e`
- Environment: Linux 6.8.0-142, Python 3.12.3, branch `proposal/migrate-kaltura-php83`.

## Executed

1. `TMPDIR="$PWD/tools/php83/entrypoint-inventory/.tmp-test-scope" python3 -m unittest discover -s tools/php83/entrypoint-inventory -p 'test_*.py' -v`
   → exit 0, **12/12 OK** (0.006 s).
2. In-memory synthetic probes (`parse_control_stream`/`parse_data_stream` on
   `tar_bytes(...)` BytesIO, no files written) → exit 0:

| Probe | Input | Result |
|---|---|---|
| P1 | data `opt/kaltura/bin/run.sh` mode 0755 containing `php /opt/kaltura/app/x.php` | candidate `executable`, **0 invocations** |
| P2 | data non-exec `opt/kaltura/bin/lib.sh` with php call | **excluded `.sh`**, not read |
| P3 | data `opt/kaltura/app/configurations/cron/api` (non-exec, cron line with php) | **excluded `(extensionless)`**, 0 invocations |
| P4 | postinst `$PHP_BIN /opt/...x.php` / `${PHP} /opt/y.php` | **0 invocations** (no unresolved row) |
| P5 | postinst `php -d memory_limit=-1 /opt/a.php`, `php -f /opt/b.php` | recorded, target `-d`/`-f`, `unresolved_dynamic` (not lost, but real target discarded) |
| P6 | postinst `cd /opt/x && php install.php` | `literal_php` for cwd-relative `install.php` |
| P7 | executable ELF-like extensionless | class `executable+extensionless_php_candidate` |
| P8 | `apt-get install -y php8.3 php8.3-cli` | false invocation `php8.3 → php8.3-cli` |
| P9 | php + non-php symlink + txt + dir | non-php symlink is neither candidate nor excluded (only in `data_links`) |

## Sound

- Path safety: absolute/backslash/NUL/`..` rejection, root `./` → `''`,
  post-normalization duplicate rejection in control and data; links recorded
  with `linkname`, never followed; no extraction to member paths.
- Pinned outer bundle/ZIP hashes, exact inner `SHA256SUMS`↔`.deb` set,
  per-package hash before `dpkg-deb`; scratch confined to repo, deleted.
- Upstream ZIP read-only (`zipfile` infolist, no extract), hash-pinned, root-checked.
- Output: refuse existing path + `open('x')`; builder/tool/input hashes recorded;
  `t0_04_complete: False`, `no_runtime_or_reachability_claim: True`,
  `semantic_findings_resolved: 0`. No active/full-graph claim in code or doc.
- Trusted pinned-input scope documented; no hostile-archive sandbox demanded.

## Blockers (before real-input execution counts as candidate inventory)

- **B1 — silent miss of shell/helper invocations (P1–P3).** Invocation scan
  runs only on control maintainer scripts and on data files tagged by
  `classify_config` (etc/…, systemd paths). Executable scripts, all `.sh`, and
  Kaltura config/cron templates under `opt/kaltura/app/configurations/`
  are never scanned; non-exec `.sh` is not even a candidate. Fix: scan every
  read text candidate (at least `.sh`, shebang `sh|bash`, extensionless, cron/
  conf templates) or record them as `unscanned` with a count; do not let
  them disappear into `excluded_suffix_counts`.
- **B2 — variable interpreters are invisible (P4).** `$PHP_BIN x.php`,
  `${PHP} …` produce no row. Add a variable-interpreter pattern (e.g. line
  containing `.php` or a `$…PHP…` token) emitting `unresolved_dynamic`.
- **B3 — doc overclaim.** `entrypoint-inventory.md` says "Inventories …
  literal PHP invocations" and "Reports full denominators … upstream PHP
  count". Must state: invocations only from maintainer scripts + etc/systemd-
  tagged config; upstream ZIP is a **PHP-family file count only**, not an
  original-entrypoint inventory and not reconciled to packaged candidates;
  T0 entrypoint inventory remains incomplete.

## Non-blocking findings

- N1 (P5) Options consume the target slot; keep `unresolved`, but label it
  `unresolved_option` and keep the full argv excerpt (already in `line_excerpt`).
- N2 (P6) cwd-relative literal targets should be `relative_unresolved`, not `literal_php`.
- N3 (P7) `extensionless_php_candidate` fires on executable bit alone; require
  shebang/`<?php`, keep `executable` separately.
- N4 (P8) package-name false positives; acceptable for a candidate list if doc says regex over-matches.
- N5 No reconciliation invariant: add
  `data_regular == regular candidates + regular excluded + oversize` and report
  `data_other`; non-php links (P9) should be counted explicitly.
- N6 Doc test command uses `.tmp-run-scope` (not in `.gitignore`); tests
  always write to `.tmp-test-scope` regardless of `TMPDIR`.
- N7 `inputs` hashes ledger/source-map/primary.json but never reads them;
  owner comparison with `primary.json` is not performed (doc already says open).

## Verdict

**NOT APPROVED as prepared** — B1–B3 open. Code-level safety (paths, links,
hashes, scratch, output) is sound for trusted pinned inputs; 12/12 synthetic
tests pass. This review is not execution evidence; no real-input run occurred,
and passing synthetic tests does not establish T0 entrypoint completeness.
