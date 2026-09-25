# Criteria marker representation experiment (not selected)

## Current state

Native declaration and attribute experiments have completed on PHP7.4/8.3,
including actual Claude repeats and the separate three-process logical import
classification. Declaration changes serialized representation; attribute preserves
within-runtime representation but three subclass payloads already differ across
engines. Seven imported payloads retain typed logical values. **Strict cross-runtime
byte parity remains FAIL; neither repair is selected.** No full cache/application
acceptance is claimed. Both labs are released. The current frozen result is
[`attribute/checkpoint.json`](evidence/criteria-marker/attribute/checkpoint.json).

The sections below are chronological records. Statements such as “pending”,
“not yet executed” and “preparation only” describe their labelled historical phase,
not current execution status; later result sections supersede those statuses.

## Historical phase 1 — declaration preparation

At this initial phase, no PHP runtime/VM execution had occurred.
The source-pinned experiment uses **full original** Criteria/Criterion/iterator
and actual criteriaFilter, not a reimplementation. Only DBAdapter and
Propel::getDB are stubs; no SQL or application bootstrap is exercised.

`tools/php83/criteria-marker/prepare.py` verifies original ZIP and two original
source hashes, copies original source into a new directory, and derives a second
Criteria file by adding exactly `public $creteria_filter_attached = null;`.
It does not create a selected patch or modify an artifact. This isolates marker
semantics on both74/83 without mixing the PHP8.3-only native-return patch.
Existing load-time Iterator deprecations remain visible and are not this repair.

Plan four processes, original/declaration on74 and83, using `run.sh` only after
explicit exclusive lab approval. Its hostname/case gate and read-only unprivileged
systemd sandbox prohibit network and production paths. Frozen source/probe hashes
are verified before execution. Parent must preserve process exit, raw synthetic
stdout/stderr and independently verify the frozen identities before/after.

15 cases cover fresh/disabled, apply once/twice, two filters, preset true/false/null,
unset/reapply, clone, clear, empty filter, nested OR/order, duplicate constraint,
exception-before-copy and attached serialization. Exact event messages, severity,
source line and phase are captured while the PHP error handler returns false,
preserving native stderr. No global suppression or AllowDynamicProperties is used.

Comparator input is ordered records `{mode,exit,stderr,body}` for original74,
declaration74, original83, declaration83, where body is the decoded exact stdout.
`compare.py records.json identities.json new-report.json` verifies source/mode,
case inventory and original83 dynamic-marker diagnostic/native stderr, comparing
filter behavior separately from four explicit representation snapshots. Those
snapshots retain property_exists, public vars, full synthetic serialized bytes
(base64), length/hash and byte-roundtrip. Every representation delta is reported;
functional agreement cannot become full representation parity or patch selection.
The original runtime is the differential oracle, not independent goldens for all
15 cases. Cross-runtime import of separately generated74 serialized payloads and
actual descendant collision tests are **not yet implemented**; current roundtrip
and cross-report byte comparisons must not be described as those tests.

Local synthetic guard tests and source-only preflight are in
`evidence/criteria-marker/`. No runtime diagnostic/count/serialization delta is
invented before actual execution. Native PHP lint also awaits an approved runtime
(no local PHP binary). Tagged KalturaCriterion behavior, full SQL generation,
cache and whole API auth remain follow-up scope, not exercised here.

If this experiment motivates a repair, its Criteria target must become a
cumulative replacement of existing Criteria-native-returns, preserving null-alias
and native signatures. Do not append a second manifest entry or mutate exp11.

Independent actual OpenCode attempt ended with provider exit0 but **no final
review or executed-test sidecars**. It hit a ripgrep size error and an automatically
rejected external-directory `/tmp` permission request. Neither was bypassed.
This attempt is INCOMPLETE, not independent validation. The preparation requires
a completed independent review before VM scheduling; see
`evidence/criteria-marker/preparation-result.json` and `opencode-errors.json`.

Subsequent fresh **actual Claude** repository-only review completed with exit0,
independently executing14 guard tests and shell syntax (both0), without accessing
the earlier denied tempfile. `claude-review.md` identifies preparation issues:
verify/load shared JSON for74 under `-n`; report unrelated diagnostic deltas;
bind identities manifest and enforce before/after identity checks; bind decoded
reports to exact raw stdout. **Resolve these before VM scheduling.** The earlier
OpenCode failure remains preserved; no runtime result has been inferred.

## Historical phase 2 — declaration preparation hardening

`run.sh` now requires `(original|declaration) EXPECTED_IDENTITIES_SHA256`; the
parent host supplies the frozen manifest hash, never a hash learned from remote
files. `verify.py` checks that hash, exact six-file inventory, symlinks and all
fixture bytes before execution and again in the shell EXIT trap; drift makes the
run fail. Parent must independently freeze/verify run.sh and verifier themselves
when staging; a verifier is not protection against a malicious replacement of
its own executable. No such staging has occurred yet.

PHP74 explicitly loads `-d extension=json`, matching existing audited
`autoload83/run.sh` and `base-object-ternary/run.sh`; PHP83 uses built-in JSON and
no duplicate extension load. Runtime module presence still needs actual checking.

Each collected record now also requires exact raw `stdout`; parsed JSON must
equal `body`. Native stderr hashes and all target events remain in the report.
Unrelated diagnostic lists are compared within74 and within83, not flattened
across runtime versions. Only Criteria filename and the exact one-added-source-
line mapping are adjusted for that comparison, with both original lists retained.
Unrelated message/severity/phase/order changes fail. This is not an assertion that
all stderr bytes are identical across versions; native logs must stay available.

22 local tests pass after hardening. The original14-test evidence and initial
Claude findings are preserved separately; follow-up review is a new phase.

The follow-up Claude review executed22 tests/syntax successfully. Afterwards,
`prepare.assert_source_lines` explicitly checked original Criteria declaration
line38 and filter assignment line51; three new local tests cover exact and
shifted lines (25 local tests total), and the actual pinned-source preflight
passed. This small post-review addition is recorded separately and must not be
reported as25 Claude-executed tests. Probe/run/verifier bytes are unchanged from
the22-test review. Runtime scheduling still needs coordinator approval and frozen
read-only stage ownership; remaining native-stderr/non-handler and transient
stage-tampering limits are retained in `claude-hardening-review.md`.

## Phase 3 result — actual declaration primary observation

Coordinator-authorized primary collection used fresh
`/home/vagrant/php-criteria-marker` on each lab, root-owned with write bits removed.
Parent-host expected hashes were checked before/after; manifest pin was
`f03b69e171349142c4f1efeef66a73a54cf7f48363b2cd666e2c86440d04ce3d`.
The original ZIP/source and proposed declaration were unchanged. Native runtime
attestation before/after matched: PHP7.4.33 (17 binary/module/library files) and
PHP8.3.6 (16 files), loaded modules/INI state recorded. No SQL/network/application
bootstrap was used. See `evidence/criteria-marker/primary.json` and each
`primary-{original,declaration}{74,83}.{stdout,stderr,exit}`.

All **four functional processes exited0**; all15 differential behavior cases
matched. Native original83 emitted18 exact dynamic-marker deprecations, including
`Creation of dynamic property Criteria::$creteria_filter_attached is deprecated`
at actual filter assignment line51. Declaration83 emitted none of that target
class. Six unrelated Iterator load deprecations persisted on both83 variants;
the raw events are retained and match under only the exact source-line mapping.
Both74 variants had no captured diagnostics. The null-source exception remained
`Error: Call to a member function keys() on null`, with marker already set true;
no attempted behavior cleanup changed this existing failure.

**Representation parity failed, deliberately reported rather than waived:**

| Snapshot | Original74/83 | Declaration74/83 | Difference |
|---|---:|---:|---|
| Fresh serialized Criteria | 669 bytes | 703 bytes | +34 bytes; added null public property |
| Fresh property_exists | false | true | externally observable state change |
| Attached serialized Criteria | 1080 bytes | 1080 bytes | different exact bytes/hash; property ordering |

The marker occurs at byte1049 in original attached serialization but byte25 in
the declaration; cloned/round-tripped attached snapshots likewise change hashes.
Every individual variant round-trips its own bytes, which **does not** establish
cross-version legacy cache/import compatibility. Original74 matches original83;
declaration74 matches declaration83 in these snapshots. Eight representation
deltas across the two declaration modes remain explicit in the comparator output.

Conclusion: diagnosis confirmed and the declaration preserves this15-case filter
behavior, **but it is not an exact-representation-preserving selected repair**.
Do not silently choose it or promote a cumulative patch. Next decision is explicit
representation compatibility/invalidation requirements versus a reviewed narrower
state-preserving alternative; class-wide AllowDynamicProperties remains unselected.
The new runtime collector was coordinator-authorized and executed by Codex; it was
not part of the earlier Claude22-test preparation review. Independent runtime
repeat, cross-runtime legacy unserialize and actual subclass collision audit are
still outstanding. Both labs were released immediately after collection.

## Phase 4 result — independent actual Claude declaration repeat

After the other lab owner released baseline74, Claude CLI executed the frozen
`repeat.py` against existing stages only. CLI and helper both exited0. All four
rows matched primary **exactly**, including raw stdout/stderr, decoded records,
source identities, and runtime pre/post attestations. `claude.json` status is
`EXACT_PRIMARY_REPEAT_BOUNDED_ONLY`; raw results and command evidence remain under
`evidence/criteria-marker/claude-*`. This is an independent executor repeating the
same harness, not an independently designed oracle. The unchanged representation
deltas still prevent selecting the declaration. Both labs were released again.

## Historical phase 5 — attribute alternative assessment

A separate unselected alternative is `#[\AllowDynamicProperties]` on **Criteria
only**, with no marker declaration and no magic/WeakMap rewrite. This is an
explicit compatibility opt-in, **not a marker-specific exemption**: PHP applies
it to child classes as well. The broad effect must be reported, never disguised
as removal of only one warning. [Official PHP migration documentation](https://www.php.net/manual/en/migration82.deprecated.php).

Inventory evidence: `attribute-source-inventory.json` records exact hashes,
property declarations, lexical assignment candidates and serialization/magic
locations for the base, 15 previously graph-discovered descendants, and query
interface. Index refreshed as ready231336/800641; all17 exact file paths were
coverage checked (`metadata_match`, `no_recorded_issue`, generation
2026-09-25T12:19:00Z) and source bytes matched prior audit hashes. This is a
bounded lexical inventory, not an exhaustive inference about variable property
names, external plugins or generated future classes. No marker declaration was
found in those inventoried property declarations; unexpected property writes and
visibility collisions still require focused subclass cases, not graph absence.

**Concrete additional dynamic write:** actual
`alpha/apps/kaltura/lib/myCriteria.class.php:78-81` `addHint()` assigns
`$this->hint[$table_name]`; neither that class nor its direct parent Criteria
declares `hint`. This is separate from `index_hints_map`, which is declared.
The attribute would also exempt this existing child behavior and arbitrary future
member typos from dynamic-property diagnostics. Do not silently fix the apparent
hint-name inconsistency inside this compatibility experiment.

**Concrete representation consumers:** direct read and clean matching coverage of
`alpha/apps/kaltura/lib/cache/kQueryCache.php:310` and
`plugins/search/providers/sphinx_search/lib/cache/kSphinxQueryCache.php:104`
confirm actual cache keys use `md5(serialize($criteria) . CACHE_VERSION)`.
`plugins/search/providers/sphinx_search/lib/SphinxCriteria.php:517` also logs
serialized state when tests are enabled. Thus the declaration's changed bytes
can alter real cache identity. No cache backend or invalidation behavior has been
executed here; these lines demonstrate dependency, not correctness of a cache
migration. Attribute compatibility might preserve these bytes, but **has not yet
been executed**.

Small executable next experiment (not selection): derive a separate attribute
variant from the exact original bytes; replay the existing15 cases, require exact
serialized/public-property bytes against original74/83, and add actual myCriteria
`addHint` plus KalturaCriteria inherited marker cases and one unrelated-class
negative control. Record the additional `hint` diagnostic exemption explicitly.
Test74 parsing/execution of the exact attribute-bearing source and report native
results; do not assume comment-style compatibility. Compare genuine legacy74
serialized payload imports on83, including marker-absent/present and subclass
payloads, before deciding on cache/layout parity. Preserve all unrelated warnings.
Only after those observations should the coordinator decide whether the explicit
Criteria hierarchy exemption is preferable to a declared-property/cache-identity
change. Neither alternative is selected by this assessment.

## Historical phase 6 — attribute follow-up v1 preparation

Separate `tools/php83/criteria-marker/attribute/` and
`evidence/criteria-marker/attribute/` preserve the earlier frozen declaration
experiment. Attribute-only source transformation adds one standalone
`#[\AllowDynamicProperties]` before the exact original Criteria declaration,
without adding fields. Five original source files are ZIP/hash-pinned, including
real myCriteria, KalturaCriteria and IKalturaDbQuery. No attribute patch or
artifact manifest has been selected.

Planned four processes original/attribute74 and original/attribute83:
19 state cases (prior15 plus actual hint, both subclass markers and an unrelated
class negative control). Seven original74 synthetic serialization snapshots are
extracted from recorded output, bound to the source74 report and frozen as the83
`legacy.json` fixture. Both83 modes import these genuine74 payloads, require exact
round-trip representation bytes and compare post-import filter behavior. Each
host gets a fresh root-owned read-only stage;83 has a distinct manifest because
its legacy fixture differs. Parent-pinned full source/runtime before/after checks
are enforced. No cache-key rewrite, WeakMap or magic accessor is introduced.

Comparator requires exact19 rows, including every serialization/property snapshot;
seven source-bound imported payloads; real `myCriteria::$hint` and inherited marker
warning controls on original83; and retained unrelated-class warning in both83
modes. Only the explicitly documented Criteria hierarchy warnings may disappear.
Other handler diagnostics compare per runtime with the exact inserted-line map;
raw native logs remain evidence. Attribute74 parsing/behavior is still unproven
until actual execution; a native exit0 plus exact rows will establish only this
bounded source compatibility, not generalized pre8 attribute support.

Attribute preparation review: actual Claude completed with exit0, executed14
local guard tests and shell syntax with exit0, and found no blocking defect.
Its three binding advisories were subsequently tightened: comparator verifies
canonical empty74/actual-payload83 legacy fixture hashes, stage verification
rejects extra entries, and runtime identity must equal the earlier reviewed marker
primary rather than merely matching itself before/after. Two new local tests
bring the Codex total to16; do not relabel these as16 Claude-executed tests.
`attribute/final-preparation.json` freezes this phase. VM execution remains pending
exclusive coordinator scheduling; fresh attribute stages have not been created.

## Phase 7 result — attribute strict cross-runtime layout failure retained

Actual primary and independent Claude four-process repeat both completed with
all process exits0; source/runtime/module pre/post identities match. Repeated raw
stdout/stderr/decoded records are exactly equal. The strict comparator reports
`Exact state/representation differs`: this remains a **FAIL**, not silently relaxed.
See `attribute/{primary,claude,primary-attribution}.json` and native output files.

Within74, original/attribute19 rows are exactly equal; within83 they are also
exactly equal, including serialized bytes. The attribute-bearing original source
actually executed on74, so its bounded comment-compatible behavior is observed.
Original83 has38 hierarchy dynamic-property events; attribute83 has zero. Both83
retain six Iterator warnings, one unrelated-class negative-control warning and
one null-strlen warning when importing the hint-only object. This is an explicit
hierarchy-wide exemption (including myCriteria hint), not marker-only cleanup.

Three **original74 versus original83** subclass snapshots differ in property
ordering before the attribute is introduced: myCriteria hint (792 bytes),
myCriteria marker (1175 bytes), KalturaCriteria marker (1239 bytes). Lengths are
unchanged, hashes differ. The74 output begins with child-declared properties;
83 begins with inherited Criteria properties. This attributes the observed
ordering delta to the source-identical cross-engine baseline, not the attribute.
Four base-Criteria payloads imported from74 reserialize byte-identically on83;
the three subclass payloads reserialize in the changed order in both83 variants.

A different hash is **not evidence of object data loss or cache corruption**.
Actual cache keys depend on serialized bytes, so existing cache identity reuse
needs an explicit cold/warm/invalidation decision under task5.9/T1-03. No cache
backend was executed and no cache-key or serialization rewrite is proposed just
to force byte parity. A separately named typed-state observation is being prepared
to classify private/protected/public values and types independent of only object
property order, without replacing this strict failed report or selecting a patch.

## Phase 8 result — separate typed logical-state classification (actual Claude)

A separately named immutable logical stage imported the same seven original74
payloads in three native processes: original74, original83, attribute83. Actual
Claude reviewed the new snapshot/collector, executed23 local tests and shell
syntax (exit0), then executed all three processes (exit0). No original attribute
stage, source, payload or prior strict report was replaced. Parent-pinned source,
fixture and runtime/module identities matched before/after. Both labs are released.
Evidence: `attribute/logical-primary.json`, `claude-logical-review.md`,
`claude-logical-command.{log,exit}`, `logical-*.{stdout,stderr,exit}`.

The snapshot uses native `get_mangled_object_vars` to include private, protected
and public properties, with explicit scalar types and binary string encoding.
It sorts **only object property names**, retains array order/key types and tracks
object identity/aliases. Seven imported payloads have identical typed logical
state in all three modes. This supplies bounded evidence **against interpreting
the observed ordering/hash delta as value/type loss**. It is not proof about all
application objects, array-reference identity/cycles, cache interoperability or
full migration state.

Raw byte parity remains original74 7/7, original83 4/7, attribute83 4/7. Strict
layout comparison still FAILS; the typed-classification result is separate and
does not change that verdict. Offline `cache-digest-observations.json` applies the
actual kQueryCache digest formula with source `CACHE_VERSION='2'` to captured
serialized bytes: three of seven cross-engine digests differ, zero same-runtime
original-versus-attribute digests differ. This does not execute a backend or imply
cache corruption. Cold/warm invalidation/namespace policy remains an explicit
5.9/T1-03 decision and test requirement, not a reason to rewrite serialization
just to make old/new hashes equal.

Current decision boundary: the declaration is not selected (introduces own layout
delta); the attribute is also **not selected automatically**. Attribute has exact
within-runtime state/layout parity in this19-case corpus and does not add to the
observed baseline cross-engine subclass-order delta, but intentionally exempts
future/all dynamic properties in the Criteria hierarchy. Any selection must state
that scope and retain the cross-engine/cache gate and full acceptance limits.
