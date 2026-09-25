# Symfony bootstrap investigation

## Result

Seven held, minimal source patches advance the public Kaltura Symfony bootstrap
on PHP 8.3 beyond removed `__autoload` declarations, curly string offsets,
`each()` and `create_function()`. **Bootstrap acceptance still fails.** The next
observed fatal is duplicate `sfOutputEscaperObjectDecorator` declaration in the
newly generated `config_core_compile.yml.php` (line 3459 in this run).

Original PHP 7.4 and patched PHP 7.4 both complete this bootstrap. Unpatched 8.3
fails immediately on `sfCore`'s `__autoload`. Patched 8.3 reaches compilation of
the configuration cache, but does not return from bootstrap. This is a CLI
preflight of real public configuration/bootstrap code, not an installed HTTP
application, authenticated API, database, worker or playback acceptance test.

## Changes held outside the active ZIP

See `patches/php83/held/symfony-bootstrap.json` for all before/after/patch hashes.
Each patch is standalone against the pinned original file; license headers are
retained. Exact application with zero fuzz/offset and resulting hashes was
verified, along with PHP 7.4/8.3 lint of all seven candidate files.

| File under vendor/symfony | Repair |
| --- | --- |
| controller/sfRouting.class.php | One curly string offset to square brackets |
| helper/UrlHelper.php | One curly string offset to square brackets |
| util/sfCore.class.php | Replace two obsolete non-SPL fallback declarations with explicit failure; preserve SPL registration order and callbacks |
| util/sfFinder.class.php | Eight curly string offsets to square brackets |
| util/Spyc.class.php | One curly offset; index the locally packed value array instead of consuming it with removed each() |
| util/sfToolkit.class.php | Replace generated constant-substitution callback with closure |
| config/sfConfigHandler.class.php | Replace generated recursive callback with by-reference closure |

The Spyc value array is created by `array_merge(array_values(...), ...)`, aligned
with the locally packed keys array. Its pointer is not otherwise used in that
method. Numeric duplicate-key and NULL behavior remains in the regression
fixture; no conversion to generic array_merge semantics was made.

Claude reviewed the initial approach and was given the complete patch series
for a second advisory review, now saved alongside the evidence. The second review
found no semantic regression in the supplied diffs and recommended comparing
generated cache content and autoload order. Its stale-cache hypothesis does not
fit these fresh-per-process tmpfs runs; the underlying duplicate remains untriaged. Its initial suggestion to remove non-SPL branches
entirely was not adopted: explicit failure is retained for an unsupported
runtime, without changing the supported SPL path. Review is not runtime evidence.

## Executed checks

- Four comparisons: candidate 7.4/8.3 against original 7.4, standard and minimal
  INI, actual route registration/generation/parsing, seeded byte encoding
  (ASCII, UTF-8, NUL/high byte), SPL registration/simple discovery and recursive
  constant substitution. All pass.
- Two comparisons: YAML parsing and protected merge numeric/NULL/duplicate-key
  behavior, standard INI. Both pass. Minimal INI lacked `ctype_digit` even on
  unchanged 7.4; this fixture explicitly requires standard modules rather than
  claiming the missing-extension run passed.
- Eight existing JSON comparisons pass; 38 offline Python tests pass.
- Full bootstrap comparison: patched 7.4 matches original; patched 8.3 fails.
  The collector returns failure for this comparison, not a silent expected-pass.

E_ALL diagnostics are retained. Remaining exercised diagnostics include Zend
return types, libxml deprecation, Symfony parameter ordering and a Spyc dynamic
property. No warning suppression or acceptance waiver was added. The shutdown
recorder preserves fatal diagnostics even after application code changes error
logging/display settings.

## Isolation and reproducibility

The existing hostname-guarded `.74`/`.83` runner uses an unprivileged systemd
namespace, denied socket creation, read-only source binds, inaccessible live
`/opt/kaltura` and bounded memory/time. Only `symfony-bootstrap` adds a private
writable tmpfs at `/audit/app/cache`; no host cache is modified and each process
gets a new cache. The initial fully read-only attempt hit the expected cache
write restriction on 7.4 and is retained as setup history, not a PHP defect.

Both lab trees were restored to their original seven source hashes after tests,
leaving the previous exp2 JSON-only state. `.20`, main, active patch manifest,
experimental ZIP, published packages and CI remain unchanged.

To reproduce, apply the seven individually hash-verified held patches to the
lab candidate copies, sync the versioned fixture/runner, then run:

```sh
python3 tools/php83/patch-tests/collect.py /tmp/symfony.json --case symfony
python3 tools/php83/patch-tests/collect.py /tmp/yaml.json --case symfony-yaml --mode standard
# Currently returns nonzero: preserve this failure.
python3 tools/php83/patch-tests/collect.py /tmp/bootstrap.json --case symfony-bootstrap --mode standard
```

Restore original files after collection. Do not add held patches to the ZIP by
globbing. Evidence is under `evidence/symfony-bootstrap/`: `behavior.json`,
`yaml.json`, `bootstrap.json`, `json-regression.json`, `source-checks.json` and
historical bootstrap stages.

Graph generation `2026-09-25T12:19:00Z` was current by metadata. Coverage was
checked for every investigated source. Partial ranges in routing, UrlHelper,
Spyc and the entire sfFinder file were read directly. This is bounded discovery,
not an exhaustive Symfony compatibility audit.

## Next acceptance step

Trace duplicate declaration/autoload behavior during core cache generation,
without weakening escaping or disabling compilation merely to force success.
Once bootstrap returns, proceed to configured synthetic HTTP/API and worker
acceptance. Registry and raw PDO/JSON contract divergences remain independent
release blockers; successful Symfony fixtures do not resolve them.
