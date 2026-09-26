# Draft PHP7.4 baseline protocol — preparation plan

**Status: PLAN, NOT_EXECUTED.** No VM, package installation, media generation,
benchmark, recovery action or task closure was performed for this document.
Scope: finish the frozen protocol for proposal1.2 / detailed5.5(T0-05), while
preserving related5.22(T5-01), media5.14 and recovery5.23–5.24 gates. Do not run
against `.20`, infer production authorization or describe an experimental PHP83
source probe as a full installed AIO candidate.

## 1. Existing evidence and reuse boundary

| Asset | Ready to reuse | Not established / adaptation needed |
|---|---|---|
| `deb/php74-baseline/Vagrantfile` + `bootstrap.sh` | Exact box `bento/ubuntu-24.04` `202510.26.0`;4vCPU/8192MiB; no shared host folder; `.74` identity; published repo+installer checksums; refuses existing app/DB | Disk/controller identity and host contention attestation; bootstrap is not reboot/reprovision/recovery-safe |
| `deb/php83-lab/Vagrantfile` | Same configured box/CPU/RAM and no shared folders | Runtime lab alone is not an installed full PHP83 AIO; current VM state needs fresh attestation, not historical assumptions |
| `deb/php74-baseline/smoke.sh` | Root/hostname/IP/script-hash guards; temporary owned IPv4 egress chain; restores chain on exit | Not a reusable safe media/benchmark client: pinned legacy sanity uses redirects, credentials in arguments/URLs, unbounded curl calls and existing `/tmp/sanity.mp4` without a hash check |
| `evidence/noble-baseline/smoke-http.txt` | Historical zero failures:9services, searchd, API ping/session, UI HTTP200, one short upload READY/HLS segment | No full browser login/ACL, trusted TLS,1080p60/profile/thumbnail/progressive Range, repeated timing or recovery acceptance |
| `tools/php83/lab_target.py`, `test_lab_target.py` | Literal `.74`/`.83` allowlist; rejects `.20`, userinfo,DNS names,unlisted ports and redirects; disables proxies;4 local test cases exist | Not wired into legacy sanity; explicit private-CA context for installed AIO and all nested manifest/segment URLs still need implementation/testing |
| `tools/php83/patch-tests/api-http-client.py`, `api-apache-inner.sh` | Typed JSON/auth negative assertions, no redirects/proxies, nonce/runtime/SAPI checks, trusted/untrusted-CA pattern | Loopback `/probe`, synthetic schema and private Apache; NOT an installed-AIO benchmark client or full UI/worker acceptance |
| `tools/php83/exp11-api/collect.py` | Frozen source/current+previous artifact identities, synthetic owned-unit cleanup, token-safe output allowlist and diagnostics | Session-only bounded corpus, not media.list/get workload or production-equivalent SQL/cache configuration; don't run its temporary DB collector as baseline measurement |

Local source review confirmed the legacy sanity file matches the reviewed release
blob SHA `aaf36e09e1cf87dfb1dfc610f03821903e1ef899a175dc7ef2e2ce1f9cf334e7`.
It defaults to `.20` when invoked bare; **never invoke it bare**. Reuse existing
smoke evidence as PARTIAL, not a reason to rerun an unsafe credential-bearing
client. The bootstrap `.20` rule is transient across reboot; the smoke chain is
IPv4-only and permits pre-existing connections. Neither implies a persistent
air gap, comprehensive redirect rejection or a complete IPv6 policy.

## 2. Freeze manifest before any timing

Proposed new protocol manifest (not implemented by this plan):

- Case/run ID, parent tasks, reviewed commit, executor and independent reviewer.
- Published7.4 release/repository/installer SHA and installed `dpkg` package/version
  inventory; original source-to-package map and current generated/overlay hashes.
  Never relabel upstream ZIP as identical to the complete published payload.
- Exact VM UUID/box checksum/version,4vCPU,8GiB, disk/controller/cache settings,
  filesystem/free space, host CPU/hypervisor, host load and timestamps. Both labs
  must match; snapshot restore/drift or shared contention invalidates comparison.
- PHP CLI/web binary,module,INI,Apache/FPM identity; OPcache/JIT/timezone/locale;
  ffmpeg/ffprobe and worker binary versions/hashes; DB/cache/search versions.
- Synthetic partner/user/permission IDs, stable seeded media entry for timed get,
  conversion-profile and flavor definitions, queue/worker concurrency settings.
  Restrict credentials,KS,cookies,TLS keys and raw request bodies to guest-private
  files/memory; publish only sanitized IDs, hashes and explicit predicates.
- Literal target/port/transport allowlist, private CA fingerprint and SAN identity,
  proxy/redirect/DNS restrictions, timeout/retry/response-size policy, cleanup IDs.
- Encoder command/settings, **actual generated** fixture hashes, ffprobe reports,
  expected streams/frames/duration and delivered-profile tolerances. Hash fields
  must remain absent/NOT_RUN until bytes exist; no guessed fixture checksums.
- Exact request sequence, cache-state policy, samples/statistic definitions,
  warmups/round count, media timing boundaries and diagnostic classification.

The plan's suggested profile/settings are drafts until independently reviewed and
written into this manifest. Do not infer parameters or accepted tolerances from
a successful result after execution.

## 3. Minimal synthetic fixture pair

Decision7 requires10s640x360/25fps and60s1920x1080/60fps H.264/AAC. Use technical
FFmpeg test patterns plus a synthetic tone; no YouTube material, user media or
creative-video tools. Generate **once**, checksum, inspect and copy identical
bytes to both labs rather than regenerate on each encoder build. FFmpeg documents
synthetic video/audio sources; ffprobe provides machine-readable stream/frame
inspection. [FFmpeg filters](https://ffmpeg.org/ffmpeg-filters.html),
[ffprobe documentation](https://ffmpeg.org/ffprobe.html).

Suggested freeze inputs: testsrc2+sine, yuv420p, libx264 preset medium/CRF18,
fixed GOP of two seconds, explicit25/60 constant rates, AAC128k/48kHz/stereo,
single-threaded generation and stripped variable metadata. Record the exact
encoder build/options; these settings alone are **not** proof of cross-build
byte reproducibility. Verify250/3600 decoded video frames and exact source raster/
nominal rate; freeze audio/container duration tolerances before tests.

Conversion profiles must explicitly include the accepted delivered360p25 and
1080p60 properties; do not assume the baseline's default flavors retain60fps.
Each upload must produce READY, expected flavor set and thumbnails. Inspect
actual delivered progressive and HLS streams: raster, frame rate, duration,
codec/audio, manifest structure, referenced segment identity and successful
bounded retrieval; verify206/Content-Range on a valid byte range. Every resolved
manifest/segment URL re-enters the target guard before connection. Negative
wrong-origin/redirect/untrusted-CA cases run before credentials or uploads.

Proposed bounded limits for independent review before the manifest is frozen:
API/manifest/thumbnail total monotonic deadline30s, no automatic retry; upload120s(short)/600s(long);
READY polling every2s with600s(short)/1800s(long) deadline; manifest cap1MiB,
JSON cap1MiB (read cap+1 and reject overflow, never truncate silently), segment cap64MiB and progressive byte-range window1MiB. Actual
fixture/upload byte caps must be set from the generated file lengths, not guessed.
Require exact delivered raster and declared25/60fps profile, duration tolerance
at most one video frame plus one AAC frame for stream/container accounting;
if the selected baseline encoder/profile cannot meet this draft tolerance,
review/version the protocol before timed runs rather than widen it afterward.

## 4. API/media repetitions and statistics

Decision7 freezes2warmups + at least5measured rounds,100sequential API calls per
round, with session.start/media.list/media.get recorded separately and both
fixtures uploaded/verified each round. One explicit proposed interpretation is
**34 session.start +33 media.list +33 media.get =100 calls**, fixed order each
round; approve this split before implementation (do not silently interpret as
100 calls per endpoint). Use a pre-seeded fixed get entry and fixed pagination,
ordering/filters so the growing upload corpus does not change list payload size.
No hidden client retries; failures/timeouts retain their sample and mark the row
FAIL rather than disappearing from the denominator.

Run HTTP and trustedHTTPS as separate protocol rows. At the proposed minimum,
each runtime/transport has700API calls total (200warmup+500measured) and14uploads
(4warmup+10measured). Both transports mean1400calls/28uploads for one runtime;
never call those28 independent fixtures. Compare candidate only when its full
installed lab is ready and identically configured; baseline collection can finish
first without a candidate PASS or release date.

Per endpoint/round report sample count, median and nearest-rank p95
(zero-based integer index `(95*n+99)//100 - 1`), raw durations and errors. Report pooled endpoint
summaries separately; never mix endpoints or pool away a slow round. For each
fixture distinguish client upload duration, queue wait, worker conversion and
READY visibility plus delivery verification; predeclare timestamp sources and
clock checks. Report at least5 measured sample durations per fixture/transport,
not a misleading latency p95 from one transcode. Warmups remain recorded/excluded.

Matching workload API median/p95 and transcode wall time must not regress >20%
without explicit review (Decision7). Freeze comparison pairing and aggregation
before measuring; preserve dispersion and every run. Concurrent agent workloads
on either VM **or the shared benchmark host** make measurements INCONCLUSIVE,
not PASS. Separate compatibility changes from optional dependency upgrades.
All exercised-path diagnostics must be classified; fatal/type,worker/job,auth,
extension or contract regressions block acceptance. No blanket warnings waiver.

## 5. Small recovery and baseline-preservation boundary

For protocol readiness, specify a **coherent synthetic baseline checkpoint**:
restrict intake, drain/stop workers, record app/runtime/config/package state,
DB snapshot and media/config file hashes, then preserve a matched snapshot or
reviewed backup set with restricted secrets. Never take/recover a production clone.
A live VM snapshot alone is not evidence of application-consistent recovery.

Preserve baseline before repeated synthetic uploads so later rounds/retests have
known state. Prefer tagged test fixtures and exact owned-resource cleanup; do not
reset arbitrary partners or delete a DB by a returned untrusted path. Cleanup or
snapshot restore must verify identity, stop only owned work and check services,
login/API/media state afterward. A reboot needs outbound guard reinstallation
**before requests**, not the assumption that bootstrap firewall state survived.

The complete upgrade/failed-cutover rehearsal remains tasks4.1/4.2 and5.23/5.24:
restore matched app/runtime/config/DB/media after controlled synthetic writes,
account for discarded writes and drain old workers. This plan does not promise
lossless downgrade or waive those later cases. Criteria subclass serialization
already has a native74/83 ordering/cache-key difference; choose and test a real
cold/warm invalidation policy under5.9, not a custom serialization rewrite or
an invented cache-corruption claim.

## 6. First three runnable work packages (after review)

1. **Local-only protocol/guard tests:** implement manifest validation and fixed
   case inventory; extend literal-target guard to bounded body reads/private CA;
   negative fixtures for proxies,IPv6,DNS/redirects,nested HLS destinations,
   wrong hashes/secrets in reports,changed profiles/missing samples. No VM needed.
2. **Local synthetic media freeze:** generate/ffprobe/hash the two technical
   fixtures using pinned tools; independently verify stream counts/settings and
   invalid-media detection. This needs compute reservation, not production access.
3. **Exclusive baseline functional rehearsal before timing:** attest existing
   published74 lab, restore/verify guards, install lab-only trustedTLS identity,
   seed scoped synthetic data and run one untimed HTTP/HTTPS API/media/browser
   smoke with cleanup verification. Only afterward run the frozen repetitions.

Actual Claude/OpenCode/other authorized independent reviewer must execute/review
frozen inputs and retain terminal/test evidence. Current AGENTS prioritizes
Claude,Cursor,OpenCode; historical Grok-first prose is not a requirement to retry
Grok. Local tests alone do not close1.2/5.5; full acceptance requires the manifest,
real applicable baseline API/UI/worker/media/TLS rows, resources/timings,
independent repetition and documented gaps. No task checkbox changes here.

## 7. Retrieval and source provenance

Installed ai-memory retrieval was used before planning (explicit returned project
scope `default/platform-install-packages-php83`; thin hits broadened globally).
It did not provide a completed baseline protocol; current design/evidence above
are authoritative. Structural graph project for the main worktree was ready
9934nodes/17666edges, generation2026-09-25T19:28:02Z. Coverage reports the migration
baseline/harness paths as `freshness: missing`; all relied exact files were read
directly. `deb/noble/sanity.sh` had matching metadata. No graph absence/exhaustive
coverage claim is made for this separate migration worktree. Decision7 and
`coverage-matrix.md` retain the broad baseline/performance/recovery gaps.

## 8. Actual independent planning review and revised draft decisions

Actual Claude CLI completed read-only review with exit0, no stderr, no test/VM/
network/FFmpeg execution. It read the draft and specified source files, identified
missing protocol decisions, and did **not** approve execution. Codex separately
verified the legacy release-blob hash and read the four guard test methods; those
claims are not attributed to Claude's restricted file review. This document is a
revised draft, not a frozen executable protocol. All counts and values derived
from the proposed34/33/33 split remain **DRAFT** until manifest review.

The following decisions resolve or explicitly bound the review findings:

- **Baseline identity first:** current `.74` has hosted copied83 isolated probes;
  that alone does not prove installed74 package contamination. Attest published
  package versions/checksums, installed app/overlays/config against the recorded
  post-bootstrap baseline, and inspect inactive owned probe services/workloads.
  Missing historical comparison or unexplained drift makes timing INCONCLUSIVE;
  obtain coordinator approval for a fresh isolated published74 clone rather than
  silently reprovision the current shared research VM. No such action is done here.
- **Draft request/session policy:** USER KS with frozen minimum list/get/upload
  privileges for one synthetic partner;34 measured session.start POSTs followed
  by33 media.list and33 media.get using the final freshly issued KS. Setup-only
  admin credentials are never timed. Keep secrets/KS in memory or restricted
  request-body files, not URLs/argv/logs. Freeze expiry/clock constraints to exceed
  the bounded round. Wrong-secret/cross-partner/expired negatives are separate
  functional rows, not hidden timing retries.
- **Client and ordering:** one fixed host-only client location/resource envelope
  for both labs. Complete the API block with workers idle, then one fixture upload
  and wait for READY/delivery, then the second; wait until queues drain before the
  next round. Never run timed API calls during conversion. HTTP/HTTPS order is
  alternated by a fixed schedule, and baseline is remeasured bracketing candidate
  runs (A-before/B/A-after) to detect host/time drift; early baseline results alone
  do not establish a later candidate comparison.
- **Cache state:** use the same published cache/OPcache settings for steady-state
  warm measurements; record API response-cache and backend hit/miss observations,
  not a claim that repeated get calls benchmark uncached PHP. Cold/cache-restart
  functionality is a separate untimed row. Freeze memcached/APCu warm/cold state
  and cache policy per round; do not flush or globally disable a backend just to
  improve timing. Full cross-engine invalidation remains task5.9.
- **Draft20% comparator:** pooled measured API median/p95 per endpoint+transport
  is the primary latency comparison, with all five round summaries retained.
  If max/min round medians exceed1.20 or host contention occurs, classify as
  INCONCLUSIVE and repeat. These are proposed stability limits, not observations.
  Transcode reports median and maximum for five samples (do not pretend this is
  a well-estimated tail distribution); separately gate median worker start→finish
  and median upload-complete→READY at20%, keeping queue and polling effects visible.
- **Guard semantics:** the existing Python30s timeout is a socket-operation
  timeout, not a total deadline; the new client must enforce elapsed monotonic
  budgets. Reject all automatic redirects. A delivery-only manual redirect may
  be allowed by a separately reviewed maximum-hop policy only after validating
  each Location, stripping credentials and rechecking literal destination/port;
  until that policy exists, redirect is explicit FAIL, not silently followed.
  Service URLs must match the frozen literal-IP allowlist; redact query/path KS.
- **Real browser playback:** choose a fixed browser build and actual browser
  executor (for example existing console E2E tooling after inventory), install
  only the lab CA in its isolated profile, reject external egress/assets and
  capture login/session/ACL plus actual playback progression. HTTP200/segment
  retrieval alone does not satisfy this row. Browser executor/profile/asset
  policy remains a concrete implementation gap, not a waived task.
- **Encoder/duration:** add explicit metadata removal, bitexact flags where
  supported, fixed GOP/min-keyint/scene-cut and thread settings to the generated
  command manifest. These do not guarantee cross-build encoding identity.
  Validate AAC priming/padding during the untimed rehearsal before freezing the
  draft frame-based tolerance; version any revision before measured execution.

Immediate local implementation can proceed on guard/manifest/statistic tests;
media generation and baseline VM operations still need their separate resource
reservations and reviewed frozen inputs. No measured baseline is claimed here.
