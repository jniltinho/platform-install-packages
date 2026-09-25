# Exp11 whole-artifact paired syntax audit

Status: **bounded whole-artifact compiler regression passed in two actual runs;
seven rejections remain**. The initial null-pin preparation contract is preserved
in evidence. Final staging used the verified exp11 pin below. No application,
package or release acceptance follows from this compile-only test.

## Bounded contract

Compare pinned exp10
`de177e6cbaedf3a3207661c2325f466cce37febb73190f3a49d31f24b740c053`
against verified exp11
`f2474f5b951bfd2d121291025c8dd4554697fb5bb4024e132987643dab6144a7`,
using copied audited exp10-syntax machinery;
old tools and reports remain unchanged. Each ZIP is fully inventoried and source
files verified before/after. Every 11,784 PHP-family file (`.php`, `.phtml`, `.inc`,
`.php5`) receives native PHP8.3 `-n -l`, E_ALL and short tags. Other extensions are
explicitly listed exclusions, never silently treated as passed PHP files.

Exactly four changed PHP targets are expected: `baseObjectUtils.class.php`,
HTMLPurifier's autoload entrypoint, the full Symfony CLI entrypoint, and sfCore.
All other source outcomes and diagnostic text must match across artifacts.
Expected rejection reduction is 11 to 7, including still-rejected raw templates;
those remaining failures are neither waived nor called application-compatible.
Accepted files with diagnostics are distinguished from compiler rejection.
No missing/incomplete scan is acceptance.

## Isolation and repeat

Only exclusive native `php83lab` (`php83`, port 2200), never baseline74 or `.20`.
Fresh `/home/vagrant/php-candidate-syntax-exp11` stage; no overwrite/restage of
old artifacts. Source, full ZIPs and harness are mounted read-only; sockets and
network remain denied. No application includes, entrypoints, SQL or backend calls.
Runtime binary, linked-library hashes, native module list and no-INI identity are
recorded and verified unchanged. The scanner uses four compiler workers inside
one owned matrix, not competing external workload owners.

Codex primary and actual Claude independent repeat were serialized on that
lab. Actual Cursor local guards/reconciliation and OpenCode review are coordinated
separately; no new routine Grok attempt is required. Genuine execution is supported
by actual CLI command/tool-call evidence, not identical deterministic JSON alone.

38 local tests pass in `evidence/exp11-syntax/local-tests-r1.*`, covering archive
safety/hash drift, selected paths, missing/duplicate rows, strict integer exits,
compiler command and diagnostic preservation. These are local harness tests,
not executed PHP runtime evidence. The collector/report statuses remain typed;
independent comparison ignores only per-record durations.

## Actual primary and independent compiler results

Two complete runs are recorded in [primary.json](evidence/exp11-syntax/primary.json)
and [claude-scan.json](evidence/exp11-syntax/claude-scan.json). Both runner exits
are 0 and runner stderr is empty. [Independent comparison](evidence/exp11-syntax/claude-compare.json)
ignores only per-record elapsed durations; every other recorded field matches.
Actual Claude CLI commands/tool calls in its second-invocation stream establish
fresh execution, not report equality alone. The CLI, its 38 local tests and its
host comparator each returned exit 0.

| Artifact | PHP-family files | Accepted | Rejected | Incomplete | Diagnostic files | Accepted with diagnostics |
|---|---:|---:|---:|---:|---:|---:|
| exp10 | 11,784 | 11,773 | 11 | 0 | 77 | 66 |
| exp11 | 11,784 | 11,777 | 7 | 0 | 73 | 66 |

Each run executes 23,568 individual compiler processes: 11,619 `.php` and 165
`.phtml` files per artifact; `.inc` and `.php5` inventories are zero. Each of the
four reviewed changed targets moves from rejection 255 to acceptance 0 with no
candidate diagnostic. All unchanged sources retain exactly the same outcome
and diagnostic text. Sixty-six accepted files still have diagnostics; compiler
acceptance is not warning-free application compatibility.

The seven rejected paths remain explicit:

* `vendor/aws/Doctrine/Common/Cache/RiakCache.php`
* `vendor/symfony-data/generator/sfPropelAdmin/default/skeleton/actions/actions.class.php`
* `vendor/symfony-data/generator/sfPropelCrud/default/skeleton/actions/actions.class.php`
* `vendor/symfony-data/skeleton/batch/default.php`
* `vendor/symfony-data/skeleton/batch/rotate_log.php`
* `vendor/symfony-data/skeleton/controller/controller.php`
* `vendor/symfony-data/skeleton/module/module/actions/actions.class.php`

Their unchanged compiler failures are not waived by template classification.
Whole-artifact counts are 15,236 versus 15,240 verified files; four added patch
provenance files are non-PHP exclusions. Native runtime identity is PHP8.3.6
without INI; binaries, linked libraries, native module inventory, full source,
ZIP and frozen harness identity checks pass before/after. The independent run
uses the same VM/runtime, not a second-platform compatibility claim.

## Preserved attempts and evidence boundaries

The first actual Claude invocation returned exit 1 before compiler execution
because its variadic CLI option consumed the positional prompt. It is retained
as **NOT_EXECUTED**, not a failed PHP test or a pass. The corrected stdin-prompt
invocation uses new `claude-cli-r2-*` evidence and performed the fresh scan.
The initial local repeat-ZIP discovery looked for two ZIPs in one directory and
stopped; the actual second build lives in sibling `exp11-repeat`. The corrected
local byte/hash verification is recorded in
[artifact-verification.json](evidence/exp11-syntax/artifact-verification.json).
No ZIP or prior report was modified to satisfy either check.

The primary self-comparison artifact is only a host-comparator sanity check;
it is not independent execution. Cursor's initial prep review returned exit 0
with 38 local tests and unchanged frozen inputs, while the candidate pin was
still pending. Its final local full-report reconciliation is tracked separately.
OpenCode artifact review belongs to the separate candidate build cycle; this
compiler audit does not relabel that review as runtime execution.

This bounded evidence closes only the four-source compiler-regression check.
`candidate_all_files_compile` and `application_acceptance` remain false. There
are no application includes, autoload or task runtime, SQL, backend, package,
release, deployment or production operations here.

For commit-safe execution evidence, Claude streams retain only current actual
tool calls/results, task-completion metadata and the public final result.
Lifecycle-hook historical context and explicit reasoning blocks were removed;
original hashes, event counts and the sanitizer policy are preserved in
`claude-stream-sanitization.json`. There is no raw reasoning archive. The initial
non-executing CLI failure retains its original exit/stderr and stream hash even
though it had no current tool-call events to retain.

## Final independent local reconciliation

Actual Cursor's final local invocation completed exit 0:
`cursor-final-review.json` records 38 passing tests and an independent host
comparison of the two genuine runtime reports, exit 0. All 11 frozen inputs
remain unchanged. It confirms the exact counts, four repaired paths, unchanged
outcomes/diagnostics and all seven retained rejections. This is local evidence
reconciliation, not another guest execution. The completed bounded cycle is
ready for a source-validation checkpoint; broader application/release gates
remain open.
