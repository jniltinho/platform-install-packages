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

## R2 consolidated follow-up — PREPARED_ONLY, authorization blocked

R1 source/harness/reports remain unchanged at checkpoint 0e46d5e2. R2 adds a
write-time guard in three bridges: false/non-string legacy payload throws the
same native83 Exception class/message before any O envelope is returned. All six
concrete classes in this bounded family return string or false; external custom
subclasses returning null are not accepted (native Serializable permits null).
This is not a generic Serializable migration helper.

A separate fourth patch only swaps two arguments in Doctrine FileCache's implode.
Three native83 trees isolate this dependency: original, FileCache fix only, and
FileCache fix + guarded AWS bridges. Patch hashes/families are separately recorded
in patches/php83/held/serialization-contracts/manifest.json. No framework
replacement, legacy method/property/cache path or backend changes.

One consolidated native batch is prepared: **38 original74 + 96 native83**
observations, in that order. Original74 emits six real C payloads, tests legacy
and O cross-import, and exercises unmodified real FilesystemCache. Native83 adds
original74 C readers plus three isolated cache variants. Cache cases: hit,
expired, corrupt wire, refresh-hit, refresh-miss, invalidUTF save-time failure,
recorded C and recorded O input. Real Doctrine FilesystemCache and Guzzle
DoctrineCacheAdapter are used; expiry refresh uses real CacheableCredentials and
seeded local credentials, never role/metadata network calls or fake backends.

Each cache process gets systemd PrivateTmp and a fixed synthetic cache folder;
variants never share a writable cache. Raw cache file bytes are base64/hash
(sentinels only); metadata namespace writes are distinguished from target-object
writes. InvalidUTF must leave target absent. Cross-import cache files are seeded
from recorded native83 payloads and labelled accordingly, not fabricated74 output.
Native83 also consumes real original74 wires from the preceding report. Old83
implode failure remains an explicit control, not whole-cache acceptance.

New guarded runner supports only native83/baseline74 hosts; on74 it refuses all
but original and explicitly loads pinned JSON with -n. Full stage and both
runtime-library sets are checked before/after. Private /tmp is the only extra
PHP-readable writable fixture path. No app config, API/SQL or real credentials.
STS/profile external refresh, mixed-version cache isolation/rollback and installed
application remain open gates even if bounded contracts pass.


### R2 checkpoint status and read-only review

- Fifteen authorial offline tests pass. No R2 native execution or independent
  test execution occurred. The 38/96 counts are planned, not passed cases.
- Actual OpenCode read source but its test shell operation redirected output to
  `/tmp/opencode-r2-tests.*` and was denied. CLI exit0 is not a review/test pass.
  That operation was not retried or routed through another executor.
- Separate work reported denied reads of the two `/tmp/kaltura-php*-ssh.conf`
  files. No dependent VM operation will be attempted until explicitly authorized.
  These are specific denials, not evidence that every `/tmp` path was denied.
- Actual Cursor source-only review completed exit0 with no shell/tests/VM calls.
  Its public findings remain retained, not interpreted as runtime approval.

Read-only findings to adjudicate before acceptance: the copied native failure
message mentions NULL although the bounded bridge rejects null from unsupported
custom subclasses; the guard in the unextended NullCredentials class is redundant
(but external overrides are not exhaustively inventoried); cache original83 fails
at namespace/implode before UTF-8 serialization, intentionally isolated by the
**cachefix-only** control and not attributed as an UTF-8 failure. The happy-path
C/O import reference is explicitly R1 native83, while original74 produces its own
pending C records. No file/cache/exception contract is accepted just from source.
The PHP7.4 reader outcome is still unexecuted, despite the known PHP8.3 rollback
failure. Absolute existing-source paths are preparation dependencies, not portable
installation commands.

Next action requires explicit authorization for the denied operations, then
independent guard execution and the original74/native83 primary+repeat matrix
on fresh immutable stages. Cache namespace/rollback design, external subclass
null policy and all installed-application gates remain unresolved. R2 tools,
held patches, manifest and local preparation are frozen at this checkpoint;
there is no artifact selection, package build or deployment.

An additional authorial offline rerun during checkpoint preparation is retained
separately as `r2-final-author-tests.*` and `r2-final-shell.*`. It is **not** a
substitute for, authorization of, or independent validation of the denied
OpenCode operation. No further tests or runtime operations were attempted after
the coordinator's final freeze instruction.
