# Provider decision draft — Cursor independent review

- Case: `doc/php83/provider-decision-draft.md` + `evidence/provider-reconciliation/`
- Reviewer/executor: Cursor Agent (actual CLI reviewer), repository-local only
- Environment: worktree only; no VM, network, external FS, package/CI/tasks, or source edits
- Date (UTC): `2026-09-26T17:05:35Z`
- Author of draft/join: Codex (this review is independent of that authorship)

## Verdict

**PASS — no actionable factual errors.** The draft accurately consolidates recorded
provider evidence without selecting a provider, without overclaiming support or
security coverage, and without inventing stronger release gates. External URL /
calendar claims were **not** re-fetched here; per assignment they were checked by
Codex on 2026-09-26.

## Executed (synchronous)

| Step | Result |
|---|---|
| `python3 …/build.py --output …/cursor-repeat.json` | exit **0**; wrote `cursor-repeat.json` |
| `cmp -s primary.json cursor-repeat.json` | exit **0** (byte-identical) |
| SHA-256 both | `a6dc6f58bae355d8a9bfbfcbd973f03796dbea02a9a02de7567eb28fb80b85ae` (38174 bytes) |
| Rebuild to same path again | exit **1** `FileExistsError` (refuses overwrite, as designed) |
| Recount from `primary-report.json` + `independent-report.json` | **18** rows; **9** unique `(target,method)`; 9+9 by evidence |
| Module tokens on all 18 source probes | `soap` **0**; exact `apc` **0**; `apcu` **18/18**; `memcache` **18/18** |
| `primary.json` input sha256/bytes vs live files | **9/9 OK** |
| Linked local docs exist | `provider-runtime.md`, `apcu-cache.md`, `apcu-web.md`, `xml-lifecycle.md`, `riak-provider.md` |

Unique combinations verified: noble/resolute/remi × CLI/GET/POST. PHP/SAPI strings match the draft table (noble `8.3.6` apache/cli; resolute `8.3.35` apache/cli; remi `8.3.35` fpm/cli). Rocky AppStream memcache/ssh2 failure is present in `provider-runtime.md`.

## Draft boundary check

| Separation | Finding |
|---|---|
| Historical 35/36 probe vs application inventory | Stated; `full_extension_use_inventory: false`; T4-01 / T1-03 / packaging gate left open |
| Private Noble SOAP fixtures vs installed services | Stated as coverage gap; not retrofitted into the old probe; Resolute/Remi SOAP not claimed tested |
| Real application acceptance | Explicitly not closed; `provider_selected: false`; no production/`.20` approval |
| Update/support policy | Finite PHP 8.3 window + no transfer of extension SLA; Sury/Remi guides treated as config provenance, not support promise |
| Provider choice | Candidates/preferred-by-design only; no stack selected |

## Actionable errors

**None.** Optional editorial nits only (compact missing spaces such as `records18` / `historical35` / `checked2026`) — not factual blockers and not corrected here.

## Explicit non-claims of this review

- Not web retrieval of php.net / Sury / Remi pages
- Not runtime/VM re-probe; `runtime_executed_now: false` retained
- Not feasibility go/no-go, package/CI integration, or release approval
- Review ≠ execution evidence beyond the local rebuild/compare above
