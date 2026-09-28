# Nginx privacy preparation — partial local milestone

2026-09-28. OpenSpec remains 4/51 complete; no new acceptance checkbox.

## Executed

- Codex sanitizer author and coordinator independently ran 12 Python tests: exit 0.
- Codex guardian author and coordinator independently ran 11 Python subprocess tests: exit 0.
- Coordinator authored three hash-bound configuration transforms; a separate Codex reviewer independently ran all 6 tests: exit 0. Source templates, error severity, safe scalar fields and unchanged RTMP/tuning were inspected.
- Independent native fixture executor used exact nginx binary SHA256 `1a995dddd470f013258b1890cfc7c9e3b10c344461eb085de6b2ef8f991faec0` with installed host libraries, not an installed lab service. Four guardian cases passed: reload/reopen and subsequent requests, collector disappearance, invalid startup, invalid reload retaining old workers. Synthetic canaries were absent from persisted event/access output; listeners closed and direct children were reaped. See `../nginx-log-privacy-native-r1/guardian-integration-r2.json`.
- The earlier syslog-only foreground fixture leaked synthetic request data to stderr even with a collector. It is retained negative evidence, not a pass or proof of deployed-daemon behavior.

## Actual external CLIs

Claude returned exit 0 for bounded advisory reviews. Reviews are not executions. The design review reported two read-only shell operations despite its requested read-only-tool constraint; no mutation was reported. Findings include classification spoof resistance, fallback template coverage and explicit private output permissions. Native review correctly limited foreground observations and required requests after reload/reopen.

Cursor's guardian review attempt returned exit 1 with authentication required. Review NOT_EXECUTED; no credential changes or authentication attempts. Codex review does not relabel this failed CLI attempt successful.

## Frozen implementation identities

- Sanitizer: `b44f3cdc8c38c6c00a1ef099c0a4742650b3b209e70814924115c1c5f146fffb`
- Guardian prototype: `498269bbef1c5a68ffedc4ba5f6215cd4662c3dcc7d0ef5ee2bc4d3b3f7ecc21`
- Pure template transformer: `af2e7e54c9196df2d65e67fb22c428c485b97e00d45935517a5c6a83f72f44ce`

## Remaining deployment prerequisites

The guardian is deliberately a <=120-second disposable fixture, not a daemon. Its single 0700 working directory cannot directly serve dropped-privilege kaltura workers. Complete include/library identities, trusted owner/ancestor checks, exit-time pipe draining, root/private sink and worker socket separation, bounded operational lifetime policy, rotation and systemd cgroup cleanup must be reviewed before packaging. Pure transforms do not provide those facilities. Full effective native configuration and installation/restart behavior remain untested.

No VM, package installation, production, worker release, full application acceptance or release approval is claimed. Existing D2 installation is preserved. No new task-completion email is warranted by these partial tests.

## Independent review finding after the passing fixtures

A separate Codex reviewer reproduced an exit-drain defect in the frozen guardian:
a synthetic child emitted 2,000 stderr records and exited, but each of three runs
persisted only 1,506 events. Passing the 11 original tests therefore does not
establish complete diagnostic capture. A separate adapter/revision and regression
are required; the frozen prototype is NOT approved for deployment. Reload signal
plus subsequent 404 requests also does not prove successful worker replacement.
