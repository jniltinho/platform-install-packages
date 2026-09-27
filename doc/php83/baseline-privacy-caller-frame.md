# Caller attribution after the trace writer overlay

## Bounded result, not a privacy fix

The actual native PHP 8.3 primary and independent actual Claude CLI repeat passed three isolated processes, 18 cases and
36 compiler checks. All three cohorts loaded the same 11-file logger closure
except their explicitly pinned overlay changes. The base is the verified exp14
ZIP, **not an upstream PHP 7.4 execution**. Each process retained zero handler
diagnostics and zero native stderr bytes. No lab application was modified.

The control reproduces a real display regression: with the structural Throwable
writer overlay, actual `LogMethod` reports `KalturaSerializableStream->_write`
for all six cases instead of their useful caller. The repaired pipeline matches
the no-overlay control for string and Exception messages from each of:

- `UsefulEmitter->emit`
- `OtherStream->_write` (same method name, unrelated class)
- `KalturaSerializableStreamSibling->_write` (similar class, not exact match)

The real factory installs a real `LogMethod` event item; the real Simple formatter
and Stream writer render it into a synthetic memory sink. A writer filter observes
the unchanged message object/string, context extra and LogMethod object. The
Throwable state is identical before and after. This does not fix SQL payload
logging or provide whole-application privacy acceptance.

## Minimal source repair

Extend the existing `LogMethod::__toString` frame-skip predicate with exactly
`class === 'KalturaSerializableStream' && function === '_write'`. Do not change
its initial stack index, broad existing Log/log policy, formatter or emitter.
The old writer inherited the vendor `_write`; the overlay adds its own `_write`
which is neither a `Log`-named class nor a `log` method, so the old walker stops
there. This is confirmed by full-class native observations, not inferred only
from a synthetic backtrace array.

Source discovery found `LogMethod` and its method in the full-source graph.
The dynamic trace returned unrelated builtin-name matches and is **not** used as
callgraph evidence. Direct source reads establish the mechanism: KalturaLog
lines 202–232, Simple formatter lines 69–82, vendor writer lines 94–98; the held
writer overlay delegates to `parent::_write`. Exact coverage/freshness is retained
in [coverage.json](evidence/baseline-rehearsal/privacy/caller-frame-v1/coverage.json).
No recorded gap is not a completeness proof.

## Evidence and reuse

- [Preparation](evidence/baseline-rehearsal/privacy/caller-frame-v1/preparation.json):
  exp14 source closure, helper hashes, before/after and patch pins.
- [Primary](evidence/baseline-rehearsal/privacy/caller-frame-v1/primary.json) and
  [typed validation](evidence/baseline-rehearsal/privacy/caller-frame-v1/validation.json).
- Runtime snapshots retain binary/modules/linked libraries and configurations;
  the isolated interpreter uses `-n`, E_ALL, native stderr and no error hiding.
- The `original74-composition.json` and `caller-original74-overlay.patch` target
  the already reviewed upstream-based overlay hash `e73b0743…0778`, producing
  `40e4db57…03dd`. This is a separately verified zero-fuzz patch replay, **not** a
  PHP 7.4 runtime result or authorization to apply it.
- Eight local guard tests are synthetic contract/anchor tests, not the native proof.
  Independent Codex reviewer ran all eight, checked all six frozen tool pins and
  found no blocker before execution. Diagnostics remain observational; primary
  reconciliation separately checks actual twelve lints per cohort.

The source tree and runtime snapshots must remain identical before/after. The
runner refuses an existing stage and cleans only its owned systemd unit. Private
network, read-only host filesystem and synthetic memory-only sink bound runtime
scope. There is no application bootstrap, auth, backend, SQL or real credential.

Actual Claude CLI exited 0 after executing the eight local tests and the native
repeat command; its public command/exit report and fresh repeat artifacts are
retained in `claude-review.json` and `repeat.*`. Raw CLI tool-call streams were not
captured by this JSON-output invocation; the public executor report explicitly
identifies the commands. Byte equality alone is not execution provenance. Both
executions had 36 successful lints, zero diagnostics/stderr, exact typed records
and unchanged sources. The 39-object runtime snapshots are equal before primary,
after primary and after repeat. Both owned units are inactive.

The same-class/different-method case was not exercised; strict pair matching is
source-reviewed. The Throwable corpus here uses Exception, not all Throwable
subtypes. The separately completed PHP 7.4 control is summarized below. Installed
integration and the real media privacy regate remain separate gates.

## Separate upstream74 follow-up

`observe74.py` prepares a distinct immutable stage and reuses the exact frozen
probe and guest algorithm. Six exact-count adaptations change only stage,
host/interpreter and explicit JSON extension pins/pre/post checks. The base ZIP
is the original `58d534…ab28`, not exp14. The eight original guards remain
unchanged; three additional local guards check adapter/source identity and reject
83 reports/runtime drift. `preparation74.json` is separate from the 83 manifest.
This preparation alone is not native74 evidence. Commands, under exclusive lab
ownership after independent review, are `observe74.py primary` then
`observe74.py repeat`; the runner refuses overwrites and verifies all 12 lints per
cohort plus the existing typed caller contract.

### Completed upstream74 phase

The primary and actual Claude CLI repeat each passed three processes, 18 cases
and 36 lints on PHP 7.4.33, with zero captured diagnostics/native stderr. All
primary/repeat bytes and typed records match, all eight tool hashes remain
frozen, and the 55-object runtime snapshots before/after are equal. The actual
Claude commands/results are retained in sanitized `claude74-tools.json` plus its
public `claude74-review.json`; 11 local tests also passed in that execution.

The upstream74 records equal their corresponding exp14/native83 cohort records:
original useful caller, overlay regression, repaired useful caller. Sources are
not claimed identical across runtimes; the manifests explicitly distinguish
originalZIP-based74 from exp14-based83. The original preparation and original83
reconciliation retain their historical NOT_EXECUTED74 state;
`reconciliation74.json` is the later authoritative runtime result.

Both native units are inactive and both labs were released after all commands
terminated. The installed .74 application was never modified by this cycle.
The prepared caller patch may now be composed by the separate application owner
under its own reviewed source joins, rollback and real media privacy gates.
