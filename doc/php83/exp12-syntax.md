# exp12 whole-artifact compiler nonregression

**Executed and independently repeated; application acceptance remains open.**
Codex and actual Claude each ran23,568 native PHP8.3 compile processes:11,784
PHP-like files from each verified exp11/exp12 artifact. No application include,
bootstrap, SQL, SOAP module or package/production change was performed.

| Result | exp11 | exp12 |
|---|---:|---:|
| Files selected | 11784 | 11784 |
| Compiler accepted | 11777 | 11777 |
| Compiler rejected | 7 | 7 |
| Accepted with diagnostics | 66 | 66 |
| All diagnostic files | 73 | 73 |
| Incomplete subprocesses | 0 | 0 |

The three changed sources (Criteria, pakeApp, sfPakeGenerator) were already
compiler-accepted in exp11. All remain accepted without compiler-diagnostic
changes. Every unchanged source has identical outcome/diagnostics; seven residual
rejection paths are identical. Six are unsubstituted Symfony templates; one is
the previously rejected Riak legacy class alias. These are retained, not waived.
No three/four-newly-compiling-target claim is made.

The read-only stage is `/home/vagrant/php-candidate-syntax-exp12` on native83.
ZIP/source bytes are compared before/after, runtime executable/libraries/modules/
minimal INI and six staged tool hashes are checked before/after. Parent-pinned
tool hashes match. The sandbox denies network/socket access and runs only
`php8.3 -n ... -l`, with E_ALL and short tags. This is not full-system attestation.

Actual Claude R2 executed the complete paired scan, comparator and40 local tests,
all exit0. Reports are equal except explicitly normalized per-file duration_ns.
Codex independently reran the comparator; its bytes match Claude's comparator.
See [comparison](evidence/exp12-syntax/codex-compare.json),
[primary summary](evidence/exp12-syntax/primary-summary.json),
[actual CLI evidence](evidence/exp12-syntax/claude-r2-public.json) and
[public execution report](evidence/exp12-syntax/claude-r2-review.md).

## Retained incomplete attempts and review scope

OpenCode local-preparation CLI exited0 but stopped on a denied external-artifact
tool call and wrote no final review. It is explicitly INCOMPLETE, not approval;
the denied operation was not retried by the later repository-only Cursor review.
Cursor's review executed40 tests and found two stale operator-facing comparator
strings, corrected before the native phase with no gate-logic change. It did not
independently read host ZIP bytes; the explicitly authorized staged native scanner
subsequently verified its lab archives and extracted sources directly.

The first Claude native CLI returned while merely waiting, leaving empty output
and no scan exit marker. Parent checks found no surviving local SSH or remote
scan/transient unit. That attempt remains INCOMPLETE; fresh R2 output names
preserve it. R2 used synchronous completion and retained actual tool calls.
One oversized inspection result listing excluded files is bounded in the public
CLI log with a full-output hash; neither it nor hidden reasoning was mistaken
for native compiler proof.

Native83 was released after R2 terminated. No original ZIP, old experiment,
selected patch manifest or application acceptance checkbox was changed.
