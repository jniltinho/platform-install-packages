# Current bounded language-repair cycle — coordinator review

This is ongoing lab work, not application acceptance or release authorization.
The exp10 ZIP remains unchanged with eleven compiler rejections; the four new
held repairs are not yet selected in a new candidate.

## Actual independent execution

- Claude selection: three strict held-patch replays, exact before/after identities;
  no PHP execution in that selection phase.
- Claude ternary repeat: ten local tests and all four real runtime processes;
  147 cases in each positive mode (441 rows), original83 exit255 control.
  Primary and repeat records are byte-identical in every record field, including
  stdout, stderr and source identities. Runtime before/after identities match.
  The only top-level report difference is the newly present test file in the
  glob-derived harness inventory; common tool hashes are identical.
- Cursor initial: ten ternary and fifteen autoload local tests, shell syntax;
  no VM execution. Its broad assurance did not detect the defects below and
  is not accepted as blanket approval.
- Grok: bounded attempt ended124, no execution evidence; not a pass.
- OpenCode initial: exit0 without completed review/execution; two external-source
  read permission rejections. Not a pass and denied operations were not retried.
- OpenCode safe repository-only fallback: eight named local ternary record tests
  and patch hash verification. Two tests requiring external immutable source were
  intentionally not executed. This is OpenCode, not Grok, and not runtime proof.

## Required hardening and retained failures

Coordinator reproduced an accepted duplicate candidate74 record replacing
candidate83 in the first ternary validator. Actual primary and Claude reports do
contain all four distinct modes, so their executions stand, but the validator's
coverage guard was insufficient. Required follow-up: exact mode inventory,
negative tests, explicit harness inventory and exact native diagnostic controls.
Neither Claude nor OpenCode independently identified the duplicate-mode gap.

The hardened validator now rejects duplicated, missing, unknown, extra and reordered
modes and checks exact native diagnostics, stderr hashes and fatal stdout. Its
21 local tests pass, and it revalidates both retained actual runtime reports. The
probe, guest runner, patch and source are unchanged; this is local revalidation,
not a new runtime execution. Actual Cursor follow-up passes all 21 tests and revalidates both reports. It
explicitly identified the remaining oracle limitation: seventeen rows compare
against actual native74 behavior rather than independently fixed goldens. The
first 130 rows have fixed expected values; no all-147 golden claim is made.

Initial autoload runtime evidence has seventeen successful bounded positive
processes. All three full CLI task-list attempts fail with missing `kConf` in the
empty-project fixture, including original74. They are not passed or waived.
The initial collector then crashes on a JSON empty-array/object mismatch during
a fatal control; twenty rows are retained and the three fatal processes are
separately captured. Required follow-up: robust fail-closed report validation,
required loaded-source identities, exact case and callback traces, and a
representative real task-entrypoint fixture. No application stubs are authorized
to hide dependency failures. Superseding reports must preserve these first files.

## Static advisory qualifications

The Symfony CLI candidate appends its closure to an existing SPL queue; it is
first only when the queue starts empty. This intentionally changes the legacy
implicit-autoload behavior when handlers already exist. No universal PHP74 queue
parity is claimed. Disabling SPL registration would produce explicit exceptions
in the HTML Purifier/sfCore guarded paths, but Symfony's direct registration call
would fail with an undefined-function Error, not that same RuntimeException.
Bounded static searches do not prove absence of dynamic callers. Source-only
review does not establish the real CLI, template, ORM or application behavior.

T0-04/T0-05/T0-06 and feasibility, packaging, release and cutover gates remain open.

## Frozen r2 guest / r3 collector independent outcome

Actual Claude CLI completed exit0; its collector command correctly returned1.
The complete `claude-primary.json` is byte-identical to `primary-r3.json`:
20 positive process passes, three original83 expected fatal controls, and three
retained empty-project task-list failures. Before/after runtime identity files
are identical. Actual Cursor ran nineteen local tests and independently
revalidated this same exact 20/3/3 inventory, not a claim of 26 passes.

A separate configured-project full `-T` now executes the real session/config
chain and lists identical 38 tasks and six aliases on all three positive
runtime/source variants. It loads 37 real files from source trees containing
1,630 files per variant. Listing/registration is not execution of those tasks.
Synthetic local configuration is explicit; the actual framework classes are not
replaced. Private networking/socket denial establishes isolation; absence of
warnings alone would not prove absence of attempted or suppressed I/O.

Claude identified still-unpinned diagnostic message hashes and fatal line numbers
in the collector; exact actual repeat diagnostics agree, but these validator
contracts require additional hardening. Composition tests for later handlers,
duplicate-class winners and exception propagation remain separately pending.
No broader autoload or application acceptance is inferred from the current matrix.

## Composition independent-repeat quota observation

The first actual Claude composition attempt ended exit1 before executing any
command, reporting its session quota and an18:20 America/Sao_Paulo reset. No
composition repeat/runtime snapshot outputs were created. That attempt is
NOT_EXECUTED, not a failed application test or a pass. Its raw public result is
retained in `composition-claude-review.json`; a later retry must have separately
named CLI evidence and cannot overwrite this result. Independent Cursor local
review continues separately. This temporary CLI limit does not block other
approved local preparation or establish a full-goal blocking condition.

## Checkpoint integrity note

The final staged whitespace check reports only retained raw Cursor text formatting
(two report files) and the three exact unified patch files. Raw report whitespace
and unified-diff context (including upstream tabs/trailing whitespace) are
preserved because their recorded hashes and strict replay evidence must not be
silently changed. The scoped check excluding only those five named files passes;
this is an explicit evidence-preservation exception, not a warning-free claim.
