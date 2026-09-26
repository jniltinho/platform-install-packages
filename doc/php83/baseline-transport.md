# Total-deadline transport preparation

Local-only implementation; no VM, baseline workload or application acceptance.
The existing guarded_http.py and its fixed-origin policy are unchanged.

deadline_transport.get accepts only the exact production Origin type (literal
.74/.83, fixed scheme/allowed port). It retains explicit pinned private CA,
hostname verification, disabled ambient proxies, rejected redirects and bounded
body semantics. Its current interface remains GET-only.

Transport runs in a spawned child. URL/configuration travel through private
multiprocessing memory, not command arguments or logs. Bounded anonymous shared
memory carries at most the configured body limit; only a numeric length/error
status is returned. Child exceptions are not serialized, preserving URL privacy.
There is no blocking framed-pipe receive that can escape the parent deadline.

A monotonic request budget includes allocation, spawn, network/SSL/body reading,
child completion and copying the body back. Initial parent configuration validation
is outside that transport budget. On expiry, the parent terminates, waits at most
250ms, escalates to kill and waits another 250ms, then joins/closes the process.
Successful return requires a dead child and time remaining. This is an operation
deadline plus a separately bounded cleanup allowance, not a hard realtime promise
against OS scheduling stalls or an unkillable kernel task. Cleanup failure is
explicit and never accepted as request success. Request timeout never triggers a
retry or a fallback to relaxed origin/TLS settings.

## Executed local evidence

Initial eleven actual local tests passed (approximately 5 seconds): HTTP success with poisoned
proxy environment; real TLS success against a generated synthetic IP-SAN cert;
real wrong-CA refusal; redirect never forwarded; body limit; slow streaming that
exceeds total deadline without exceeding socket inactivity timeout; SIGTERM-
resistant worker requiring kill/reap; and public origin/parameter rejection.

Loopback fixture origins exist **only in the test module** and enter through a
private executor seam. The public get rejects that subclass and unmodified Origin
continues rejecting loopback. Synthetic certificate keys are temporary test data,
never copied into evidence. Tests assert no surviving multiprocessing request Process children
and shut down/join their local listener threads. No lab network was accessed.

Run:
    python3 -m unittest discover -s tools/php83/baseline-protocol -p 'test_deadline_transport.py' -v

Actual Claude executed the initial eleven tests and reviewed the first version.
It identified a real avoidable RawArray list allocation, now replaced by a byte
memoryview on both sides. Eight new tests cover the actual production worker
with mocked network boundary, public configuration rejection and a real
unframed response that exceeds read(limit+1). Actual OpenCode Muse independently executed all nineteen tests and reviewed
the corrected implementation (exit0, no blocking defect). A separate narrow
OpenCode follow-up executed nineteen tests again after two test-only proof
guards: actual /drip server receipt and a shared ready flag set only after the
SIGTERM-ignore handler is installed. Both pass, distinguishing genuine slow
transport/kill paths from a mere process-startup timeout.

The multiprocessing resource tracker may remain until the parent exits; it is
not a request worker and is not counted by active_children(). Anonymous shared
memory may use an unlinked backing file. Integration must use a standard
if __name__ == '__main__' runner guard because spawn imports that module. Integration into the baseline runner
remains coordinator-owned; API authentication/POST/upload, HLS/browser validation,
media timings, restore/recovery and full baseline acceptance remain open.

## Integration limit

A new worker is spawned for every GET. Parent elapsed time includes spawn and
copy overhead and must not be labeled server/API latency. Freeze an explicit
benchmark timing boundary before measured rounds; this safety wrapper does not
supply child-only transport timing or a reviewed reusable-worker protocol.
