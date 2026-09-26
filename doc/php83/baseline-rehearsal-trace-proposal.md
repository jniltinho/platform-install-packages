# Exception trace display: narrow pending option

**PROPOSED_NOT_APPLIED.** No application source/configuration changes, valid USER
requests, benchmark, integrated artifact or privacy acceptance. The existing
four native log-copy probes/twelve lints passed their bounded helper contracts;
all retain the synthetic exception-prefix leak and full_privacy_accepted=false.
Coordinator is obtaining explicit authorization for masking argument values in
trace display, not for dropping errors or suppressing diagnostics.

## Exact source path and smallest candidate hook

Graph project kaltura-rigel-18.20.0-full is ready (231336 nodes/800641 edges),
generation2026-09-25T12:19:00Z. Exact coverage for the seven paths below reports
no_recorded_issue/metadata_match; this is best effort, not exhaustive coverage.
Their relevant complete method bodies were read directly from immutable original
server-Rigel-18.20.0 source; writer, factory, formatter and Zend logger files were
read in full. The proposal must still be checked against the actual configuration.

1. infra/log/KalturaLog.php: err/alert/crit retain an existing Exception object
   and call logger->log. Non-Exception inputs are wrapped; an Error converted to
   a string at this boundary can already contain a rendered trace.
2. infra/log/KalturaLogFactory.php: getLogger constructs Zend_Log; getWriter
   maps configured Zend_Log_Writer_Stream to **KalturaSerializableStream** and
   attaches configured Simple formatter and filters. Event extras are added
   separately; no unconditional message concatenation occurs in this factory.
3. vendor/ZendFramework/library/Zend/Log.php: log packs message directly into
   event, then array_merge with extras, invokes filters and writer->write.
   **An extra named message can overwrite it**; that configuration is not yet
   excluded by native evidence. This conditional source path is not proof that
   every installed event reaches the writer as Throwable.
4. vendor/ZendFramework/library/Zend/Log/Writer/Abstract.php: write passes event
   through filter accept calls and then _write. Filters can observe the original
   value; custom behavior/side effects must be inventoried, not assumed absent.
5. infra/log/KalturaSerializableStream.php: currently inherits _write; its own
   state is URL/mode with explicit sleep/wakeup. No existing custom formatter.
6. vendor/ZendFramework/library/Zend/Log/Writer/Stream.php: _write delegates to
   formatter->format(event), then writes the resulting string.
7. vendor/ZendFramework/library/Zend/Log/Formatter/Simple.php: substitutes each
   event value into format; an Exception with __toString is implicitly rendered.
   The native synthetic test of this actual formatter established prefix leakage.

Candidate minimal hook: a core-only KalturaSerializableStream::_write override
that makes a local event copy, renders **only a Throwable message** structurally
with masked argument values, and calls parent::_write. No vendor rewrite,
factory/config edit, new serialized writer state, global INI switch or logger
level change. A string message is NOT regex-rewritten. This hook is a hypothesis
until the complete actual factory/logger/filter/writer pipeline proves it still
receives the original Throwable. If it receives a pre-rendered string, this hook
is insufficient and execution must stop for a narrower earlier-point design.

## Explicit semantic tradeoff and unresolved risks

Keep original exception identity, class, code, message, originating file/line,
frame order, call names and frame file/line. Display placeholders for argument
values, retaining count/types without invoking object conversion or exposing
array keys/contents. Render previous exceptions structurally too. Actual
exceptions, caller arguments, priority, event/filter decisions and unrelated
fields remain unchanged. Log text necessarily changes and arbitrary custom
Exception::__toString additions may not be preserved; inventory/test before any
claim of compatibility. No universal downstream log-parser equivalence.

**Mandatory blockers, not waivers:** intrinsic exception messages can contain
secrets; previous-chain messages can contain secrets; pre-rendered strings and
Errors wrapped by KalturaLog can embed traces; context/extras or other writers
can leak. Masking trace args alone cannot prove overall privacy. Never erase
these diagnostics or broadly replace all strings to manufacture a pass. Preserve
positive leaking controls, actual failure receipts, and historical logs.

## Required executable test plan before deployment

- Freeze original74 and exp12 source bytes plus cumulative three-site helper
  policy, exact new hook and all vendor dependencies; strict no-offset replay.
- Use full actual KalturaLog + factory + Zend_Config + Zend_Log + filters + core
  writer + Simple formatter, not stub logger. Configured php://memory sink;
  verify original Throwable identity at entry and retained real caller object.
- Positive original prefix/full/encoding leak controls and repaired arg-value
  controls, native exception_ignore_args=0 on both PHP versions. Test ERR,
  ALERT, CRIT, ordinary DEBUG strings, configured prefix/context/event extras,
  multiple writers, filter acceptance/rejection, and message-extra collision.
- Cases: no args, mixed scalar/array/object args, nested calls, previous chain,
  custom Exception rendering, intrinsic secret-bearing message, wrapped Error,
  already-rendered trace string. Last cases are explicit privacy-negative
  controls: no success relabeling if the scoped hook cannot protect them.
- Retain exception message/code/type/file/line, every frame and arg count/type;
  real args/objects unchanged, no magic method invocation, sleep/wakeup writer
  behavior unchanged, stream error behavior unchanged. Never print raw traces or
  secrets publicly; compare within guest and emit bounded typed booleans/hashes.
- Independent actual CLI local review/tests, then separately authorized paired
  synthetic native execution with runtime/module/source pre/post pins. Only a
  subsequently reviewed complete policy can permit a real nonce-auth attempt.
- Before real requests: audit actual writer/filter/extras configuration without
  exposing values; use new synthetic credentials and a bounded append-window
  log audit with inode/truncation/rotation controls. History remains unaudited
  for that phase; no log deletion/rotation. The same explicitly changed privacy
  policy must be applied to both labs and no longer called published-intact.

No tests of this new hook have executed and no hook patch is selected here.
