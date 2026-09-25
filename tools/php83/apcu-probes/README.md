# Original APC wrapper / APCu synthetic probe

`wrapper.php` loads the **unchanged** Rigel `infra/cache/kInfraBaseCacheWrapper.php`
and `infra/cache/kApcCacheWrapper.php` from an explicit source root. There is no
`infra/cache/kCacheWrapper.php` in this source. Both actual file hashes are in
JSON; callers must match them against their audited original inventory.

Run only inside a disposable, isolated CLI environment with real APCu:

```sh
php -d apc.enable_cli=1 -d apc.use_request_time=0 \
  tools/php83/apcu-probes/wrapper.php /path/to/server-Rigel-18.20.0 control
php -d apc.enable_cli=1 -d apc.use_request_time=0 \
  tools/php83/apcu-probes/wrapper.php /path/to/server-Rigel-18.20.0 adapter
```

Requires PHP 7.4 or PHP 8.3 CLI, recording the actual runtime version. This is **APCu-only** in both cases, not a legacy APC baseline. It rejects
pre-existing `apc_*` functions and disabled APCu. The original control requires
`init()` to return false, demonstrating unavailable legacy functions, not a
healthy application cache. The optional experiment subsequently defines six
**fixture-only** direct aliases (`fetch/store/add/delete/inc/dec`). They are not
an application patch, proposed production shim, or proof that APC and APCu have
identical semantics. Never load this fixture in an application process.

The alias experiment records strict per-assertion actual/expected JSON for:

- initialization, set/get/delete, nested values and add without overwrite;
- a synthetic `stdClass` object roundtrip with exact class and nested property
  values (not PHP instance identity), followed by deletion;
- stored false versus cache miss: wrapper get returns false for both, while
  direct fetch's success reference distinguishes them;
- multi-get retaining stored false and omitting a missing key;
- increment/decrement and missing counters (no implicit creation);
- immediate and expired one-second TTL (three-second wait);
- each of these with `serializeData` false and true, including the actual
  serialized false representation.

All PHP diagnostics are fatal, including diagnostics under the original source's
`@unserialize`; the fixture never alters source or suppresses its diagnostics.
Any failed assertion/exception exits nonzero. Requires wall-clock APCu expiry
(`apc.use_request_time=0` when the setting exists). A scheduling delay before the
immediate TTL read may correctly fail the fixture; retain that evidence rather
than silently retrying it into a pass. Only uniquely named keys are removed;
there is no global cache flush. Runs take about six seconds in adapter mode.

## Limits

Passing asserts only these concrete synthetic wrapper behaviors against the
installed APCu. It does not establish legacy APC parity, cross-request/shared
cache persistence, atomicity under concurrency, memory-pressure eviction,
worker/API/config/autoload/logger consumer compatibility, locking behavior,
legacy application serialized-object compatibility, FPM/Apache SAPI behavior,
or performance. The object case covers only the newly constructed synthetic
`stdClass`, not old serialized application classes or their autoloading.
Serialized counter operations in the original base wrapper use get/set rather
than an atomic APCu increment and reset TTL through the original setter default;
this fixture does not certify those properties. Full application source has
other direct APC consumers: fixing only this wrapper is insufficient.

No production source, package, workflow, VM, release or cutover changes are
made or authorized by running this probe. `application_acceptance` and
`adapter_is_production_solution` deliberately remain false in every report.

## Existing isolated lab runner

From this migration worktree, the coordinator-owned runner can execute each case
in the existing isolated audit VMs (not `.20`):

```sh
bash tools/php83/apcu-probes/run-lab.sh 74 control
bash tools/php83/apcu-probes/run-lab.sh 74 adapter
bash tools/php83/apcu-probes/run-lab.sh 83 control
bash tools/php83/apcu-probes/run-lab.sh 83 adapter
```

It verifies configured loopback SSH target, port, user and guest hostname;
streams only this public fixture; runs as `nobody` with a read-only packaged
source bind, private network and denied socket syscalls; and bounds each unit
at 30 seconds/256 MiB. It uses the system PHP selected by the explicit `74`/`83`
argument. Each process has its own CLI APCu cache; no application cache is
modified. Record runner exit status alongside JSON and compare source hashes
across versions. A control passing on **both** runtimes demonstrates a pre-existing
APCu-only incompatibility in this fixture, not a new PHP 8.3 regression.

## Counter contract limitation

The missing-counter `false`/no-creation expectation is an explicit proposed
contract consistent with the original base class serialized path, **not a
measured legacy native APC contract**. Initial direct-alias experiments failed
four native-counter assertions on both PHP 7.4 and 8.3: APCu creates the missing
counters. Do not change these expectations merely to turn the experiment green,
or call the result a PHP 8.3 regression. Native APC/APCu-BC historical behavior
and actual callers must be reconciled before choosing a repair. The official
[APCu increment API](https://www.php.net/manual/en/function.apcu-inc.php) documents
TTL for newly inserted values. This fixture is allowed to fail and is not an
approved application adapter.
