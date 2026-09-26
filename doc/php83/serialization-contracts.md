# AWS credential serialization: rejected R1 candidate, repair in preparation

## Current result — 60 native83 observations independently repeated

The first candidate is **REJECTED**, not accepted: invalid UTF-8 changes failure
from write-time native Exception to a stored O payload and read-time
UnexpectedValueException in five classes. No product was promoted. Actual
OpenCode repeated all60 process records byte-identically; both collectors exited0
with deliberate OBSERVED_NOT_ACCEPTED, and four39-object runtime snapshots are
identical. Complete handler events and raw stderr remain in primary/repeat JSON.
The labs were released/transferred after actual independent CLI terminal0.

For six normal classes: original83 writes C; candidate writes O and reads both C/O.
Original83 reads C but rejects O with false plus native warnings. This is observed
rollback incompatibility, not merely a risk hypothesis. Original74 remains pending.
A separately versioned guard must reject invalid legacy payload before writing O;
FileCache's reversed implode needs a separate patch/control before real cache tests.

Actual Cursor first review/test8 exited0. Cursor executor-readiness review timed
out124 after19guards+shell all0 (not a completed review). Actual OpenCode then
completed the scoped safety review0, and later executed independent60repeat0.

## Historical preparation

The exp12 API attribution has 2 groups / 48 events. The message-free API ledger
is not native declaration proof. This local cycle targets a cohesive credential
family without upgrading AWS or suppressing diagnostics. No VM, archive extraction,
new ZIP, production credentials or backend execution has occurred in this phase.

## Source-supported contract

The original graph is ready at generation 2026-09-25T12:19:00Z. Exact relied
files have metadata-match/no-recorded-issue coverage (best-effort, not exhaustive).
The class trace has zero recorded edges; this is NOT evidence of no consumers.
Direct complete source from pinned original and exp12 ZIP members supplements it.
[Source identities and numbered bodies](evidence/serialization-contracts/source-pins.json)
retain exact archive and member hashes. No archive is extracted.

- Credentials serializes a JSON dictionary (key, secret, token, expiration).
- NullCredentials uses `N;` and its legacy reader ignores input.
- AbstractCredentialsDecorator is concrete; it delegates payload production and
  restores a new plain Credentials. It does not restore the wrapped subclass.
- AbstractRefreshableCredentials overrides serialize to refresh expired values.
  The bridge must call `$this->serialize()` dynamically, not bypass this behavior.
- CacheableCredentials, RefreshableInstanceProfileCredentials and RefreshableRole
  inherit that implementation. Cache adapter/key, profile client and role's private
  ARN/region are not serialized by the legacy method. Their loss is a baseline
  defect/limitation, not permission to change it unnoticed.
- Real CacheableCredentials::refresh passes objects to its cache adapter;
  Doctrine FilesystemCache::doSave calls native serialize and doFetch calls native
  unserialize. Its disk envelope is lifetime plus newline plus payload. Therefore
  native C/O changes affect a real cache boundary, not only test formatting.

PHP documents that magic serialization takes precedence over Serializable and
that implementing Serializable without both magic methods is deprecated since
8.1 ([magic methods](https://www.php.net/manual/en/language.oop5.magic.php),
[Serializable](https://www.php.net/manual/en/class.serializable.php)). These are
API semantics, not evidence that our candidate preserves wire compatibility.

## Small provisional design, not selected

Three targets: Credentials, NullCredentials, AbstractCredentialsDecorator.
Add `__serialize(): array` with a single `payload` field produced by the actual
legacy serialize method, and `__unserialize(array): void` that validates the exact
new envelope then delegates to the existing legacy reader. Keep Serializable,
all legacy methods, properties, constructors and refresh methods unchanged.
`prepare.py` generates only metadata and a candidate hash preview; no application
file is changed. Local tests validate this proposal's deterministic insertion.

Native writes necessarily move from C to O framing. Direct `$object->serialize()`
should retain JSON/N; bytes, but this needs runtime proof. Legacy C imports should
remain possible via retained Serializable; new O is NOT assumed readable by
original74/original83. Even PHP7.4 supports magic methods, but the *unchanged old
class* does not implement them. A raw O array may create a dynamic `payload`
property and leave real credential state unusable. No rollback-safe assertion.
Malformed new envelope rejection is intentionally new; malformed legacy JSON
behavior must remain visible. Invalid UTF-8 may make the legacy JSON method return
false; observe actual native outcome rather than inventing byte parity.

## Reviewed execution plan required before VM use

Three cohorts: unchanged original74, unchanged original83, bridge83 using exact
exp12 source. Before staging assert every relied member's original/exp12 identity,
not only three patch targets. Source hash mismatches are stop conditions.

1. Declaration-only full real classes confirm precise diagnostic attribution.
2. Six concrete classes × roundtrip plus focused malformed JSON and invalid UTF-8
   controls. Capture typed getters, full declared-property reflection, direct
   payload, native wire/base64/hash, exception, all handler events AND raw stderr.
   All credentials are fixed sentinels; null expiration prevents accidental refresh.
3. Readers original74/original83/bridge83 × real recorded C legacy and O new
   payloads for all six classes. Write records sequentially, freeze payload hashes,
   then import in fresh processes. Never synthesize C and label it native74 output.
   Record expected broken old-reader O behavior without updating old classes.
4. Real FilesystemCache + DoctrineCacheAdapter synthetic private directory:
   write/read/fresh-process old/new cache envelope, cache hit/expired/corrupt values.
   This fixture remains TO IMPLEMENT; no cache roundtrip acceptance yet.
5. Expiration/refresh: use real CacheableCredentials with seeded real local cache
   to refresh expired values without network. Real role STS and instance-metadata
   refresh require a separately reviewed transport seam or remain untested.
   Current profile/cacheable object preparation uses constructor bypass only,
   labels that limitation, and does NOT validate real client construction/refresh.
6. Native sandbox E_ALL and handler returns false, private network/socket denial,
   immutable source/runner/runtime pre/post identities; isolated writable cache only.
   Strict exact inventory/typed exit/diagnostic contracts and independent actual
   CLI execution are required before accepting the repair.

The current `probe.php` is a preparation fixture, not a safe standalone launcher.
No PHP execution is permitted until the coordinator grants the VM and a guarded
runner is reviewed. Native failures/diagnostics remain observations, not forced
passes. Offline Python tests are not PHP behavior evidence.

## Recovery/release gates

If original readers cannot consume O, mixed-version/shared cache rollout requires
an explicit versioned private cache namespace or controlled invalidation and a
rollback procedure. This cycle does NOT change cache paths or delete old data.
External sessions/queues/object stores and dynamically supplied decorators remain
unmapped; bounded graph discovery is not a global serialization inventory. Full
artifact regression and installed application acceptance remain separate gates.

## Preparation follow-up: native83 wire-only stage (not executed yet)

Actual Cursor local review exited 0 and executed 8 offline guards. It found a
separate real obstacle: `Doctrine FileCache::getFilename` passes reversed implode
arguments, invalid on PHP8. This remains visible. A separately reviewed fix may
follow, but no silent change is included in the three AWS targets. Cache execution
is deferred until that dependency control is addressed explicitly.

The wire-only stage is now prepared by copying existing original source files
whose bytes match both pinned archives, never extracting either archive. It
contains complete classes and real AWS autoloader/required enum/interface files,
not a substitute class implementation. The first bounded matrix is **60 native83
processes**: two variants × six classes × three operations, followed by 24
cross-reader/writer cases. Original74 is explicitly pending its separate lab;
original83 payloads must not be mislabelled original74. Collector status only
indicates complete observations, never diagnostic or application acceptance.

`run.sh` rejects unexpected host/uid/case/pin, checks exact stage inventory and
source/runtime files before/after, and confines PHP under systemd read-only/private
network/socket-denial protections. Sources and fixtures are read-only, and read
payloads arrive as bounded synthetic stdin. `stage.py` refuses an existing remote
stage. Runtime snapshot command remains the unchanged public helper
`doc/php83/evidence/exp10-runtime/snapshot-php83.py` to new evidence outputs.
An independent review of this execution wrapper and 19 local tests must finish
before any VM use. No denied `/tmp` object is an input to this work.
