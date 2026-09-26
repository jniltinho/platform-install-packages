# Baseline API protocol v1 — preparation only

**No VM/AIO calls or measured benchmark rounds.** This is a new baseline74-only
POST/auth/typed-response harness. Source/provider attestation, real fixture
freezing, guest log privacy and coordinator lab reservation remain prerequisites.
No baseline acceptance is inferred from local tests.

## Fixed workload and denominator

One round plans exactly 100 calls: 34 session.start USER sessions (type 0), then 33
media.list, then 33 media.get. Last session.start must succeed before media calls;
if it fails, all 66 dependent rows remain explicit NOT_EXECUTED_DEPENDENCY. Any
failure invalidates the whole round, including an earlier failed session followed
by a later successful one. There are no automatic retries and no smaller successful
denominator. Every planned row persists (planned/attempted/passed/failed/
not_executed). A worker-cleanup failure aborts further requests and retains the
remaining slots as NOT_EXECUTED_ABORT, rather than continuing with a live worker.

Credentials are supplied only by an absolute private **guest file path**: regular
file, owner is effective UID, exact 0600 and one hard link, immediately inside an
owned 0700 directory. Directory components are opened with dir_fd/O_NOFOLLOW,
not merely checked before following a path; nonregular/FIFO inputs are rejected
without blocking. All credential/fixture/CA reads are bounded.
The contents contain partner_id (>0), synthetic user_id and user secret. The
secret has no CLI flag/default/environment fallback and is omitted from repr,
reports, exception text and URL. Session tokens remain private memory only.
All auth data goes into application/x-www-form-urlencoded POST bodies; the sole
URL is fixed /api_v3/index.php without a query. Admin tokens are not requested.

The fixture is independently hashed before/after execution and pins one existing
READY video entry, explicit positive media.get entry_version (never latest/-1),
source_media_sha256, pageSize/pageIndex 1, idEqual and +createdAt ordering. Actual
upload-to-source-hash correspondence/asset immutability still requires provider
attestation before the native run; a declared hash is not proof of media bytes. Its exact
five-field media projection is objectType/id/partnerId/status/mediaType; numeric
wire types and totalCount type are frozen by the fixture, not coerced. Extra
volatile media fields are not part of this projection. A wrong entry, partner,
state, type, API exception, malformed JSON, duplicate key, nonfinite number,
HTML200 or oversized response fails. Untimed real74 fixture observation and
review are required before freezing; the synthetic local test fixture is not
asserted to be a live baseline response.

## Timing and transport

The adapter imports the separately reviewed deadline executor and unchanged
fixed-origin client. Public transport permits exact Origin .74 only; no DNS,
.20/.83, test-subclass, proxy, redirect or default-public-CA fallback. HTTPS needs
the pinned explicit CA. Response is bounded at 1 MiB and private IPC at 2 MiB. Spawn
carries parameters privately; only generic error state crosses failed requests.

Child HTTP timing starts immediately before opener.open and ends after the full
bounded body and response close. It includes TCP/TLS/request/response, but excludes
spawn, request encoding, CA context setup and JSON decoding. Parent timing spans
spawn/IPC/body decoding; its overhead relative to child HTTP is recorded separately.
Attempt wall time additionally includes response contract validation. Transport
failures retain attempt wall time with unavailable child/parent timing null;
they are never dropped from planned 100 or advertised as successful samples.
Contract failures after a transport success retain their child/parent times with
status FAIL; they are not successful timing samples. No success-only statistic
can make a failed round eligible.

No medians/p95 or performance claims are produced here. The runner identifies
warmup 1–2 or measured 1–5; the coordinator still owns the complete 2+5 round schedule,
HTTP/HTTPS ordering, runtime/OS attestation, cache policy, worker idleness and
endpoint-stratified statistics. Upload/READY/HLS/browser and recovery are separate
unimplemented workload gates, not waived.

## Source grounding

Graph ready 231336 nodes/800641 edges, generation2026-09-25T12:19:00Z. Exact coverage
for MediaService.php, KalturaJsonSerializer.php, KalturaSerializer.php and the
three media/playable/base order enums: no_recorded_issue/metadata_match. Direct
immutable original-source reads confirm media.get entryId/version, media.list
filter/pager/KalturaMediaListResponse and inherited +createdAt ordering. JSON
serializer emits objectType, preserves scalar representations and removes nulls.
Clean coverage is best effort, not complete application proof.

Legacy deb/noble/sanity.sh was read only. Its insecure .20/default secrets,
curl -L and secret-bearing query strings/argv are deliberately NOT reused.
Existing api-http-client.py provides session.start USER/type0 + format1 precedent,
not a substitute for installed-AIO runtime validation.

Run local tests:
    python3 -m unittest discover -s tools/php83/baseline-api -p 'test_*.py' -v

No runner VM command is executed during preparation. Future native execution must
be on hostname kaltura-php74-baseline, with reviewed fixture SHA, credential path,
transport/port and explicit CA when HTTPS. Reports contain no raw API bodies,
tokens or secrets. Guest application/server log configuration must independently
be checked before real credentials are used; harness privacy is not proof that
the application never logs request bodies.

## Review and evidence identities

Initial actual Claude review ran 25 tests and flagged three concrete gaps.
They are repaired: every report records scheme/port/CA hash/hostname/UTC timestamp
and pre/post harness/fixture integrity; a real synthetic loopback spawn→POST→
private-envelope test corroborates timing; worker cleanup failure aborts without
shrinking the100-slot denominator. Post-run identity failure preserves all rows
and makes the round fail instead of discarding observed calls.

Local tests now cover real POST/TLS/redirect and response bounds, secret/token
redaction, native worker packing and .83 rejection, full100-call success and
failure accounting, dependency/cleanup blocks, typed metadata, private file
mode/link/symlink/FIFO/bounds, and fixture version/source pin. All credentials and
certificates used by these tests are synthetic. Actual OpenCode Muse follow-up completed exit 0 and independently ran all 36
tests (3.289 seconds), finding no new blocking implementation defect. This is
local preparation readiness, not baseline acceptance.

The real loopback spawn test substitutes only a test worker so the production
worker never accepts loopback; its production body is separately unit-tested with
a mocked HTTP boundary. Cleanup-failure typing is intentionally coupled to the
frozen deadline helper’s fixed error string. Intermediate credential-path
directories are symlink-safe via dir_fd but not ownership/mode-validated; only
the immediate parent must be owned 0700. These limits are retained, not waived.
