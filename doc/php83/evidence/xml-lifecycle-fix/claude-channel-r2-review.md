# Claude channel r2 review — correction + design (LOCAL only)
Executor/reviewer: Claude CLI (Opus 5.5). No VM/SSH/PHP/network/credentials/source edits. Not runtime acceptance.

## Correction verdict: PASS (local harness scope)
- `python3 tools/php83/xml-lifecycle-fix/test_observation.py -v` → exit 0, 15/15 OK (claude-channel-r2-tests.*).
- baseline-channels.json: exactly 44 cases = {74,83}×{original,exp11}×11; each has only handler/native_stderr/runtime/probe_sha256; no "candidate" data (scope: "not expectations for modified application").
- All 44 match primary records exactly (handler list, stderr string, runtime, probe sha): 0 mismatches.
- References: primary74 == claude-native74-matrix (sha 755dc2a8…), primary83 == claude-native83-matrix (sha 3e5382b2…), byte-identical (cmp) and equal to recorded sha256.
- Contract now requires `type(stderr) is str`, `stderr == recorded` and typed-exact handler list == recorded ⇒ r1 findings 1–5 closed; each has a dedicated rejecting test (drop stderr-present, unknown stderr, duplicate, truncated, changed line, list stderr).
- Old FAIL semantics unchanged: FAIL_CASES still require SoapFault + wrappers/marker left open (cleanup flaw preserved).
- Residual (LOW, non-blocking): the per-diagnostic `in stderr`/handler-only checks are now subsumed by exact equality (redundant, harmless); reference sha256 is not re-checked by the contract at runtime; golden applies only to unmodified baseline — a patched candidate needs its own separately reviewed expectations.

## Design review (xml-lifecycle-fix.md) — recommend A
Option A (standalone private-state helper) is preferable to B: no global function API, private registry, explicit require from kConf and kSoapClient, works when kSoapClient is used standalone. Required properties confirmed as stated in the doc: dedicated owned deny Closure + saved predecessor (incl. null); SOAP entry delegates only when getter returns *exactly* the owned closure; foreign current callback stays active (no indiscriminate null); finally restores own callback and removes only wrappers this scope restored; startup deny outside SOAP must hold even with a prior permissive callback; native `libxml_get_external_entity_loader()` (8.2+) on 8.3, 7.4 untouched, no emulated getter.

## Blocking design questions (answer before any patch)
1. Nested LIFO: token stack semantics; behavior on non-LIFO/invalid token (fail closed, keep primary exception); inner scope when outer already delegated (getter returns predecessor, not owned closure → must still be recognized as "our delegated state", not foreign).
2. Wrapper ownership: record per-scope which of http/https were actually restored; never unregister a pre-existing custom wrapper; define result if third party changes wrappers inside a scope.
3. Callback identity: identity comparison rule for Closure (===), named string, array [class/obj, method], invokable object — for predecessor restore and for foreign detection; getter return for non-closure callables must be verified natively on 8.3.
4. Init/class ordering: idempotent init (repeat must not save the owned closure as predecessor); who initializes when kSoapClient loads before/without kConf; file inclusion order.
5. Callback mutated inside scope by third party: restore-or-respect decision must be documented and tested.

## Risks / limits
Process-global loader/wrapper policy: traditional synchronous scope only; no fiber, reentrancy or global isolation claim. New helper file needs artifact-builder/inventory support in a future artifact; exp12 unchanged. SOAP options/headers repair stays separate. No patch invented; no runtime/application acceptance.
