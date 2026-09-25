# Seven baseline compiler rejections: execution plan

**Plan only; no source repair, generator execution, VM operation or waiver.**
This bounded prerequisite contributes to open tasks 1.3 / T0-04; it cannot close
baseline/API/media T0-05, feasibility T0-06, package integration or release gates.
See the [migration proposal](../../openspec/changes/migrate-kaltura-php83/proposal.md)
and [tasks](../../openspec/changes/migrate-kaltura-php83/tasks.md).

## Fixed denominator and evidence

[exp10 remaining triage](evidence/exp10-syntax/remaining-triage.json) retains eleven
raw-file compiler rejections. Four are separately held compatibility work; this
plan covers only the other **seven baseline rejections**, never subtracting them
from raw syntax totals:

- Six tokenized Symfony skeletons: admin actions, CRUD actions, module actions,
  default batch, rotate-log batch, controller.
- `vendor/aws/Doctrine/Common/Cache/RiakCache.php`, reserved `Object` import alias.

[Identity ledger](evidence/remaining-baseline-syntax-plan/identities.json) records
exact immutable/original/exp10 source hashes and archive pins; the six templates'
complete direct source, Riak Object occurrences, and actual replacement prerequisite
are retained. [Graph evidence](evidence/remaining-baseline-syntax-plan/graph.json)
uses ready graph generation `2026-09-25T12:19:00Z`, 231336 nodes / 800641 edges,
with exact coverage on fourteen relied files. Six skeletons are partial; all their
contents, including missed ranges, were read directly. Clean coverage elsewhere
is best-effort, not a reachability guarantee. Existing [consumer evidence](evidence/compiler-triage/template-consumers.json)
provides positive consumer functions and complete exact snippets. No class-level
empty caller graph is treated as unreachable proof.

## Immediate prerequisite: real pake replacement is blocked on PHP 8.3

Actual `pake_replace_tokens` (`pakeFunction.php:214–232`) calls
`pakeApp::get_files_from_argument($arg, $target_dir, true)`. For a nonempty target
directory, its relative-path branch calls `create_function` at line357. Source:
`vendor/symfony/vendor/pake/pakeApp.class.php`, SHA-256
`72f538165dd3226b46c35ddac7700c0f3a6046e74f4646b74ca5bd541d59b120`.
This positive call chain applies even to a single explicit filename; replacing
pakeFinder with a string does not bypass the removed function.

Proposed **separately reviewed minimal held transform**, not yet implemented:

```php
// before
$files = array_map(create_function('$f', 'return 0 === strpos($f, DIRECTORY_SEPARATOR) ? substr($f, 1) : $f;'), $files);
// candidate
$files = array_map(function ($f) { return 0 === strpos($f, DIRECTORY_SEPARATOR) ? substr($f, 1) : $f; }, $files);
```

No captured variables (`use` list empty), no bound `$this` (static method), same
parameter, global constant, ternary, return and array_map ordering/keys. Do not
silently rename filenames, normalize paths, or change Finder behavior. Native74
must first exercise the original full class; preserve its create_function
E_DEPRECATED. Candidate74 removes that specific notice; original83 must fail on
the removed function; candidate83 must preserve values and all remaining notices.
Focused method cases: string/list/Finder inputs, relative false, empty target,
absolute contained path, relative filename, leading separator, empty string,
zero-string filename, nested name, mixed associative keys, outside-target path,
invalid argument and empty list. Reject duplicate case/runtime IDs and unexpected
native stderr; hash every loaded helper and output before/after.

## Real generation: staged execution contract

First construct a disposable project root on the coordinator-owned lab, outside
application/database paths. Source subtree is read-only; only the fresh generated
project directory is writable. Network/socket access denied; private tmp; protected
system/home; `/opt/kaltura`, database and production paths inaccessible. Do not
execute generated controller/batch scripts: they boot application configuration or
rotate logs. Generate, inspect and lint them only.

Use full actual bundled pake/Symfony classes and actual task functions, not a
handwritten token replacer, extracted-function reimplementation or fake Finder.
A synthetic task-property provider may supply only project/author values, labelled
explicitly; actual `sfConfig` points all paths to the disposable fixture. Loading
actual task files executes registration (`pake_desc`, `pake_task`, aliases), so
freeze the real registration/bootstrap dependency closure before running. Include
actual `pakeApp`, `pakeGetopt`, `pakeTask`, Finder, exception, color helpers and
sfConfig/sfLoader as encountered; hash and coverage-check additions first. Existing
exp10 curly repairs may be necessary for helpers; compare original74 against the
precisely identified exp10-derived candidate, not an undocumented mixed tree.

Run each task in a fresh process/project to avoid registrations, constants and
class definitions leaking between cases. Confirm no plugin/project skeleton
override directories exist for the bundled-template cases; separately test one
explicit override with a sentinel when verifying lookup precedence.

| Template | Actual consumer / concrete argument shape |
|---|---|
| module actions | `run_init_module($task, ['auditapp','AuditModule'])` |
| admin actions | `run_propel_init_admin($task, ['auditapp','AuditAdmin','AuditModel','default'])` |
| CRUD actions | `run_propel_init_crud($task, ['auditapp','AuditCrud','AuditModel'])` |
| default batch | `run_init_batch($task, ['default','audit_job','auditapp','dev', DEBUG])` |
| rotate-log batch | `run_init_batch($task, ['rotate_log','auditapp','prod','dev', DEBUG])` |
| controller | `run_init_controller($task, ['auditapp','dev','audit_front', DEBUG])` |

The rotate-log function uses argument2 when constructing the batch filename, then
overwrites environment from optional argument3; preserve and assert both facts.
Use identifiers without injected PHP/comment tokens. Do not assert safety for
untrusted identifier input without separate validation/security testing.

Minimum generator matrix: one case each for module/admin/CRUD, plus default,
true, false, `'0'`, and `'false'` DEBUG cases for each of batch/rotate/controller:
**18 logical cases** per positive runtime. `'false'` is truthy after the actual
boolean cast, unlike `'0'`. Negative controls: missing required arguments,
existing module target, unknown batch, missing input skeleton, read-only output;
retain actual exception/exit semantics, don't turn every failure into PASS.

For each generated output, retain relative path, exact bytes/hash, tokens remaining,
expected class/constant names, and native `php -n -l` result on both74/83. Compare
74 original versus74 candidate versus83 candidate file inventory and bytes exactly
(no broad timestamp/path scrubbing). Log output may contain the private fixture
root: normalize only that explicitly pinned root in a separate presentation field,
retain raw logs/hashes. Full real task run may reveal an earlier removed function:
record the first blocker, not guessed success further down the chain.

### DEBUG=false is a baseline defect, not a reason to fake the generator

All three templates contain `define('SF_DEBUG', ##DEBUG##);`. Consumers cast DEBUG
to bool; actual `str_replace` receives false and can produce
`define('SF_DEBUG', );`. Record exact output and both runtime lints first. Expected
failure is a baseline characterization, **not generated-code acceptance**.
No implicit replacement with `'false'` or `'0'` is authorized in the closure repair.
Fixing this legacy behavior needs a separate intentional-behavior-change patch,
review and tests. True/default generation must still demonstrate valid output.
Raw six skeleton failures remain six, even after generated artifacts pass.

## Riak alias: smallest safe decision tree

Direct source shows import line26 `use Riak\Object;`, construction lines132/243,
and private typehint line207; preserve documentary fully qualified names. Proposed
minimal syntax candidate would use `use Riak\Object as RiakObject;` and change only
the two `new Object` sites and `isExpired(Object ...)` alias to `RiakObject`.
The resolved dependency must remain `\Riak\Object`, public class stays
`Doctrine\Common\Cache\RiakCache`, constructor stays `Bucket`, methods/visibility
unchanged. Do not rename vendor classes, widen the parameter to untyped/object,
remove the backend, or substitute a different client API merely to pass lint.

Original74 and original83 are compiler-fatal controls here: no valid original74
behavior baseline exists for this unchanged file. Candidate74/83 syntax equality
and reflected resolved type/public signature equality are useful but **not original
functional parity**. Parent `CacheProvider` implements four cache interfaces and
public fetch/save/contains/delete/stats/flush behavior; load the actual parent and
interfaces for candidate tests, not a stand-in parent class.

Before claiming backend behavior, identify a pinned compatible provider exposing
`Riak\Bucket`, `Riak\Object`, Input classes and exceptions, its license, build/runtime
requirements and installed module identity. No provider availability is inferred
from an empty class graph or bundled import. First safe lab check is read-only
module/class inventory in a fresh process (no autoload side effects). If unavailable,
leave backend integration BLOCKED and seek a reviewed provider/upgrade/defer
choice. Synthetic transport doubles may test call contracts only if exact class
names/types can be faithfully represented; do not bypass language-reserved class
constraints with renamed doubles and call that integration.

Once a provider is available, a disposable isolated backend may be proposed under
separate authorization. Tests: empty fetch/contains, scalar/array/null/false save
and fetch, TTL zero/positive/expired, deletion exceptions, flush ordering, stats,
namespace keys and sibling conflict handling. Source's `resolveConflict` indexes
`$objectList[count($objectList)]` (line238), not count-minus-one: retain/test this
independent possible baseline defect rather than silently repair it alongside
alias spelling. No cache deletion or flush against shared/production backend.

## Sequence, runnable boundaries and completion criteria

1. Freeze this plan and review the one-line closure transform/case contract.
2. Build new dedicated held prerequisite+harness locally; verify exact bytes and
   task/helper closure. No current four held patches or exp10 ZIP change.
3. After autoload primary+independent repeats release baseline74, acquire exclusive
   owner; snapshot runtime/modules/libraries before and after. Stage fresh project.
4. Smallest first actual commands inside the isolated runner are
   `php7.4 -n GENERATOR_PROBE.php method-relative-string` and
   `php8.3 -n GENERATOR_PROBE.php method-relative-string` with **actual pake classes**.
   `GENERATOR_PROBE.php` is a planned harness, not an existing executable: do not
   run these illustrative commands before implementation/hash review. Assert74
   return plus deprecation and83 actual removed-function failure, then candidate
   parity; expand to the eighteen generator cases. Lint generated files without
   executing them. No fake wrappers around removed functions.
5. In parallel, prepare Riak provider inventory/decision; do not imply alias lint
   alone restores an operational backend.
6. Actual independent Claude/Cursor/Grok or permitted OpenCode fallback repeat and
   review; separate runtime execution, local validation and advisory review.

Realistic blockers: lab serialization, actual pake bootstrap dependencies, removed
create_function prerequisite, DEBUG-false baseline invalid output, missing/pending
Riak provider evidence and absence of an original compilable Riak baseline. None
justify a waiver or closing aggregate tasks. A template-generation subcase may
close only for enumerated actual consumers with retained baseline failures and
explicit unresolved bad-input cases; raw syntax accounting remains unchanged.
