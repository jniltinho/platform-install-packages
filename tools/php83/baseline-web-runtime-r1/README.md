# Separate current Apache PHP7.4 probe

Current result: root executed frozen r4 successfully; independent closed-receipt
review accepted PHP7.4.33/apache2handler and53 loaded modules, nonce match, owned
file removal, inactive unit and unchanged VM. See
`doc/php83/evidence/baseline-web-runtime-r1/native.json` and
`doc/php83/evidence/baseline-freeze-independent-r1/web-runtime-native-review.json`.
The fresh stage is now consumed: do not rerun this wrapper automatically. Earlier
pre-execution review notes below are retained as history, not current status.
This is not full application/baseline acceptance.

Root coordinator only. This case creates one random-named PHP file under the existing installed vhost, posts a synthetic nonce and verifies owned-inode cleanup. No app bootstrap/credentials/DB, service restart, configuration or package changes. Passing means only that this exact current route returns PHP7.4 apache2handler and the expected php.ini path/module names; never full baseline acceptance.

The PHP expression is byte-equal to pinned legacy probe code (AST-expression test); request uses unchanged legacy._probe_worker, guarded origin and30s/64KiB bounded process. The legacy probe's unchecked path/return projection is replaced by this narrow owned-file wrapper. No old media main executes.

## Safe blockers / metadata

Guest must be root on kaltura-php74-baseline/.74 and not carry .20/.21/.30/.83. Every `/opt/kaltura/app/api_v3/web` ancestor must be nonsymlink root:root directory, no xattrs, mode0755;0775 only when supplementary and primary root-group membership is exclusive to root. Other actual legitimate ownership requires separate review, never automatic chmod. File creation O_EXCL/NOFOLLOW; existing/symlink names not touched. Cleanup requires original device/inode/rootowner/singlelink and exact bytes; changed/replaced file is retained and operation fails. Strong unit termination can leave its own probe; failed/incomplete receipt requires root inspection, not assumed cleanup or automatic replay.

Host Vagrant UUID9e954729-16f3-4eda-9db5-b94e5ada9e44, exact name/resources/NAT forwarding; strict config and public hostkey hashes are reused from reviewed R2 support. This is the previously documented local TOFU identity, not out-of-band provisioning. `/var/lib/kaltura-baseline-web-r1` must be absent. Fresh stage is root-owned, source files0444 and manifest pinned; no reuse. Unit is .74/loopback only,60s lifecycle,90s hostbound,128KiB capture, readonly filesystem except exact webparent; private diagnostic output is unnecessary because there are no app secrets. Host result writes exclusive path, no raw HTTP/stderr.

## Coordinator invocation after independent review

```
python3 -B tools/php83/baseline-web-runtime-r1/run.py --output <new-check.json>
python3 -B tools/php83/baseline-web-runtime-r1/run.py --execute --output <new-actual.json>
```

First command performs bounded read-only target/path preflight (no probe/stage). Execution repeats preflight then stages and runs. It is NOT safe to replay after a failed consumed stage. No operator should use a symlink/shared untrusted host output parent.

Local test command: `PYTHONDONTWRITEBYTECODE=1 python3 tools/php83/baseline-web-runtime-r1/test_web.py -v`. Twelve tests passed, including real temporary-file cleanup/timeout/drift, nonce-before-open, occupied/symlink rejection, root-group/metadata negatives, exact legacy PHP expression, response/FPM rejection and closed host projection. Test cleanup models root ownership under unprivileged temporary directory; this is not native root/web/Apache proof. Actual CLI independent review and guest execution remain pending, not PASS.

Review correction: TERM/INT handlers now raise a controlled interruption before entering owned-probe work, allowing its inode-bound finally cleanup; repeated TERM/INT are ignored during that cleanup. Actual isolated subprocess SIGTERM test verifies immediate owned-file removal (13 tests total). SIGKILL/host failure cannot guarantee cleanup and remain failed/incomplete requiring root inspection. Initial twelve-test freeze remains historical in evidence/frozen.sha256; revised pins are frozen-r2.sha256. No VM run.

Final signal refinement (frozen-r4.sha256): block TERM/INT from O_EXCL creation through complete write/fsync/close and during inode/hash/unlink cleanup. Unmask inside the outer try only once bytes are cleanup-verifiable. This handles a first signal in normal cleanup and a queued signal during initial write, without permitting removal of arbitrary changed files. Local13tests still pass; independent reviewer is checking these deltas. Disk-write failure or SIGKILL still fails closed and can require explicit own-file recovery.
