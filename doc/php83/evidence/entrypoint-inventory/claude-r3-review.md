# Independent r3 targeted review — entrypoint-candidate inventory (Claude)

- Executor/reviewer: actual Claude CLI (Claude Opus 5.5), independent of the
  author/repair. Targeted delta validation of r2 blocker B4 only; not a repeat
  wide audit, not real-input execution. `claude-review.md` (r1) and
  `claude-r2-review.md` (r2) are preserved unchanged; the prior OpenCode `/tmp`
  permission denial stays preserved and was not retried.
- Boundaries kept: repository only; no real archives, no `/tmp` or external
  directories, no VM/network, no source/index edits.
- Reviewed identities (sha256):
  - `build.py` `d2ed28e1df69479a2f795861c1713966cab0d4ba2f32511afcc15dd3702b3202`
  - `test_entrypoint_inventory.py` `2e220d949e50986024e95beb6096ace8fd51b2691c26a2c0553516ee8578b80a`
  - `entrypoint-inventory.md` `ab833d866f42bbabba6ac9c0954a4f937224d534c5eb8825bc455ec8ced47746`
  - r1 `claude-review.md` `5bc7871f7232320fe075a7a56a3f6e5934f7cf651966cd3f29a852465af1200c` (unchanged)
  - r2 `claude-r2-review.md` `4921d9a559ab4c39d1f8d3fd2054a50cb75ac7c34af639fce67bb695ba22b931`
- Environment: Linux 6.8.0-142, Python 3.12.3, branch
  `proposal/migrate-kaltura-php83` @ `898183a9` (worktree changes untracked).

## Executed

1. `TMPDIR="$PWD/tools/php83/entrypoint-inventory/.tmp-test-scope" PYTHONDONTWRITEBYTECODE=1 timeout 60 python3 -m unittest discover -s tools/php83/entrypoint-inventory -p 'test_*.py' -v`
   → exit 0, **17/17 OK** (0.006 s). `.tmp-test-scope/` is gitignored.
2. Stdin Python (same `TMPDIR`, `timeout 30`) importing `build` and feeding
   single **tracked repository lines** to `scan_php_invocations` → exit 0:

| Input | Rows | `$PHP_BIN` `unresolved_dynamic` |
|---|---|---|
| `deb/kaltura-batch/debian/kaltura-batch.init:85` | 2 (`$PHP_BIN` twice; 2nd is the argv copy) | yes |
| `deb/kaltura-elasticsearch/debian/kaltura-elastic-populate.init:65` | 1 | yes |
| `RPM/SOURCES/kaltura-populate:94` | 1 | yes |
| `RPM/SOURCES/kaltura-populate:92` (`echo`) | 1 | yes |
| whole `kaltura-batch.init` | lines 48 (awk regex, known overmatch) and **85** | — |
| `"$PHP_BIN" /opt/x.php`, `"${PHP}" /opt/y.php`, `${PHP_BIN:-php} /opt/x.php` | 1 each | yes (N8 closed) |
| `echo $HOME; $PHP a.php` | 1 (`$PHP`) | — |
| `su $U -c "$X $Y"` | 0 | — (no false row) |
| `$(which php) /opt/y.php` | 0 | still missed |

3. Static checks: `VARIABLE_INTERPRETER_RE` now puts the target in a lookahead
   (`build.py:40-42`), so `finditer` advances past each `$VAR` only; the
   tautological "Unreconciled" check is gone (N10); `config_taxonomy` includes
   `application_config_candidate` (N11, `build.py:448`); summary adds
   `regular_dispositions` (`build.py:469`); r2 N13 doc spacing typos no longer
   match. New test `test_nested_shell_variable_interpreter_not_consumed_by_prior_var`
   uses the R1 idiom and quoted/default forms.

## Findings

- **B4 closed** for the tracked daemon idiom (R1–R3, R5 line 85).
- N14 (non-blocking) Line 85 yields a second `$PHP_BIN` row whose "interpreter"
  is actually an argument; covered by the doc's overmatch caveat.
- N15 (non-blocking) `$(which php) script` is still missed and not named in the
  doc; not found as an idiom in the probed tracked scripts. Mention it or extend later.
- N7/N9/N12 from earlier reviews remain as documented limitations.

## Verdict

**APPROVED — prepared candidate-discovery scope only.** B4 is closed and
regression-tested; 17/17 synthetic tests pass. This does not approve or
evidence real-input execution, full inventory, owner/source reconciliation,
original-tree entrypoint discovery, active-path classification, T0-04, or any
provider/release claim. This review is not execution evidence on real inputs.
