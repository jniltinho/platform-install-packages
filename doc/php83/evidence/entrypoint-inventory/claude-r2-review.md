# Independent r2 review — entrypoint-candidate inventory (Claude)

- Executor/reviewer: actual Claude CLI (Claude Opus 5.5), independent of the
  OpenCode author and the local author/repair. Supersedes nothing; the rejected
  r1 review (`claude-review.md`) is retained unchanged.
- Scope judged: **PREPARED candidate discovery only** (`tools/php83/entrypoint-inventory/*.py`,
  `doc/php83/entrypoint-inventory.md`). Not real-input execution, not full
  inventory/T0-04 approval.
- Boundaries kept: repository-only; no real archive/DEB/ZIP read, no `/tmp`
  access, no retry (any tool/path) of the preserved OpenCode `/tmp` denial or
  the local-author exit124; no VM/network/index/source edits. The external-input
  denial is preserved; no broader gate is waived.
- Reviewed identities (sha256):
  - `build.py` `7cb89a2cffa493b8a5650be3ceb69131ba98cce4e1729a2c38e99d7562f5b4a7`
  - `test_entrypoint_inventory.py` `a70b82b02854cb9b28d818505f263ed85cb688a1fe94e118afd8c8921ed6d651`
  - `entrypoint-inventory.md` `6ae78553258266ee9c346f001918a3cb8da4e8607ffc9ca4b6acf1f6ef4e3c57`
  - r1 review `claude-review.md` `5bc7871f7232320fe075a7a56a3f6e5934f7cf651966cd3f29a852465af1200c` (unchanged)
- Environment: Linux 6.8.0-142, Python 3.12.3, branch
  `proposal/migrate-kaltura-php83` @ `898183a9` (worktree changes untracked).

## Executed

1. `TMPDIR="$PWD/tools/php83/entrypoint-inventory/.tmp-test-scope" python3 -m unittest discover -s tools/php83/entrypoint-inventory -p 'test_*.py' -v`
   → exit 0, **16/16 OK** (0.006 s). Matches author `local-r4-tests.*`.
2. In-memory probes (stdin Python, `TMPDIR` = repo `.tmp-test-scope`,
   `PYTHONDONTWRITEBYTECODE=1`; tar streams built with the test module's
   `tar_bytes` in `BytesIO`; no files written) → exit 0.
3. Same, feeding **tracked repository script lines** (not archives) to
   `scan_php_invocations`/`parse_data_stream` → exit 0.

### r1 probes reproduced

| Probe | r1 result | r2 result | Status |
|---|---|---|---|
| P1 exec `opt/kaltura/bin/run.sh` | 0 invocations | `executable+shell_script_candidate`, 1 `literal_php` | fixed |
| P2 non-exec `lib.sh` | excluded, unread | `shell_script_candidate`, 1 `literal_php` | fixed |
| P3 `opt/kaltura/app/configurations/cron/api` | excluded | `config:application_config_candidate`, 1 `literal_php` | fixed |
| P4 `$PHP_BIN /opt/x.php`, `${PHP} /opt/y.php` | 0 rows | 2 `unresolved_dynamic` | fixed (see B4) |
| P5 `php -d …`, `php -f …` | `unresolved_dynamic` | `unresolved_option` (argv kept in `line_excerpt`) | fixed (N1) |
| P6 `cd /opt/x && php install.php` | `literal_php` | `relative_unresolved` | fixed (N2) |
| P7 exec ELF | `executable+extensionless_php_candidate` | `executable` | fixed (N3) |
| P8 `apt-get install php8.3 php8.3-cli` | false row | still false row `unresolved_dynamic` | accepted; doc states overmatch (N4) |
| P9 php + non-php symlink + txt + dir | link uncounted | regular rows carry `scan_disposition`; links in `data_links`; `data_other` reported | fixed (N5) |

Also verified: control regular members keep full metadata + `sha256`;
invocation rows carry `source_sha256` equal to the scanned member hash (control
and data); doc test command now uses gitignored `.tmp-test-scope` (N6); doc
states ZIP is a PHP-family count only and owner records are not reconciled (B3).

### New probes

| Probe | Input | Result |
|---|---|---|
| R1 | `deb/kaltura-batch/debian/kaltura-batch.init:85` `su $OS_KALTURA_USER -c "nohup $PHP_BIN $BATCHEXE …"` | **0 rows** |
| R2 | `deb/kaltura-elasticsearch/debian/kaltura-elastic-populate.init:65` `su $OS_KALTURA_USER -c "$PHP_BIN $ES_PLUGIN_SCRIPT …"` | **0 rows** |
| R3 | `RPM/SOURCES/kaltura-populate:94` (same `su … -c` idiom) | **0 rows** |
| R4 | `RPM/SOURCES/kaltura-populate:92` `echo "$PHP_BIN $SCRIPTEXE …"` | 1 `unresolved_dynamic` |
| R5 | whole `kaltura-batch.init` as `etc/init.d/kaltura-batch` (0755) | file is candidate `config:init+executable`; only invocation row is line 48, an awk regex `/php [K]GenericBatchMgr.class.php/` (false positive); real launch line 85 absent |
| N-a | `"$PHP_BIN" /opt/x.php`, `"${PHP}" /opt/y.php` | 0 rows |
| N-b | `${PHP_BIN:-php} /opt/x.php`, `$(which php) /opt/y.php` | 0 rows |
| N-c | `sudo -u k php …`, `/usr/bin/env php …`, `exec php …` | 3 `literal_php` |
| N-d | non-exec `opt/kaltura/bin/tool.template` (`#!/bin/bash` + php), `etc/monit/conf.d/k.rc` | both `excluded` by suffix, unread; visible only as `.template`/`.rc` counts |

## Blocker

- **B4 — B2 not closed for the repository's own daemon idiom (R1–R3, R5).**
  `VARIABLE_INTERPRETER_RE` target is `[^\n;|&]+`; `finditer` is
  non-overlapping, so the first `$VAR` on a line (`$OS_KALTURA_USER`, not
  PHP-named, target without `.php`) consumes the rest of the line and is then
  discarded by the filter at `build.py:159`. `$PHP_BIN` later on the same line is
  never tried. This silently drops the actual batch, elastic-populate and
  populate PHP launches in the tracked init scripts
  (`dh_installinit` installs `kaltura-batch.init` as `etc/init.d/kaltura-batch`).
  This is the canonical Kaltura launch form, not "unusual command
  construction", so the doc's caveat does not cover it. Minimal fix: stop
  consuming the target (e.g. match each `\$\{?NAME\}?` with a lookahead
  `(?=[ \t]+(?P<target>…))`, or scan every `$VAR` start position) and add a test
  using the R1 line expecting an `unresolved_dynamic` row with interpreter
  `$PHP_BIN`.

## Non-blocking findings

- N8 (N-a/N-b) Quoted `"$PHP"` and `${PHP:-php}` interpreters are missed. Not
  found as interpreter idioms in tracked repo scripts; state it in the doc or
  extend the pattern alongside B4.
- N9 (N-d) Non-executable shell/rc files with other suffixes are excluded
  unread; visible in `excluded_suffix_counts` only. Acceptable given the
  per-suffix denominators; doc wording "etc/systemd … path candidates" should
  say only cron/init/default/web/php etc paths are tagged, not all `etc/`.
- N10 The "Unreconciled regular member denominator" check (`build.py:307`) is
  tautological (every regular row is assigned one of the three values just
  before), so it can never fire. Per-row dispositions are correct; either
  compare against independent counters or drop the check.
- N11 `config_taxonomy` in the report omits `application_config_candidate`,
  which is emitted as a class.
- N12 R5 line 48: regex over awk/grep patterns produces false rows; covered by
  the doc's overmatch caveat.
- N13 Doc formatting: missing spaces in "The2MiB", "had12", "with3", "ran12",
  "expanded16-test", "exit124".
- N7 (from r1) still open by design: ledger/source-map/primary hashes are
  recorded, not joined; doc states this.

## Verdict

**NOT APPROVED as prepared** — B4 open. B1, B3 and N1–N3/N5/N6 are verified
fixed; B2 is fixed only for lines whose first `$VAR` is the interpreter.
Path/link/hash/scratch/output safety remains sound for trusted pinned inputs;
16/16 synthetic tests pass. After B4 plus a regression test, the prepared
candidate-discovery scope is approvable; that would still not approve real-input
execution, owner/source reconciliation, original-tree entrypoint discovery,
active-path classification or T0-04. This review is not execution evidence.
