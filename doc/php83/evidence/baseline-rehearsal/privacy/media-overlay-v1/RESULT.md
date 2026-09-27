# Real media functionality observed; final privacy window INCOMPLETE

Actual Codex native execution, started 2026-09-27 00:49:54 UTC, guest exit2,
stderr0, transient unit inactive after cleanup. This is NOT an overall PASS.

Observed successes on the PHP7.4 laboratory install with privacy overlay:
- New synthetic USER session and wrong-secret/admin-negative gates passed.
- One pinned 10-second synthetic source uploaded.
- Owned entry `0_i4z2bysv` (partner102) reached READY after27 polls.
- Original asset `0_ozqfxxfn`, version2, FileSync297 bound to that entry/tenant.
- Stored source and fixed-origin HTTP delivery both exactly matched SHA256
  `612d179c75f8f2374b7ac59c2dd7edba65e38eb357b870e8ad8c2e83d63b5473`.
- Filtered media.list matched the owned entry. The fixture is retained, not deleted.

Final media privacy audit and its failure-path audit raised `Incomplete`.
The harness retained only the exception class, losing scanner identity/reason.
Neither media privacy nor the full workload is accepted. No benchmark, TLS/HLS
matrix, decoder acceptance or PHP8.3 deployed-AIO claim is made.

Subsequent read-only diagnosis found410 unchanged path names, no removals/new
paths or file sizes below the earlier USER cutoff;12.77MB grew across20 files,
below the64MB file-scanner budget. A bounded historical journal type check found
87 records/106.5KB and no unsupported fields. Fresh file/journal scans and an
actual historical-journal cursor scan (317records/389KB) completed using NEW
random diagnostic patterns, not the original secrets. Those checks do NOT replay
or retroactively accept the lost original media window.

Non-append-only Sphinx data files are present in the broad log inventory, but
no causal attribution is proven and nothing was excluded/waived. Next replay
must retain precise phase/allowlisted code and private boundary metadata.

OpenCode actually executed18 preparation tests but missed missing ownership
joins; independent Codex found them. Strict tenant/entry/asset joins and negative
tests were then added; independent review executed21 tests with11 hashes intact.
