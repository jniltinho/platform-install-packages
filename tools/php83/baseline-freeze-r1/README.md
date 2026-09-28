# Existing-media baseline observation, not an approved freeze

Task 1.2's smallest next observation. The coordinator alone executes the guest.
No upload, profile modification, transient web PHP file, package change, worker
release or performance round. Session authentication and ordinary API logging
still occur. Root-only diagnostic files and immutable collector staging are the
only intentional guest filesystem writes by this collector.

## Reproducible source and local validation

`prepare.py --output NEWFILE` derives `guest.py` from the exact pinned historical
media-overlay-v3 guest. Never run that historical upload runner again. The new
guest verifies its old staged Python dependencies before import, V4 overlay
manifest, five installed sources, runtime module pins and private configuration
equality. Graph coverage is not claimed: these are literal authenticated source
and prior-receipt reads.

Run locally (no VM):

```
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tools/php83/baseline-freeze-r1 -p 'test_*.py' -v
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tools/php83/baseline-api -p 'test_protocol.py' -v
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tools/php83/baseline-api -p 'test_transport.py' -v
```

Author results: 21 / 22 / 12 tests, all exit 0. These are pure/local fixture
results, not native .74 observations. Transport tests use isolated local fixture
servers, not the VM. Independent review is recorded separately.

## Coordinator execution after independent review

From the migration checkout, verify `source-pins.json` and use:

```
python3 -B tools/php83/baseline-freeze-r1/run.py --check
python3 -B tools/php83/baseline-freeze-r1/run.py --output NEW_EXCLUSIVE_LOCAL_DIRECTORY
```

`--check` performs only read-only host and guest target/permission preflight;
it does not stage code, create a unit or use application credentials. It pins
`/tmp/php74-baseline-strict-r1.conf` and `/tmp/php74-baseline-hostkey-r1` to the
coordinator's strict-SSH receipt. That host key has recorded TOFU provenance,
not independent out-of-band attestation. VBox UUID, running 4 CPU/8192 MiB
VM and exact 127.0.0.1:2201→22 forwarding are checked before SSH staging.
Guest hostname/.74 address and protected-address exclusion are rechecked.

Actual mode exclusively creates `/var/lib/kaltura-baseline-freeze-r1`, with
root-owned immutable guest.py and observation.py. Existing stage or output
refuses reuse. Strict root-only non-writable ancestors are mandatory. Never
chmod an unexpected parent to get past a failure. The old .74 V4/media stages
and private diagnostic parent must already exist and match pins; this runner
neither reconstructs nor repairs them.

A unique `baseline-freeze-<8hex>` transient unit permits only loopback/.74
network, NoNewPrivileges, read-only system/home and private tmp. Only
`/root/kaltura-baseline-private` is writable; **no webroot write exemption**.
The unit has 1100-second lifetime; host capture is bounded to 1130 seconds and
4 MiB combined output. Raw stderr is counted and discarded. The coordinator
runner always attempts stop/inactive verification after execution and preserves
failure as failure. A stage/intent left by failure is not permission to retry.
Root must review partial state and make any recovery decision separately.

Public result contains fixed status-only checkpoints and a validated, reduced final projection. Raw nested scanner offsets/errors are not copied into host receipts. Root diagnostic
boundaries remain private. No secret, KS, HTTP response/error, profile name or
arbitrary entry data is intentionally exported. The invalid-secret privacy gate
precedes reading the real synthetic partner secret; USER session and rejected
admin escalation controls precede media reads. File/journal/file-after-journal
finite scans remain mandatory. This proves only those finite windows.

## Observation and envelope

The existing entry is `0_wzmt2sfy`, partner 102, original asset `0_ewuu0o46`,
asset version 2, FileSync 315. The source media hash is independently rechecked.
**Entry version is derived from entry.data**, not asset.version: authenticated
entry::getVersion uses the first `^` segment (or `&` when no `^`) and its filename
stem. Unsupported representation stays unresolved. Native media.get is observed
separately for -1, 0 and positive concrete version; a concrete typed projection
match is required to construct the fixture. Conversion profile lookup is get-only;
missing/inaccessible profile is unresolved, never replaced.

The protocol fixture retains exactly **eight** top-level keys (not seven).
The environment/profile envelope is separate. Extract the final successful
phase receipt and the coordinator sidecar's `environment` object into new local
public JSON inputs; invoke `assemble.py` with both exact externally supplied
input SHA-256 values and a new exclusive output path. It refuses malformed
privacy, fixture/source/runtime joins or unsafe fields. Environment snapshot and
box checksum may be null as observations; this is not recovery attestation.

Every assembled envelope says `approved_freeze:false`, `full_acceptance:false`,
`recovery_snapshot_attested:false`. Current Apache PHP runtime is explicitly
unverified; CLI version is not an Apache proof. Configured profile versus actual
asset versions remain distinct. Environment approval, native web runtime,
long-media flow, HTTPS/HLS/decode, warmups and measured repetitions remain open.

## Actual R1 result — preserved failure

Root preflight exited0; actual execution exited2 with
`FAILED_OR_INCOMPLETE_CAPTURE`, guest exit unavailable and unit confirmed inactive.
See `doc/php83/evidence/baseline-freeze-r1/actual-r1.json`. Do not replay R1 against
its consumed stage. Independent local reproduction found that a producer-valid
unresolved fixture is rejected by the success parser, and parser failure can
discard the guest exit before it is recorded. This is a confirmed harness defect,
not a proven explanation of the lost native result. The journal exposed only a
trusted systemd deactivation event, not recovered test assertions. R2 is a separate
reviewed derivative; no PASS is retroactively assigned to this attempt.
