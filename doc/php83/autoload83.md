# Three legacy global-autoload compiler repairs

Status: **held experiment; bounded runtime/entrypoint validation and independent
review recorded, with retained failures and explicit limits**. No integrated ZIP, installed application, package or release is
changed. The exp10 archive remains immutable.

PHP 8 removed the global `__autoload` function; an unreachable conditional
declaration still prevents these files from compiling. The supported replacement
is SPL registration, whose callback queue and legacy-loader preservation rules
matter to coexistence. See the official [PHP 8 migration guide](https://www.php.net/manual/en/migration80.incompatible.php)
and [SPL registration documentation](https://www.php.net/spl-autoload-register).
Removing compiler rejection alone is not autoload behavior acceptance.

## Selection and identities

| Target | Patch selection | Patch SHA256 |
|---|---|---|
| `vendor/htmlpurifier/library/HTMLPurifier.autoload.php` | New `patches/php83/held/autoload83/HTMLPurifier-autoload.patch` | `f1038cce8807ccb7f139fa9608a2b27c25bfd2a4eccc71a6f71b036bc8e32d20` |
| `vendor/symfony-data/bin/symfony.php` | New `patches/php83/held/autoload83/symfony-cli-autoload.patch` | `2ff7fdf8f13d0fb14f23bce79a0f5c6ade5c569a1ce6e3bc3a677ac45a0d4e05` |
| `vendor/symfony/util/sfCore.class.php` | **Reuse** `patches/php83/held/sfCore.class.php.patch` | `7a5b4cb0453336d6ad71f5e107df6d8d68c93d4991d75480c69636ee39e85db7` |

The first two have adjacent JSON metadata. The third retains its existing
`patches/php83/held/symfony-bootstrap.json` entry: no duplicate patch or false
claim of newly authored repair. [Audit identities](evidence/autoload83/audit-identities.json)
pin every before/after/patch hash and exact immutable-source identities. All
three input files equal the corresponding exp10 members. GNU patch applied
each with no offset/fuzz to private temporary copies and matched its after
hash; this is **not PHP execution**.

## Behavior audit and bounded intent

### HTML Purifier

`HTMLPurifier.auto.php:7–9` sets the include path, loads Bootstrap and requires
the registration file once. In `HTMLPurifier.autoload.php:9–15`, the existing
SPL path calls `HTMLPurifier_Bootstrap::registerAutoload()` and explicitly
retains a pre-existing legacy `__autoload` callback on PHP 7.4. Bootstrap's
`registerAutoload():79–121` prepends its loader on supported runtimes; its
`autoload():38–51` returns false for unrelated/missing classes and uses
`require_once` for known paths. None of those behaviors is edited.

Only the no-SPL fallback's forbidden global declaration is replaced by a clear
`RuntimeException`. SPL-disabled or older pre-SPL environments are not a
supported compatibility promise; the failure is explicit rather than silent.
No new global function or blanket error suppression is introduced.

### sfCore

The existing held patch replaces both no-SPL global declarations with explicit
failure. `initAutoload()` still sets `unserialize_callback_func` to
`spl_autoload_call` and appends `sfCore::splAutoload` through
`addAutoloadCallable`. `initSimpleAutoload()` still builds the class map via
the real finder, sets the same unserialize hook and registers
`sfCore::splSimpleAutoload`. Registration ordering, class map lookup and hit/miss
logic are unchanged in the SPL branches. `vendor/symfony/symfony.php:55`
invokes the former during bootstrap. Earlier bounded bootstrap evidence is
recorded in [symfony-bootstrap.md](symfony-bootstrap.md); it is not proof of
this new combined experiment or all serialization cases.

### Symfony CLI: explicit composition delta

The unconditional global function at `vendor/symfony-data/bin/symfony.php:107–118`
becomes an anonymously registered SPL callback at the same textual location.
Its body is unchanged: one static initialization flag, initialization from the
real `sfConfig`, and delegation to the existing
`simpleAutoloader::__autoload` **method**, which is not the removed global
function. Class-path lookup, ordered callable fallbacks and exceptions remain
unchanged. There is no invented globally named replacement function to collide
with another library.

The closure is appended without unregistering/replacing earlier SPL callbacks.
This is an **intentional compatibility-composition change**: an implicit legacy
global loader does not automatically join an existing SPL queue, whereas the
new callback can handle a miss after existing handlers. Existing-handler hits
and order must remain unchanged; the new miss fallback must be explicitly
tested, not normalized into a claim of universal PHP 7.4 parity.

Actual entrypoint tests are necessary. The original unconditional function has
compile-time visibility, while closure registration happens when execution
reaches that statement after the pake requires. The inspected `pakeFunction`
performs explicit includes, and `pakeGetopt` has a top-level class-existence
guard; no assertion that these timing details are harmless replaces execution.
`--version` exits before `sfConfig` initialization and must not force lazy
initialization. `-T` and a controlled synthetic task must exercise the later
path. Existing unrelated dependency failures remain evidence, not reasons to
stub out the real entrypoint until it passes.

Neither the CLI's existing `simpleAutoloader` class nor sfCore is made safely
redeclarable by this patch. Test normal `require_once` behavior and repeated
registration separately; do not promise arbitrary duplicate plain `require`
support. Autoloading serialized application objects is relevant; serializing
the newly registered closure itself is not an existing application contract
established by this audit.

## Runtime plan and evidence boundaries

[The test plan](evidence/autoload83/plan.json) requests four-tree compiler
controls, actual HTML Purifier registration/hits/misses and ordering,
sfCore simple/full loaders and unserialize, and the real Symfony CLI with empty
and pre-existing callback queues. Use isolated exp10-derived copies, original
PHP 7.4 controls, unsuppressed diagnostics, pinned source/runtime/harness
identities and explicit cleanup. Original PHP 8.3 compiler failures are
counterfactuals, not successful behavior cases. Additional prerequisites must
be identified rather than silently added to the three-patch series.

Historical source-audit phase only: no runtime results were asserted in this
initial section. See the subsequent runtime and final checkpoint sections.
The runtime worker and actual external
CLI review/execution are separate from this source-audit author. Other exp10
compiler rejections, six template renderers, diagnostics, complete service/media
workloads and final integration/release approvals remain open.

## Graph verification and limitations

Tier 2 discovery used `kaltura-rigel-18.20.0-full`, ready at generation
`2026-09-25T12:19:00Z` (231,336 nodes; 800,641 edges). Relevant name search had
seven results with no further page; both-direction depth-one traces and exact
snippets are retained in [audit-graph.json](evidence/autoload83/audit-graph.json).
All nine relied-on source paths received a [coverage check](evidence/autoload83/coverage.json).
The recorded partial range in `pakeGetopt.class.php:1–275` was read directly;
other checked paths had no recorded issue and matching metadata. All material
code was also read from the immutable raw source, not edited graph-view files.

Coverage is best effort, not proof of exhaustive consumers. An erroneous graph
resolution of built-in `file_get_contents` to a same-named Kaltura method is
explicitly excluded from reasoning. Zero static callers for a global autoload
function do not imply it is unused: engine-triggered loads are the reason for
the runtime cases.

## Runtime update: bounded primary matrix (2026-09-25)

The earlier source-only audit and [preparation plan](evidence/autoload83/behavior-plan.md)
are **historical phases**, not the current execution status. Actual primary
runtime testing has now occurred. The repeat/review was pending at this phase;
the final checkpoint below records its eventual outcome. The patches remain held, unintegrated, and do not authorize a
release.

[Final primary evidence](evidence/autoload83/primary-r3.json) records **26
isolated processes: 20 positive passes, 3 expected PHP8.3 removed-autoload fatal
controls, and 3 real empty-project CLI failures**. The collector deliberately
returns exit 1 and overall FAIL. All three empty-project `-T` invocations failed
because real `constants.php` requires `kConf`; those results were not converted
into passes or omitted.

A separately configured `-T` case succeeds on before74, candidate74 and
candidate83 using actual `kConf`, `kEnvironment`, `kConfCacheManager`, cache
factory and cache classes from the pinned exp10 archive. Synthetic local and
cache configuration maps are inserted through the real session cache API;
there are no replacement application classes or private-property mutations.
Each configured case loads 37 hash-verified source files and emits the identical
full task listing. This tests task registration/listing, **not task execution**,
SQL, a deployed project or cache misses. The fixture required no writable source
or cache directory and retained network/socket denial.

Other bounded passes cover actual HTMLPurifier EntityLookup loading, prefixed
and unrelated misses, existing callback order and PHP7.4 legacy preservation;
sfCore's real Finder-generated map, full/simple loaders and an
unserialize-created class; and actual Symfony `-V` plus explicitly labeled
post-exit queue tests. Existing SPL callbacks retain precedence; their misses
reach the candidate Symfony fallback. The original global loader does not
participate in a pre-existing SPL queue. This intentional composition difference
is recorded, not mislabeled universal PHP7.4 parity.

Native warnings remain visible. The obsolete global-autoload declaration
warnings disappear with the patches; PHP7.4's old `pakeYAMLNode` constructor
warning remains, and configured PHP8.3 execution retains the
`libxml_disable_entity_loader()` deprecation. The final collector checks exact
expected diagnostic phases/severities/files/lines/counts. It also requires
actual loaded targets/dependencies, exact functional row inventories, ordered
callback-hit traces, and task-list content/comparison. Before/candidate74
HP/core functional rows match. [Runtime identity](evidence/autoload83/runtime-before-r2.json)
and [final identity](evidence/autoload83/runtime-after-r3.json) objects match;
binaries, modules, linked libraries and configuration hashes were observed,
and the entire staged source/harness inventory remained unchanged.

[Attempt history](evidence/autoload83/behavior-results.md) preserves the first
collector's empty-array handling crash and all intermediate failures. The final
19 local tests pass, but local tests are not runtime acceptance. Broader
composition cases—later appended/prepended callbacks, duplicate class winners,
throwing callbacks and repeated includes/registrations—remain outside this
matrix and require separate evidence. Missing-SPL behavior remains unsupported
and unexecuted. No whole-application or broad composition acceptance is claimed.

### Subsequent bounded composition phase

The previously untested composition cases now have separate
[primary evidence](evidence/autoload83/composition-primary-r2.json) and an
[explicit scope/attempt report](evidence/autoload83/composition-results.md):
**30 processes, 27 positive passes and 3 expected redeclaration fatals**.
Independent repeat/review was pending at this phase; its terminal result is
recorded in the final checkpoint below.
The first matrix still retains its three empty-project failures; those were not
removed by the additional phase.

Actual loaders were exercised with later append/prepend callbacks, duplicate
class winners, throwing callbacks and exact callback/exception traces, repeated
HP/sfCore registration and full CLI repeat inclusion. Native74 implicit-loader
loss when its first SPL callback is registered differs intentionally from the
candidate's persistent SPL closure. Repeated CLI inclusion still fails—original74
on global function redeclaration, candidates on class redeclaration. There is
no new idempotence promise. Reflection winner paths, included-file hashes and
exact native warning/fatal messages and line numbers are checked. Source/runtime
identities remain unchanged, and 13 local composition tests pass.

Base diagnostic validation was also tightened after independent review: exact
message hashes and fatal source lines now have negative tests (21 base tests
pass). A collector-only replay of both retained primary and Claude reports
preserves the exact first-matrix results; no new guest execution is implied by
that replay. No-SPL, all third-party combinations, task bodies and full
application acceptance remain outside these bounded tests.

A subsequent in-memory adversarial mutation exposed Python boolean/integer
equality in the collector despite the prior independent review passing. The
mutation is preserved; collectors now require strict JSON value types and
integer exit codes. Current local totals are 23 base and 15 composition tests.
Collector-only replay preserves all genuine runtime outcomes; it is not a new
guest run. Final-revision independent validation is tracked separately in the
[composition report](evidence/autoload83/composition-results.md).

## Final bounded-cycle checkpoint

The actual Claude composition attempt first ended with a quota failure and no
runtime execution: [initial report](evidence/autoload83/composition-claude-review.json),
exit 1, **NOT_EXECUTED**. After the stated reset, the separate
[actual CLI retry](evidence/autoload83/composition-claude-retry-review.json)
completed with exit 0. It ran the final collector against the approved lab:
[30 new records](evidence/autoload83/composition-claude.json), **27 positive
passes and 3 expected redeclaration fatals**; 15 composition and 23 base tests
passed. Fresh before/after runtime snapshots were byte-identical. All 30
record contents match the primary run; the collector-hash metadata correctly
identifies the later typed validator, so the entire report is not byte-identical.

Independence is established by the actual CLI invocation and its executed tool
calls/commands (retry session `7d65fa9e-e973-463c-ae29-ca9dcccb52e4`), **not by
JSON equality**: deterministic reports can also be copied. Source/harness
inventory checks passed before and after genuine execution.

Cursor's preceding independent local review completed with exit 0. Its separate
final typed follow-up ran 15 + 23 tests and retained-report replay successfully,
and rejected 24 adversarial mutations while accepting four positive controls;
then the overall CLI hit its 150-second timeout, exit 124. Its
[written review](evidence/autoload83/composition-cursor-typed-review.json) and
[terminal status](evidence/autoload83/composition-cursor-typed-status.json)
preserve completed command results separately from the CLI timeout. It is not
reported as an exit-0 final CLI attempt.

The bounded cycle is ready for a source-validation checkpoint, **not application
or release acceptance**. The original three empty-project `-T` failures remain
FAIL; the separately configured real-class task-list cases pass. CLI composition
checks run in a labeled shutdown phase after actual `-V`, not inside task
execution. The additional sfCore composition coverage is **repeat registration
only**, not its append/prepend/throw combinations. Native74 queue deltas,
no-SPL exclusion, untested backends/SQL and untested arbitrary third-party
combinations remain explicit. Patches stay held; this cycle performs no
integration, package, release or production change.
