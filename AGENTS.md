# Project agent instructions

<!-- codebase-memory-mcp:start -->
# Codebase Memory

For structural code discovery, prefer the `codebase-memory` skill and the
`codebase-memory-mcp` graph tools. Confirm index freshness before broad analysis;
use `check_index_coverage` for every file that supports a graph-based conclusion.
<!-- codebase-memory-mcp:end -->

## PHP 8.3 migration test coordination

For every migration validation cycle, involve the Claude CLI, Grok CLI and
Cursor Agent CLI (`agent`) in both test execution and independent review over
the cycle. Assign explicit, non-overlapping cases and rotate reviewers; an
author's review alone is not independent validation. Codex coordinates the
results. Use the actual CLIs, not another agent merely named after them.

Run independent reviews and isolated tests in parallel. Never run competing
writers, destructive fixtures or benchmark workloads against the same VM,
database or worktree; use separate disposable clones or serialize with an
exclusive owner. Every executor must stay within existing approved lab scope.

Record CLI availability/authentication/quota/permission failures as BLOCKED or
NOT_EXECUTED, not successful tests. Do not bypass safeguards to satisfy this
rule. A review is not execution evidence. If a CLI is unavailable, report the
gap explicitly and continue only independently authorized safe work.

Each result must identify the case, executor and reviewer, source/patch/harness
identities, environment, command, exit status, sanitized evidence and any
remaining limitation. Report executed cases, failures, untested scope and
release gates separately; passing harness tests does not prove full application
acceptance. Do not invent a completion percentage or release date.

These coordination rules do not authorize production changes, `.20` writes,
package/CI integration, publishing, or bypassing the migration proposal's
feasibility, release and cutover approvals.
