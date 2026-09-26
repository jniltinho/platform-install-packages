# XML lifecycle repair — held prototype observations

No application patch selected and no change to exp12. The held candidate now meets
**PASS_BOUNDED_HELD_CONTRACT_R2**: 38 native PHP8.3 process observations were
independently repeated by actual Claude, with exact source/runtime identities.
The original report remains **36 accepted + 2 expectation FAIL**. Two additional
instrumented processes establish that both unchanged and candidate native SOAP
wrap the resolver's RuntimeException in a SoapFault with no previous exception.
Only the versioned expectation changed; product bytes and old reports did not.

The [reconciliation](evidence/xml-lifecycle-fix/reconciliation-r2.json) checks all
38 records, complete diagnostic inventories, exact raw stderr, source hashes and
six unchanged runtime snapshots. Actual Claude independently ran 23 offline
guard tests and the reconciliation (both exit 0, byte-identical output), then
[reviewed the contract](evidence/xml-lifecycle-fix/claude-reconcile-review.json)
with no blocker. These tests are not additional native executions. No diagnostic
is suppressed or fabricated; handler-only SOAP warnings are explicitly required.
Both labs were released. This is bounded held-source validation, **not full
application acceptance, artifact selection or real network transport testing**.

The candidate changes kConf and kSoapClient and adds one dependency-light helper.
It preserves startup HTTP/HTTPS policy and uses owned deny/predecessor callbacks,
opaque LIFO scope tokens and finally cleanup. The new file is HELD and requires
future artifact-builder support; no ZIP was built or updated by this work.
The held manifest status describes its initial preparation, not native acceptance. Original strict failures remain committed in lifecycle checkpoint
`1a88b5dc`; its 74/83 independent repeats are unchanged.

## First gate: two native diagnostic channels

`tools/php83/xml-lifecycle-fix/observation_contract.py` is a versioned local
interpretation of captured records, not a rewrite or rerun. It retains every old
functional assertion. Every handler diagnostic must also occur in native stderr,
except an **exact bounded list** matching runtime, case, original/exp11 path,
source line, phase, integer severity, message and multiplicity:

- missing WSDL: handler-only E_WARNING at kSoapClient.php:8; runtime7.4 uses the
  native SoapClient::SoapClient prefix, runtime8.3 uses ::__construct.
- nested construction: handler-only E_NOTICE for http/https restore, lines27/28.

The exact exceptions must be captured and absent from stderr; removing a handler
record, changing its fields, adding duplicates, dropping other native stderr or
changing its observed channel fails. No synthetic stderr is appended. Native
errors are neither suppressed nor fabricated. These facts were observed twice
per runtime by actual independent execution, not inferred from return codes.
Mechanism inside ext/soap remains unproven; this records both observed channels.

Fifteen local tests include replay of44 real primary rows and adversarial mutations.
Actual Claude found weaknesses in the initial stderr-present channel: dropped or
duplicate handler entries, extra stderr, substring/line mutations and non-string
stderr. That rejected first revision remains preserved. The corrected contract
now pins the complete ordered handler inventory AND exact raw native stderr for
each baseline case, with exact native runtime and probe identity. The manifest
references byte-identical primary/independent repeat reports. It is an observed
baseline ledger, not invented candidate expectations or a claim that observed
behavior is secure. Any candidate must have separately reasoned contracts.
This does not approve a future candidate's different diagnostic inventory.

## Source and native API scope

The graph is ready at generation2026-09-25T12:19:00Z; both exact source paths have
no recorded issue and metadata-match freshness. Class trace has zero recorded
call edges, which does not mean no calls: full pinned ZIP source directly shows
parent calls, loader toggles and wrapper mutation. No exhaustive callgraph claim.

The [official getter manual](https://www.php.net/manual/en/function.libxml-get-external-entity-loader.php)
documents the getter starting in8.2 and returning the previous callback or null.
The [setter manual](https://www.php.net/manual/en/function.libxml-set-external-entity-loader.php)
documents a callback returning null as denial. Its currently displayed return
type `true` is an8.5 change; the8.3 implementation must not assume that signature.
Existing native8.3 fixture records observe getter availability and exact callback
identity. Native7.4 remains a separate unchanged control; no getter fallback that
cannot preserve prior callbacks is silently invented.

## Held repair design to review next

- kConf installs an identifiable owned deny callback instead of the deprecated
  global disable call. kSoapClient may open only that owned denial temporarily.
- A foreign custom callback must remain active; setting null blindly would
  bypass restrictions and is rejected as a design.
- Each SOAP entry stores its exact previous callback and owned wrapper changes,
  restoring them in finally on success, SoapFault and nested exceptions.
- Nested calls must leave the outer state intact. Already registered HTTP/HTTPS
  wrappers must not be replaced; only wrappers restored by this scope are removed.
- A small shared helper or identifiable named callback is needed to distinguish
  owned denial from foreign policy; no implementation chosen yet.
- Test success/malformed/missing/invalid method, nested construction and calls,
  custom allow/deny/throwing callbacks, custom wrappers and cleanup failures.
  Real network/backend acceptance and arbitrary concurrent fibers remain outside
  the prior fixture; do not claim coverage without additional isolated controls.

Changing existing cleanup/nesting bugs is an intentional improvement, not
baseline parity. The old __soapCall drops options/headers; repairing that is a
separate decision and must not slip into a supposedly minimal lifecycle patch.

## Two minimal ownership designs (proposal; neither implemented)

### A — shared independent helper class (recommended)

Add one dependency-light helper file under infra/general, explicitly required by
kConf and kSoapClient. It defines no application/config/cache dependencies.
The helper retains the exact pre-kConf callable (including null) and a private
dedicated deny Closure that it creates itself. kConf installation sets that
owned closure as the global loader, blocking all parsers outside SOAP while
retaining the original policy for delegated SOAP loading.

At SOAP entry, inspect the getter. Only when it returns the exact owned closure
does the helper replace it temporarily with its saved predecessor. A foreign
current callback is left active, not set to null. Null is delegated only when
the preserved predecessor was genuinely null, not as a shortcut around a custom
restrictive callback. Each entry retains its previous callback and exact wrapper
changes in an explicit scope token. The finally exit restores that callback and
removes only wrappers this scope restored; nested tokens must be LIFO.

Repeated initialization must not overwrite the original predecessor with our
owned deny closure. Existing custom HTTP wrappers must not be replaced. If a
custom callback is installed after kConf, that external mutation is not secretly
overridden at SOAP entry; its own policy stays active. Restore behavior if a
third party changes global state *inside* a scope requires a documented ownership
decision and test, not blind claims of concurrency safety.

Benefits: private state, explicit initialization and no assumptions that kConf
has already loaded when kSoapClient is used standalone. Costs: one additional
application file and two explicit require_once edges; autoload/package inventory
must include it. Native getters/setters and callable identity must be tested for
closures, named functions, static methods and invokable objects. No hidden
PHP7.4 branch can pretend to recover a previous callable absent the getter.

### B — kConf-defined prefixed policy functions with private static registry

Keep changes within the two existing files by defining narrowly prefixed policy
functions at top level of kConf. A private static registry in a single function
retains the owned Closure, predecessor and token stack. kSoapClient detects the
policy function without autoload; if absent, standalone SOAP preserves its
current external callback and wrappers rather than trying to open a nonexistent
application-owned denial. The same getter/owned-closure/token rules apply.

Benefits: no added helper file or include edge. Risks: new global function API,
name collisions and mutable process-global policy state exposed through a
function protocol; more difficult testing and maintenance than a small helper.
Top-level function availability and bootstrap ordering must be demonstrated,
not assumed from class ordering. No duplicated independent registries in both
files, no arbitrary reflection/Closure identity guessing and no hidden global
variable containing a privileged permissive callback.

### Shared risks and required controls

Neither design isolates unrelated parser calls occurring reentrantly during an
active SOAP scope: native loader/wrapper policy is process/request-global.
Fibers/overlapping lifetimes are not proven safe by ordinary nested LIFO tests.
An invalid token or non-LIFO close must fail closed and preserve the primary
exception, not permanently leave permissive state. Cleanup failure injection
and custom wrappers are therefore required before acceptance.

Tests must show an original restrictive callback denying a WSDL remains
restrictive through SOAP, a permissive synthetic callback still serves only its
whitelisted local resources, startup blocks the marker even with such a prior
callback, and original callback identity is restored after success/fault/nesting.
SOAP options/headers forwarding is explicitly not bundled into this repair.

The coordinator prefers option A. A new file is allowed but must be explicitly
supported by the artifact builder and inventory counts in a future artifact;
exp12 is unchanged. Candidate execution targets traditional synchronous PHP,
not arbitrary interleaved fibers or universal isolation of global parser policy.
Using existing kXml solely to avoid one new file is not justified without a
separate dependency audit; option C is not selected.

### Wrapper guarantee boundary agreed before implementation

Retain kConf's existing startup HTTP/HTTPS unregister security policy. SOAP
preserves wrappers registered at **scope entry**, including custom registrations
after bootstrap, and removes only scope-owned restores. PHP's wrapper listing
exposes protocol names, not an API to recover an unregistered custom wrapper's
class. Pre-bootstrap custom registration lost by original kConf is therefore an
existing limitation, not something this patch claims to repair. Removing startup
unregister calls merely to claim broad preservation would change security policy
and is not authorized. Required cases: entry-present custom wrapper, entry-absent
built-in restore, nested success/fault, callback failure and outer final cleanup.

Independent correction/design review completed: actual Claude exit0, 15 tests0,
all five diagnostic-channel gaps closed. It recommends A but requires resolution
of LIFO handling, wrapper ownership, native callable forms, initialization/order
and third-party mutations before accepting a patch. At that review phase no source patch had been created; the later held prototype
and its separate review are described above.

A native8.3 capability prerequisite is prepared at
`tools/php83/xml-lifecycle-fix/capabilities.php`: it saves/restores the actual
loader and records getter/setter identity for Closure, named function, static
array callable, invokable object and null. It neither loads application classes
nor parses external resources. It subsequently ran once under granted native83 ownership: all five callable
forms retained strict identity, setters returned boolean true, original callback
was restored, and diagnostics were empty. Source/runtime identities and actual
results are retained; this proves API identity only, not SOAP or parser behavior.

### Proposed invariants for A (to adjudicate before source changes)

1. Installation is explicit and idempotent. The first predecessor is retained;
   a second install while the current loader is the owned closure is a no-op.
   Standalone kSoapClient without installation must not invent a prior policy.
2. Tokens are opaque objects owned by a private LIFO registry, not caller-provided
   arrays. Entry records the current callable and restores missing wrappers only;
   partial entry failure rolls back already-owned changes before propagation.
3. Normal close restores the exact previous callable first, then removes only
   this token's restored wrapper names. An inner close restores the outer policy,
   not the application startup denial prematurely.
4. Token mismatch/non-LIFO close must never restore a permissive guessed state.
   Proposed action is owned deny plus a visible logic failure; preserving the
   original SoapFault versus representing a cleanup failure needs an explicit
   exception-chain contract rather than silently losing either error.
5. A foreign callback changed *during* a scope can be detected by the getter.
   Proposed behavior is fail-closed denial and a visible ownership error rather
   than restoring a previously permissive callable over a new restriction.
   This is distinct from an unchanged foreign callback present at scope entry,
   which remains active and is preserved normally.
6. PHP cannot identify a custom wrapper class replaced under the same scheme
   mid-scope. Such uncontrolled mutation is outside this traditional synchronous
   ownership contract and must not be advertised as preserved. Entry-present
   custom wrappers and ordinary nested scopes are the required supported cases.

Items4/5 are proposed behavior changes requiring explicit coordinator and
independent review approval; they are not implementation or native test claims.

## Historical primary phase and subsequent causal resolution

The actual helper review passed7 patch/static tests and15 observation tests;
actual final harness review passed12 guard tests and shell syntax checks. These
local tests are not native proof. The native matrix is13 real-source cases for
baseline and candidate plus12 actual-helper cases. All helper cases passed,
including foreign restrictive callback, custom wrapper at scope entry, nesting,
non-LIFO rejection, idempotent installation and preservation of a synthetic
SoapFault as the prior exception on cleanup failure. Global runtime snapshots
(39 objects) are unchanged; private SOAP/provider hashes are checked separately
in the readonly stage wrapper.

The first fixture captured only exception class/message, leaving a causal gap.
That limitation was subsequently resolved by the separately reviewed and executed
`behavior-chain.php` instrumentation; the helper-only primary-chain control was
not substituted for full-source evidence.

The observed full-source candidate produced37 handler diagnostics and zero
E_DEPRECATED events versus114 diagnostics/77 deprecations in the baseline13-case
corpus. This is a bounded diagnostic observation, not a performance benchmark or
application-wide deprecation claim. Two candidate handler-only SOAP diagnostics
remain captured and are required by the separately reviewed complete candidate
diagnostic contract; no native stderr was synthesized.

The instrumentation-only follow-up ran through actual Claude: two process exits
0, exact unchanged source/runtime pins, and identical original/candidate chains.
The thrown RuntimeException message is `SYNTHETIC_LOADER_FAILURE`; native SOAP
returns only `SoapFault("SOAP-ERROR: Parsing WSDL: Couldn't load from 'file:///audit/probe/fixtures/good.wsdl'")`.
Its previous exception is null and the bounded chain is not truncated. This
native conversion is not a new helper regression. The separate helper cleanup
failure control preserves its primary SoapFault as the previous exception.

### Remaining gates and limitations

- Add-file artifact builder support, full built-artifact regression, installed
  application/backend acceptance and release/package approvals remain open.
- Traditional synchronous scopes only; foreign same-scheme wrapper mutation
  within a scope and fiber/global isolation are not accepted.
- Real HTTP transport is not covered: the authorized fixture overrides only
  `__doRequest` with a fixed synthetic envelope.
- Offline replay currently depends on the pinned preparation manifest in `/tmp`;
  the executed manifest identity and preparation evidence are retained. Reviewer
  notes untested file-level guard mutations; no exhaustive mutation claim.
- The held manifest's preparation status is historical and frozen, not the
  current bounded contract verdict.

### Patch formatting preservation

GNU patch reconstruction and output hashes retain historical source CRLF bytes.
`kSoapClient.php.patch` therefore has whitespace-check findings; unified patch
context also contains required prefix spaces. The executed frozen
`collect-native.py:66` also retains one whitespace-only line; it was not silently
changed after native proof. The separate
[format check](evidence/xml-lifecycle-fix/format-check.json) retains commands,
exits and findings. No `.gitattributes` suppression was added and no global clean
whitespace claim is made. Reproducible `candidate-tree/` output is ignored, not
committed; canonical helper, patch bytes, builder and identity metadata remain.
