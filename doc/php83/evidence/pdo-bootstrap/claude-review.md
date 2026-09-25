# Claude CLI independent bootstrap review

English summary by Codex; the original CLI-written report is retained verbatim
in `claude-review-original.txt`, with the CLI response in
`../exp9-candidate/agents/claude-bootstrap.json`.

Claude executed the collector on exclusively owned baseline74, exit 0. Both
variants pass 23 rows; the owned SQL unit stops inactive. Claude also executed
11 local tests, all passing, reported in its CLI response rather than a separate
test-log file. Its artifact/harness/collector/helper identities, typed rows,
source hashes, diagnostics and stdout hashes equal the corrected primary report.
The raw stderr hashes differ; because raw logs are not retained, their cause is
not independently established and must not be asserted to be only timings.

Exactly nine exp8-to-exp9 return slots change null to bool. Other tested data,
cache identity, dry-run and exception values agree. Seven real dependency hashes
match their artifact; only the two patched dependency hashes differ by variant.
The failed first fixture is retained, and its sole correction is mapping the
named SQL parameter explicitly. No application bytes changed for that correction.

Remaining limits: retained synthetic datadirs, no structured partial report on
mid-collector exceptions, inherited copied-runtime/SQL binary provenance and SSH
host-key policy, only seven runtime class hashes supplemented by full extracted
ZIP verification, no full application acceptance. Equal API responses do not
prove that no caller consumes the changed return values. Claude released the lab
without production, publishing or commit actions.
