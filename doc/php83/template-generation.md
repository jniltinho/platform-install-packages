# Pake relative-path closure prerequisite — bounded validation

**HELD / BOUNDED RUNTIME VALIDATION COMPLETED. No new ZIP or application acceptance.**
Actual primary and independent Claude runs cover method65, generation90, negative30
and isolated DEBUG arity4; detailed evidence and limitations appear below.
The historical preparation sections record the state before those executions.
Implements only the prerequisite proposed in the
[seven-rejection plan](remaining-baseline-syntax-plan.md), not DEBUG=false repair.

## Historical preparation: selected change and local proof

`vendor/symfony/vendor/pake/pakeApp.class.php:357` changes one expression:

```php
create_function('$f', 'return 0 === strpos($f, DIRECTORY_SEPARATOR) ? substr($f, 1) : $f;')
// becomes
function ($f) { return 0 === strpos($f, DIRECTORY_SEPARATOR) ? substr($f, 1) : $f; }
```

No captures or `$this`; unchanged argument/body/global constant, return and array_map
call. Before SHA256 `72f538165dd3226b46c35ddac7700c0f3a6046e74f4646b74ca5bd541d59b120`;
after `d5bdc4612a5c9ae76fe8f594eaefeff1059175f0a36d756a1010612830bf39b8`.
[Manifest](../../patches/php83/held/pake-relative-path/manifest.json) records pinned
original/exp10 archives and all **32** explicitly selected helper/skeleton files.
Candidate derives from exp10, retaining its three prior curly repairs in pakeFinder,
pakeGetopt and pakeYaml. Only pakeApp differs from exp10. This is not represented as
one change against a completely untouched original subtree.

[Strict patch proof](evidence/template-generation/patch-proof.json) applies the
patch with `--fuzz=0`, no offsets and exact resulting hash. Ten synthetic local tests
pass: precise substitution, ambiguous/missing/wrong-pin input rejection, archive
hash, missing file, traversal and symlink rejection, and no-capture assertion.
Neither these tests nor source inspection proves PHP parsing or runtime behavior.
No host PHP interpreter was available; PHP lint is pending authorized lab use.

## Historical preparation: actual-function harness (then unexecuted)

`tools/php83/template-generation/probe.php` loads actual full classes. It uses
actual pakeTask properties and registrations, actual Finder/copy/mirror/token
replacement, real sfConfig and sfLoader—not fake generation or extracted methods.
Model/database boot is never required. Actual registration may expose additional
legacy runtime problems; those are blockers, not permission to invent substitutes.

[Case plan](evidence/template-generation/case-plan.json): **37 logical cases**:
13 relative-path method cases, 18 actual generation cases and six negative cases.
Planned variants are original74, exp10_74, exp10_83, candidate74, candidate83 (185
invocations if all stages are approved). Original83's unpatched helper has earlier
curly syntax failures; exp10_83 is the meaningful removed-create_function control.
Nonrelative/empty-target/invalid-input cases need not hit that function, so no
blanket fatal expectation is imposed.

The probe catches Throwable with explicit class/message/source/line and process
exit10; exit0 denotes no caught exception, **not acceptance**. Load/compiler failures
remain native failures outside that boundary. Diagnostics are recorded and returned
to the normal native channel (`return false`), never blanket-suppressed. Loaded
source hashes, generated path→hash/base64 maps, raw task logs and runtime version
are emitted. A fresh `/tmp/template-audit` is mandatory per process; the future
sandbox must give each invocation a private tmp. No generated file is executed.

Generation covers actual module/admin/CRUD consumers plus default batch, rotate
batch and controller with omitted/true/false/string-zero/string-false DEBUG.
Negative cases: missing module argument, missing admin model, unknown batch,
existing module, missing skeleton and read-only output. False/zero may generate
invalid PHP in the baseline; those failures remain explicit. Negative calls may
emit warnings without throwing: output and diagnostics must be classified, not
converted to an assumed successful exception result.

## Historical preparation: review and execution boundary

Local preparation is reproducible without VM access:

```bash
python3 -m unittest discover -s tools/php83/template-generation -p 'test_*.py' -v
python3 tools/php83/template-generation/build.py /tmp/NEW-UNUSED-PREPARATION-PATH
```

Both archives are pinned and only regular safe selected members are read. Existing
output is refused. Fresh staging is `/tmp/php83-template-generation-prep-r2` locally;
no SSH/upload/guest stage has been created. Graph coverage for new helpers is in
[coverage.json](evidence/template-generation/coverage.json); partial Finder/Getopt
and YAML locations were source-read for relied loading/call sites. No completeness
or absence claim is made; runtime loaded-file inventory remains a required check.

Before runtime: independent source review, exclusive lab grant after the autoload
owner releases it, final isolated runner/collector with fixed command/case IDs,
source/runtime before/after pins, native stderr contract and time/resource bounds.
First run the focused method cases, retaining original deprecations and exp10_83
removed-function evidence. Then execute generation and lint decoded outputs on both
interpreters. Compare generated bytes/inventory exactly; do not execute generated
controllers/batches or rewrite false DEBUG tokens. Negative cases and generated
invalid-output baseline defects need explicit classifications before any passing
summary. Future collector must reject duplicated/missing mode/case rows and unknown
statuses, and have adversarial tests. Those runtime collector checks are **pending**,
not satisfied by this prepared probe. Aggregate T0-04/T0-05/T0-06 remain open.

## Prepared runner and observation collector

`run.sh` now specifies the lab/UID gate, read-only source/runtime mounts, private
network/tmp/devices, socket syscall denial, protected system/home, inaccessible
application/database paths and 45-second/256MiB per-process bounds. PHP generated
output is linted through **stdin with `-l`**, never evaluated. Runner/probe have not
been executed on PHP or a VM in this phase.

`collect.py` enumerates the exact ordered five-variant ×37-case matrix and rejects
unknown statuses, duplicate/missing/reordered rows, unsafe generated paths, byte
hash drift and unexpected loaded source identities. It collects runtime/module/
library identity through the existing audited literal snapshot program and requires
stage/runtime before-after equality. Generated PHP is linted by both interpreters.
First observations deliberately return exit2 with runtime/generated-syntax acceptance
false: no unreviewed diagnostic or output baseline becomes an automatic golden.
The later reviewed contract must classify exceptions, exact stderr, generated bytes,
DEBUG-false syntax failures, and every negative case before any bounded PASS claim.

### Actual CLI review and r2 preparation correction

Grok's actual bounded attempt timed out at120s (exit124), after named-file reads
but **no test execution**; no pass credited. One earlier CLI option parse failure
is separately recorded. Actual OpenCode fallback used the resolved free model
`opencode/muse-spark-1.3-contributor-free`: exit0, **10 synthetic tests executed PASS**,
`bash -n` PASS and patch/manifest hash match. No denied read or external source/VM
access occurred. Public exports exclude thought/reasoning events/fields;
[CLI summary](evidence/template-generation/cli-summary.json) distinguishes executors.

Parent and OpenCode independently found the initial collector's native255 branch
was unreachable in its selected variants. After OpenCode terminated, r1 collector
was preserved and r2 now rejects native255 for all probe rows: removed-function
errors are caught Throwable→exit10, while unknown compiler/runner failures remain
failed observations. Lint255 remains a separately retained syntax result.

r2 defaults to `--phase method` (**65** invocations), with explicit `generate`
(90), `negative` (30) or `all` (185), so focused prerequisites run first. It creates
an exclusive report immediately and atomically persists every returned row/lint,
pending-case identity, failure and terminal state. SSH/identity/timeout/signal
failures preserve progress instead of losing the entire run. Hard process kill
still cannot guarantee a terminal summary, but the last atomic progress survives.
The runtime snapshot helper and expected exp10 lab reference are now pinned before
fresh runtime identity comparison. **21 local tests pass** (10 builder +11 collector);
new tests cover ordered matrix/missing/duplicate rows, boolean/timeout/native fatal
statuses, generated path/hash/base64 safety and atomic progress. This r2 preparation
has not yet had independent CLI follow-up or VM execution; prior actual CLI review
applies to the preserved r1 snapshot, not to unreviewed new changes.

## r3 fixes, independent review and first focused observations

After actual Cursor's r2 review, unique sibling temporary files with finally cleanup
replaced the fixed progress filename. Strict checksum parsing now deliberately
rejects malformed/duplicate rows. Preserved old collector:
`cursor-reviewed-r2-collect.py`. **27 tests pass**. Actual OpenCode using the installed
`minimax-coding-plan/MiniMax-M3` independently ran27 tests, shell syntax and additional
safe adversarial probes; exit0, no narrow-fix defects found. Its statement that the
old parser silently accepted all malformed lines is overbroad: some caused IndexError;
the new strict parser addresses both duplicate and malformed cases. No paid model
purchase or authentication configuration changes were made.

With coordinator's subsequent exclusive baseline74 grant, a fresh
`/home/vagrant/php-template-generation-r1` was staged. The unchanged probe passed
native74 and copied83 `php -l` via stdin (both0). **Focused method phase only** ran:
65 rows, zero observation-validation failures, fresh expected runtime/source
identities equal before/after. Collector exit2 is intentional nonacceptance.
[Raw records](evidence/template-generation/method-primary.json) and
[observation comparison](evidence/template-generation/method-observation-summary.json)
retain the evidence.

All12 positive method outputs and the invalid-type exception match exactly across
original74, exp10_74, candidate74 and candidate83. exp10_83 produces the caught
undefined-create_function Error in10 cases; nonrelative/empty-target succeed and
invalid type retains its separate exception. Original74 retains16 load-phase curly
deprecations per process plus create_function deprecation on10 cases; exp10_74
retains only that latter notice; both candidates have no diagnostics in these
focused cases. These observations are not a newly approved output/diagnostic golden:
independent runtime repeat and exact native stderr/expected-contract review remain
pending. **No generation case was executed**, no DEBUG-false result was waived, and
baseline74 ownership was returned to the coordinator after focused completion.

### Explicit focused-method contract

`validate_method.py` is a separate local validator; the observation collector and
its exit2 semantics are unchanged. It derives fixed expected values from the actual
path-prefix/one-leading-separator transformation and controlled fixture inputs:
string-zero remains a string, keyed array remains keyed, outside absolute path
loses only its leading separator, nonrelative input remains absolute. Finder's
observed order is pinned to this explicitly constructed fixture (nested directory
created before the plain file), not assumed portable for arbitrary filesystems.
[Source contract](evidence/template-generation/method-source-contract.json) records
exact source lines/hashes for the transformation and all original curly notices.

The contract enforces each of65 ordered unique mode/case rows, exact source/runtime/
harness identities, literal typed values and exception data, generated fixture
bytes, empty task logs, exact structured diagnostics and native stderr/hash. It
expects50 positive results and15 explicit exceptions (ten removed-function controls
plus five invalid-type cases). It approves only the bounded method contract, never
template generation or application acceptance. Primary report passes this contract.
Expanded local suite: **39 tests pass**, including typed zero/boolean replacement,
array key loss, duplicated cases/variants, extra stderr, boolean diagnostic metadata,
loaded-file omission, runtime drift and fixture-output mutation. An actual Claude
independent repeat was scheduled separately; do not infer its success from primary
validation or local tests.

### Actual Claude independent focused repeat

Claude CLI completed exit0 after its separate65-case lab execution:39 local tests
exit0, observation collector exit2 (expected), bounded validator exit0. Primary and
independent reports are **byte-identical** SHA256
`9fb502d6f2c902403296a39a96a7ee62dec249332059aac044417b8488ad2ef9`.
Fresh before/after runtime/stage identities agree; frozen tool hashes are unchanged.
[Independent summary](evidence/template-generation/method-independent-summary.json)
and [public actual CLI report](evidence/template-generation/claude-method-public.json)
retain counts, commands/results and limitations. An initial CLI argument parsing
failure occurred before any execution and is preserved separately; stdin-based
retry succeeded without permission bypass.

This is an executor/reviewer independent of the Codex patch/harness author, but
uses the same lab and fixture, not independent environment coverage. Claude found
no discrepancy in actual results, and noted validator limitations: object-key
ordering is canonicalized; JSON cannot separately identify integer7 versus string7
object keys; command, generated-syntax acceptance flag, snapshot-program hash and
absence of pending/terminal-error fields were manually checked rather than asserted.
Those limitations remain explicit, not silently treated as tested guards. The
bounded **method** proof passed; generation90/negative30 were not run. baseline74
ownership was released back to the coordinator after Claude terminated.

## Generation observations: failed collector attempt and faithful rerun

First actual generation attempt preserved37/90 rows then stopped on a collector
shape error: PHP's empty output array encoded as JSON `[]`, while `decode_outputs`
expected only an object. The raw exp10_83 module result correctly reported caught
undefined-create_function before producing any file. Failed report and explicit
post-failure source/runtime equality evidence are retained; nothing was overwritten.

Coordinator authorized **collector-only** handling of exactly empty[] as empty map;
nonempty lists, scalar and null remain rejected. Source/probe/runner unchanged.
Old collector is preserved as `generation-reviewed-r3-collect.py`. Actual independent
OpenCode/MiniMax ran10 builder +19 collector tests and the single-script shell
syntax check, all exit0; reviewed the sole decode_outputs hunk, no defects found.
Historical method reports retain their original collector/test identities; their
old validator's current-file-hash assertions do not automatically transfer to this
new collector phase. This is an evidence-version distinction, not permission to
loosen original pins or claim the old method reports used new tools.

Fresh [generation r4 report](evidence/template-generation/generation-primary-r4.json)
completed **90 rows**, zero collection-validation failures, exact expected identities
before/after, collector exit2/nonacceptance. No negative30 case ran. Four positive
variants (original74, exp10_74, candidate74, candidate83) each completed18 task calls
and42 successful lints (168 total). exp10_83 retains18 caught undefined-create_function
errors and30 failed lints of batch/controller files copied before token replacement;
module/admin/CRUD fail before producing files. All18 generated inventories and byte
hashes match original74 exactly for each of the other three positive variants.
See [observation summary](evidence/template-generation/generation-observation-summary.json).

**Correction to the earlier plan's DEBUG-false syntax prediction:** observed false
and string-zero output is `define('SF_DEBUG', );`, but native74 **and**83 lint both
succeed. The trailing comma is syntactically accepted; the call still supplies only
one argument. Runtime arity/constant semantics were **not executed**, so no claim of
working generated application, no waiver and no silent DEBUG repair follows from
lint success. The earlier anticipated syntax failure was a hypothesis disproved by
these native compiler results. A separately authorized isolated call-arity test may
characterize the baseline issue without booting generated application scripts.

No generated controller/batch script was executed, no source/task/framework was
modified during observation, and baseline74 was released after completion.
Independent generation repeat and reviewed exact output/diagnostic contract remain
pending; raw six template compiler failures remain in the denominator.

### Source-derived generation validator (independent repeat pending)

`validate_generation.py` independently constructs the expected generated files from
hash-verified original template bytes and explicit task argument/token maps. It does
not use primary generated output hashes as a functional oracle. Only human-visible
pake action logs and native compiler wording for unsubstituted controls are frozen
from observations in the separately pinned `generation-contract.json`.

The validator checks exact90 ordered mode/case rows, all16 loaded source identities,
32-file ×3-variant stage and runtime pre/post identities, execution harness hashes,
snapshot helper/program hashes, commands, acceptance flags and terminal state. It
checks output inventory/bytes, exceptions, exact structured/native diagnostics and
all198 ordered dual-runtime lint results. Counts are accumulated from checked rows:
72 successful tasks,18 expected removed-function errors,168 successful lints,
30 expected unsubstituted-source failures,24 positive-variant false/zero DEBUG
outputs still containing an empty argument. Their runtime semantics remain untested.

Primary observations satisfy this bounded contract. Fifteen new tests reject missing/
duplicate cases, boolean/timeout exits, stderr/diagnostic drift, altered/extra output,
missing lint, boolean lint status, wrong command, pending state, changed snapshot
program and unapproved generated-syntax acceptance. Actual Claude is separately
assigned10 builder +19 collector +15 generation tests and a fresh generation90
execution; no completion is inferred until that CLI terminates with evidence.

### Actual Claude independent generation repeat completed

Claude CLI terminated exit0 after executing all three suites separately:
10 builder +19 collector +15 generation-contract tests (**44**, all exit0), a fresh
90-case collection (expected exit2), and bounded contract validation (exit0).
The new report and primary-r4 are byte-identical SHA256
`43074293abfe7a9bda134a6305a72adf66e4139b6888d13e220d93a674696a86`;
no output/diagnostic normalization was used. Frozen source/harness/contract hashes
and fresh runtime/stage pre/post identities are unchanged. Independent review
confirmed72 positive tasks,18 retained removed-function errors,168 lint successes,
30 unsubstituted-control lint failures and24 empty DEBUG argument outputs.

[Independent summary](evidence/template-generation/generation-independent-summary.json)
and [actual CLI public report](evidence/template-generation/claude-generation-public.json)
record the result. No new review defect was found. Reproducibility is not a claim
of correct generated application semantics: DEBUG-false runtime arity remains
NOT_EXECUTED, raw action-log/compiler wording remains recorded-contract evidence,
and negative30/generated-app execution/application/release gates remain open.
Exclusive baseline74 ownership was released when the independent CLI terminated.

## Followup-v1 preparation: negative inputs and isolated DEBUG arity

New files under `tools/php83/template-generation/followup-v1/` leave all previous
source/probe/collector phases and reports unchanged. **No VM or native PHP execution
in this preparation phase.**

The explicit [30-row negative plan](evidence/template-generation/followup-v1/negative30-contract-plan.json)
uses the existing six actual negative task cases across five pinned variants.
Missing module/model arguments, unknown batch and existing module have explicit
source-derived exception predictions. Missing skeleton and read-only output retain
copy/read/write warning paths; exp10_83 may fail earlier at create_function. An
exit0 under read-only output is not successful generation. Exact native warning/
exception/output contracts must be confirmed from retained observations and reviewed;
predictions are not test results and no row is accepted in advance. The unchanged
collector's future `--phase negative` run remains exit2/nonacceptance until a proper
30-row outcome/diagnostic validator is frozen.

`prepare_arity.py` reads only the pinned actual generation90 report, verifies seven
candidate83 generated-output hashes and extracts exactly one line matching an
allowlisted literal `define('SF_DEBUG', <empty-or-1>);`. Extra statements, expressions,
comments, duplicates and missing definitions are rejected. Six false/zero cases
share the same literal; the true case is a control. It inserts only this validated
statement into a tiny fixture that captures native return type/value, whether the
constant was defined, diagnostics and any Throwable. **No eval, include, autoload,
application configuration or generated controller/batch is executed.**

[Fixture provenance](evidence/template-generation/followup-v1/manifest.json) records
the generated source/report/statement hashes and the two tiny fixture hashes.
`arity-run.sh` is a separately versioned read-only sandbox planned for a fresh
`/home/vagrant/php-template-arity-v1` stage; it has not been staged. `collect_arity.py`
plans four separate processes (74/83 ×empty/true), with stage/runtime identities and
incremental evidence. It returns nonacceptance until exact native behavior is
reviewed. This establishes only PHP call-arity/constant semantics, not generated
application boot or delivery correctness. PHP74 empty-call warning/return and PHP83
exception outcomes must be observed, not assumed from the earlier lint results.

Six local extractor tests pass; independent local CLI review is recorded separately.
All shell syntax checks are per script. Actual negative30 and arity4 execution need
an explicit lab release/grant; neither source compiler rejections nor DEBUG behavior
is waived by preparing these fixtures.

### Followup-v1 review hardening before runtime

Actual OpenCode/MiniMax initially executed six extraction tests and shell syntax
successfully, but its PHP-behavior prose included unsupported claims (for example,
that returning false from the handler causes TypeError). Those claims are **not**
adopted as evidence. Actual Claude local review confirmed six tests and identified
concrete guard gaps; initial files are preserved under `reviewed-initial/`.

Authorized follow-up fixes now pin the manifest and validate both local fixture
hashes before remote access; validate exit/exception/schema consistency; retain all
four raw observations even if one native call fails; bind unique selected source
cases to empty/true literal names; use `sudo -n`; and recheck stage/runtime identity
before and after each process. Source/probe fixtures themselves remain unchanged.
Nineteen local tests pass, including a fully mocked four-process loop with first
native-fatal result retained as failure while remaining rows are captured.

Actual OpenCode/MiniMax independently reran19 tests plus bash syntax (exit0),
reviewed the scoped changes, and found no new implementation blocker. It did not
open the manifest in that follow-up, so its pin review is explicitly limited;
prior Claude checked fixture/manifest identities and local frozen-hash checks cover
all current files. No VM or PHP execution has occurred yet. The planned four-process
arity observation and negative30 native diagnostic contracts remain open pending
exclusive-lab release and controlled execution.

### Followup-v1 actual primary observations (contracts still pending)

After the separate lab owner released baseline74, authorized execution collected
all30 negative task rows and all4 tiny literal-call rows. Both collectors finished
with exit2/nonacceptance, zero observation-validation failures and unchanged expected
runtime/source/fixture identities before and after. Negative tasks used the unchanged
read-only template stage; arity used fresh `/home/vagrant/php-template-arity-v1`.
No generated application script was executed and no source repair was performed.

[Primary summary](evidence/template-generation/followup-v1/primary-summary.json):

- Negative30:26 exception exits10; four read-only-output cases return exit0 despite
  warnings and no generated file (original74, exp10_74, candidate74, candidate83).
  This is preserved legacy behavior, **not successful generation**. Missing skeleton
  creates an empty file before throwing in those four variants; exp10_83 instead
  reaches the retained removed-create_function error. Warnings and lints remain raw.
- Literal empty DEBUG call on PHP74: native warning `define() expects at least 2
  parameters, 1 given`, NULL return, `SF_DEBUG` undefined, exit0.
- Same literal on PHP83: caught `ArgumentCountError`, `SF_DEBUG` undefined, exit10.
- Literal true control on both runtimes: returns boolean true, defines integer1,
  no diagnostic, exit0.

These native results establish a real baseline/runtime defect hidden by lint
success; they do not authorize repairing DEBUG semantics or claim application boot.
Exact reviewed negative/arity validators and independent runtime repeat remain
pending. baseline74 ownership was released after both primary collectors terminated.

### Followup-v1 explicit contracts and independent repeat

The [bounded validator](../../tools/php83/template-generation/followup-v1/validate_followup.py)
now independently enumerates negative-case exceptions, exit statuses, empty output
and empty-file side effects, exact lint rows, and literal-call values/types.
Native warning spelling/order and task logs are separately pinned observations,
not an independent functional oracle. Both retained primary reports pass.

Actual Claude ran all **34 local tests**, then repeated negative30 and literal
arity4 on the unchanged isolated baseline74 stages. Collectors retained exit2
observation status; the two explicit validators returned exit0. Both raw reports
are byte-identical to primary, including native stderr, generated bytes/lints,
and expected source/runtime identities before/after. Frozen tool hashes remained
unchanged. See [independent summary](evidence/template-generation/followup-v1/independent-summary.json)
and [public Claude review](evidence/template-generation/followup-v1/claude-repeat-public.json).
Baseline74 was released after terminal execution.

This closes only the enumerated negative-consumer and isolated literal-call
observation contracts. Four read-only-output exit0 rows remain **failed generation
with legacy exit handling**, not successes. Empty DEBUG remains a proven
compatibility defect: native74 warns/returns NULL; native83 throws
ArgumentCountError. No generated controller/batch application was executed,
no source repair was selected, and no raw-template compiler failure or aggregate
migration gate is waived.

Review limitations: the repeat has an independent executor but the same harness
and stages; unit tests use primary fixtures while fresh reports are validated by
the actual validator commands. Runtime body checks the version family while
pre/post snapshots pin exact native bytes/modules. Validator output publication
uses an exists/write check rather than atomic exclusive creation; these runs used
unique outputs and one serialized owner, but concurrent-writer robustness remains
a small local tooling improvement rather than a proven property.

### Separate generator-debug-v1 repair preparation

A [new held experiment](evidence/template-generation/generator-debug-v1/case-plan.md)
changes only three DEBUG token mappings to `(int) (boolean) $debug`, preserving
true output integer1 and making false output integer0. The held Pake closure is
an explicit prerequisite. Old frozen evidence is untouched; no ZIP selection.
Graph coverage, exact source pins, seven local tests and strict patch replay are
retained in that evidence directory. Actual72 consumer observations and isolated
new literal calls remain pending; prior proofs do not validate this new repair.

Actual Claude local review executed23 tests, bash syntax and frozen hashes. It
identified a real case-plan self-consistency gap: removing an unchanged case could
leave the validator claiming72 rows. Reviewed files are preserved under
`generator-debug-v1/reviewed-r1/`. The new phase pins case-plan bytes, requires
exactly72 rows, and adds an adversarial omitted-module test; all24 tests pass.
The new frozen set also covers prior builder and case-plan dependencies. Independent
re-review, isolated literal0/1 fixture preparation and new VM execution remain
pending. No proof is claimed from synthetic validator fixtures.

### Generator-debug-v1 bounded native validation completed

The new repair now has actual primary and Claude-repeat evidence, not merely the
historical controls. OpenCode/MiniMax executed35 local tests; follow-up tests cover
full literal extraction/prepare and both retained-stage identities. Actual Claude
then executed40 tests, separately checked both shell scripts and17 frozen hashes,
and found no blocking guard defect. Reviewed phase snapshots remain preserved.
OpenCode's claimed vanished generation stage and empty-map comparison defects were
incorrect and are not adopted; its genuine missing extraction-test coverage was
addressed. Remaining missing adversarial tests are listed in Claude's public review.

On fresh immutable baseline74 stages, using native74 and copied83:
- Actual72 generator calls:18 cases × prerequisite/debug × two runtimes, zero
  observation failures. Collector exit2 remains observation-only; exact validator
  exit0 verifies12 changed false/zero outputs and60 unchanged rows.
- [Direct byte delta](evidence/template-generation/generator-debug-v1/exact-byte-delta.json)
  independently compares actual prerequisite/debug pairs: each of12 changes inserts
  exactly byte0x30 (`0`), with every other generated byte preserved.
- Seven validated actual generated definitions supply two tiny fixtures. Four native
  literal calls return boolean true, define integer0/1, and produce no diagnostics
  or exceptions. No generated application file is loaded/executed.
- Actual Claude independently reruns40 local tests and both runtime phases. All
  generation, validation and literal reports match primary byte for byte; frozen
  source/harness and native runtime identities remain unchanged before/after.

See [bounded summary](evidence/template-generation/generator-debug-v1/independent-summary.json)
and [actual Claude repeat](evidence/template-generation/generator-debug-v1/claude-runtime-public.json).
The original empty-argument74 warning/83 ArgumentCountError remains preserved as
pre-repair evidence. String-`false` intentionally remains legacy truthy→integer1.
This closes the enumerated DEBUG generator/literal defect only. Same-harness/stage
repetition is not independent implementation, and historical native diagnostic
spelling is retained evidence rather than an independent oracle. No SQL/backend,
whole generated application, source ZIP/package promotion or aggregate acceptance
is implied. Patch remains HELD; both labs were released after terminal repetition.
