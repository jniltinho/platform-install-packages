# Baseline API logging privacy: proposed policy only

## Proposed narrow privacy policy — not selected or applied

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

