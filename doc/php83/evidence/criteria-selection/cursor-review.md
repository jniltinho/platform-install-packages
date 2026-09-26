# Criteria marker attribute — independent selection review (Cursor)

- Reviewer/executor: Cursor Agent (Composer), read-only, repository-local only.
- Scope: decide whether `#[\AllowDynamicProperties]` on `Criteria` is justified as an **explicit compatibility repair** for a **NEXT EXPERIMENTAL ZIP**, not application/release acceptance.
- Non-goals: no VM/SSH/network; no edits to application, patches, selected manifests, tasks, or existing evidence under `criteria-marker/`.
- Date context: 2026-09-25.

## Verdict

**ALLOW_BOUNDED_EXPERIMENT** for a next lab-only experimental ZIP that cumulatively replaces the existing exp11 `Criteria` target with attribute + preserved native-return/null-alias contracts.

Evidence does **not** block that bounded experimental selection. The same evidence **does** continue to block cache-backend reuse, invalidation acceptance, custom serialization, and full application/release gates. Strict cross-runtime byte parity remains **FAIL** and must stay FAIL (not waived). Declaration remains rejected on its own layout delta; do not substitute it.

This review is **not** approval of production integration, packaging, CI publish, or cutover.

## Local verification executed

| Check | Command / method | Result |
|---|---|---|
| Unit tests | `python3 -m unittest discover -s tools/php83/criteria-marker/attribute -p 'test_*.py' -v` | **23/23 OK**, exit **0** (12 compare + 7 logical + 4 prepare; ~0.004s) |
| Checkpoint hashes | SHA-256 of all 16 tool paths + 6 evidence paths listed in `attribute/checkpoint.json` | **22/22 OK**, **0** mismatch/missing |
| Strict comparator | Re-ran `compare.validate(primary.records, identities74, identities83, legacy-original74)` | Raises `ValueError: Exact state/representation differs` (FAIL retained) |
| Logical comparator | Re-ran `logical-compare.validate(logical-primary.records, legacy payloads)` | Status `BOUNDED_TYPED_IMPORT_VALUES_MATCH_RAW_LAYOUT_GATE_STILL_FAILED`; raw bytes 7/7, 4/7, 4/7 |
| Same-runtime row equality | `original74.rows == attribute74.rows`; `original83.rows == attribute83.rows` | Both **True** (19 cases) |
| Primary↔Claude repeat | stdout/stderr byte-equal for all four modes | **True**; exits `[0,0,0,0]` |

Checkpoint frozen status: `CHECKPOINT_NO_PATCH_SELECTED_STRICT_LAYOUT_FAIL_PRESERVED`; `attribute_selected=false`; `cache_application_acceptance=false`.

### Checkpoint hash sample (full set verified)

Tools (all OK): `prepare.py` `96b143e4…`, `compare.py` `a2d8c7b3…`, `logical-compare.py` `09b18c2d…`, plus collect/probe/run/verify/tests/source-pins as listed in checkpoint.

Evidence (all OK): `primary.json` `68bc8916…`, `claude.json` `ba406e90…`, `logical-primary.json` `3be5ce3c…`, `primary-attribution.json` `d4ac419b…`, `cache-digest-observations.json` `cf93727c…`, `doc/php83/criteria-marker.md` `4416e132…`.

## Comparator inspection (actual code)

`prepare.py`: inserts exactly one `#[\AllowDynamicProperties]` immediately before the unique `class Criteria implements IteratorAggregate {` anchor at original line 38; refuses duplicates/existing attribute/line drift; pins five original ZIP sources; marks `patch_selected:False`.

`compare.py`: requires four ordered modes, exact 19-case inventory, serialization integrity, seven legacy import paths on 83, original83 hierarchy diagnostics (marker + `myCriteria::$hint` + inherited `KalturaCriteria` marker), retained unrelated-class control on both 83 modes, and per-runtime unrelated-diagnostic parity after the one-line attribute map. Success label remains `…ATTRIBUTE_NOT_SELECTED` / `patch_selected:False`. Cross-mode exact row equality is mandatory → baseline original74≠original83 fails the gate.

`logical-compare.py`: three modes × seven payloads; typed logical JSON must match; raw reserialize equality recorded separately and **not** used to waive the layout FAIL.

## Assessment against selection criteria

### 1. Same-runtime 19-case parity

Within PHP 7.4 and within PHP 8.3, original and attribute rows (state + representation snapshots) are exactly equal. Process exits all 0. Attribute source executed on 7.4 (comment-compatible attribute parsing observed). This is bounded harness parity, not application acceptance.

### 2. Broad hierarchy / typo warning exemption (explicit, not marker-only)

original83: **38** hierarchy dynamic-property events (`Criteria::$creteria_filter_attached` 25, `myCriteria::$creteria_filter_attached` 5, `myCriteria::$hint` 4, `KalturaCriteria::$creteria_filter_attached` 4) plus 1 unrelated control and 6 Iterator return-type deprecations (+ strlen-null on hint import).

attribute83: **0** hierarchy dynamic-property events; unrelated control **retained** (1); Iterator warnings **retained** (6); strlen-null retained (1). Total events 46 → 8.

This is an intentional class-hierarchy opt-in: it also exempts the real `myCriteria::addHint()` `$this->hint` write and would silence future hierarchy member typos. That breadth must be stated in any experimental ZIP notes; it is not “marker-only cleanup.”

### 3. Baseline cross-engine 3 subclass property-order differences

original74 vs original83 (source-identical, **before** attribute attribution) differ only on three subclass snapshots; lengths unchanged, hashes differ:

| Snapshot | bytes | hash equal? |
|---|---:|---|
| `/mycriteria_hint/representation` | 792 | no |
| `/mycriteria_marker/representation` | 1175 | no |
| `/kalturacriteria_marker/representation` | 1239 | no |
| four base-Criteria payloads | 669 / 1080 | yes |

Prefixes show 74 emits child-declared properties first; 83 emits inherited `Criteria` properties first. Attribute does **not** add layout diffs within either runtime (0 original-vs-attribute layout hash diffs on 74 and on 83). Strict FAIL is therefore baseline cross-engine ordering, not an attribute regression.

### 4. Seven typed logical payloads

Separate three-process logical stage: typed mangled property values/types/aliases identical across original74, original83, attribute83 for all seven imports. Supports “ordering/hash delta ≠ value/type loss” for this corpus only. Limits recorded: object property order ignored by design; array-reference identity/cycles not tested; not all application objects.

### 5. Unchanged real cache digest formula

Offline `cache-digest-observations.json` applies `md5(serialize($criteria) . '2')` matching `kQueryCache.php:310` / Sphinx sibling consumers. `same_runtime_attribute_delta=false`; `cross_runtime_digest_delta_count=3` (the three subclass snapshots); `cache_acceptance=false`; no backend executed; no serialization rewrite proposed.

### 6. Declaration vs attribute

Declaration experiment already showed its own layout change (+34 fresh bytes, `property_exists` flip, attached property reordering). It must **not** be substituted as the “easier” fix. Attribute is the representation-preserving within-runtime alternative under review.

### 7. What the FAIL blocks vs does not block

| Gate | Blocked by current evidence? |
|---|---|
| Strict cross-runtime byte/layout parity as a release claim | Yes — FAIL retained |
| Cache backend warm reuse / invalidation acceptance (5.9/T1-03) | Yes — offline digest deltas + no backend |
| Custom serialization / WeakMap / secret cache acceptance | Yes — forbidden; not proposed |
| Full application / auth / packaging / release / cutover | Yes — untested here |
| Bound **next experimental ZIP** selection that states hierarchy exemption + keeps FAIL/cache gates open | **No** — within-runtime parity + typed imports + no added layout delta support that narrow step |

## Risks (must travel with any experimental selection)

1. Hierarchy-wide dynamic-property silence (including `hint` and future typos), not marker-scoped.
2. Cross-engine subclass serialize order already differs; warm cache identity across 7.4→8.3 subclass payloads already needs an explicit cold/warm policy even without this attribute.
3. Must be a **cumulative replacement** of exp11 `Criteria-native-returns.patch` (preserve native returns + null-alias). Do not append a second Criteria manifest entry or mutate frozen exp11 in place without a new experimental identity.
4. Harness is synthetic (stub DBAdapter/Propel::getDB); no SQL, Sphinx, or live filter peer paths.
5. No performance or security benefit is claimed from fewer deprecation events.

## Concrete remaining integration cases (not executed here)

1. Build next experimental ZIP as cumulative Criteria target (attribute + existing native-return/null contracts); refuse dual-entry manifests.
2. Re-run `tools/php83/criteria-probe/` alias controls and `tools/php83/criteria-return/` 16-row iterator/clone/serialization corpus against the cumulative target.
3. Focused filter SQL/constraint parity beyond the 19 synthetic cases (tagged `KalturaCriterion`, disabled clauses, real Peer callers such as `BasePartnerPeer`).
4. API HTTP / trusted-HTTPS auth/denial corpus with unchanged response contracts and diagnostic accounting (exp10 site was 132 events at `criteriaFilter.class.php:51` — prediction only until measured).
5. Explicit 5.9/T1-03 cache cold-start / namespace / invalidation decision and backend test (digest formula already known; backend not run).
6. Broader subclass/plugin collision audit beyond the bounded lexical inventory (external plugins, generated peers).
7. Packaging/feasibility/three-distro gates remain separate; this review closes none of `tasks.md` 3.4/5.11/5.22/release items.

## Sources consulted (read-only)

- `AGENTS.md`, `doc/php83/criteria-marker.md`, `doc/php83/runtime-next-repair-plan.md`
- `tools/php83/criteria-marker/attribute/{prepare,compare,logical-compare}.py`
- `doc/php83/evidence/criteria-marker/attribute/{checkpoint,primary,claude,logical-primary,primary-attribution,cache-digest-observations}.json`
- Graph coverage (best-effort, `kaltura-rigel-18.20.0-full`, generation `2026-09-25T12:19:00Z`): `Criteria.php`, `criteriaFilter.class.php`, `myCriteria.class.php`, `kQueryCache.php` → `no_recorded_issue` / `metadata_match` (not completeness proof)

## Bottom line

**ALLOW_BOUNDED_EXPERIMENT** for a coordinator-owned next experimental ZIP with explicit hierarchy-exemption language, cumulative Criteria patch rules, preserved strict cross-runtime FAIL, and open cache/application gates. **HOLD** remains correct for cache acceptance, production integration, and any claim of full representation or release readiness. Declaration is still not selected.
