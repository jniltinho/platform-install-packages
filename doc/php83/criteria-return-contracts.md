# Criteria and CriterionIterator native return contracts (held)

## Cumulative, PHP 8.3-only patch

`patches/php83/held/Criteria-native-returns.patch` adds six return declarations:
`Criteria::getIterator(): Traversable` and iterator `rewind(): void`,
`valid(): bool`, `key(): mixed`, `current(): mixed`, `next(): void`.
Method bodies, cursor/key snapshots and live map lookup are unchanged.

The patch also contains the **already tested null-alias guard**. Its before hash
is the immutable original Criteria file; its previous-candidate hash matches the
old null-alias patch's after hash. A future ZIP manifest must **replace** the old
Criteria-null-alias entry with this cumulative entry, never apply both to the
same target. Keeping both historical patches in `held/` is intentional, not a
selection of both. No combined ZIP or active manifest changes in this cycle.

The candidate targets PHP 8.3 only. Native mixed is not a universal return type on
7.4 (it parses as a class name). The fixture uses the prior null-alias Criteria
class on 7.4 and 8.3, and the new class only on 8.3; this does **not** imply that the
whole exp7 application supports 7.4. Full integration still needs the unchanged
original 7.4 API/behavioral reference, not just this focused class comparison.

## Source and inheritance evidence

Graph generation `2026-09-25T12:19:00Z` is ready. INHERITS tracing from Criteria,
depth 10, returns 15 descendants, including two direct classes and Sphinx-derived
providers; tracing CriterionIterator returns none. Exact coverage for the base,
15 descendants and the loaded query interface is metadata-matching with no
recorded issue. Direct source inspection finds no selected-method redeclaration
in those descendants. This is bounded evidence, not proof about external,
dynamically generated or unindexed subclasses.

[Coverage](evidence/criteria-return/coverage.json),
[file hashes/declarations](evidence/criteria-return/source-inspection.json).
The actual implementation returns a new CriterionIterator, boolean comparison,
raw key/mapped Criterion-or-null, and no values from next/rewind. In particular,
`current(): mixed` must retain null when a snapshotted key was removed; declaring
it as always Criterion would be incorrect.

## Executed state and alias controls

`tools/php83/criteria-return/` uses real Criteria, CriterionIterator, myCriteria,
KalturaCriteria and its real interface. Only `Propel::getDB` and DBAdapter are
stubs. It does not execute SQL, application bootstrap, cache or Sphinx queries.
The full exp7 archive is byte-verified before/after each lab, but the Criteria
file under test is separately hash-pinned and mounted read-only at a canonical
path. Unprivileged PHP has private temp/network, socket denial and inaccessible
production paths. No source archive or application installation is modified.

Sixteen positive rows agree across previous 7.4, previous 8.3 and candidate 8.3:

- Empty aggregate and Traversable identity.
- Ordered iteration and exact Criterion values/comparison for the base class and
  both direct subclasses, including object identity and void results.
- Independent iterator cursors.
- Append after iterator construction: old key snapshot versus new iterator keys.
- Replacement after construction: live value lookup sees the replacement.
- Removal after construction: retained key snapshot has a null mapped value.
- Clone and serialization **mid-iteration**, draining from the retained position
  without rewind; serialized roundtrip preserves bytes.
- Rewind after exhaustion.
- Missing/null/empty/table/zero-string alias behavior, retaining the earlier fix.

Two explicit invalid-operation controls (empty/exhausted key/current access)
retain null results and two diagnostics each: E_NOTICE on 7.4 and E_WARNING on 8.3.
Same-runtime 8.3 diagnostics match **exactly**, including message/file/line. Those
warnings are observed controls, not suppressed or called clean valid operations.
Original/prior 8.3 emits six load-time return-contract deprecations; candidate 8.3
emits none. Six reflected native signatures are checked separately from values.

[Primary](evidence/criteria-return/codex.json),
[independent Claude](evidence/criteria-return/claude.json),
[comparison/outcomes](evidence/criteria-return/result.json).

## Failed harness control and correction

The first Codex and Claude collectors exit 1 before writing a complete report.
The application warning severity, text, line and values already matched, but
`basename($file)` was `previous.php` versus `candidate.php`, so strict equality
correctly rejected the differently named fixtures. The failed traces, initial
runner and diagnostic observations remain under
[`attempts/variant-paths/`](evidence/criteria-return/attempts/variant-paths/).

The correction mounts the chosen source file at **the same canonical path**
`/audit/Criteria.php`. It does not ignore filenames, remove diagnostics, weaken
equality or modify the application patch. Both complete collectors then pass;
Claude independently repeats all three variants and checks full report equality.
The runner's unsupported-7.4 candidate guard is checked separately by Cursor.

## Independent review and boundaries

Cursor executes 126 local tests and reviews the cumulative patch and source;
Claude executes the actual runtime collector (initial failure and corrected
repeat) and independently diagnoses the filename mismatch. Grok times out at
120 seconds with exit 124; after termination, OpenCode Zen Muse Spark 1.3 Free
executes 126 tests and reviews patch/fixture/collector. Cursor follows up with the
runtime guard and final evidence comparison. Exact roles/exits are retained.

Advisory corrections: Cursor's initial “mixed does not parse on 7.4” is incorrect;
its “fixture directory empty” observation predates the implementation. Historical
held entries for the same file are not themselves a build defect; selecting both
would be rejected and is not planned. Local 126 tests do not exercise this new
live fixture or supply new collector fault-injection coverage. Independent reruns
with the same harness prove repeatability, not independent implementation of its
oracle. Distinct CLI reviews and explicit absolute assertions supplement that.

The strict patch inventory passes all 28 entries (3 active, 25 held). No broad
acceptance task closes. Remaining work includes separately built ZIP integration,
actual SQL/API/HTTP/TLS regression, Sphinx/worker/cache paths, production-equivalent
extensions and full distro/media/performance/recovery acceptance. Existing SSH
aliases do not pin host keys; runtime binaries are not rehashed here. The read-only
source verification does not validate filesystem permissions. Release/package/CI
and `.20` cutover approvals remain separate gates.
