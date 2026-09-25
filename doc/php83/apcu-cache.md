# APC/APCu application-cache investigation

Status: **PARTIAL / experimental adapter rejected**, 2026-09-25. Supports
T1-03/5.9, T4-01/5.16 and source inventory; closes none of their acceptance gates.
No source patch, provider selection, package integration or release decision.

## What was actually executed

The original packaged `kApcCacheWrapper` and `kInfraBaseCacheWrapper` were loaded
unchanged in the isolated Noble baseline/candidate labs. Source hashes match
both labs and the pinned raw Rigel tree. Each invocation ran as nobody under
systemd with private networking, socket creation denied, read-only source,
private temporary storage, 256 MiB and 30 seconds maximum. Only the synthetic
fixture was copied; its directory was removed on exit. APCu CLI memory belongs
to the short-lived process; no shared application cache was cleared.

| Runtime / APCu | Original control | Direct-alias experiment | Independent rerun |
|---|---|---|---|
| PHP 7.4.33 / APCu 5.1.28 | PASS: init is false, 1 assertion, exit 0 | FAIL: 59/63 assertions, exit 1 | Claude reproduced both |
| PHP 8.3.6 / APCu 5.1.22 | PASS: init is false, 1 assertion, exit 0 | FAIL: 59/63 assertions, exit 1 | Cursor reproduced both |

These are **four logical runtime rows**, not eight different tests after reruns.
Controls prove an existing CLI cache-selection gap, not a PHP 8.3-only regression.
They do not establish the baseline's Apache surface or application bootstrap.
Both runs deliberately enabled APCu for CLI and selected wall-clock TTLs with
`apc.enable_cli=1` and `apc.use_request_time=0`; these are fixture options, not
changes to installed configuration. Native and serialized values, false/miss,
by-reference fetch success, add/no overwrite, multiget, counters, TTL and
synthetic stdClass round trips were exercised. No application objects or
cross-request serialization were tested.

The four failures in each adapter run are the native missing increment/decrement
return values (`1`/`-1`, expected false) and the resulting key creation (true,
expected false). The serialized base path does not create missing counters.
All diagnostics arrays and stderr files were empty. **The adapter remains red;
it was not installed or promoted.**

## Counter contract provenance

Initially the no-creation expectation was explicitly derived from the base
serialized path, not an observed native APC baseline. Subsequent upstream source
inspection strengthens that expectation: the pinned APCu-BC implementation
checks existence and returns false before increment/decrement on missing keys.
That is source evidence, not a local execution of the historical extension.
The APCu API itself permits creating counters. A direct function alias therefore
is not a complete compatibility implementation. An existence check followed by
increment also has a deletion/expiry race; concurrency remains untested.

- [APCu increment API](https://www.php.net/manual/en/function.apcu-inc.php).
- [APCu-BC counter implementation, pinned commit](https://github.com/krakjoe/apcu-bc/blob/144a3347e1ca6849529bd577f4889cdb028e16f3/php_apc.c#L113-L155).
- [Original APC increment/decrement source, pinned commit](https://github.com/php/pecl-caching-apc/blob/401a7e4730132664bd82b62beb22af0e0624fc47/php_apc.c#L678-L729).

No legacy extension was built or installed. No blanket alias, blind rename or
new cache activation is accepted by this investigation.

## Application surface and why one wrapper is insufficient

A raw literal sweep covered 15,175 regular files: 135 matching lines across
31 files. Ten legacy called APIs appear: add, cache_info, clear_cache, dec,
delete, exists, fetch, inc, sma_info and store. No literal `function apc_*`
definitions or matched APCu compatibility loader were found. This does **not**
exclude dynamically constructed names, external modules or prepend files.
Graph lookup was verified per relied-on file; parser gaps were read directly.
Global negative statements rely on the raw sweep, not graph completeness.

Important original-source paths:

- `infra/cache/kApcCacheWrapper.php`: checks `apc_fetch`, not APCu availability.
- `alpha/apps/kaltura/lib/cache/kCacheManager.php`: failed wrapper init becomes
  null; its single-layer selection does not automatically try all alternatives.
- `alpha/config/cache/kApcConf.php`: APC map/version storage is disabled in CLI;
  a CLI test cannot establish real configuration-map persistence.
- `alpha/config/kConfCacheManager.php`: other layers can mask unavailable APC.
- `infra/KAutoloader.php`, `kLoggerCache.php`, reflection classes, plugin manager,
  DB configuration and other consumers call legacy functions directly.
- `infra/general/kLockBase.php`: absent `apc_add` returns null. Under applicable
  flags/misses, `kApiCache.php:772–793` can loop through 20 sleeps of 50 ms;
  this is a conditional source inference, **not a measured latency regression**.
- `alpha/scripts/clear_cache.php`: separates system and user cache clearing.
- Vendored Zend APC backend requires `extension_loaded('apc')`; aliases do not
  satisfy that guard. Its cache-info schema must be checked separately.
- Admin APC view and upload-progress integration expect legacy opcode/statistics
  or `apc.rfc1867` capabilities. APCu function availability does not provide them.

[Literal matches](evidence/apcu-cache/source-literals.txt) and
[file identities](evidence/apcu-cache/source-surface.json) retain the bounded
inventory. Vendor Composer's native APCu calls do not adapt Kaltura's caches.

## Review and reproducibility

Commands: `tools/php83/apcu-probes/run-lab.sh {74,83} {control,adapter}` with each
combination executed separately. See the [fixture README](../../tools/php83/apcu-probes/README.md).
[Result and identities](evidence/apcu-cache/result.json) distinguish the failed
experiment from passing controls. Initial pre-object-coverage runs are retained
under `attempts/`; final reviewed fixture contains 63 adapter assertions.

Claude reviewed and independently executed baseline rows; Cursor reviewed and
executed candidate rows. Grok exited 1 at its turn limit and supplied no complete
execution result. Authorized OpenCode Zen Muse Spark 1.3 Free then independently
reviewed the fixture/primary evidence and executed the **109-test local Python
suite**, exit 0. Codex reran that suite. This is harness support, not application
acceptance, and does not cancel the two failed adapter rows.

Current laboratory SSH configuration uses loopback forwarded ports and hostname
checks but does not pin host keys. These are existing isolated synthetic labs,
not production transport assurance. Per-command duration was not retained;
30-second execution limits are bounds, not performance measurements. No full
T1-03 case completion is claimed.

## Next required evidence

1. Establish baseline/candidate real Apache cache surface and two-request
   configuration/reflection hit/invalidation behavior in an owned isolated pool.
2. Reconcile counter callers and concurrent expiry/delete semantics before
   choosing an explicit user-cache migration or narrowly scoped adapter. Keep
   system/opcode management and upload-progress capability decisions separate.
3. Complete actual cache backend/serialized-object/restart tests and inventory;
   then reconcile the legacy RPM capability with the reviewed provider manifest.
   T1-03, T4-01 and all production/release approvals remain open.
