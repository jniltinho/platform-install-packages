# Trace policy v1 — synthetic matrix repeated, not deployed

Current checkpoint: four native processes and52 lints repeated by actual
OpenCode Muse CLI; exact typed/stdout/stderr repeat,23 local tests. First host
validator failure is retained and classified only for legacy Error wrapping.
Known intrinsic/pre-rendered/extras leakage remains; no whole privacy acceptance.
Broad55-file/runtime/library/INI snapshots match across repeat (not primary).
Both VM slots released; no application installed/configuration changed.
See evidence README/comparison.json for authoritative current outcomes.
The preparation paragraphs below are chronological, not current pending status.

User authorized display-only trace-argument masking and matched lab policy.
Four core targets, never vendor: the three existing log-copy targets plus
KalturaSerializableStream. KalturaLog alert/crit/err now recognize Throwable
before the legacy new Exception conversion; Error objects reach the writer
rather than becoming unsafe strings. Prior exp14 target changes are composed,
not replaced by original sources. Existing frozen helper/pipeline files unchanged.

Writer `_write` copies the event by value and replaces only a Throwable message
with a structural display: class, intrinsic message, code, file/line, every
frame's class/call type/function/location and argument count/type; argument
values become fixed markers without casting objects. Previous chain rendered
oldest first. Existing formatter/filter/priority/event routing remain in place;
filters see the original event before `_write`, as before. Formatting changes
intentionally; actual exception/trace/arguments are not modified. No new instance
properties; writer __sleep/__wakeup unchanged. No generic string regex.

Explicit negative controls: intrinsic messages containing a marker, pre-rendered
trace strings, and Zend extra.message overrides remain leaking observations.
They are NOT PASS/privacy acceptance. Before lab auth, effective logger config
and exercised emitters must be audited. Reject dangerous extra.message, log
filters that render raw objects to external sinks, unexpected writers/formatters,
and observed premature stringify in that exercised flow; do not disable events.
Unrelated arbitrary message sanitization is not claimed or a universal gate.

Nine synthetic pipeline cases currently prepared (Exception/previous/Error x3,
three negative controls, ordinary string), no native execution yet. Original and
policy sources run separately. Source construction uses exact original+exp14 ZIP
pins and strict zero-fuzz/zero-offset incremental and cumulative replays.
Output /tmp/php83-privacy-trace-policy-v1 is local scratch, not deployed.
11 local tests are static/source/replay guards, not PHP tests. Native paired74/
copied83, serialization round-trip/argument-type cases and actual configuration
audit remain next steps; .83 compiler is owned by another worker.

Prior source graph kaltura-rigel-18.20.0-full checked ready, generation
2026-09-25T12:19:00Z; eight relevant logging/FrontController/Dispatcher paths
report no_recorded_issue/metadata_match, best effort only. Exact original core
source and retained full-pipeline observation provide the mechanism evidence;
no global coverage claim. Prior observation commit 8f6d39a0 remains immutable.

## Follow-up preparation r2

Source patch unchanged after independent Codex review. Probe now includes writer
serialization/unserialization and subsequent actual logger write, mixed six
argument types including an explosive __toString object, and a priority filter
rejecting ERR before observer/formatter. Eleven positive/control rows plus
rejected-event control. validate.py checks exact inventory/types/priorities,
original leaks and preserved known-negative leaks. 17 Python tests; PHP still
NOT_EXECUTED. Native configuration/source prepost runner is not ready yet.
An actual Claude review attempt terminated quota exit1, not PASS.

Any future modified lab must be labelled **baseline with approved privacy
overlay**, never untouched published packages. Equal policy on both sides
supports comparability only within its audited scope; no benchmark/full baseline
acceptance or published-artifact changes in this phase.
