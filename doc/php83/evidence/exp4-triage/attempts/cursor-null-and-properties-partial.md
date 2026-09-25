# Cursor triage — null-string + dynamic properties (exp4)

**Role:** Cursor Agent CLI independent source review (read-only).
**Writable output:** this file only. No source/patch/manifest/doc edits; no SSH/VM/production.
**Fixture:** exact exp4 API groups from `locations.json` — **40 groups / 1073 events** (sum of `count`; verified).
**Artifact:** `/home/nilton/Projetos/nilton/NOVOS/platform-install-packages-php83-artifacts/exp4/Rigel-18.20.0-php83-experimental.exp4.zip` root `server-Rigel-18.20.0/` (ZIP not modified).
**Artifact SHA (locations.json):** `a1ce4c46792667b07a733e622a3ee71dd01c87a94f7841edfc72d58746ab9d08`.
**Graph:** project `kaltura-rigel-18.20.0-full`, generation `2026-09-25T12:19:00Z`, Tier2 best-effort; cited paths `metadata_match` / `no_recorded_issue` (not completeness proof).

## Local harness (not application acceptance)

| Item | Value |
|------|--------|
| Command | `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tools/php83 -p 'test_*.py'` |
| Result | **122 tests**, exit **0** |
| Scope | Local PHP83 tools harness only — **not** green application / API / release gate |

## Certainty legend (raw messages absent)

| Label | Meaning |
|-------|---------|
| **STRUCT** | Confirmed from exact artifact source (control flow, declarations, call sites). |
| **INFER** | Source-supported inference of PHP 8.1+ null→string or PHP 8.2+ dynamic-property diagnostics at the fixture line. **Not** confirmed error text. |
| **UNRESOLVED** | Cannot accept; needs focused runtime/API evidence. |

Never treat INFER/UNRESOLVED as accepted fixed.

## Scope of this report

**Null-string candidates only:** myCustomData28, Partner1431, PermissionPeer329, FrontController76, KalturaLog122.
**Dynamic-property candidates only:** criteriaFilter51, FrontController23.
Other exp4 groups are out of scope.

SHA256 of reviewed artifact members match `locations.json` `source_sha256` for all seven path/line targets.

---

## A. Null-string candidates

### A1. `myCustomData` L28 — count 22 — ApplicationDiagnostic

**Source (artifact):** `alpha/apps/kaltura/lib/myCustomData.class.php`
**STRUCT:** Constructor: `empty($str)` sets `$this->data = array()` but **does not return**; execution always reaches `@unserialize($str)` at L28. Docblock claims `@param string $str`; callers can pass null/empty from DB/custom-data loaders.
**INFER:** PHP 8.1+ deprecation *Passing null to parameter #1 ($data) of type string* on `unserialize`, when `$str === null`. `@` does not make the fixture line non-diagnostic in this harness.
**Not confirmed:** exact raw message text.

**Minimal repair (null-only; no blanket cast):**
- After `empty($str)` branch, **return early** (or `else` the try block) so null/empty never call `unserialize`.
- Optionally: `if (!is_string($str)) { $this->data = array(); return; }` — reject non-strings without coercing arrays/objects into serialized payloads.
- Do **not** `(string)$str` broadly (would turn arrays into `"Array"`, hide corruption).
- Keep `@unserialize` removal as a separate hardening decision; not required for null path.

**Security:** `unserialize` on partner/entry custom data remains sensitive; null-fix must not widen accepted input types. No warning suppression.

**Tests required:**
- Unit: `myCustomData::fromString(null)`, `fromString('')`, `fromString('a:0:{}')`, invalid string → empty array / no deprecation.
- Focused: load object with NULL custom_data column; assert no null→string diagnostic at constructor.

**Status:** INFER + STRUCT control-flow bug — **unresolved until tests**.

---

### A2. `Partner` L1431 — count 20 — ApplicationDiagnostic

**Source:** `alpha/lib/model/Partner.php` `getAlwaysAllowedPermissionNames` (graph: L1426–1436).
**STRUCT:** `$names = $this->getFromCustomData('always_allowed_permission_names');` with no default. `BasePartner::getFromCustomData` returns `$defaultValue` (null) when missing. Then `if (!trim($names))` and later `trim($names, ',')`.
**INFER:** `trim(null)` null→string deprecation when key unset.
**Callers (graph inbound):** `kPermissionManager::getPermissionsFromDb` → permission resolution (`$alwaysAllowed = ... getAlwaysAllowedPermissionNames()`).

**Security (permission-sensitive):**
- Intended: unset/empty → inject `PermissionName::ALWAYS_ALLOWED_ACTIONS` (`ALWAYS_ALLOWED_ACTIONS`).
- Explicit dummy non-empty string → **must not** auto-inject (comment L1429–1430).
- Repair must treat **only null/empty-string** as “unspecified”. Do **not** `(string)` / cast arrays/bools — could collapse structured values or invent permission name lists.
- Wrong coercion can **widen or shrink** always-allowed actions → authz bug.

**Minimal repair:**
```php
if ($names === null || $names === '') {
    $names = PermissionName::ALWAYS_ALLOWED_ACTIONS;
} elseif (!is_string($names)) {
    // fail closed or log+treat as unspecified per product policy — do not stringify
    ...
} else {
    $names = trim($names);
    if ($names === '') {
        $names = PermissionName::ALWAYS_ALLOWED_ACTIONS;
    } else {
        // preserve explicit list (incl. dummy disable path)
        $names = trim($names, ',');
        // only prepend ALWAYS_ALLOWED when still “blank after trim” — match current !trim semantics for whitespace-only
    }
}
```
Preserve semantic of whitespace-only ⇒ treat as unspecified (current `!trim($names)`). Avoid changing comma-trim rules for explicit lists.

**Tests required:**
- Unit: custom data absent → result contains `ALWAYS_ALLOWED_ACTIONS`.
- Unit: explicit `'DUMMY'` / dummy list → **no** forced prepend of `ALWAYS_ALLOWED_ACTIONS` beyond current spec; still no `trim(null)`.
- Unit: whitespace-only string → same as unspecified.
- Unit: non-string if writable via `putInCustomData` → no silent cast; assert chosen fail-closed policy.
- API/integration: partner session permission bootstrap via `kPermissionManager` with null vs explicit always-allowed custom data.

**Status:** INFER high — **unresolved; security-gated**.

---

### A3. `PermissionPeer` L329 — count 32 — ApplicationDiagnostic

**Source:** `alpha/lib/model/PermissionPeer.php` `filterDependencies` L329.
**STRUCT:** `$dependsOn = trim($permission->getDependsOnPermissionNames());`
`BasePermission::getDependsOnPermissionNames()` returns `$this->depends_on_permission_names` (protected; **no default** → null from DB NULL).
**INFER:** `trim(null)` null→string. Subsequent `explode(',', $dependsOn)` and empty-token skip (L336–338) already treat blank dependency text as inert.
**Callers:** `getAllValidForPartner`, `filterDependenciesByNames` → role/permission validity.

**Security (permission-sensitive):**
- Null/empty depends-on ⇒ no dependency constraint (permission kept unless other deps fail).
- Do not cast non-strings to string (could invent dependency tokens or strip constraints).
- Incorrect handling can **drop valid permissions** or **keep undeclared ones** when dependency graph is wrong.

**Minimal repair:**
```php
$raw = $permission->getDependsOnPermissionNames();
if ($raw === null || $raw === '') {
    continue; // or $dependsOn = [] — equivalent to no deps
}
if (!is_string($raw)) {
    // fail closed: treat as invalid dependency text / skip permission — product choice; no (string) cast
    ...
}
$dependsOn = explode(',', trim($raw));
```

**Tests required:**
- Unit: permission with `depends_on_permission_names = NULL` → retained when no deps; no trim deprecation.
- Unit: `'PERM_A,PERM_B'` missing peer → unset as today.
- Unit: empty string / commas-only → continue path unchanged.
- API: `getAllValidForPartner` / role `getPermissionNames` with NULL depends_on rows.

**Status:** INFER high — **unresolved; security-gated**.

---

### A4. `KalturaFrontController` L76 — count 14 — ApplicationDiagnostic

**Source:** `api_v3/lib/KalturaFrontController.php` `onRequestEnd` analytics payload.
**STRUCT:**
`'kuserId' => '"' . str_replace('"', '\\"', (kCurrentContext::$uid ? kCurrentContext::$uid : kCurrentContext::$ks_uid)) . '"'`
`kCurrentContext::$uid` / `$ks_uid` are public statics often reset to **null**. If both falsy, ternary yields **null** → `str_replace` subject null.
**INFER:** null→string on `str_replace` (and/or concatenation).
**Related:** same request path feeds `KalturaLog::analytics` (A5).

**Minimal repair (null-only):**
```php
$uid = kCurrentContext::$uid ?: kCurrentContext::$ks_uid;
$uid = is_string($uid) ? $uid : '';
'kuserId' => '"' . str_replace('"', '\\"', $uid) . '"',
```
Do not cast arbitrary types; non-string → empty quoted field (logging only).

**Security:** analytics field only (KS logged separately as `ks`). Avoid expanding logged identity beyond current intent.

**Tests required:**
- Unit/API: `onRequestEnd` with both `$uid` and `$ks_uid` null → quoted empty kuserId; no null→string diagnostic.
- With string uid containing `"` → escaping preserved.

**Status:** INFER — **unresolved until tests**.

---

### A5. `KalturaLog` L122 — count 54 — ApplicationDiagnostic

**Source:** `infra/log/KalturaLog.php` `analytics(array $data)` L117–126 (graph).
**STRUCT:** `strtr($value, ',', ' ')` for every value. Callers (graph): `KalturaFrontController::onRequestStart` / `onRequestEnd` pass many nullable fields (`partnerId`, `ks`, `errorCode`, etc.) and also pre-quoted strings that may embed null via concatenation upstream.
**INFER:** `strtr(null, ...)` null→string when a value is null (dominant fixture volume).

**Minimal repair:**
```php
if ($value === null) {
    $message .= ',';
    continue;
}
if (!is_scalar($value)) {
    // skip or log placeholder — do not (string) objects/arrays
    ...
}
$message .= strtr((string)$value, ',', ' ') . ',';  // cast only after scalar check; or stringify int/float/bool explicitly
```
Prefer: null → empty field; int/float/bool → explicit `(string)` only for scalars; reject array/object without coercion.

**Tests required:**
- Unit: `KalturaLog::analytics(['a', null, 1, 'x,y'])` → stable CSV-ish line; no deprecation.
- API smoke: request_start/request_end analytics under anonymous / no-ks context.

**Status:** INFER — **unresolved until tests**.

---

## B. Dynamic-property candidates

### B1. `criteriaFilter` L51 — count 132 — ApplicationDiagnostic

**Source:** `alpha/apps/kaltura/lib/criteriaFilter.class.php` `applyFilter` L45–54 (graph).
**STRUCT:** Writes `$criteria_to_filter->creteria_filter_attached = true` (typo name preserved by design) after `isset(...)`.
**Owning type:** parameter is `Criteria` (`vendor/propel/util/Criteria.php`). Artifact Criteria declares only **private** fields; **no** `creteria_filter_attached`; no `AllowDynamicProperties`. Subclasses (e.g. `KalturaCriteria`) also lack this flag. Plain `new Criteria()` used in permission paths.
**INFER:** PHP 8.2+ *Creation of dynamic property Criteria::$creteria_filter_attached*. Highest volume in assigned set (132).

**Property declaration constraints:**
- Declare on **`Criteria`** (actual runtime owner for external write/isset), not on `criteriaFilter`.
- Visibility **`public`** (external isset/assign from `criteriaFilter`).
- Default must keep `isset` false until set: use `public $creteria_filter_attached;` (implicit null). **Do not** default `false` — `isset(false)` is true and would **skip** `copyCriteriaConstraints` (behavioral break).
- Preserve exact name `creteria_filter_attached` (typo) for compatibility.
- Serialization: Criteria has no `__sleep`; public props participate in `serialize` like prior dynamic props when set. Avoid renaming. Re-test any query-cache / criteria clone paths that serialize Criteria.

**Rejected approaches:** blanket `#[AllowDynamicProperties]` on Criteria; warning suppression; declaring only on `KalturaCriteria` (misses plain `Criteria`).

**Tests required:**
- Unit: two `applyFilter` calls on same Criteria → constraints copied once; flag isset after first.
- Unit: fresh Criteria → first apply copies; no dynamic-property diagnostic.
- Regression: peer filters using `setUseCriteriaFilter` / partner criteria attachment still apply constraints.
- If Criteria serialization exists in lab: round-trip with flag true/null.

**Status:** STRUCT dynamic write + INFER diagnostic — **unresolved until declaration + tests**.

---

### B2. `KalturaFrontController` L23 — count 24 — Deprecated

**Source:** `api_v3/lib/KalturaFrontController.php`.
**STRUCT (certainty high):**
- Declared: `private $disptacher = null;` (L15, typo).
- Assigned/used: `$this->dispatcher = KalturaDispatcher::getInstance();` (L23) and `$this->dispatcher->dispatch(...)` (L116, L323).
- Declared `$disptacher` is never read; `$dispatcher` is undeclared → dynamic property.

**INFER:** matches severity **Deprecated** at L23 (dynamic property creation).

**Minimal repair:**
- Rename declaration to `private $dispatcher = null;` (same visibility + default).
- Keep assignments/usages as `$this->dispatcher`.
- Do not leave both names; do not publicize; do not `AllowDynamicProperties` on the controller.

**Serialization:** singleton front controller; private property rename is low risk but confirm nothing serializes `KalturaFrontController` expecting `disptacher`.

**Tests required:**
- Unit/smoke: `getInstance()->run()` / multi-request dispatch path still calls dispatcher.
- Assert no dynamic-property deprecation on construct.
- Multi-request branch L323 dispatch.

**Status:** STRUCT typo mismatch — **unresolved until rename + tests**.

---

## C. Needed tests (focused checklist)

| ID | Area | Focus |
|----|------|--------|
| T1 | myCustomData | null/''/valid/invalid string; no unserialize(null) |
| T2 | Partner always-allowed | null vs '' vs whitespace vs explicit dummy; permission manager integration |
| T3 | PermissionPeer deps | NULL column; missing dep drops; empty tokens |
| T4 | FrontController kuserId | both uids null; quote escaping |
| T5 | KalturaLog::analytics | null/scalar/comma values |
| T6 | criteriaFilter flag | once-only attach; Criteria declaration; no dynamic prop |
| T7 | FrontController dispatcher | construct + single/multi dispatch |

Prefer PHPUnit under existing php83 harness or disposable lab API against exp4 artifact — **not** production.

## D. Minimal repair proposals (summary)

1. **myCustomData:** early-return on non-string/empty before `unserialize`.
2. **Partner:** null/''/whitespace-only guard before `trim`; no broad cast; preserve ALWAYS_ALLOWED / dummy semantics.
3. **PermissionPeer:** null/'' skip before `trim`; no broad cast.
4. **FrontController L76:** normalize uid to string or `''` before `str_replace`.
5. **KalturaLog::analytics:** null-safe / scalar-safe before `strtr`.
6. **Criteria:** `public $creteria_filter_attached;` (null default) on **Criteria**.
7. **FrontController L15/L23:** rename `$disptacher` → `$dispatcher`.

**Forbidden here:** blanket casts, `@`/error-control as fix, warning suppression, unreviewed `ReturnTypeWillChange` sweeps, `AllowDynamicProperties` as substitute for the two properties.

## E. Blockers / non-acceptance

| Blocker | Impact |
|---------|--------|
| Raw diagnostic messages intentionally absent | Cannot mark INFER items as confirmed error text |
| No focused/API tests executed in this review | All seven remain **unresolved** (not accepted) |
| Partner + PermissionPeer touch authz | Fixes need security review + T2/T3 before accept |
| Criteria is vendor Propel | Declaration is correct owner but needs package/patch policy ownership outside this review |
| Local 122 unittest OK | Does **not** prove application acceptance or exp4 API silence |

## F. Graph coverage note (best-effort)

`check_index_coverage` for the six assigned paths: all `no_recorded_issue` + `metadata_match` at generation `2026-09-25T12:19:00Z`. Signal is best-effort only; claims grounded in ZIP `zipfile.read` + graph snippets for `applyFilter`, `getAlwaysAllowedPermissionNames`, `analytics`.

## G. Verdict

Source supports **null→string** risk at five fixture lines and **dynamic properties** at two (Criteria flag + FrontController dispatcher typo). None are accepted as fixed. Highest volume: criteriaFilter51 (132) and KalturaLog122 (54). Highest security sensitivity: Partner1431 and PermissionPeer329. Next gate: implement minimal null/property repairs under separate approved change ownership, then T1–T7 with independent review — not this read-only pass.
