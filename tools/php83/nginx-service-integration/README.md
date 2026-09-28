# Fixed bounded lab service integration candidate

No installation is performed here. `generate.artifacts()` returns the complete
`kaltura-nginx.service` and replacement init script; `generate.manifest()` joins
reviewed complete config-directory regular-file pins with fixed binary/adapter/
sanitizer identities. Deploy only after independent review and root approval.

## Fixed start contract

- Wrapper `/usr/local/lib/kaltura-nginx-lab/service.py`, invoked by
  `/usr/bin/python3 -I -B`; adjacent adapter090c and sanitizerb44f frozen.
- Manifest `/etc/kaltura-nginx-lab/manifest.json`, root-owned non-writable trusted
  ancestry, schema1/seconds120/socket_gid7373. Every start repeats the fixed .83 hostname,
  machine hash/IP exclusion and native held-marker checks. Duplicate keys reject.
- Canonical config `/opt/kaltura/nginx/conf/kaltura-nginx.conf`; every regular file
  in the configuration directory must be in the exact manifest. Both original
  symlinks are separately authenticated: nginx.conf -> canonical config and
  server.conf -> sibling kaltura.conf. No generic symlink exemption or implicit
  include discovery. Preserve MIME/base/cors pins as well as generated configs.
- Unit creates `/run/kaltura-php83-nginx-log` root:root0750, initially empty.
  Wrapper changes only that owned runtime leaf's group to the reviewed socket_gid;
  adapter creates root:group0660 syslog. Root/worker traversal and group membership
  are checked against actual observed kaltura UID/GID7373 and explicit group
  members `['www-data']`, with only kaltura using that primary GID. Membership is
  preserved, never changed. Legitimate www-data can forge closed diagnostic
  events; these events must never authorize actions. No application log parent changes.
- Prepare `/var/lib/kaltura-php83-nginx-log-sink` root:root0700. Each start creates
  a fresh root:root0700 run directory; closed0600 rotated events and terminal.json
  stay there. No raw native stderr or stdout inherits journald. Unit null stdio
  is a transport containment backstop, not a replacement for sanitized diagnostics.
- Renderer must direct native error syslog to the exact socket. Scalar access
  sink `/var/lib/kaltura-php83-nginx-access/access.log` remains the separately
  reviewed renderer/executor's ownership/bound/rotation obligation.

The replacement init supports normal start/stop/restart/status through systemd.
Reload, force-reload and configtest reject explicitly: none can launch raw nginx.
The package must install this unit/init/closure before its first restart, and its
fresh-start guard must explicitly pin these new bytes rather than forbid units.
Do not invoke the old init once the supervised layout is installed.

`Type=simple` start success does NOT prove readiness. Executor must observe root
master/worker identities, exact allowed listeners and synthetic response. Wrapper
unexpected childexit, timeout or failure returns1. Operator stop returns0 only
when child is reaped. Lifetime120s is intentional; no automatic restart. Expiry
is a contained bounded probe result, not permanent service acceptance.

## Actual cgroup containment probe for root

Use a separately reviewed synthetic harness under the exclusive approved guest
fixture directory. This fixed-path installed wrapper cannot be pointed at an
arbitrary prefix without changing its reviewed bytes; clearly label transient
harness evidence as unit/cgroup semantics, not exact installed-wrapper execution.
Match Type=simple, User=root, KillMode=control-group, Restart=no,
TimeoutStopSec=6, RuntimeMaxSec=126 and SIGTERM->SIGKILL semantics. Give the harness
private captured/sanitized child diagnostics and root-only receipts, not raw
systemd stdout. Have it spawn a synthetic child plus grandchild in the unit.

1. Start the uniquely named transient fixture unit and attest MainPID,
   ControlGroup, active state, child's+grandchild's exact process start identities.
2. Request SIGKILL of **main only** (`systemctl kill --kill-whom=main
   --signal=SIGKILL <exact-fixture-unit>`). Do not kill all first; that would not
   prove automatic residual cgroup cleanup.
3. Bound observation until unit terminal and cgroup has no live members; verify
   recorded descendants no longer live and no listener remains. On incomplete
   cleanup, explicitly contain the entire exact fixture unit and record failure.
4. Separately test normal stop and120s expiry. No raw logs, no guessed production
   service name, no daemon restart loop. Cleanup transient state only after root
   preserves sanitized evidence and verifies all descendants gone.

Local pure checks: `python3 tools/php83/nginx-service-integration/test_service.py`
(11 tests). These do not execute a unit, root wrapper, package hook or guest.
