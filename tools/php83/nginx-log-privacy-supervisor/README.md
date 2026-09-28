# Bounded local nginx privacy guardian prototype

Not a VM executor, package, systemd unit or production approval. `guardian.run`
executes the explicit SHA256-allowlisted binary/config pair without a shell,
binds `<root>/syslog` before child startup, owns stdout/stderr pipes, and passes
both streams and Unix datagrams to the closed sanitizer. Only independently
schema-checked enum events reach exclusive-created 0600 rotated output files.
Input bytes, individual reads, elapsed time, output bytes and segment bytes have
bounds. An exception never exports its text. Socket disappearance, I/O failure,
parser failure, bounds, timeout, SIGTERM/SIGINT or caller stop terminate the
session process group and reap the direct child. This does not defend against
SIGKILL of the supervisor or privileged hostile process/config replacement.

Run from the main thread (signal ownership). `Spec.require_root=True` is the
default; root-owned 0700 working directory gives root-owned 0600 output.
`require_root=False` is only for explicitly unprivileged disposable fixtures.
No ownership changes or chmod occur outside the exclusively-created output files.

The caller must review and pin the complete configuration/include closure and
binary dependency identities before using the API. The prototype hashes the two
explicit paths, **not** includes or libraries; it does not claim safe arbitrary
nginx configuration. Configure foreground operation, the guardian's Unix socket,
stderr fallback and no raw file sinks. Do not expose real credentials in fixtures.
The socket is deliberately not removed after execution: preserve the disposable
root as evidence or let its owner discard it after all child processes finish.

API: `Spec(binary, config, root, allowlist=((binary, sha), (config, sha)), ...)`,
then `run(spec, sanitizer_module, stop=threading.Event())`. Import the reviewed
`../nginx-log-privacy/sanitizer.py` (frozen review identity
`b44f3cdc8c38c6c00a1ef099c0a4742650b3b209e70814924115c1c5f146fffb`).
The guardian additionally validates every event against its own finite schema.
No CLI wrapper is supplied, avoiding accidental production invocation.

Tests: `python3 tools/php83/nginx-log-privacy-supervisor/test_guardian.py`.
Eleven executed local tests cover simultaneous datagram/stderr/stdout handling,
canary non-persistence, fixed event schema, pin drift, parser/socket failure,
timeout/stop/signal reaping, output I/O failure, input bounds, output rotation bounds and 0600 creation. Native nginx
integration is separately owned by `nginx-log-privacy-native`; it is not implied
by these Python subprocess tests. Package/unit integration remains root review.
