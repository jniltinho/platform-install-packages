# Baseline .74: bounded privacy overlay application checklist

**PLAN ONLY — no installed overlay or VM action performed by this review.**
Proceed only after the trace-policy primary and actual independent repeat are
reconciled, the coordinator grants exclusive .74, and the application step is
approved. The synthetic memory-sink proof is not installed-configuration proof.
Do not touch .20, .83, package/release state or historical checksum operations.

The resulting reference is **published PHP7.4 plus an explicitly identified
privacy overlay**, never published-intact. A later candidate comparison must use
the same reviewed logging policy, with each runtime's source composition pinned.

## 1. Freeze and inspect, without exposing configuration values

- Keep the original failed canary receipts and the trace-policy R3 failure/R4
  classification. Require primary/repeat sources, runtime, native channels,
  cleanup and all four bounded contracts; preserve intrinsic-message,
  pre-rendered-string and extras.message leaks as negative controls.
- Verify hostname/address using the existing lab guard: only
  `kaltura-php74-baseline` / `192.168.56.74`; reject other lab/production addresses.
- Reuse the public inventory fields in `guest_inventory.py`, not CLI-version
  inference about Apache. Identify the actual vhost/provider, running workers
  and their logger configuration. Keep private configuration comparisons inside
  the guest; export class names, public paths/counts and drift booleans, **not
  raw configuration, credentials or hashes of secret-bearing values**.
- Extend the existing `untimed_driver.py:logging_preflight` audit for this
  concrete flow: resolve enabled logger sections/includes and factory mapping;
  enumerate effective writer classes, formatter classes/templates, filter
  classes/order/priority and extras **keys only**. Verify configured Stream
  maps to the core `KalturaSerializableStream`, no `message` extra overrides the
  Throwable, and no filter/formatter/other writer emits it before masking.
  A static logger.ini string match alone does not prove effective configuration.
- Keep existing Apache/nginx/body/pipe logging, forwarding-agent and local-sink
  checks. Include the effective PHP error sink, worker logs and journal in the
  reviewed inventory. Unknown forwarding or a second unreviewed sink means stop
  before credentials, not silently disable logging or reduce its level.
- Inventory the exercised emitters for premature `(string)`/rendered traces
  and intrinsic sensitive messages. The hook does not repair those cases.
  This is a gate for the selected synthetic USER flow, not universal privacy.

## 2. Installed source join and recoverable application

The four exact targets are:

```
infra/log/KalturaLog.php
infra/log/KalturaSerializableStream.php
api_v3/lib/KalturaFrontController.php
api_v3/lib/KalturaDispatcher.php
```

Resolve their installed paths under `/opt/kaltura/app`; verify regular files,
no unexpected symlinks/hardlinks and every before hash against the **original74**
overlay manifest. Do not apply the exp14 cumulative source to PHP7.4. Unexpected
installed modifications require an explicit source join, not force/fuzzy patch.

Before writes, record exact files' bytes, ownership/mode and source hashes in a
guest-private backup location under the already protected lab-private area;
keep backups outside the web root and repository. Reuse restrictive backup
mechanisms only after approval; this checklist changes no permissions. Do not
copy private configuration into public evidence. Record a backup receipt and
rollback mapping before touching any target.

Stop/drain the exact affected lab application processes before replacing this
interdependent four-file set. Reuse `prepare.py`'s exact-anchor/zero-fuzz replay
and prepared hashes; lint candidate files with the actual PHP7.4 provider.
Install all four only as a coherent batch, preserving installed metadata;
verify after hashes. On any mismatch restore the whole four-file backup,
verify original hashes and leave auth testing stopped. Do not rely on reversing
a patch against possibly drifted files.

Invalidate process-local code by restarting the **identified** Apache/PHP worker
and relevant long-lived lab workers after coherent installation (or rollback).
A CLI `opcache_reset()` is not evidence that the web SAPI cache was refreshed;
a graceful restart with old workers still serving is not a completed boundary.
Verify old PIDs are gone/drained, new web-provider identity and the installed
source pins before sending any credential-bearing request. Do not invent a
generic service list or restart unrelated services.

## 3. Bounded append-window privacy gate

Reuse the existing `log_snapshot`, `log_continuity`, `scan_stream` and guest-only
pattern scanning, with a **reviewed small driver revision**, not a second logging
framework. The historical driver scans each file from byte zero: it is not an
append-only implementation and should not be described as one.

For the new phase, before the first request record each approved regular file's
device/inode/size and a journal cursor/time boundary. Open with no-follow and
verify fstat identity; scan `[start_size, end_size)` for surviving files, and the
complete bounded new file for a newly created approved sink. Keep cross-chunk
pattern overlap. Freeze the cutoff, verify inode/size again, and capture bytes
appended after that cutoff in a subsequent bounded drain window before approval.
Report uncovered tail bytes; a nonzero unreviewed tail is **INCOMPLETE**, not zero
leaks. A quiet/flush bound cannot imply universal asynchronous delivery coverage.

Rotation, truncation, new/unapproved sinks, journal gaps, deadline/size limit or
read failure must stop the gate. Either reconcile the exact rotated inode and
continuous interval under a reviewed rule, or retry a fresh owned phase; do not
reset offsets, erase/truncate logs or quietly skip compressed/rotated files.
Existing `log_continuity` already rejects inode changes and truncation; retain
that fail-closed behavior until an explicit rotation reconciliation exists.

Use a fresh synthetic invalid-secret nonce first. Require its expected API
rejection, then no full canary **or its previously observed trace-display prefix**
in any reviewed append window/journal. Export only counts, public sink inventory
and interval/continuity metadata; never log lines or request/response bodies.
Only then may the dedicated synthetic USER session be attempted. No ADMIN
substitution and no real user credentials. Keep secret/KS guest-private, off
argv/URLs; use existing POST transport and protected-memory helpers.

After successful USER auth, scan for that synthetic secret and KS (and applicable
truncated display signatures) before proceeding to upload/READY. Absence of an
invalid nonce alone is insufficient. Any hit stops the run, preserves the leak
receipt, and triggers cleanup/revocation of this owned disposable session/test
credential; never rotate a shared credential or erase evidence implicitly.
Use an explicitly approved synthetic partner; historical partner102 reuse is
not authority to mutate unrelated state. Recheck effective config and source
identity at the end. Keep upload/media acceptance separate from this privacy gate.

## Existing mechanisms and commands to reuse

Repository-local tests (no VM, no installed changes):

```bash
python3 -m unittest discover -s tools/php83/baseline-rehearsal/privacy/trace-policy-v1 -p 'test_*.py' -v
python3 -m unittest discover -s tools/php83/baseline-rehearsal -p 'test_*.py' -v
```

Reuse rather than rerun historical entrypoints blindly:

| Existing path | Reuse / constraint |
|---|---|
| `tools/php83/baseline-rehearsal/privacy/trace-policy-v1/prepare.py` | Exact source/patch construction, original74 and exp14 remain distinct; no installer. |
| `tools/php83/baseline-rehearsal/privacy/trace-policy-v1/run.py`, `guest.py` | Synthetic-only frozen stage/host/pin/cleanup patterns; **not application deployment**. |
| `tools/php83/baseline-rehearsal/guest_inventory.py`, `collect_inventory.py` | Public inventory checks; fixed historical outputs prevent overwrite. Inventory is not full attestation. |
| `tools/php83/baseline-rehearsal/run_untimed_r2.py` | Exclusive host guard, bounded unit, protected transport/receipt shape; stage/output names already used. Its published-source identity check must not be bypassed for an overlay. |
| `tools/php83/baseline-rehearsal/untimed_driver.py` | Provider nonce/removal, private SQL/POST helpers, canary→USER→upload sequencing and continuity scanner. Requires the explicitly named overlay identity, effective-policy audit and bounded append-window revision above before new real auth. |
| `tools/php83/baseline-api/{transport,protocol}.py` and `baseline-protocol/{guarded_http,deadline_transport}.py` | Existing guarded requests/private reads; do not substitute curl with credentials in flags. |

There is currently **no reviewed turnkey installed-overlay command** in these
paths. Do not invoke historical `run_untimed_r2.py` unchanged: it checks the old
published baseline, consumes existing stage/output names and continues through
upload after its old privacy gate. The next implementation should be a minimal
versioned extension of this runner/driver, with preserved historical evidence,
reviewed rollback and synthetic local guards. This document adds no executable
framework and authorizes no VM writes.
