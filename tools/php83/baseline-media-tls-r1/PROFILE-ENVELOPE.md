# Local native profile mutation envelope

> Historical preparation contract, NOT a rerun instruction. Actual R2 reached
> `NESTED_TRANSACTION` after native saves. A later independent read-only
> observation found the intended stored split, but atomicity/cache/selection
> remain unproven. Do not retry prepare/apply or call the original attempt a
> committed-success terminal. See `profile-native-attempt-r2.json` and
> `profile-recovery-native-r1.json` in the matching evidence directory.

No credentials in argv/environment/stdin, no API authentication or KS. Root
coordinator is the sole VM operator. This preparation is not actual DB
mutation, successful selection, HLS playback or full task acceptance.

## Frozen staging and execution

Create a fresh root-owned immutable staging directory (no reuse). Copy and
verify current reviewed source hashes for these files, all root0444:

- `profile_runtime.py`, `profile_envelope.py`, `profile_process.py`
- `credential_patterns.py`, `credential_read.py`, `privacy_logs.py`
- existing reviewed `install.py`, `observe_r2.py`
- frozen `baseline-freeze-r1/delivery_profile_split.php`
- existing `baseline-tls-r1/privacy_logs_r2.py`
- existing `baseline-freeze-r1/settle.py`, `convergence.py`
- exact public `pre-change-snapshot.json`, named `snapshot.json` in stage.

Runtime pins each imported own module and the native PHP payload, source
methods, existing legacy privacy stages and prior overlay manifest. Do not
modify old stages to make guards pass. Installed TLS8444 config and public
certificates must match reviewed identities. Root's current externally
verified snapshot receipt is an attestation, not an in-guest restore proof.

Run as a bounded transient root unit with name `baseline-profile-<8 lowercase
hex>`, `NoNewPrivileges=yes`, `IPAddressDeny=any`, allowed loopback IPv4/IPv6
and exactly192.168.56.74/32. Execute:

`python3 <fresh-stage>/profile_runtime.py <unit-name-without-service-suffix>`

The unit must allow native MariaDB loopback, read-only source/config/log
inspection and existing journal observation; it must allow only the intended
private state writes and native application's existing log/cache lifecycle.
Do not silently apply a strict filesystem sandbox that prevents creation of
initially absent `/var/lib/kaltura-baseline-delivery-split-r1`. Coordinate the
same reviewed bounded systemd strategy as the TLS lane. Root must serialize
all other API/background workloads during the finite windows. Source/runtime
child limits are60s wall,45/46s CPU,1GiB AS and64KiB per output pipe; privacy
convergence has separate unchanged finite bounds. Outer unit timeout must
cover preparation/apply plus audits; TERM triggers bounded cleanup/failure
scan, SIGKILL can leave ambiguous commit requiring snapshot/row inspection.

## Privacy and failure contract

Every inventory composes legacy sinks + Apache TLS logs + new nginx8444 logs.
The original file/journal boundary precedes private credential reads and all
native bootstrap execution. Exact fixed DB key `propel.connection.password`
and authorized root DB password remain in memory, scanned full +15-byte
prefix. This is explicitly NOT whole-bootstrap secret coverage.

Private child stdout/stderr are bounded and checked against these patterns;
only closed native JSON fields may enter public result. Full19-column backup
and precommit rows stay root0600, never public values/hashes. Backup file and
parent are fsynced before apply. Prepare privacy/guards must pass before
apply. No automatic apply retry or rollback. Original source and logging
configuration/runtime guards run after apply without requiring the old DB
protocol to remain null.

A success terminal is `NATIVE_PROFILE_SPLIT_COMMITTED_FINITE_PRIVACY`,
`privacy_passed:true`, `full_acceptance:false`, with native `profile_result`
containing allocated numeric HTTPS profile ID. Root exports/pins the actual
stdout/status receipt before any follow-up context observation. Presence of a
backup or apply-intent file is never success. Any failure after attempted
apply is recovery-required, even if a subsequent known-pattern audit passes.
