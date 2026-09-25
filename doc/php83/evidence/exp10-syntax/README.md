# exp10 paired syntax results and independent comparison

Primary execution completed on the isolated `.83` lab under PHP 8.3.6.
`primary.json` contains all records; `primary-summary.json` preserves counts,
runtime/library/module/INI and harness identities. Runner exit is 0, external
stderr empty, with no scan processes remaining in the post-run check. The
original null-pin contract is retained as preparation history. No SQL or
application entrypoint ran.

| Artifact | Selected files | Rejected | Accepted with diagnostics | Incomplete |
|---|---:|---:|---:|---:|
| exp9 | 11,784 | 54 | 64 | 0 |
| exp10 | 11,784 | 11 | 66 | 0 |

All 43 pinned new targets changed from rejection to acceptance. Every unchanged
file retains the same source hash, compiler exit and diagnostic text. This is
the anticipated bounded improvement, not whole-candidate syntax acceptance:
`candidate_all_files_compile=false` and `application_acceptance=false`.

## Two newly visible diagnostic files

The increase from 64 to 66 accepted-with-diagnostics files is explained by two
previously rejected files now reaching acceptance:

- `vendor/symfony/vendor/phing/tasks/system/CvsPassTask.php:141`: private methods
  cannot be final. Patch `0035-CvsPassTask.php.patch` changes only
  `$password{$i}` to `$password[$i]`; the pre-existing `private final function`
  declaration is unchanged (visible in patch context).
- `vendor/symfony/vendor/phing/util/FileUtils.php:74`: three optional parameters
  (`$overwrite`, `$preserveLastModified`, `$filterChains`) precede required
  `$project`. Patch `0038-FileUtils.php.patch` changes only curly-offset reads
  at later lines; it does not alter that method declaration.

These existing declaration diagnostics become visible in accepted files after
the fatal syntax blocker is removed. They are retained, not waived or counted
as clean-runtime success. The patch files and resulting source hashes remain
pinned in the reviewed candidate manifest.

## All 11 remaining compiler rejections

`remaining-triage.json` joins each result to
`../compiler-triage/primary-r2.json`, requiring identical source hash, exit and
diagnostic text. Counts match the previous classification: **one nested
ternary, three removed autoload declarations, one reserved Object alias and six
unexpanded templates**. Four are PHP 8.3 language rejections newly observed
relative to the historical PHP 7.4 baseline; seven were already rejected there.
Baseline rejection does not grant an exception or prove generated code works.

| Exact path | Classification |
|---|---|
| `alpha/apps/kaltura/lib/baseObjectUtils.class.php` | Unparenthesized nested ternary |
| `vendor/aws/Doctrine/Common/Cache/RiakCache.php` | Reserved `Object` import alias |
| `vendor/htmlpurifier/library/HTMLPurifier.autoload.php` | Removed `__autoload` declaration |
| `vendor/symfony-data/bin/symfony.php` | Removed `__autoload` declaration |
| `vendor/symfony/util/sfCore.class.php` | Removed `__autoload` declaration |
| `vendor/symfony-data/generator/sfPropelAdmin/default/skeleton/actions/actions.class.php` | Unexpanded template |
| `vendor/symfony-data/generator/sfPropelCrud/default/skeleton/actions/actions.class.php` | Unexpanded template |
| `vendor/symfony-data/skeleton/batch/default.php` | Unexpanded template |
| `vendor/symfony-data/skeleton/batch/rotate_log.php` | Unexpanded template |
| `vendor/symfony-data/skeleton/controller/controller.php` | Unexpanded template |
| `vendor/symfony-data/skeleton/module/module/actions/actions.class.php` | Unexpanded template |

## Independent Claude report comparison

The standalone host comparator is **not part of the six frozen/staged scan
files**. Neither it nor its new tests should be uploaded into the existing
stage: doing so changes the report's harness identity and invalidates exact
repetition. The original scan files remain byte-identical to `frozen-tools.sha256`.

After the actual Claude repeat has finished and `claude-scan.json`, `claude-scan.exit`
and `claude-scan.stderr` exist, run from the migration worktree:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 tools/php83/exp10-syntax/compare.py \
  doc/php83/evidence/exp10-syntax/primary.json \
  doc/php83/evidence/exp10-syntax/claude-scan.json \
  doc/php83/evidence/exp10-syntax/comparison.json
```

The comparator requires real zero-exit/empty-stderr sidecars, report identity
except **per-record `duration_ns` only**, exact frozen harness/contract, computed
summaries, repeated 43-target/unchanged-file checks and explicit remaining
rejections. It refuses to overwrite its output and fails closed on mismatch.
Report identity includes command, diagnostics, source hashes, selected and
excluded inventories, runtime/modules/libraries and both ZIP pins. Reviewer or
mock reports must not substitute for independent execution evidence.

No comparison result is asserted by this README; inspect actual `comparison.json`
and its execution evidence when created. Local comparator unit tests are host
tests, not another compiler run. No aggregate migration checkbox is closed.
