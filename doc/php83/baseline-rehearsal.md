# Untimed published-PHP7.4 rehearsal: plan and offline guards

## Current authoritative state

Two actual baseline74 untimed attempts have executed and **failed closed**. R1
verified PHP7.4.33/apache2handler through the installed web vhost and removed its
nonce probe, then stopped at LOG_SIZE_UNREVIEWED. R2, after independent Cursor
review and63 local tests, scanned4,005,834,245 bytes across210 local files plus
the bounded journal and stopped at **INVALID_CANARY_LOGGED**. The new invalid
synthetic secret appears twice in one matching chunk: DEBUG parameter dumps from
KalturaFrontController and KalturaDispatcher. No real USER secret was submitted
to session.start, no valid KS was created by this driver, and no media was uploaded.
Guest-private SQL was used to identify the existing published-smoke synthetic
partner102; its secret never left guest memory. Source/stage pre/post identities
matched. No logging level/configuration/source repair has been applied.

Baseline74 was released to the coordinator after redacted sink/emitter diagnostics.
A privacy repair changes the published baseline, requires explicit approval and
identical policy on baseline/candidate, and must not be labeled published-intact.
Tasks1.2/5.5, full source/config attestation, media/TLS, timing and5.9 remain open.
The following earlier plan/inventory sections are chronological history, not a
claim that no native rehearsal occurred. Synthetic offline receipts remain only
validator fixtures, never native execution evidence.

### Subsequent synthetic privacy preparation (not real API success)

A separately reviewed three-target log-copy policy passed two isolated synthetic
native probes and six lints on each of PHP7.4.33/PHP8.3.6, with unchanged source
and runtime identities and empty stderr. Nevertheless the actual Zend formatter
still exposes a synthetic secret prefix in exception arguments on both runtimes.
Both comparisons retain full_privacy_accepted=false. No application repair,
valid USER request or media upload followed. See the
[privacy proposal/current receipts](baseline-rehearsal-privacy-proposal.md) and
[pending trace-display option](baseline-rehearsal-trace-proposal.md).

## Historical preparation: sequence and ownership

1. Coordinator grants exclusive baseline74; verify guest hostname and actual
   192.168.56.74 address before even querying PHP. Reject .20/.21/.30/.83. Keep the
   management SSH channel separate from the workload egress policy; do not lock
   out or silently exempt arbitrary established outbound application connections.
2. Read-only public inventory first: published repository/installer hashes, CLI
   PHP7.4 version, default module names, installed package versions, known public
   Apache PHP module files, and five critical source hashes. The collector sends
   reviewed Python over SSH stdin; no guest files/configuration are changed, no
   SQL/HTTP/credentials/private config reads. This subset is explicitly **not**
   full source or web/provider attestation.
3. Join installed package archives to the checksum-pinned published repo and
   installer; collect complete source/runtime/provider/module/config identities.
   Do not infer web PHP from CLI PHP or merely from an installed libphp file.
   A separately reviewed temporary nonce-bound web probe must use the installed
   application vhost/provider configuration and return only allowed metadata.
   Remove the probe and verify its removal. CLI and web identities are distinct.
   Expected identities must be frozen from trusted package/install evidence,
   not learned from a candidate run and immediately relabeled the reference.
4. Freeze a secret-free public configuration manifest (provider, module/INI
   policy, cache mode, DB endpoints without credentials, workers, profile IDs).
   Compare secret-bearing configuration **inside the guest** and return only a
   drift boolean; never export its contents or dictionary-attackable secret
   digests. Verify CPU/RAM/disk/controller/box and network policy separately.
5. Validate log privacy before live auth: inventory Apache/nginx/app/debug/audit
   sinks and forwarding configuration; issue a synthetic invalid canary and scan
   only approved logs privately. Then use a disposable successful USER session
   to check both its valid secret and valid KS remain absent from all reviewed
   sinks. Export only zero/nonzero match counts and public log-inventory hash,
   never raw lines/token hashes. Invalid-canary absence alone is insufficient.
   Any hit stops the run; fix the owned lab logging configuration under review,
   revoke/rotate that disposable credential, and repeat privacy checks. Do not
   erase arbitrary logs to turn a failed privacy observation into success.
6. Snapshot/record the synthetic starting state before mutations; use a unique
   baseline-<nonce> ownership namespace and a dedicated test partner. Provision
   through an owned helper that reads guest-private credentials (0700 parent,
   0600 single-link file) and uses API POST bodies/private memory or a protected
   local DB connection. Never execute legacy sanity/create_partner/upload_test
   command lines that put admin/user secrets into argv or URLs. Administrative
   setup is outside measured work; benchmark sessions stay USER type0. Confirm
   wrong-secret rejection and attempted admin escalation rejection. No automatic
   reuse or deletion of preexisting partners/media outside this exact namespace.
7. Select the already frozen technical source media bytes from Decision7.
   Hash the source before upload, hash exactly the uploaded stream, identify
   original-source flavor/asset and file-sync record, and hash the stored source
   and source again afterward. Join nonce→partner→entry→profile→original asset→
   file-sync→resolved version→exact source SHA. A READY status or matching filename
   alone is not that join. Preserve the receipt. Any ingestion rewrite of the
   original bytes requires explicit investigation, not comparison to an unrelated
   transcoded rendition. No arbitrary YouTube/user material is used.
8. Untimed API observation: create one USER session, list the exact owned entry
   with idEqual/pageSize1/pageIndex1/+createdAt, get it, and record typed five-field
   projection and totalCount **as returned**, Content-Type and permission outcome.
   Do not coerce numeric strings or silently replace USER with ADMIN. Queryless
   POST URLs only; redirects/DNS/proxies rejected and HTTPS uses the pinned CA.
9. Observe media.get requests at -1,0 and the actual chosen concrete version.
   Preserve accepted/rejected outcomes and resolve successful responses back to
   the original asset/file-sync/source digest. Freeze a version only after this
   evidence, not from an assumed version numbering scheme. See zero below.
10. Recheck source/runtime/config, fixture hashes, owned media and log privacy.
    Only authentic reviewed native receipts, not self-asserted booleans, can make
    the offline guard useful as a completeness/equality check.
11. Freeze the actual typed fixture and only then schedule the full2warmup+5
    measured rounds per transport. Keep the complete100-call34/33/33 denominator
    and all failure/dependency/abort rows. No performance statistics from this
    untimed rehearsal are acceptance evidence.
12. Full10s/60s upload→READY→stream metadata→trustedTLS/HLS/browser, workers,
    reboot/recovery and cache cold/warm behavior remain separate required gates.

## Version0 is not an API rejection

Direct immutable-source review:
- MediaService.php getAction(entryId, version=-1) delegates to getEntry.
- KalturaEntryService.php:1221–1222 calls setDesiredVersion for every value other
  than integer-1; there is no positive-only restriction there.
- entry.php:1041–1044 stores the supplied desired version. Its data-content path
  at1092–1093 maps a falsy value (including0) or-1 to null/current.

This is bounded source evidence, not proof of all native response semantics.
The earlier baseline-api v1 >0 guard was a conservative explicit-version corpus
choice, **not a claim that version0 is unsupported**. This rehearsal guard accepts
selected version0 if an authentic observation binds it to the owned immutable
asset/source. It then returns protocol_revision_required=true: create/review a
versioned protocol correction before using v1, never manufacture a positive
number to satisfy the old guard. Frozen v1 and its historical tests stay intact.

## Offline guard and evidence semantics

guards.py checks exact schema/nonce/target/published pins, before/after runtime/
web-provider/source/public-config identities, network/privacy controls, USER-only
ownership, source-stream/stored-source hash joins, version outcomes and the
three untimed typed API successes. Unknown fields (including accidental secrets)
are rejected with fixed error codes. It does not authenticate input JSON, perform
uploads or attest native execution. Tests contain synthetic invented hash values
and cannot be published as native attestation. Intermediate observed versions
may legitimately fail; the selected version must have the complete binding.

guest_inventory.py/collect_inventory.py are an initial read-only inventory,
not the full guard input collector. A successful inventory must never be fed
into guards.py as if it supplied missing source/provider/log/media evidence.

Local command:
    python3 -m unittest discover -s tools/php83/baseline-rehearsal -p 'test_*.py' -v

Actual independent CLI review must precede the authorized read-only inventory.
No benchmark, legacy sanity invocation, network-policy change, provisioning,
credential access or application deployment is part of that inventory.

## Historical read-only inventory checkpoint

Actual OpenCode completed the initial local review and24 tests, then a focused
r2 parser review and27 tests, both exit0. Authorized exclusive74 read-only
inventory was then exercised; **no credentials, SQL, HTTP, guest staging or
configuration writes** were performed. Baseline74 ownership was released.

The first inventory failed closed at package parsing. Its exit/hash and original
program snapshots remain. A fixed safe diagnostic reported only the package
parsing stage. Dpkg wildcard matching includes uninstalled package aliases with
empty version/architecture; r2 requests dpkg status and separates them from the
installed-package inventory. It does not invent installed versions.

R2 actual inventory exit0: CLI PHP7.4.33; four CPUs;34 installed package rows and25
uninstalled aliases. All eleven listed public/source files were present. The
repository and installer hashes exactly match the published bootstrap pins.
The Apache PHP7.4 shared module exists; this is NOT proof the active vhost uses it.
The module-name output is filtered php -m lines and may repeat Zend module names,
not a claimed unique get_loaded_extensions inventory.

Five critical installed source hashes were compared with immutable upstream
source separately; this limited comparison is not a complete installed source
manifest, package-origin verification or provider/config attestation.
Full web/source/config/log/privacy/owned-media observations and seeding remain
next work. No offline synthetic guard receipt was relabeled as native evidence,
and no full baseline, benchmark or release gate was marked complete.

## Historical functional untimed r1 preparation (subsequently executed)

New untimed_driver.py/run_untimed.py are separate from frozen baseline-api v1.
They stage only pinned code and the frozen short360.mp4 (SHA612d179c...), reuse
only the published smoke synthetic partner identified by private state and email,
and keep its USER secret/KS entirely inside the guest. No ADMIN fallback, no
secret URL/argv, no benchmark. One fresh owned nonce/entry is retained on failure.
The temporary nonce/IP-restricted web provider probe is removed in a finally block.
The root systemd workload unit allows only localhost and literal74, prohibits
privilege escalation, and limits writes to private owned fixture state/probe path.
The SSH management channel is separate. API transport still rejects redirects,
DNS and proxies and keeps the existing total per-request deadline.

Before authenticating, the driver audits installed logger/Apache/nginx/rsyslog
configuration for unsupported sinks/body logging/forwarding and known running log
agents. It scans app/web/syslog files and the bounded journal for invalid canary,
then real USER secret/KS, before media mutation and again afterward. No raw logs,
secret-bearing configuration or configuration digests are exported. This bounded
installed-config audit is not complete host security attestation. Log file limits,
unknown sinks/agents and privacy hits stop rather than waive the check.

Short upload links exact uploaded bytes to owned entry, original flavor asset,
file_sync and stored original SHA before/after. Entry current version is resolved
using the audited entry.getVersion convention; asset version remains separate.
media.get -1/0/current and media.list preserve actual wire types. Matching dataUrl
is only a private equality observation, not playback/segment content proof.
Public inventory/source subset is checked against the prior published baseline
before/after; it is not a complete source/package/provider attestation. Full
source/config freeze, HTTPS, both-media upload/playback, browser, recovery, full
100-call rounds and all performance gates remain open.


## Executed r1/r2 evidence and bounded privacy semantics

- untimed-primary.json: r1 exit1/LOG_SIZE_UNREVIEWED. Actual web version7.4.33,
  apache2handler, installed INI path/modules; probe removed;55 logging-config
  files passed the bounded preflight. Wrong-secret control rejected. No upload.
- log-size-inventory.json:209 web/app files,3,983,981,957 bytes at that sample;
  API log3,494,276,989 bytes (~88%). This is size dominance, not proof of a loop.
- untimed-r2-primary.json: r2 exit1/INVALID_CANARY_LOGGED. Full bounded streaming
  scan,8GiB/file,12GiB total,90s budget; no rotation/truncation detected and0
  appended bytes excluded at the observed cutoff. No logs removed/rotated/skipped.
- canary-emission-map.json: two exact synthetic-canary matches in the API log,
  nearest classified DEBUG headers KalturaFrontController and KalturaDispatcher;
  only path/offset/enum emitter/priority are exported, never lines or secret data.
- Actual OpenCode initial/focal reviews:50 then52 tests, terminal0.
  Actual Cursor streaming/race reviews:57 then63 tests, terminal0. These are
  preparation reviews, not native application passes. Cursor explicitly noted
  complete privacy() fd orchestration lacks unit integration coverage.

The scanner binds pre-request and cutoff inode/device/size snapshots, rejects
rotation/truncation/removal/symlink/nonregular/short reads, and checks exact
captured-size reads plus inventory continuity. Later appends are quantified as
not covered, not silently called audited. Journal has an explicit until boundary.
This is an observed snapshot, not proof that asynchronous future logs cannot leak.
Whole-token absence alone would not prove absence of encoded/truncated fragments.
The observed real full-token leak already prevents proceeding with valid auth.

## Privacy repair proposal (separate, not applied)

See [the narrow privacy-policy proposal](baseline-rehearsal-privacy-proposal.md).
It includes both confirmed DEBUG emitters, analytics KS, exception/encoding
controls and candidate composition. Explicit policy approval, actual patch and
independent native validation remain pending; no privacy fix was applied.

## Growth triage before benchmarks (pending a new VM slot)

Do not infer a loop solely from4GB, stop services, or rotate logs to improve
results. Take two stat samples over a short bounded interval on the API log;
record monotonic elapsed time and byte delta, inode/truncation/rotation checks.
Privately inspect only a capped append window for fixed severity/category counts,
exporting no text/lines/identifiers. Account for an incomplete window explicitly.
Compare idle vs the separately identified synthetic request window before any
performance run. Baseline74 currently belongs to another coordinator-assigned
worker; this triage has NOT executed and no new access is authorized by this doc.
