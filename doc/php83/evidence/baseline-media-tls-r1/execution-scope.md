# Additive media TLS8444 — executed lab scope

Root coordinator executed the independently reviewed installer2822c11f with
observer14c9a9c4 on the UUID-pinned PHP74 lab only. Sources were staged root-owned
0444 in `/var/lib/kaltura-baseline-media-tls-tools-r1`. Host strict-SSH pins,
resource/UUID checks, previous inactive unit and snapshot existence were checked.
The snapshot is private recovery state, not a completed restore rehearsal.

Actual guest dispatch:

```text
systemd-run --quiet --wait --pipe --collect --unit baseline-media-tls-install-r1
  -p RuntimeMaxSec=180 -p TimeoutStopSec=30 -p KillMode=control-group
  -p IPAddressDeny=any -p IPAddressAllow=localhost
  -p IPAddressAllow=192.168.56.74/32 -p NoNewPrivileges=yes
  /usr/bin/python3 -B /var/lib/kaltura-baseline-media-tls-tools-r1/install.py --execute
```

The outer SSH capture was bounded to240seconds. The unit exited0 and became
inactive; stdout was projected into native-install-r1.json, stderr was empty.
No strict filesystem sandbox is claimed: exact source/path/hash/metadata guards
controlled the required creation and atomic replacement. The new state directory
and both logs were independently observed root-owned0700/0600 afterward, without
reading log contents. Private key bytes were not exported or hashed.

The actual native nginx configuration test, trusted-CA handshakes on443/8443/8444
and wrong-CA rejection passed. HTTP88 listener presence was preserved; this does
not establish HTTP response-content equivalence or complete application behavior.
The exact base.conf hash matches the repository file: its two access-log directives
are `off` for the status endpoints, not media log destinations. The new media
server uses scalar access logs and a private error log. Both paths must be joined
to every credential-window log inventory before any authenticated media traffic.

No database profile, returned URL, source package, production host or release was
changed. Profile1001 still produces HTTPS88 until the separately reviewed native
protocol split is performed. No HLS acceptance or OpenSpec task completion follows.
