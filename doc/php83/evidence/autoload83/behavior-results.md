# Held autoload patches — bounded primary evidence

**Partial validation; overall matrix remains FAIL.** Final primary `primary-r3.json` contains 26 processes: 20 positive cases passed, three removed-`__autoload` PHP8.3 fatal controls passed, and three actual empty-project `-T` cases failed (`kConf` missing). Do not call this 26 passes or application acceptance.

## Real configured CLI control

A separate configured-project `-T` case uses unchanged real `kConf`, `kEnvironment`, `kConfCacheManager`, factory and cache classes from the pinned exp10 ZIP. The real `kSessionConf::store` API receives synthetic local configuration and nonempty local/remote cache configuration maps. The real manager initializes those classes and resolves the requested `cache_root_path` from its session cache. There are no replacement application classes, reflection writes to private caches, network calls or SQL. Source and project directories remain read-only; no writable cache was necessary. Each configured case loads 37 pinned files. The full actual task list is byte-identical across before74/candidate74/candidate83; task execution itself is not tested.

The initial empty-project failure is retained separately rather than reclassified as a successful negative test. It establishes a fixture limitation, not a proven patch regression. Configured success does not waive unrelated existing migration blockers.

## Harness/evidence revisions

* `primary-r1.json` retains 20 completed records and INCOMPLETE status: empty PHP array `loaded=[]` caused a collector AttributeError during fatal-control parsing. All three native fatal controls are independently retained in `primary-fatal-attempt-r1.json`. Initial source inventory and runtime were checked unchanged afterward.
* Immutable fresh r2 stage contains explicit target hash before `require`, JSON-object loaded inventory, configured real project case. Collector requires relevant actual loaded files and fixture targets, exact row inventory and callback-hit traces. `primary-r2.json` records the full 26-process result.
* Final collector-only r3 uses the same frozen r2 PHP probe/stage. It adds positive task-list contracts, whole task-list comparison, and exact expected native diagnostic phase/severity/file/line/count validation. `primary-r3.json` is authoritative primary evidence. Previous collectors/probe are retained under `behavior-attempt-r1/` and `behavior-attempt-r2/`.
* 19 local positive/negative/static tests pass in `test-local-r6.*`. A failed intermediate local test edit is preserved in `test-local-r3.*` (NameError), corrected in r4; no runtime failure was hidden.
* Whole staged source inventory remained unchanged. PHP binaries/modules/linked-library/config identity objects in `runtime-before-r2.json` and `runtime-after-r3.json` are identical.

## Contracts and differences

HP prepend and existing callbacks, actual EntityLookup loading/misses and legacy74 preservation pass. sfCore real Finder-derived map supports both simple and full loader registration, actual mapped classes and unserialize. Before/candidate74 HP/core functional rows are identical. CLI empty/preexisting queues explicitly distinguish native implicit legacy loading from the candidate appended SPL closure: existing loader hits retain precedence, while a preexisting queue's misses now reach Symfony fallback. This is a deliberate composition change, not universal PHP7.4 parity.

Warnings remain visible on native stderr. The patched obsolete global-autoload declaration deprecations disappear. PHP74 old-style `pakeYAMLNode` constructor deprecation remains in CLI cases, and PHP83 configured CLI retains the native `libxml_disable_entity_loader()` deprecation. Diagnostic inventories are explicit, not suppressed or assumed equal between language versions.

Untested: callbacks appended/prepended **after** framework registration, duplicate class winners, exception propagation from callbacks, repeated direct includes/class redeclaration, unavailable SPL guard, real config/cache misses, task execution, application acceptance. These require later bounded cases; current results do not close them.

## Independent repeat

Baseline74 released to coordinator after primary completion. Run unchanged tools with new output names (collector exits **1**, intentionally preserving three empty-project failures):

```sh
python3 tools/php83/exp10-api/runtime-identity.py doc/php83/evidence/autoload83/claude-runtime-before.json
python3 tools/php83/autoload83/collect.py /tmp/php-autoload83-r2/identity.json doc/php83/evidence/autoload83/claude-primary.json
python3 tools/php83/exp10-api/runtime-identity.py doc/php83/evidence/autoload83/claude-runtime-after.json
python3 -m unittest discover -s tools/php83/autoload83 -p 'test_*.py' -v
```
