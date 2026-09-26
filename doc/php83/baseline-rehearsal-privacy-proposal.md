# Baseline API logging privacy: versioned lab policy

## Current phase: authorized trace-display policy repeated in synthetic lab

The user explicitly authorized checksums and the narrow trace-argument display
policy. `privacy/trace-policy-v1` now prepares four core targets against the
original and exp14 pinned archives. This does not alter published artifacts or
installed applications. Actual OpenCode Muse reviewed the initial trace source
and executed 17 local tests; Claude's attempt hit quota and is not a pass.
Follow-up adds exact safe trace-projection checks and typed validators:23
local tests pass. Four native processes and52 lints completed and were repeated
independently by actual OpenCode Muse, with exact stdout/stderr/typed reports.
The first host-validator failure on legacy Error wrapping remains preserved;
reviewed classification excludes no policy cases. Original74 and exp14/copied83
were each tested without/with the overlay. No installed application changed.
Separate broad55-file/runtime/library/INI identities match across the repeat;
no retroactive broad identity claim is made for the primary.

Only values of trace arguments are replaced; intrinsic messages and previous
exceptions remain diagnostic evidence. Intrinsic/pre-rendered/extra.message leak
controls are retained explicitly. Effective logger configuration and the real
synthetic lab flow must close their exercised leak paths before nonce USER/auth.
Future application of this approved overlay creates a **modified lab baseline**,
not an untouched published installation; both sides need the same audited policy.
No benchmark or whole application/privacy acceptance is granted by these tests.

## Historical result before authorization: helpers pass, trace privacy blocked

The reviewed r5 log-copy preparation has now run in isolated native PHP7.4.33
and PHP8.3.6 stages: **two probes and six lints per runtime**, all exit0 with
empty stderr (four probes/twelve lints total). Original/control and policy source
pins and PHP identities matched before/after; installed applications were not
modified. Both typed comparisons report SYNTHETIC_LOG_COPY_CONTRACT_MATCH but
**BLOCKED_SENSITIVE_TRACE_OBSERVED**, with full_privacy_accepted=false and
application_accepted=false. The actual Zend Simple formatter retains the first
15 characters of a synthetic secret in exception arguments, although not the
complete marker. Diagnostic text and frames remain present. This is a retained
failure, not permission to run valid USER authentication or upload.

Authoritative receipts: evidence/baseline-rehearsal/privacy/native{74,83}-
{stage,primary,comparison,cleanup}.json, primary.exit and primary.stderr.
Actual Cursor follow-up and OpenCode native83 review accepted synthetic-only
execution; the intervening Claude follow-up timed out and is not a pass.
A separate [trace-display proposal](baseline-rehearsal-trace-proposal.md) is
pending authorization/review. No logging configuration, level, application file,
selected manifest or integrated ZIP has changed. Both VM slots were released.

The sections below describe chronological preparation phases; earlier pending
native statements and public-only object views are superseded by r5/current
results, not claims about the present state.

## Historical proposed narrow privacy policy — not selected or applied

Goal: redact sensitive **log copies**, retaining actual request/dispatch values,
API outputs, error objects, levels, events and unrelated diagnostic fields.
Do not lower DEBUG globally, turn off analytics, erase historical logs or claim
that the resulting lab is the untouched published installation.

Confirmed original-source points (graph generation2026-09-25T12:19:00Z, exact
path coverage no_recorded_issue/metadata_match; best effort plus direct reads):

1. api_v3/lib/KalturaFrontController.php:96 prints raw request params. Redact
   explicitly named sensitive fields in a separate display copy, including colon
   qualified multirequest keys and nested arrays, before print_r. Decode transport
   encoding only through the already native request parser; do not rewrite the
   actual request or indiscriminately substitute arbitrary message strings.
2. api_v3/lib/KalturaDispatcher.php:97–98 prints deserialized positional args.
   KalturaRequestDeserializer.php:57–195 appends args in actionParams order; use
   that parameter-name metadata to mask corresponding display slots (secret/ks
   and explicitly enumerated authentication fields). Do not mutate arguments,
   reflected metadata or passed service objects, and fail visibly if mapping is
   ambiguous. Both points emitted the real invalid canary in r2.
3. KalturaFrontController.php:66–84 analytics request_end copies the live KS into
   its ks field. Mask only that copy. Preserve the field, order, event and type:
   null stays null; a string KS becomes a constant string marker. Other fields
   remain byte/type-equivalent. This intentionally removes correlation by KS;
   external analytics consumer equivalence is NOT established or promised.
4. Exception paths in getExceptionObject pass original exception objects to
   KalturaLog::err/alert/crit. Keep those objects/dispatch behavior unchanged.
   Native synthetic exception/trace controls must check full values and known
   truncated/encoded forms before claiming the new log policy permits live auth.
   No generic exception replacement or arbitrary-string rewrite is proposed.
   If traces remain sensitive, stop and separately review that emitter rather
   than hiding diagnostics or declaring the three-site proposal sufficient.

Bounded additional reads: KalturaLog.php passes log messages to its configured
logger; SessionService.startAction delegates to kSessionUtils.startKSession;
kCurrentContext.initKsPartnerUser stores the supplied KS and can place it in
invalid-KS exception data. kSessionUtils.fromSecureString delegates parseKS;
its logError callback forwards errors. These are follow-up risk paths, not a
repository-wide absence audit. Other endpoints/writers/plugins are untested.

Required paired native controls after local patch/harness review and explicit
approval: original leakage control; invalid secret; valid USER secret+new KS;
failed ADMIN escalation; invalid KS; nested/multirequest and POST encodings;
exception messages/traces including prefixes; non-sensitive field/type equality;
request/argument identity and API-result equality; same logging levels/events;
analytics string/null KS schema and documented correlation change. Preserve all
original failures. No real secret, KS, response body or raw log leaves the guest.

Candidate composition warning: exp12 already changes KalturaLog.php for null
analytics and KalturaFrontController.php for nullable user IDs. Any subsequent
source repair must compose with those bytes, replace each target once, preserve
prior fixes, and use the same privacy policy on the original7.4 lab. No manifest,
ZIP, patch selection, application deployment or config change occurs in this
checkpoint. The actual patch/native harness remains the next reviewed step once
policy is approved; this proposal is not a completed privacy repair.

## Local prepared implementation r3 (no application)

Coordinator reopened preparation after access was confirmed. This is not blanket
approval to rewrite logging or deploy. Baseline74 and native83 belong to other
workers until explicit handoff. No new guest execution occurred in this phase.

`tools/php83/baseline-rehearsal/privacy/prepare.py` reads and verifies the original
and exp12 ZIP bytes, prepares three source targets for each policy variant, and
strictly replays six incremental plus six original-to-cumulative patches (no
fuzz/offsets). It never makes an integrated ZIP or selects a patch manifest.
The two existing exp12 changes (null analytics/null user) are preserved. Evidence
is under `evidence/baseline-rehearsal/privacy`; prepared source trees are private
local scratch `/tmp/php83-baseline-privacy-r3`, not installed application files.

The helper masks exact authentication field names (case-insensitive, last colon
component): secret/adminSecret/ks/password/oldPassword/newPassword/token/
uploadTokenId. Raw parameters and positional metadata-bound argument values get
separate display copies. Unknown ordinary strings are not replaced. Nested arrays
are copied, with a visible depth-limit marker; mapping mismatches yield a visible
log-view marker and do not throw or change the actual dispatch arguments.

**Additional diagnostic representation tradeoff:** DTO/object log values become
class-tagged arrays of public properties, allowing resource.token to be masked
without clone/constructors/magic methods/serialization or modifying the original
object. Non-public properties are omitted, explicitly, not claimed preserved.
This changes DEBUG object representation (not API parameters), and needs review
before selection. Scalar/array non-sensitive fields retain values/types/order;
analytics retains its event, level and field order, with null→null and string KS→
constant string marker. Correlation by KS is intentionally lost, not universally
consumer-equivalent. No exception object or exception logger call is changed.

`probe.php` is synthetic, non-bootstrap/no DB/no HTTP/no credentials. It loads the
actual full KalturaLog and KalturaFrontController class files, tests helpers and
actual onRequestEnd, and observes exception identity/priority and native trace
full/prefix leakage. It does NOT execute the full dispatcher or real API; that
remains an authorized native follow-up. Original variants must show the known
unmasked controls. The trace observation can block privacy acceptance even if
helper tests pass; the output always keeps privacy_accepted=false. It does not
claim coverage of arbitrary encoded sensitive values under unrelated fields.

Twelve local Python preparation tests pass after preserving one initial test
failure (root-level replay fixture mkdir collision, fixed with exist_ok). These
are strict replay/source guards, not PHP execution. No host PHP executable exists;
PHP lint/native probe and real log privacy await independent review and VM slot.

### Follow-up r5 changes after actual Claude review (still not applied)

Actual Claude executed12+63 local tests, verified all source/patch pins and exp12
composition, and identified real gaps. Follow-up now has21 passing local tests,
including real pinned-ZIP end-to-end preparation and a typed native-report
comparator. tokenHash/hashKey/cmsPassword/otp are added as explicit sensitive
names. Empty KS remains empty rather than becoming a marker.

The r3 public-only object view is **superseded**: r5 reads `(array)$object`, without
cloning/getters/hooks, and uses class/visibility-tagged log properties. Protected
TypedArray storage and private nonsensitive values are retained in this view;
authentication-named fields are masked recursively. This still changes DEBUG
object representation intentionally, not actual objects. It is not arbitrary
message substitution and does not claim every application-specific secret name.

The synthetic probe now sends the original exception object through the actual
unmodified Zend_Log_Formatter_Simple/Interface source, not only a cast. It checks
that diagnostics/frame names survive and records full/prefix leakage under
explicit exception_ignore_args=0. No exception source/log behavior was repaired
by this patch. A positive trace observation blocks privacy acceptance even when
all copy/masking tests pass. Original analytics KS is now positively matched, and
null/empty/string behavior plus unrelated fields are compared explicitly.

The reviewed execution plan is only two PHP7.4 CLI cases plus source lint in a
fresh root-owned/read-only synthetic stage under PrivateNetwork, PrivateTmp,
ProtectSystem=strict, unprivileged vagrant and NoNewPrivileges. Source/archive/
PHP pins and JSON-module identity are recorded before/after. display_errors is
stderr, with diagnostics retained. No bootstrap, API, SQL, credentials, installed
application replacement or benchmark is part of this synthetic stage. Native83
and real USER/upload rehearsal still require their own released slot and gates.
