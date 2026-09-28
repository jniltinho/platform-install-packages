# Bounded nginx adapter correction

2026-09-28. Partial local milestone; OpenSpec remains 4/51.

The frozen guardian's independently reproduced loss of 494/2000 stderr events
remains negative evidence. A separate `lab_adapter.py` fixes bounded exit draining,
separates socket/event paths and adds explicit trust/pin checks. Its final SHA256:
`090c5e8faaf9a0fc468ad31994b2077cc8b50858b3577a0d1c7e327433be1af5`.

## Executed validation

- Author and coordinator: 5 adapter tests, exit 0, including 2000 complete
  stderr events plus a partial tail producing 2001 closed-schema events.
- Independent Codex reviewer and coordinator: 9 additional tests, exit 0,
  including pinned identity, unsafe ancestry, ACL mock rejection, symlink and
  hardlink rejection, required sanitizer pin and exit-tail capture. A transitional
  run correctly failed the old e888 source pin after the reviewed correction;
  that mismatch was not counted as a pass.
- Independent native executor and coordinator: 4 native cases, exit 0, using the
  exact lab2 nginx binary and current host libraries. Native tests use the actual
  pure access-format transform, verify custom method maps to OTHER, observe
  worker replacement after reload and subsequent requests, verify reopen, and
  exercise collector loss plus startup/invalid-reload errors. Closed outputs had
  no synthetic canary; direct child reaping and listener closure passed.
  See `../nginx-log-privacy-native-r1/lab-adapter-integration-r6.json`.

These are separate suites, not 18 completed OpenSpec tasks. The actual Cursor
review remains NOT_EXECUTED due authentication (previous milestone). No external
CLI failure is relabeled as a pass.

## Remaining

This is still a <=120-second local adapter, not an installed service. Actual
root-to-kaltura privilege separation, group membership, complete effective
configuration/includes/libraries, systemd cgroup cleanup, safe configuration-test
and package-hook paths, access rotation, fresh offline APT and lab HTTP/RTMP
binding validation remain required before deployment acceptance. Production and
workers are unchanged. No new task-completion email was sent.
