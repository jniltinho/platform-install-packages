# Separate bounded adapter

`lab_adapter.py` is a separate derivative; frozen `guardian.py` remains unchanged.
An independent reviewer reproduced the original guardian dropping burst stderr
on child exit (1506/2000 records, three runs). That negative result remains valid
for the original implementation and must not be relabeled a pass.

The adapter validates root ownership, non-writable ancestors, no ACLs/symlinks,
regular single-link files, <=64MiB input files, stable file identity and SHA256.
Its explicit allowlist must contain binary, config and imported sanitizer path;
callers must list/review other includes/dependencies, which are not discovered
implicitly. Production-policy mode requires UID0 and trusts no writable ancestor.
For disposable nonroot tests only, `fixture_roots=(absolute_private700_boundary,)`
explicitly limits trust to current-UID paths inside that boundary. This is not a
production-policy fallback or permission to use a world-writable binary parent.

`Spec(binary, config, root, socket_dir, sink_dir, allowlist, ...)` requires three
separate paths. Socket default0600; `socket_gid` optionally requires root plus
socket directory0750/matching GID and creates a0660 socket. Caller must separately
review that group's membership. Sink directory0700; output is dirfd-anchored,
exclusive-created0600, rotated with total and per-segment limits. No ancestor or
preexisting file permission is changed. No systemd/package/VM actions occur.

Exit/stop handling kills/reaps the child group, then drains bounded remaining
pipe bytes and queued datagrams, flushes partial lines and closes descriptors.
A drain/input/output failure produces fixed FAILED, never raw exception text.
The hard <=120-second lifetime remains, plus <=2-second final drain and bounded
termination grace. Draining cannot guarantee remote delivery or an infinitely
active external sender; exhaustion fails explicitly. Processgroups do not replace
service cgroup containment against guardian SIGKILL.

Own tests: `python3 tools/php83/nginx-log-privacy-supervisor/test_lab_adapter.py`
executes five cases, including2000 complete stderr lines plus a partial tail,
unsafe-parent rejection, explicit fixture policy, separate private paths and
socket-disappearance containment. Independent reviewer owns
`test_adapter_independent.py`; its outcome is separate. Real root-owned/dropped
worker/group socket behavior remains a separate test and service integration gate.
