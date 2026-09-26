# Serialization contracts — independent LOCAL review (Cursor)

- Case: `serialization-contracts` 3-target magic bridge (provisional, not selected)
- Executor/reviewer: Cursor Agent (local only)
- Scope owned: this file + `cursor-tests.*`
- Environment: workdir `/home/nilton/Projetos/nilton/NOVOS/platform-install-packages-php83`; no VM, SSH, network/backend, PHP app execution, archive extraction, ZIP creation, source/tools/patches edits, or credentials
- Harness identities reviewed: `doc/php83/serialization-contracts.md`, `tools/php83/serialization-contracts/{prepare.py,probe.php,test_prepare.py}`, `doc/php83/evidence/serialization-contracts/source-pins.json` (numbered bodies)
- Archive pins present and match recorded SHA-256: original `58d534d0…ab28`, exp12 `de5e61a1…7e8b`
- Status: **LOCAL_PREPARATION review + offline Python guards only. Not native acceptance.**

## Local test executed

```text
command: python3 tools/php83/serialization-contracts/test_prepare.py -v
exit: 0
evidence: cursor-tests.stdout (empty; unittest -v writes to stderr), cursor-tests.stderr, cursor-tests.exit
result: 8 tests OK in ~0.21s
```

Passing these guards proves deterministic bridge insertion / pin readability only. It is **not** PHP wire or application evidence.

## Proposal review (source-backed)

### C legacy reader vs new O wire

- Legacy `Serializable::serialize`/`unserialize` remain; direct `$object->serialize()` still yields JSON (`Credentials`) or `N;` (`NullCredentials`).
- Adding `__serialize`/`__unserialize` makes native `serialize($object)` prefer magic methods → wire framing moves **C → O**. That delta is expected and must be observed, not claimed away.
- Unchanged original74/original83 classes lack magic methods; raw O import can create a dynamic `payload` property and leave real credential fields unset. Doc correctly forbids assuming old readers can consume new O and forbids rollback-safe / generic byte-parity claims.
- Retained `Serializable` may still allow legacy C import on the bridged class; that needs runtime proof, not assertion from prep.

### Decorator / role / cache state loss (baseline, inherited)

Pinned sources confirm legacy gaps the bridge does **not** repair:

- `AbstractCredentialsDecorator::unserialize` rebuilds a plain `Credentials` only; wrapped subclass identity is lost.
- `CacheableCredentials`: `$cache` / `$cacheKey` never enter the payload.
- `RefreshableInstanceProfileCredentials`: `$client` never enters the payload.
- `RefreshableRole`: private `$roleArn` / `$s3Region` never enter the payload.
- Doctrine `FilesystemCache::doSave`/`doFetch` use native `serialize`/`unserialize` around `lifetime\\n` + payload, so C/O changes hit a real cache boundary.

Loss remains a baseline defect/limitation; silence about it would be a design failure. The proposal correctly treats it as visible, not as license to change unnoticed.

### Refresh dispatch

- Bridge `__serialize` calls `$this->serialize()` dynamically.
- Refreshable subclasses inherit the decorator bridge and keep `AbstractRefreshableCredentials::serialize()` (refresh-if-expired then delegate). Insertion on the three targets therefore preserves refresh-on-serialize dispatch without bypassing it.
- Probe uses `expiration=null` sentinels and constructor bypass for profile/cacheable so accidental refresh/network is avoided in prep shapes; that limitation is labeled and must not be read as refresh acceptance.

### Strict envelope / malformed / invalid UTF-8

- Envelope is exact: `array_keys($data) === ['payload']` and `is_string($data['payload'])`; else `UnexpectedValueException`. New O malformed rejection is intentional.
- Legacy malformed JSON path must remain visible via retained `unserialize($serialized)` (probe `malformed` operation).
- Invalid UTF-8 may make `json_encode` return `false`; bridging that non-string through `__serialize` would fail the strict string check on restore. Observe native outcome; do not invent parity with direct legacy calls.

### Reader matrix (plan text, not executed)

Doc plan: cohorts **original74 / original83 / bridge83 (candidate)** × recorded C legacy and O new for six concrete classes; write sequentially, freeze hashes, import in fresh processes; never synthesize C as “native74”. Expected broken old-reader×O behavior must be recorded without patching old classes. **This matrix has not run.** Current `probe.php` is preparation-only, not a guarded launcher.

## Blockers before a guarded native fixture may run

1. **No VM / coordinator permission** — AGENTS and the plan forbid native PHP until approved sandbox ownership exists.
2. **No guarded runner** — `probe.php` is explicitly not a safe standalone launcher; needs immutable inventory, typed exit, E_ALL + handler `return false`, private network/socket denial, pre/post identities, isolated writable cache only.
3. **No staged trees** — extraction / ZIP creation out of scope here; original74, original83, and bridged candidate trees with pin asserts are missing from this phase.
4. **Bridge not applied anywhere runnable** — `prepare.py` only previews `candidate_sha256`; no disposable bridge83 tree yet.
5. **Cache fixture not implemented** — FilesystemCache + DoctrineCacheAdapter private-dir hit/expired/corrupt cohort is TO IMPLEMENT; no cache roundtrip acceptance possible.
6. **PHP 8.3 FileCache implode signature** — pinned `FileCache::getFilename` still uses `implode(array, glue)`, removed in PHP 8.0. Cache-envelope work on original83/bridge83 will hit this unless a separately reviewed repair exists; credentials object roundtrips do not require it.
7. **AbstractCacheAdapter not pinned** — `DoctrineCacheAdapter` extends it; cache fixture prep should pin that member before staging.
8. **Refresh seams incomplete** — real role STS / instance-metadata refresh and real cacheable client construction remain untested or constructor-bypassed; offline prep must not claim them.
9. **Independent CLI execution + strict diagnostic contracts** — required by the plan; not present yet. Offline Python OK ≠ native evidence.

## Smallest necessary changes (still not acceptance)

1. Coordinator-owned disposable sandbox + reviewed guarded runner wrapping `probe.php` (no raw PHP CLI as acceptance path).
2. Stage pin-verified original74 / original83 / bridge83 trees; stop on any relied-member hash mismatch (all PATHS, not only three targets).
3. Apply the provisional 3-file bridge only inside disposable bridge83; keep Serializable and legacy methods intact.
4. Run declaration-only + six-class roundtrip / malformed / invalid-utf8 with full getter+property+wire+diagnostic capture; then C/O reader matrix across the three cohorts.
5. Implement synthetic private-dir cache fixture only after FileCache PHP8 implode (or equivalent) risk is explicitly handled or scoped out; pin `AbstractCacheAdapter` if that path is used.
6. Keep status labels: preparation / observation only. Do **not** treat plan completion or harness green as native or release acceptance.

## Verdict

The provisional 3-target magic bridge matches the pinned sources for C→O delta, inherited decorator/role/cache loss, dynamic refresh dispatch, and strict new envelope. Doc and tools correctly refuse generic byte parity, rollback safety, and native acceptance from prep. Offline `test_prepare.py` exit **0**. Native fixture remains **BLOCKED** pending VM permission, guarded runner, staged trees, optional bridge apply in disposable tree, and unimplemented cache/sandbox fixtures.
