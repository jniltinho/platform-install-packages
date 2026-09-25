# Exp11 paired compile-only audit

Copied bounded machinery from `../exp10-syntax/`, preserving that completed experiment.
Requires verified exp10 and exp11 archive pins and exact four changed source hashes.
A null/missing candidate pin fails closed. No artifact may be guessed.

On exclusively owned php83lab only: fresh stage, archive paths/hashes validation,
read-only source/ZIP/tool binds, native PHP8.3 `-n`, E_ALL, short tags, `-l` only.
Private network and denied socket/socketpair remain unchanged. There is no application
body/include/entrypoint, SQL, backend or package/release work.

Every 11,784 PHP-like file is scanned per artifact; unchanged results and diagnostics
must match; exactly four reviewed rejected targets must compile. Expected residual
seven compiler rejects (including raw templates) are retained, never waived.
Diagnostics on accepted files are distinguished from rejection.

Independent genuine execution is established by CLI command/tool-call evidence,
not deterministic JSON equality alone. Comparator ignores only per-record timings.
Use new evidence/stage paths; never overwrite an old attempt.
