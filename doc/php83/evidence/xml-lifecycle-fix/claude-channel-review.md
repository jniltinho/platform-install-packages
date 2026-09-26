# Claude channel review — observation_contract.py (LOCAL only)
Executor/reviewer: Claude CLI (Opus 5.5), local only; no SSH/VM/PHP/network; sources unchanged.
Tests: `python3 tools/php83/xml-lifecycle-fix/test_observation.py -v` → exit 0, 9/9 OK (claude-channel-tests.*).
Replay: 44 original records (22×74 private-r2, 22×83 private), 11 cases × 2 variants each.

## Confirmed OK
- Handler-only exception is exact: only construct-missing (1 E_WARNING, line 8, 74=`SoapClient`, 83=`__construct`) and nested-construct (2 E_NOTICE http/https lines 27/28); observed in all 8 relevant rows. Extra/changed line/phase/message/dup handler-only rejected; moving message into stderr rejected; empty stderr rejected; bool severity rejected; runtime mislabel rejected.
- Functional assertions (FAIL cleanup flaw, wrappers, callbacks, transport, nested) still evaluated on all 44 rows; `application_patch_selected` is False — not a source-fix approval.

## Findings (probe: claude-channel-probe.txt) — stderr-present channel is weak
1. HIGH: dropping a stderr-present diagnostic from the handler list is ACCEPTED (no reverse check stderr→handler; no count).
2. HIGH: unknown extra PHP Warning in native stderr ACCEPTED (unknown warnings not inventoried).
3. MED: duplicated stderr-present diagnostic ACCEPTED (multiplicity unchecked outside handler-only).
4. MED: `message in stderr` is substring — a 5-char truncated message ACCEPTED; file/line of stderr-present diagnostics not matched to stderr (line+99 ACCEPTED).
5. LOW: `stderr` type unchecked — a list of messages ACCEPTED (membership instead of substring).
6. LOW: `expected_handler_only` phase/file not variant-checked beyond path prefix; `bool` guards fine elsewhere.
Not verified: whether the old strict contract had the same stderr-side gaps (no time); if yes these are pre-existing, not introduced, but still block "every other warning required" claim.

Verdict: handler-only carve-out is precise and non-blanket; overall channel contract NOT yet sufficient — needs exact per-record stderr diagnostic inventory (count, file, line, severity) both directions + `type(stderr) is str`.
