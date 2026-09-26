# Exp14 compiler validation — local adapter ready, native pending

The coordinator supplied the independently reproduced final ZIP pin
`459feaf9caf2abe55963dce0cac51b8b593e4ff1b46d2eaf9cb7d5c3f13f62a1`
(91,210,691 bytes). The thin compiler adapter is implemented; 50 unique synthetic
local tests and two separate Bash syntax checks pass. Actual Claude returned a session limit; the OpenCode fallback executed the local
tests but received an explicit permission denial before staging. Native compiler
execution is **NOT_EXECUTED**, not PASS. No alternate executor retried the denied
read/verification. Native83 was released without any VM call in this phase.

The original [plan contract](evidence/exp14-syntax/preparation-contract.json) and
[pending input](evidence/exp14-syntax/pending-input-contract.json) are retained
as historical fail-closed preparation. The current runnable contract is
`tools/php83/exp14-syntax/input-contract.json`. Its exact whole-archive delta was
joined locally: one source modification, embedded manifest modification and one
new rank patch; no blanket metadata exemption. See
[preflight](evidence/exp14-syntax/final-pin-preflight.json).

## Prerequisites and invariants

- Prior exp13 ZIP: `6d0bc4947207e6c5457b7843948d263aa8d5f251480e58cbf9086c0add79a944`.
- Expected source delta: **one existing file only**, KalturaEntryService.php,
  `9495b584…4dd5` → `b48fd2bb…895a`. Full hashes are in the contract. No source
  additions/removals; retain all 75 prior selected targets and one new rank patch.
- Both inventories contain **11,785 PHP-family files** under the same frozen
  case-insensitive `.php`, `.phtml`, `.inc`, `.php5` selection. Other extensions
  remain outside the compiler corpus, not presumed non-executable.
- Audit every ZIP member and every extracted file, not only PHP. Preserve source
  bytes and reject duplicate members, traversal, symlinks, unexpected extraction,
  missing/truncated inventories and any second source delta. Embedded
  `.php83-experimental/` metadata is compared against the exact finite delta
  published by the artifact verifier, never a blanket ignored prefix.
- The same seven historical rejections remain open: six Symfony raw templates
  and RiakCache's reserved Object spelling. They are not waived by process exit0.

## First batch: smallest compiler adapter

Directly read the frozen exp13 scan/core/stage/run/comparator sources; their hashes
are recorded in the preparation contract. Packaging graph coverage does not
cover these migration tools, so no structural graph-absence conclusion is used.
Do not edit these frozen files or duplicate the complete API/regression modules.

Implemented compiler ownership is only `tools/php83/exp14-syntax/`:

1. A small `scan.py` wrapper verifies/imports the immutable exp13 scan and core
   by their recorded hashes. Bind explicit `VARIANTS=('exp13','exp14')`, the exact
   staged helper file set, a new strict contract loader and a paired comparator.
   Reuse the unchanged raw-channel lint, runtime snapshot, inventory and runner
   functions. These assignments are explicit public adapter wiring, not broad
   string replacement or silent mutation of persisted reports. At staging, copy
   only required frozen helper bytes; no edit to historical helper contents.
2. New contract/comparison logic enforces equal pathsets/counts and exactly the
   rank hash pair. No added-source branch is needed. Every subprocess has strict
   integer exit0 or255; timeout/signal/bool status is incomplete. Every diagnostic
   is derived from retained raw stdout/stderr using the frozen rule. No new
   diagnostic normalization is introduced.
3. Thin `stage.py` and `run.sh` bind fresh
   `/home/vagrant/php-candidate-syntax-exp14`, both pinned ZIPs and source trees
   read-only; native83 only, same network/socket prohibition, flags and limits.
   The runtime never includes or executes application entrypoints.
4. Reuse the exp13 stored-report validator/normalizer through the same pinned
   adapter boundary where practical; compare independent reports after dropping
   **only** each row's nonnegative integer `duration_ns`. Keep commands, raw
   stdout/stderr, source hashes, summaries, identities and all diagnostics exact.

The paired run executes **23,570 compiler processes per executor**. Predict, do
not claim, accepted11,778/rejected7 in each artifact. The prior exp13 measurement
is 72 diagnostic files /65 accepted-with-diagnostics; removing the rank notice
suggests 71/64 for exp14. The actual run must determine the exact delta: rank
accepted in both, only its recorded optional-before-required diagnostic removed,
all 11,784 unchanged PHP-family files retain outcomes/diagnostics. Unexpected
changes are failures, not adjustments to the expected count after the fact.

Guard tests before lab work: pending/wrong pin; wrong target hash/path; duplicate,
extra, missing or reordered matrix; missing/truncated records; bool/timeout exit;
source drift; unexpected added/deleted ZIP member; any second source change;
changed immutable helper; raw/parsed diagnostic disagreement; suppressed/new
diagnostic; changed historical reject set; and source/runtime pre/post mismatch.
These contracts are now covered by the 50 unique local tests. The first pinned
discovery executed 69 tests because an imported TestCase was discovered twice;
that report is retained, not counted as 69 distinct cases. Discovery was corrected
without changing compiler behavior. The finite metadata join and actual archive
preflight passed locally; that is not native PHP execution.

### Planned execution order and output locations

Only after final artifact pin + reviewed local adapter + explicit native83 slot:

1. Stage both immutable ZIPs into the fresh exp14 directory; extract/verify and
   make the exact stage root-owned read-only. Refuse existing stage/output files.
2. Codex primary: remote `bash /home/vagrant/php-candidate-syntax-exp14/tools/run.sh`
   → `doc/php83/evidence/exp14-syntax/primary.json`, `.stderr`, `.exit`.
3. Actual Claude independently inspects pins/stage and repeats the same command
   sequentially → `claude-repeat.json`, `.stderr`, `.exit`. Record actual CLI
   execution; timeout/quota/permission failure is NOT_EXECUTED, never approval.
4. Local strict comparator → `comparison.json`; release native83 immediately
   after the last executor terminates. Keep failed phases separately.

These command paths now exist. The local `preflight.py` loads the contract and
validates both complete ZIPs before the first SSH command in the separately
reviewed `stage-primary.sh`. Missing/invalid pins fail before staging. The stage
script is not itself authorization to use a lab.

## Separately owned API4 / CLI48 follow-up (candidate worker)

The candidate worker owns the separate versioned API/CLI adapter against immutable
exp13 tools, with an explicit map original/exp13/exp14 and fresh stage names.
Prefer a small checked staging/render adapter with exact occurrence guards for
the few hard-coded stage/version/pin fields, plus emitted-byte manifests, instead
of a repository-wide replacement or copying both directories wholesale now.
Do not silently generalize old harnesses or change their public evidence.

- API modes: original74 success, original83 expected query-signature fatal,
  exp13 copied83 and exp14 copied83. Preserve auth/HTTP/trusted-HTTPS/rejected-CA
  golden behavior and exact four logical rows. Measure diagnostic delta from
  exp13's one rank-location event toward zero; zero is a prediction, not a pass.
- CLI48: original74 ×2 INI ×6 cases (12), then native83 original/exp13/exp14 ×2
  INI ×6 (36). Keep 44 positives, four expected original83 fatal controls and
  20 typed original74 comparisons. Never claim whole exp14 supports PHP74.
- Carry r2 original-eight-source pre/post authority join and incremental API
  collector/finally cleanup. Preserve the exact owned DB unit, private socket,
  pre-DDL datadir guard, original/current/prior pins and all identity phases.
  CLI timeout may remain INCOMPLETE; do not turn missing post evidence into PASS.
- Base the comparator on final exp13 **r3** productive-output binding, including
  exact phase order, orchestrator hashes, confined report paths and nonnull SHA
  for every productive output. Only stage phases may lack JSON reports.
- No blanket source-hash normalization: if a case exposes the rank source hash,
  allow only that exact case/path old/new pair after checking both ZIPs. All
  unrelated loaded-source hashes and typed values remain exact.
- Preserve API raw-channel limitation: native stderr hash is retained, secret-
  bearing raw log bytes are not exported, and hash differences are not proven
  nonce-only. CLI raw-byte comparison does not confer whole API log equivalence.

Review this API/CLI adapter as one coherent batch, execute with serialized lab
ownership and obtain an actual independent repeat. No need to rerun unchanged
native XML or AWS experiments merely to increment a test count.

## Unchanged families and remaining acceptance

Join exact exp13→exp14 archive identities to the historical XML/AWS source
inventories and report **NOT_RERUN_SOURCE_JOIN_ONLY**. This preserves earlier
evidence and limitations; it is not a new XML/AWS pass or proof of all integrated
behavior. No new XML/AWS harness runs, schema, backend, production change or
release/package claim belongs to this compiler/API plan.

The rank repair's focused proof covers metadata/omissions, with the explicit
PHP74 reflection-default delta, not positive rank persistence. Real USER/media,
privacy rehearsal, Criteria cross-engine representation, AWS rollback, full
application/package/release gates remain distinct and open.

## Preserved independent executor failures — no native execution

Actual Claude exited 1 with session quota reset at 21:20 America/Sao_Paulo:
[public result](evidence/exp14-syntax/claude-prep-public.json). It did not execute
review/tests in that attempt. No repeated Claude retries were made.

The installed free OpenCode model was resolved and one bounded attempt ran. It
read the local adapter, executed two separate Bash parses successfully and ran
50 tests with unittest reporting OK. Its test command piped through `tail`
without pipefail, so the printed shell EXIT is the tail status rather than an
independently captured unittest exit; the visible unittest result is retained.
Author Codex's separate 50-test invocation has the direct exit status 0.

OpenCode then received the explicit tool response:
`The user rejected permission to use this specific tool call.`
The denied compound command included local tool hashes, contract inspection,
output-file listing and reading both sibling artifact SHA256SUMS files. The
**entire exact command and response**, not a guessed narrower denied component,
are preserved in [opencode-public.json](evidence/exp14-syntax/opencode-public.json).
CLI exit 0 does not approve the review or compiler run: there was no final review
verdict, stage or native report. The private stream is retained only by hash in
public evidence; reasoning/hook events are omitted.

The coordinator explicitly stopped covered operations and is obtaining specific
operator confirmation. Neither Codex nor another tool/executor retried the denied
operation or its artifact checksum reads. Earlier local preflight/author tests
predate the denial and remain historical evidence, not permission to proceed.
The compiler remains NOT_EXECUTED; source staging and native83 are untouched.
