# Exp12 remaining diagnostics: grouped repair plan

Status: source-supported classification, **not new runtime acceptance**. The
retained exp12 API report has exactly 17 groups / 371 events. Its sanitized
records intentionally omit message text; KS-bearing raw stderr is not retained.
Consequently all causal labels below are explicit source-supported inferences,
not purported reconstructions of native messages. First runtime step is safe,
secret-free full-class declaration diagnostics to confirm the attribution.

[Machine-readable classification](evidence/exp12-diagnostic-families/classification.json)
contains every original group, count, exact exp12 source SHA, numbered source
excerpt, original SHA, selected patch metadata and same-target patch SHA inventory.
The graph is ready (231336 nodes / 800641 edges), generation
2026-09-25T12:19:00Z; coverage for all eleven relied source files reports
metadata_match/no_recorded_issue. This is best-effort original-source coverage,
not a claim of exp12 graph indexing. Actual exp12 ZIP bytes were directly read
and joined to the selected manifest; unchanged targets equal original ZIP bytes.

| Family | Groups/events | Exact source evidence | Repair state |
|---|---:|---|---|
| Tentative internal return contracts | 12 / 274 | KalturaPDO exec/query; PropelPDO beginTransaction/commit/rollBack/getAttribute/prepare; PropelConfiguration four ArrayAccess methods; KalturaAPIException::__wakeup | New signatures needed. Existing selected PDO query/setAttribute patches solve different contracts. |
| Dispatcher dynamic property | 1 / 24 | FrontController line23 writes dispatcher, declaration spells disptacher | New repair; selected null-user patch is unrelated. |
| XML loader lifecycle | 1 / 24 | kConf line7 calls libxml_disable_entity_loader(true) | Existing held XML worker repair; no duplicate patch here. |
| AWS legacy serialization | 2 / 48 | CredentialsInterface extends Serializable; decorator implements it, RefreshableRole inherits through AbstractRefreshableCredentials | New compatibility design, not a blind magic-method addition. |
| Required rank argument follows optional entryType | 1 / 1 | anonymousRankEntry($entryId, $entryType = null, $rank) | New repair after caller/argument-shape inventory. |

PHP documents [tentative internal return compatibility](https://www.php.net/manual/en/migration81.incompatible.php),
[legacy Serializable deprecation](https://www.php.net/manual/en/migration81.deprecated.php)
and [dynamic-property creation deprecation](https://www.php.net/manual/en/migration82.deprecated.php).
These support the hypotheses; they do not substitute for exact native attribution.

## Initial family hypothesis: four diagnostic-source classes, twelve groups

Prepare a separately held cumulative patch set against exact selected exp12
bytes, never the original PDO source when that would drop selected fixes.
Prefer explicit native return declarations, not blanket ReturnTypeWillChange or
warning suppression. The inheritance follow-up below supersedes the initial
assumption that all twelve methods can simply acquire native declarations. No return casts, changed bodies, default changes or
ArrayAccess typo cleanup in this batch. Candidate signatures are provisional
until internal reflection and every return branch/subclass override are checked:
PDO exec int|false, query/prepare PDOStatement|false, transaction methods bool,
getAttribute mixed; ArrayAccess bool/void/mixed/void; exception wakeup void.
These PHP8 unions/mixed make this an experimental PHP8-only artifact; the
original74 class cohort remains a historical control, not candidate74 support.

Before runtime, independently review patch byte deltas, complete function bodies,
parent/child signatures, exact dependency hashes and strict collector guards.
Use real full classes loaded from an isolated full source tree, no fake replacement
class declarations. Native83 declaration-only controls first confirm exact native
messages (no application secrets). Then:

1. PDO family: approved disposable SQL fixture only after lab ownership grant;
   real PropelPDO/KalturaPDO, nested transaction counters, commit/rollback,
   prepare cache enabled/disabled, cache identity, invalid prepare/query/exec,
   zero/positive row counts, custom/parent attributes and errors. Preserve typed
   return values and exceptions; exercising successful queries alone is inadequate.
2. Configuration: offset null/false/zero/string-zero/empty-string/integer keys,
   existing/missing entries, set/get/unset/existence. Current offsetSet writes
   singular parameter while offsetGet reads plural parameters: preserve and expose
   that legacy discrepancy, do not silently fix it while changing declarations.
3. API exception: full class + real APIErrors, codeStr/message/args, repeated
   wakeup, falsy/truthy codeStr, legacy serialized payload import, native round-trip
   payload bytes and typed values, malformed payload errors. No cache-format waiver.
4. Re-run the same full API HTTP/HTTPS/auth corpus and CLI regression, all declared
   selected-artifact additions, compiler controls and source/runtime before/after
   identities. Expected removal is only the confirmed twelve groups / 274 events;
   the remaining five groups / 97 events and all other outputs must stay exact,
   allowing only previously documented time/UUID fields. This is a prediction,
   **not an observed new result**. Unexpected warnings or body changes fail closed.
5. Actual independent Claude/OpenCode/Cursor repeat on frozen inputs, with fresh
   reports and process exit evidence. Source-stage success alone cannot promote
   a ZIP or close aggregate application/release gates.

VMs are currently owned by other workers. No VM or source patch was performed
for this classification. Parent separately authorized subsequent local batch prep.

## Follow-on batches and constraints

- Dispatcher: public dynamic-property visibility and object serialization must be
  preserved. Merely declaring a private property changes access semantics; do not
  bundle it into the return-contract patch.
- AWS: use synthetic credentials and disabled networking. Test legacy C-format,
  fields, expiration paths and decorator/role state. __serialize changes wire
  format; backend refresh/STS remains a separate integration gate.
- Rank: positional/named callers, omitted entryType and reflected required-count
  must be inventoried; optional-default removal is not approved by this document.
- XML: retain the XML worker's security-focused evidence and lifecycle contract.

## Reproduction

```sh
python3 doc/php83/evidence/exp12-diagnostic-families/build.py --check
```

This read-only command validates pinned original/exp12 ZIPs, selected source
identities and deterministic report equality. It is an inventory check, not a
PHP test. No aggregate task is marked complete and no release is authorized.

## Independent review and inheritance follow-up

Actual Claude CLI exited 0, executed the inventory check successfully and reviewed
pinned ZIP bytes. Verdict: CONDITIONAL_PASS_WITH_DEFECTS, **not runtime approval**.
[Public report](evidence/exp12-diagnostic-families/claude-review-public.json).
The reviewed builder/plan are preserved alongside the report. Two local inventory
guards were then tightened: reject unknown paths instead of defaulting to AWS,
and verify selected before_sha256 against original bytes as well as after_sha256.
The regenerated classification is byte-identical; only validation logic changed.

The proposed patch count is not twelve. Direct full-source inspection confirms
KalturaPDO::prepare and beginTransaction overrides, DebugPDO::prepare, and both
MssqlPropelPDO/MssqlDebugPDO transaction overrides. Graph INHERITS positively
identifies these four descendants; its absence of further edges does not prove
absence of dynamically declared classes. MSSQL transactions return self::exec
(int|false) on outer operations and true on nested/no-op paths. Adding :bool would
coerce integer returns or conflict with an int|bool child signature. No coercion is
approved. The parent explicitly permits evaluating a **narrow documented**
ReturnTypeWillChange exception for the three conflicting PropelPDO transaction
methods, preserving untyped overrides rather than pretending native signatures
are possible. Any extra descendant attribute requires observed justification;
this is not a global suppression policy. Native reflection and an unrelated-warning
control must distinguish that exception from full return-contract repair.

A native prepare return requires compatible KalturaPDO and DebugPDO overrides.
Exp12 DebugPDO::query remains its original incompatible declaration. Its separately
held v3 repair has historical evidence in [DebugPDO experiment](debug-pdo-experiment.md)
and metadata at patches/php83/held/DebugPDO-query-v3.json; it is not selected by
this plan. Load failures must remain explicit until that prerequisite is separately
reviewed/promoted. No claim that unreachable classes can be ignored is made.

Focused configuration tests must retain new-to-this-corpus *baseline* diagnostics
from its singular dynamic parameter property and missing offset reads. Those are
not unexpected candidate warnings. The API corpus still requires exact declared
removal only. __wakeup's ApplicationDiagnostic severity differs from the other
return groups: prioritize native declaration confirmation, not an assumed message.
AWS follow-up must inventory concrete credential implementations beyond the two
observed groups before changing serialization. It cannot assume the API covers all
AWS serialization users. These findings are preparation prerequisites, not waivers.
