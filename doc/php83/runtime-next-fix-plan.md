# Next bounded runtime repair: Criteria filter attachment marker

Status: **PLAN ONLY — no patch, runtime execution or acceptance in this review.**

## Priority grounded in existing evidence

`evidence/exp10-runtime/api-primary.json`, record `runtime=83, tree=exp10`,
contains 18 diagnostic location groups / 503 events. The largest individual
location is `alpha/apps/kaltura/lib/criteriaFilter.class.php:51`: **132 events**
(26.2% of the recorded events), classified `ApplicationDiagnostic`. Exp9 has the
same count; original74 has no corresponding group. Original83 terminates at the
already-known PDO control, so its absence of this group is not a clean baseline.
The next locations each have at most 24 events. This is a ranking of individual
observed sites, not a claim that this is the most severe defect throughout the
application or the largest combined diagnostic family.

Recommend this marker issue next, rather than revisiting already integrated
PDO signatures, ternary or autoload repairs. It lies in query-filter attachment,
so preserving filtering semantics is more important than merely reducing logs.
The sanitized report intentionally does **not** retain diagnostic message/type
inside ApplicationDiagnostic. Dynamic-property creation is the source-grounded
hypothesis, not a message recovered from the report: confirm the exact diagnostic
in a synthetic focused probe before selecting any repair.

## Source and dependency evidence

Immutable source root:
`/home/nilton/Projetos/nilton/NOVOS/kaltura-rigel-18.20.0-source/server-Rigel-18.20.0`.

- `alpha/apps/kaltura/lib/criteriaFilter.class.php:45-54`: enabled guard; `isset`
  of `$criteria_to_filter->creteria_filter_attached`; write `true` at line 51;
  then `copyCriteriaConstraints`. The misspelling is part of existing state and
  must not be silently renamed.
- Same file `:60-102`: copies filter criteria, avoids identical value/comparison
  duplicates, respects disabled tagged KalturaCriterion, copies inner clauses
  and ordering. Marker is written **before** copying, including a possible
  exception; do not opportunistically change that ordering.
- `vendor/propel/util/Criteria.php:38`: base class implements IteratorAggregate;
  the marker is undeclared. `clear():213-234` resets query internals but does not
  remove the existing dynamic marker. Do not introduce a reset as a side effect.
- One directly verified caller: `alpha/lib/model/om/BasePartnerPeer.php:574-576`,
  `PartnerPeer::getCriteriaFilter()->applyFilter($criteria)`.

Tier-2 graph lookup: project `kaltura-rigel-18.20.0-full`, ready, 231336 nodes /
800641 edges, generation `2026-09-25T12:19:00Z`. Exact applyFilter symbol located;
both-direction depth-1 trace provided the above caller and copy method. Other
returned callers were not individually audited and are not an exhaustive impact
claim. An apparent graph edge from builtin `isset` to a generator symbol was not
trusted; direct source is authoritative. Coverage for **all three paths above**
was `no_recorded_issue`, `metadata_match`, generation matching; this is best-effort
coverage, not proof of all dynamic consumers. Exact source sections were read.

Installed ai-memory retrieval skill was loaded. No worktree `.ai-memory.toml`
was present, so cross-project lookup used `global=true` without guessed scope.
The returned session `sessions/90599228-78eb-4d52-8b3d-fa9ea1260fdf.md` was then
read with returned scope `default/platform-install-packages-php83`; its bounded
18/503 claim agrees with the actual JSON. Memory is historical evidence only.

## Smallest candidate and explicit compatibility risks

First prototype: declare **one public, untyped, default-null**
`$creteria_filter_attached` property in the owning Criteria class. Preserve every
branch/body and spelling. This narrowly removes creation of this known property;
PHP documentation prefers declaring known properties over opting an entire
class hierarchy into dynamic properties. [Official PHP migration guidance](https://www.php.net/manual/en/migration82.deprecated.php).

This is **not yet proven behavior-preserving**: `isset(null)` preserves the
filter's initial branch, but `property_exists`, object iteration/JSON, reflection,
serialization layout and pristine-object bytes can change. A typed bool default
false is incorrect here: `isset(false)` is true and would skip the first filter.
Do not use that shortcut. A class-wide AllowDynamicProperties attribute would
retain dynamic layout but exempts other properties and subclasses too; it is an
explicit alternative only if exact serialized compatibility requires it and a
bounded inventory/review accepts its broader effect. Do not blanket-suppress
E_DEPRECATED or replace state with WeakMap (clone/serialization semantics differ).

Existing exp11 already selects cumulative `Criteria-native-returns.patch`:
original SHA `0626bb5b976ae7eedccaf5060675cd7c7ca56b22fc2c9d6c1a51ce485a303543`,
current after SHA `e8333167c6b501c92a8ee681a3b8c63372e8bf20e81c140a242c37c75b49a89a`.
It includes the older null-alias repair. Any later selected repair must replace
that **one target's cumulative patch**, preserving native returns/null guard;
do not append a duplicate target or apply original-based alternatives together.
No proposed new identity is invented here; exp11 remains immutable.

## Focused cases before a selection decision

1. Actual original74 / previous83 / proposed83 Criteria + criteriaFilter. Keep
   PHP8.3-only native-return candidate off whole-application74. Record native
   diagnostic severity/message/location in secret-free synthetic output.
2. Fresh enabled/disabled instances; apply once/twice; two distinct filter objects
   on one target; preexisting marker true/false/null; explicit unset/reapply.
3. Empty filters; duplicate/different constraints, nested AND/OR, disabled tagged
   clauses, ASC/DESC ordering. Compare actual constraints/SQL parameter values,
   not just process exit or normalized JSON.
4. Clone, `clear()` after attachment, serialization before/after attachment,
   deserialize original74 objects on83; exact bytes and visible properties.
   Require an explicit decision for any added-null-property representation delta.
5. Exception during copying preserves marker timing and exception propagation;
   no retry/reset behavioral rewrite hidden inside compatibility work.
6. Audit marker/member collisions in actual Criteria subclasses and generated
   peers before declaring the change safe across inheritance. Existing descendant
   coverage in `evidence/criteria-return/` is useful input, not this new audit.
7. Re-run existing `tools/php83/criteria-probe/` alias controls and
   `tools/php83/criteria-return/` 16-row iterator/clone/serialization corpus;
   see `criteria-return-contracts.md`. Those tests do not currently establish
   criteriaFilter marker behavior. Then compare actual API HTTP/trusted-HTTPS
   auth/denial corpus with unchanged response contracts and diagnostic accounting.

If this diagnosis is confirmed and workload unchanged, removing only this site
would predict 17 groups / 371 events from the exp10 reference—not a pass criterion
until measured. Keep every other warning visible. No performance gain is claimed
from event counts; benchmark only after functional/serialization decisions.

## Proposal mapping and next action

`openspec/changes/migrate-kaltura-php83/tasks.md`: 1.6 and 2.1 (minimal reviewed
repair), 2.2 (bundled Criteria dependency), detailed 5.7/T1-01 and 5.8/T1-02
(focused parity), 5.9/T1-03 (serialized/cache implications), 3.4 + 5.11/T2-01
(auth/filter regression), 3.6 + 5.22/T5-01 (diagnostic/performance accounting).
These tasks remain open; this plan closes none. Packaging/feasibility/release
and three-distro application gates are not satisfied by a warning repair.

Next concrete action: authorize a separate held Criteria-marker prototype and
secret-free focused corpus, with actual independent Claude/OpenCode/Cursor review
and exclusive lab runtime scheduling. Confirm the message and representation
tradeoff **before** selecting another experimental artifact. No VM operation,
source modification, patch/build or new external review was performed here.
