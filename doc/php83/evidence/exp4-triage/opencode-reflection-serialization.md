# exp4-triage — opencode reflection + serialization (bounded)

Scope: ONLY remaining groups listed below. No source/patch/manifest/doc edits made.
Read-only analysis; this report is the sole writable output.

## Execution identity

- Executor: opencode (Muse Spark 1.3 Free path) — source-specific analysis, NOT a green application claim.
- Reviewer rotation: per AGENTS.md this cycle requires Claude CLI / Grok CLI / Cursor `agent` independent review with Codex coordination; this report is opencode's executor output only and does not substitute for those reviews.
- Command: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tools/php83 -p 'test_*.py'`
- Result: **122 tests, OK, exit 0** (verified 2026-09-25 in `/home/nilton/Projetos/nilton/NOVOS/platform-install-packages-php83`; verbose tail confirms `Ran 122 tests ... OK`).
- Limitation: harness green ≠ application acceptance. No PHP runtime present in this container (`php: command not found`); no live PHP 8.3 execution was performed by this agent. Native 8.3 behavioral evidence below is cited from checked-in fixtures, not re-executed here.

## Fixture identities (exact)

- `doc/php83/evidence/exp4-triage/locations.json`: **40 groups / 1073 events** (recomputed: `len(rows)==40`, `sum(count)==1073`). `artifact_sha256=a1ce4c46...ab9d08`.
- `doc/php83/evidence/exp4-triage/coverage.json`: project `kaltura-rigel-18.20.0-full`, `generation=2026-09-25T12:19:00Z`, `index_mode=full`, `recording_status=complete`.
- `doc/php83/evidence/exp4-triage/classification.json`: `status=source-supported triage; no diagnostic accepted as exception`.
- `doc/php83/evidence/exp4-triage/native-83.json`: `php=8.3.6, sapi=cli`, includes `Exception::__wakeup tentative_return=void` row; `native-83.exit=0`, `native-74.exit=0`.
- Raw diagnostic messages are intentionally absent (secrecy). Every classification below is labeled **source-supported inference** vs **confirmed error text**. Nothing below claims a confirmed runtime message.

## Graph evidence (Tier 2, bounded)

- Project: `kaltura-rigel-18.20.0-full` (root `.../kaltura-rigel-18.20.0-source/graph-view`), generation `2026-09-25T12:19:00Z` matches coverage.json.
- `check_index_coverage` on all 6 assigned files: each `status=no_recorded_issue`, `freshness=metadata_match`, `recommended_action=use_graph_with_best_effort_caveat`. Signal is best-effort only, not completeness proof.
- `search_graph` hits (exact lines match artifact source):
  - `KalturaEntryService.anonymousRankEntry` — `api_v3/lib/KalturaEntryService.php 1836-1852`.
  - `KalturaAPIException.__wakeup` — `api_v3/lib/exceptions/KalturaAPIException.php 40-48`; `__sleep` 35-38; `__construct` 14-24.
  - `KalturaActionReflector.getActionParams` — `api_v3/lib/reflection/KalturaActionReflector.php 110-169` (contains lines 129 + 153).
- `get_code_snippet` verified `anonymousRankEntry` and `getActionParams` bodies byte-identical to ZIP reads below.
- `trace_path anonymousRankEntry inbound`: `callers_total=3` — `BaseEntryService.anonymousRankAction`, `MediaService.anonymousRankAction`, `MixingService.anonymousRankAction`.
- Out-of-scope observed methods (NOT triaged here, listed only to avoid double-claim): `CriteriaFilter.applyFilter 45-54`, `Partner.getAlwaysAllowedPermissionNames 1426-1436`, `KalturaLog.analytics 117-126`.

## Artifact source (exact, read-only via zipfile)

ZIP: `/home/nilton/Projetos/nilton/NOVOS/platform-install-packages-php83-artifacts/exp4/Rigel-18.20.0-php83-experimental.exp4.zip`, root `server-Rigel-18.20.0/`. All 6 assigned paths present in namelist. No ZIP edit. `sha256` per locations.json rows re-checked against excerpts (match).

---

### G1 — `api_v3/lib/KalturaEntryService.php:1836` optional-before-required

Source (exact):

```php
protected function anonymousRankEntry($entryId, $entryType = null, $rank)
```

Callers (exact, artifact source):

- `api_v3/services/BaseEntryService.php:762`: `anonymousRankEntry($entryId, null, $rank)`
- `api_v3/services/MediaService.php:1128`: `anonymousRankEntry($entryId, KalturaEntryType::MEDIA_CLIP, $rank)`
- `api_v3/services/MixingService.php:371`: `anonymousRankEntry($entryId, KalturaEntryType::MIX, $rank)`

Finding (source-supported inference, NOT confirmed error text): `$entryType = null` (optional) precedes required `$rank`. PHP 8.0+ deprecates optional-before-required (treated as required). Inference only — raw exp4 message absent, no live PHP run here.
Confirmed: signature shape + all 3 callers pass 3 positional args; any reorder changes caller mapping.

Minimal repair proposals (choose ONE, scoped; do not blanket-cast):

- **Option A (preferred for call-site stability):** keep order, make trailing param nullable-optional:
  `anonymousRankEntry($entryId, $entryType = null, $rank = null)` + explicit guard `if ($rank === null || $rank <= 0 || $rank > 5) throw ...INVALID_RANK_VALUE`. Zero caller edits; preserves positional mapping; converts deprecation into validated required-at-runtime.
- **Option B (clean signature, touches callers):** `anonymousRankEntry($entryId, $rank, $entryType = null)` + update exactly the 3 call sites above. Cleaner long-term, larger blast radius (reflection-derived API param maps must be re-checked).

Required tests (none executed here — needed before accept):

1. Reflection test: `ReflectionMethod(...anonymousRankEntry...)->getParameters()` — assert no optional-before-required (or assert explicit deprecation-free on 8.3 target).
2. Caller-mapping test: each of the 3 `anonymousRankAction($entryId, $rank)` wrappers forwards `($entryId, <expectedType>, $rank)`; assert Media/Mix type constants preserved.
3. Rank validation: `0, -1, 6, null, "3"` → `INVALID_RANK_VALUE`; `1..5` → `kvote` path (mocked peer).
4. Doc-comment/API-map test: service-map / reflector output for `anonymousRank` actions unchanged in arity/order.

Blockers / unresolved: deprecation vs fatal not confirmed (no raw text, no PHP run). **Not accepted.**

---

### G2 — `api_v3/lib/exceptions/KalturaAPIException.php:40` `__wakeup`

Source (exact, 1-49 read):

```php
public function __sleep() { return array('code','message','args','codeStr'); }
public function __wakeup() {
  // When running on PHP7 the code string does not get un-serialized
  // (This is probably due to the fact that the Exception base class has a code attribute which is of type int)
  if($this->codeStr) { $this->code = $this->codeStr; }
}
```

Corroborating fixture (not a live run): `native-83.json` records `Exception::__wakeup tentative_return=void`, `declared_return=None`.
Finding (source-supported inference): missing `: void` return on `__wakeup` mismatches PHP 8.3 tentative return; expected deprecation class (same family as other `native-return-contracts` rows). Raw message absent → severity unconfirmed. Additional semantic risk is independent of deprecation: `Exception::$code` is int-typed; string codes round-trip via `$codeStr` hack — any signature change must preserve that.

Minimal repair (scoped to this class only; NO blanket `ReturnTypeWillChange` sweep, NO warning suppression):

- Add explicit `: void` to `__wakeup()` (and audit `__sleep(): array` in the same edit only): `public function __wakeup(): void`.
- If PHP 7.4 compat must be kept in the same branch, gate is NOT a version check in code — instead backport via separate patch branch; do not add `#[\ReturnTypeWillChange]` here without reviewer sign-off (per task ban on unreviewed sweep).

Required tests:

1. `serialize()` → `unserialize()` roundtrip on PHP 7.4 and 8.3 fixtures: `code`, `codeStr`, `args`, `message` preserved; string code (e.g. `ENTRY_ID_NOT_FOUND;...`) survives via `codeStr`.
2. Serialized-bytes compatibility: bytes produced on 7.4 unserialize on 8.3 and vice versa (session/cache interop).
3. `__sleep` allowlist unchanged (`code,message,args,codeStr`); no new props leaked into session/cache payloads.
4. Exception-parent alias: `getCode()` int vs `getCodeStr`-equivalent behavior documented; no caller relies on `->code` being string post-wakeup.

Blockers / unresolved: tentative-return deprecation text unconfirmed; session-store consumers of this exception not enumerated. **Not accepted.**

---

### G3 — `api_v3/lib/reflection/KalturaActionReflector.php:129,153` `getClass`

Source (exact):

```php
// 129
$paramClass = $reflectionParam->getClass(); // type hinting for objects
if ($paramClass) { $type = $paramClass->getName(); }
// 153
else if ($reflectionParam->getClass() && $reflectionParam->allowsNull()) // for object parameter
```

Finding (source-supported inference): `ReflectionParameter::getClass()` is deprecated since PHP 8.0 (still callable in 8.3 but emits deprecation; successor is `getType()`). Double call (129 + 153) means two deprecation hits per object param. Raw message absent → unconfirmed whether exp4 counted deprecations or fatals. Behavior risk beyond deprecation: `getClass()` does not represent union types, `?Type`, `self`/`parent` aliasing, or builtins — `getType()` path must replicate the doc-comment fallback (`$parsedDocComment->param`) and `allowsNull` → `setOptional(true)` semantics.

Minimal replacement (scoped helper, no blanket cast):

```php
private static function getParamClassName(ReflectionParameter $p, ReflectionClass $declaringClass = null) {
  $t = $p->getType();
  if ($t instanceof ReflectionNamedType && !$t->isBuiltin()) {
    $n = $t->getName();
    if ($n === 'self' && $declaringClass) return $declaringClass->getName();
    if ($n === 'parent' && $declaringClass && $declaringClass->getParentClass()) return $declaringClass->getParentClass()->getName();
    return $n; // 'static' left as-is; caller decides
  }
  return null; // union/intersection/builtin/no-type → doc-comment fallback
}
```

Call sites: line 129 `$paramClass = ...getClass()` → `$paramClassName = self::getParamClassName($reflectionParam, $reflectionClass)`; line 153 `getClass() && allowsNull()` → `$paramClassName !== null && $reflectionParam->allowsNull()`. Keep `isOptional()` branch first (unchanged), keep doc-comment `throw Type not found...` fallback unchanged, keep `allowsNull → setOptional(true)` for objects.

Required tests:

1. Scalar + doc-comment type: `($id)` with `@param int` → type from doc comment, no crash.
2. Class type: `(MyObj $o)` → class name; nullable `(?MyObj $o = null)` → optional via `isOptional` path.
3. Nullable-object without default (the line-153 path): `(MyObj $o = null)`-vs-`(?MyObj $o)` where `isOptional()==false && allowsNull()==true` → `setOptional(true)`.
4. Self/parent aliases: method on `Foo` with `(self $x)`, `(parent $x)` → resolved FQCN.
5. Union type: `(A|B $x)` → falls back to doc-comment type (no crash, no wrong single-class pick).
6. No-type-no-doc → same `Type not found in doc comment` exception text.
7. Cache compat: `cacheReflectionValues()` / APC path stores same `actionParams` shape before/after.

Blockers / unresolved: `getType()` availability on the running reflection target (union/intersection edge) and any subclass overriding `getActionParams` not enumerated. **Not accepted.**

---

### G4 — `infra/storage/RefreshableRole.class.php:21` + `vendor/aws/Aws/Common/Credentials/AbstractCredentialsDecorator.php:22` serialization

Source (exact):

- `RefreshableRole extends AbstractRefreshableCredentials` (line 21), `refresh()` is `public function refresh()` while parent declares `abstract protected function refresh()` (widening — allowed).
- `AbstractCredentialsDecorator implements CredentialsInterface` (line 22); `CredentialsInterface extends \Serializable` (artifact source confirmed).
- `AbstractCredentialsDecorator::serialize()` → `$this->credentials->serialize()`; `::unserialize($s)` → `new Credentials('','')` + `->unserialize($s)`.
- `Credentials::serialize()` = `json_encode([key,secret,token,ttd])`; `::unserialize()` = `json_decode` assign. `AbstractRefreshableCredentials::serialize()` refreshes-if-expired then delegates; `CacheableCredentials`/`RefreshableInstanceProfileCredentials` extend the same chain (artifact sources read).

Finding (source-supported inference): `Serializable` interface is deprecated in PHP 8.1; classes implementing only `serialize()/unserialize()` (old style) without `__serialize()/__unserialize()` emit deprecation on serialize paths (file cache via `DoctrineCacheAdapter(FilesystemCache)`, `CacheableCredentials::save/fetch`, any `$_SESSION` store). Raw message absent → unconfirmed. Second risk: `unserialize()` rehydrates as base `Credentials`, dropping decorator subtype (`RefreshableRole`/`CacheableCredentials` wrapper) — pre-existing design, must not be silently "fixed" by changing class instantiated without cache/session compat review.

Minimal repair (scoped; NO `Serializable` removal, NO upgrade recommendation):

- In `AbstractCredentialsDecorator` (and `Credentials` for the leaf): ADD `__serialize(): array` / `__unserialize(array $data): void` forwarding to existing `serialize()/unserialize()` logic; KEEP old methods for BC:
  `public function __serialize(): array { return ['payload' => $this->serialize()]; }` + `public function __unserialize(array $d): void { $this->unserialize($d['payload']); }` (leaf `Credentials::__serialize` returns the 4 fields directly; `__unserialize` assigns with `?? null` guards).
- Do NOT change `unserialize()`'s `new Credentials('','')` target or `RefreshableRole::refresh()` visibility in this repair.

Required tests:

1. Roundtrips: `serialize→unserialize`, `__serialize→__unserialize`, and cross (`serialize` bytes → `__unserialize` wrapper) for `Credentials`, `CacheableCredentials`, `RefreshableRole` (mock STS).
2. Serialized-bytes/cache compat: payloads written by old code readable by new code and vice versa; `DoctrineCacheAdapter(FilesystemCache)` save/fetch cycle; `isExpired→refresh()` still fires on `getAccessKeyId/getSecretKey/getSecurityToken/serialize`.
3. Session compat: `session_encode`/`session_decode` or explicit `serialize($_SESSION)` with a decorator inside does not emit `Serializable` deprecation on 8.3 target.
4. Type-alias check: `self`/`parent` not involved here, but `instanceof CredentialsInterface` and `get_class()` post-unserialize documented (subtype-drop acknowledged, unchanged).

Blockers / unresolved: live session/cache consumers and STS-mocked refresh not executed (no PHP here); old-payload interop matrix not run. **Not accepted.**

---

### G5 — `alpha/config/kConf.php:7` `libxml_disable_entity_loader(true)`

Source (exact): line 7 `libxml_disable_entity_loader(true);` at top-level of `kConf.php` (after `setlocale`).

Fixture note: no `native-83.json` row for libxml (function-level deprecation, not a method contract) — no fixture confirmation either way.
Finding (source-supported inference): `libxml_disable_entity_loader()` is deprecated in PHP 8.0+ (no-op; external-entity loading is off by default). Removing the line without compensating controls would WEAKEN XXE posture if any parser relies on it. Bounded artifact scan (non-vendor PHP, capped 60 hits) shows many unguarded sinks: `myFlvStreamer`/`myMetadataUtils`/`myCCMixterServices`/`myYouTubeServices`/`facebookUtils` `new DOMDocument()->loadXML($external)`, `kXmlConfig`/`PartnerPackages` `simplexml_load_string(file_get_contents(...))` without `LIBXML_NONET`. `KDOMDocument extends DOMDocument` adds encrypted-load/schema-validate wrappers but no entity-loader hardening (artifact source read). Raw message absent → deprecation unconfirmed; XXE exposure unconfirmed without parser-option audit.

Minimal repair (scoped; NO deletion-only edit, NO libxml upgrade, NO suppression):

- Keep line 7 guarded for old runtimes, add explicit per-parser hardening instead of relying on global:
  ```php
  if (PHP_VERSION_ID < 80000 && function_exists('libxml_disable_entity_loader')) { libxml_disable_entity_loader(true); }
  ```
  plus at each network/metadata XML sink (starting with the enumerated `loadXML`/`simplexml_load_string` sites): pass `LIBXML_NONET | LIBXML_NOERROR` where compatible and/or `libxml_set_external_entity_loader(function(){ return null; })` in the bootstrap path that owns untrusted XML. Each sink change is its own reviewed patch with behavior test — not a sweep.
- Do NOT add `LIBXML_NOENT` anywhere; audit that none is currently passed (bounded scan saw none in the 60-hit window; full enumeration still open).

Required tests (XXE guards):

1. XXE fixture: external-entity (`<!ENTITY xxe SYSTEM "file:///etc/passwd">`) and billion-laughs payloads through `KDOMDocument::loadXML`, `myXmlUtils::validateXmlFileContent`, `kXmlConfig` load → entity NOT expanded, load fails-closed or returns sanitized.
2. `LIBXML_NONET` presence test on network-fed sinks (`mySearchProxyServices`, `myYouTubeServices`, `S3.php:1030` response parse).
3. Regression: local config XML loads (`partnerPackages.xml`, referrer/base XML) still parse with the guard active.
4. Deprecation check: bootstrap include of `kConf.php` on 8.3 target emits no `libxml_disable_entity_loader` deprecation (guarded path).

Blockers / unresolved: full sink enumeration incomplete (scan capped, vendor excluded); DTD/subset handling per parser not reviewed; no live XXE probe executed. **Not accepted.**

---

## Cross-cutting constraints honored

- No blanket casts, no `@`-suppression additions, no `ReturnTypeWillChange` sweep, no upgrade recommendation — each proposal is scoped to its group with caller/compat evidence.
- Nullable-type and self/parent-alias handling specified where reflection/serialization semantics require it (G3, G4).
- Serialized-bytes / cache / session compatibility tests required for G2 + G4 before any accept.
- XML XXE guards required for G5 before any accept.
- Unresolved items are marked **Not accepted** above; nothing is marked accepted.

## Handoff for independent reviewers

- Needed: Claude CLI / Grok CLI / Cursor `agent` independent source review of G1–G5 (non-overlapping cases, rotated), Codex coordination; record BLOCKED/NOT_EXECUTED for any CLI auth/quota failure rather than substituting.
- Suggested split: (i) G1+G3 reflection/signature, (ii) G2+G4 serialization/bytes-compat, (iii) G5 libxml/XXE sink enumeration + fixture probes.
- This report used exact artifact source (`zipfile.read`, root `server-Rigel-18.20.0/`), graph Tier 2 (`kaltura-rigel-18.20.0-full @2026-09-25T12:19:00Z`, 6/6 files `metadata_match/no_recorded_issue`), and checked-in fixtures (`40/1073`, `native-83.json php-8.3.6`). No code edited. Bounded time: single pass, no follow-up scans.
