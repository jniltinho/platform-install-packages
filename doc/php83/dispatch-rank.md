# Dispatcher storage and rank argument contract — bounded observations

**Latest: four native83 primary + four actual Claude repeat observations and
three PHP74 dispatcher observations completed. Typed state/serialization parity
is bounded to the recorded fixture. No repair selection or release.**
Historical local-preparation phase: six local builder tests passed.
Two complete FrontController comparison variants are prepared, not selected.
No rank patch/default removal exists. New preparations originate within this
repository; this task never accesses or relocates the separately denied return
contract stage/identity object.

## Source and caller evidence

Original-source graph ready, generation2026-09-25T12:19:00Z,231336nodes/800641edges.
Exact file coverage is metadata_match/no_recorded_issue (best effort, not complete
caller discovery). Actual selected exp12 ZIP SHA
`de5e61a1b54f472e605ef2e87669302a3915616fd85378e0f05706fcb06a7e8b`
was directly read; complete source bytes and hashes reside in
[evidence/preparation-r2](evidence/dispatch-rank/preparation-r2/manifest.json).
The selected FrontController null-user repair is retained.

Three positive graph callers agree with literal source and archive lookup:

| Caller | Actual call shape |
|---|---|
| BaseEntryService::anonymousRankAction | parent::anonymousRankEntry($entryId, null, $rank) |
| MediaService::anonymousRankAction | parent::anonymousRankEntry($entryId, KalturaEntryType::MEDIA_CLIP, $rank) |
| MixingService::anonymousRankAction | parent::anonymousRankEntry($entryId, KalturaEntryType::MIX, $rank) |

The three public action methods accept entryId/rank. BaseEntry additionally disables
response caching. The actual protected body loads an entry, verifies type, rejects
rank outside1..5, creates kvote and saves entry/user/rank. Graph outbound name-only
matches included unrelated model methods; **those ambiguous matches are not used
as semantic call evidence**. Literal archive matches are candidate inventory, not
proof that dynamic callers or named dispatch do not exist.

## Dispatcher: prefer explicit class-scoped policy, not a private-property fix

The class declares private `disptacher` but writes public dynamic `dispatcher` in
the constructor. It later calls that object's dispatch method. Renaming the private
property would change external access and serialized key visibility; prohibited.

Public-declaration comparison preserves external access but adds a default-null
property to fresh objects, changing property_exists, reflection default/declaration
flags and serialized fresh state. It cannot be called exact storage parity.
The attribute comparison adds only AllowDynamicProperties before the real class.
It preserves dynamic-property storage but changes reflected attributes and exempts
**all dynamic properties on this class and descendants**, including future typos.
This deliberately broader class-scoped policy is a proposed compatibility tradeoff,
not a blanket policy. PHP documents [descendant inheritance of this attribute](https://www.php.net/allowdynamicproperties).
No class attribute is added anywhere else in this experiment.

The future dispatcher probe loads each complete real variant separately and tests:
fresh object via reflection, public assignment, serialization round trip, unset/
recreation, unrelated property on same class, real constructor and singleton, plus
an explicitly synthetic descendant solely to expose inherited policy. A separate
real KalturaDispatcher dynamic-property write must still warn: no global suppression.
Native stderr is retained by an error handler returning false.

The real constructor has a small dependency closure: KalturaDispatcher,
requestUtils→infraRequestUtils→kString, and kCurrentContext. The fixture populates
the **real helper's existing requestParams cache**, so its real getRequestParams
returns the controlled array, then the real FrontController constructor executes.
No replacement dispatcher/helper classes are supplied. This does not exercise HTTP
parsing, kConf/preprocessor branches or actual service dispatch; those require the
existing full API HTTP/HTTPS corpus before selection. Array/object state and exact
serialization must be compared per cohort, allowing only explicitly documented
reflection/diagnostic deltas. Constructed behavior does not erase fresh-state deltas.

## Rank: metadata and binding first, functional proof before source change

PHP8.1 [treats an optional-before-required parameter as required even for named arguments](https://www.php.net/manual/en/migration81.incompatible.php).
That suggests removing entryType's default might preserve PHP8.3 binding, but it
is not proof for this application or its metadata generator. No default is removed.

The prepared rank probe loads real full KalturaBaseService/KalturaEntryService,
records ReflectionParameter name/order/isOptional/isDefaultValueAvailable/default/
nullability/type and required count. It attempts only missing-argument paths that
must reject before entry/database access, retaining native errors. It does not
claim successful rank body execution. A dependency Error instead of the expected
ArgumentCountError must be reported as a failed prerequisite, never accepted.

Before authorizing any rank repair, execute real three service actions and actual
rank persistence against an owned fresh fixture using real entryPeer/kvote/kuser:

- all three positional shapes; type null,MEDIA_CLIP,MIX; missing/wrong-type entries;
- rank0,negative,1,5,6 and typed string/numeric inputs permitted by existing dispatch;
- full named parameters, reordered named parameters, omitted entryType/rank,
  unknown/duplicate names; exact error class and required/default metadata;
- no vote on invalid input; one correctly bound vote on valid input; caller cache
  behavior retained; response/doc generator metadata unchanged or explicit delta.

Do not substitute dummy peers that always return an entry or dummy save methods.
Use the existing synthetic API SQL lifecycle, extend only its explicit entry/vote
schema and seeds after review. This needs the shared lab owner release; local
preparation does not invent a backend acceptance gate result.

## Minimal next runtime slots

1. Native83, once AWS owner releases: three isolated dispatcher processes plus
   one unchanged rank metadata/missing-binding process, read-only full class files,
   no network/SQL, runtime/source/harness pre/post snapshots. This can decide storage
   tradeoffs and metadata observations, not rank functional parity.
2. Existing baseline74 with copied83, after rehearsal: real API dispatch/rank and
   persistence corpus. Candidate full exp12 remains PHP8.3-only; historical74 helper
   controls are not whole-artifact74 support.
3. Actual independent CLI review/repeat and then explicit selection decision.

Current local reproduction:

```sh
python3 -m unittest discover -s tools/php83/dispatch-rank -p 'test_*.py' -v
```

No isolated runner/VM staging is executed in this preparation phase. Both repair
families remain open; diagnostic counts24+1 are historical API observations, not
newly removed warnings.

## Actual local review and guard follow-up

OpenCode Muse free executed all six initial tests, exit0, and reviewed the new
repository-local prepared sources/probes without /tmp/VM/archive access. It did
not execute PHP. [Public review](evidence/dispatch-rank/opencode-public.json).
It correctly identified missing successful archive tests and the need to fail
on non-ArgumentCountError binding results. It also highlighted constructor-cache
and unrelated-warning assumptions. Those are now explicitly checked in the probes.
All eleven complete source hashes and selected-manifest SHA are now checked in
addition to the whole ZIP pin; the review's assertion that dependency bytes were
previously entirely unverified overlooked the pinned whole archive, but per-file
guards improve attribution clarity. Twelve local tests now include synthetic full
archive success and hash/dependency/manifest drift negatives. Old reviewed scripts
and source preparations remain separate evidence; no PHP runtime claim follows.

Transitive requires of infraRequestUtils and kString are actual source includes,
not missing mock dependencies. The future runner must bind the preserved relative
source tree. Per-variant process isolation remains a runner prerequisite; the
/audit/probe paths are deliberately virtual sandbox paths, not instructions to
edit probes to bypass repository review constraints.

A separately held, one-line attribute prototype exists at
`patches/php83/held/dispatch-rank/FrontController-dynamic-policy.patch`, with exact
before/after/patch identities. It remains comparison-only and explicitly permits
all dynamic properties on this class and descendants. No default removal/rank
patch, source ZIP selection or deployment is part of this checkpoint.

## Actual native83 primary — latest checkpoint

Coordinator granted four isolated native83 processes after AWS handed off the
exclusive lab. All four exited0; source/runtime identities before/after are exact.
The collector exit2 remains observational, not selection/acceptance.
[Raw primary](evidence/dispatch-rank/native-primary.json),
[consolidated result](evidence/dispatch-rank/native-primary-summary.json).

- Attribute variant preserves serialized bytes in all eight object states,
  including the real cached-request constructor. Public declaration differs in
  seven of eight states (only unset matches), so it is not a parity repair.
- Diagnostics: original7, public3, attribute1. The attribute suppresses unrelated
  future properties on the class and descendant too, explicitly demonstrating
  the policy cost. The real unrelated KalturaDispatcher warning remains visible.
- Real constructor/singleton identity checks are true in every variant. HTTP
  parsing/service dispatch remains untested; its real helper cache branch was used.
- Original rank has three required parameters, no available defaults in Reflection,
  and all five omissions—including named entryId/rank without entryType—throw
  ArgumentCountError. No successful rank body/persistence or rank patch exists.

The second actual OpenCode review executed12 tests successfully but incorrectly
claimed the named omission enters the body on all PHP>=8.0. Its preserved advisory
[report](evidence/dispatch-rank/opencode-followup-public.json) conflates PHP8.0
with the documented8.1 change. The actual native8.3 result above resolves that
claim without hiding it. Its portability concern about warning controls below8.2
is outside this explicitly8.3-only probe; an explicit version guard was added.
Missing-manifest FileNotFoundError remains fail-closed, not a swallowed success.

No independent runtime repeat or PHP74 state comparison has run at this checkpoint.
The class-scoped prototype stays held; no source ZIP selection follows. A brief
PHP74 helper-only comparison and independent native repeat are separately queued;
whole exp12 is never claimed PHP74-compatible.

## Repeat preparation / blocked execution (2026-09-26)

The separately versioned PHP74 helper changes only runtime guard, reflection API
availability and the expected absence of dynamic-property deprecations. It uses
the same full source variants and cached real constructor; it does not claim
whole-exp12 PHP74 compatibility. The native observer now has an explicit
`--reuse-reviewed-stage` option which verifies all exact stage bytes before any
probe; original primary collector bytes remain in
[reviewed-observe-primary.py](evidence/dispatch-rank/reviewed-observe-primary.py).

Actual Claude returned session quota and executed no tests or runtime probes.
Actual OpenCode free executed12 local tests and two separate shell syntax checks;
an initial incorrect unittest module invocation failed and the correct test
working directory then passed. Its later explicit request
`cat /tmp/kaltura-php83-ssh.conf; echo ===; cat /tmp/kaltura-php74-ssh.conf`
was denied by the tool permission boundary. CLI exit0 is **NOT_EXECUTED** for the
runtime repeat and PHP74 comparison. No configs were read, no VM probes ran, and
no alternative tool/path/agent was used to bypass that denial. Both labs were
released. See [public execution evidence](evidence/dispatch-rank/opencode-repeat-public.json)
and [quota result](evidence/dispatch-rank/claude-repeat-public.json).
The operator must resolve this access boundary before the blocked operation can
continue. The prepared runtime helpers remain unexecuted; independent native
repeat, PHP74 state parity and successful rank-body tests remain open.

The historical full-source snapshots intentionally preserve upstream whitespace.
Consequently `git show --check 30c397af` is not clean for those snapshots; they
must not be normalized because their hashes are evidence. A separate check of
new harness and authored Markdown is clean. No global whitespace exemption was
added. Private CLI streams were reduced to public execution/text events; thought
fields and hook history are not part of the committed report.

## Authorized independent native repeat (2026-09-26)

After the operator explicitly authorized audit temporary paths, SSH configuration
access and lab tests, actual Claude completed the four native83 processes in a
new phase. The historical denial above remains intact. Twelve local tests and
shell syntax passed. Each native probe exited0, while the observer intentionally
exited2 (`OBSERVED_NOT_ACCEPTED`). The independent executor's report is
[authorized-claude-public.json](evidence/dispatch-rank/authorized-claude-public.json).

[Canonical typed comparison](evidence/dispatch-rank/authorized-native-comparison.json)
checks exact records (including stdout/stderr), source-file identities and checksum
manifest against the original primary. Source and runtime identities are equal
before/after. The collector hash differs only because the explicit reuse option
was added; output filenames also differ, not probe records. No source or probe
was changed. Claude's caveat about reviewing its own comparison does not replace
the distinction: Codex ran the primary, actual Claude ran this independent repeat.
No rank-body success, application boot, SQL or release acceptance follows.
Native83 was released immediately after the CLI terminated. PHP74 comparison
remains queued pending the other worker's exclusive-lab handoff.

## PHP74 helper comparison completed

After the AWS worker explicitly handed off baseline74, Codex executed the three
real dispatcher variants with the reviewed PHP74-specific helper. Each exited0,
with empty stderr and zero diagnostics; source/runtime snapshots match exactly.
The lab was immediately returned to AWS. The collector remains observation-only
(exit2), and whole-exp12 PHP74 support is not implied.

[Reproducible comparator](evidence/dispatch-rank/compare-authorized.py) verifies
[the stored result](evidence/dispatch-rank/authorized-state-comparison.json):
original74 and attribute74 have identical nine rows; original74 and attribute83
have identical typed state and eight serialized byte strings except exactly
seven direct-class `AllowDynamicProperties` reflection metadata entries. The
synthetic descendant has no own reflection attribute but inherits the exemption.
Attribute83 retains the single unrelated KalturaDispatcher deprecation. Public
property declaration remains only a counterexample, not a selected repair.

The held patch manifest's `NOT_RUNTIME_VALIDATED` status describes its original
preparation phase and is retained as frozen provenance, not current whole-app
acceptance. These newer records add bounded runtime proof without promoting it.
Rank still has only reflection/omission evidence; valid positional/named calls,
real persistence and API behavior need their separately scoped positive contract.

Actual Claude independently ran and reviewed the stored comparator (exit0,
byte-identical output), without another VM execution:
[public review](evidence/dispatch-rank/authorized-state-review-public.json).
Its useful limits are retained: PHP74 `class_attributes=[]` is an explicit
unavailable-API adapter, not native reflection evidence; runtime74 inventory also
includes copied83 libraries not loaded by this probe; executor labels come from
CLI orchestration provenance, not PHP stdout; public-comparison74 is not asserted
as equivalent by the comparator. The review's reference to the final row as
index9 is a numbering slip (nine rows have indices0–8); the exact records and
comparator are authoritative. This does not expand the bounded acceptance scope.
