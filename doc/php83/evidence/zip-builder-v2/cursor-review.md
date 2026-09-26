# Cursor independent review — zip-builder-v2

| Field | Value |
| --- | --- |
| Case | Synthetic new-file support (`operation: add`) for held XML helper staging; not selected manifest / artifact build / packaging |
| Executor | Cursor Agent CLI (this session) |
| Reviewer | Cursor Agent CLI (independent of author primary run) |
| Branch | `proposal/migrate-kaltura-php83` @ `d171110f00fc46d7654950f2ddc2f3f767c9bba0` |
| When (UTC) | 2026-09-26T17:24:30Z |
| Scope | `tools/php83/zip-builder-v2/{build.py,test_builder.py}`, `doc/php83/zip-builder-v2.md` |
| Compare-only (unread-only edits) | `tools/php83/build-experimental-zip.py`, `tools/php83/test_experimental_zip.py` |
| Lab bound | Repository-local only; `TMPDIR` under worktree; no `/tmp`, Rigel ZIP, bundle, VM, or network |
| External archive denial | Not retried |

## Source identities (SHA-256)

| Path | sha256 |
| --- | --- |
| `tools/php83/zip-builder-v2/build.py` | `3fc3e7f1524c044ef91f390cd6e4836bfeb6b9442ab45fefa6c07d6fcaba1707` |
| `tools/php83/zip-builder-v2/test_builder.py` | `4ffd489ce300efbca0fa40738a09e5d3c15a947284073f4d53f883d84d34344e` |
| `doc/php83/zip-builder-v2.md` | `7a9add7da680a3418ff33775fe498c52c3bf2a2836d7d9bf101ca1c2f4ef4f3d` |
| `tools/php83/build-experimental-zip.py` (legacy, read-only) | `055443730325459ff2f4e5ad093542e3aa544f6d82af8b21174027f5cdbf523e` |
| `tools/php83/test_experimental_zip.py` (legacy, read-only) | `ed605fc266e29c2ee564e5e568a0a634cfe2b3974b28fd4215c7ae400e74b573` |

Legacy git index blobs unchanged (`git status` clean for both legacy paths; `git hash-object` matches `git ls-files -s`). v2 is a separate tree; old builder was not silently edited.

## Environment

- Python `3.12.3`
- GNU patch `2.7.6` (`/usr/bin/patch`)
- `TMPDIR=$PWD/tools/php83/zip-builder-v2/.scratch`
- `PYTHONDONTWRITEBYTECODE=1`

## Command and exit

```sh
mkdir -p tools/php83/zip-builder-v2/.scratch doc/php83/evidence/zip-builder-v2
TMPDIR=$PWD/tools/php83/zip-builder-v2/.scratch PYTHONDONTWRITEBYTECODE=1 \
  python3 -m unittest discover -s tools/php83/zip-builder-v2 -p 'test_*.py' -v
```

- Exit: `0`
- Result: `Ran 24 tests in 0.027s` → `OK`
- Composition: 13 inherited `ZipTests` controls + 11 `BuilderV2Tests` addition controls (all synthetic local ZIPs)

All 24 method names observed OK in this run:

Inherited: `test_archive_traversal_rejected_even_with_matching_hash`, `test_existing_output_preserved`, `test_later_patch_cannot_mutate_earlier_verified_output`, `test_offset_rejected`, `test_output_hash_mismatch_rejected`, `test_patch_cannot_collide_with_metadata`, `test_patch_drift_rejected`, `test_preserves_comments_and_executable_bit`, `test_rejects_reserved_source_metadata`, `test_rejects_symlink`, `test_reproducible_and_original_unchanged`, `test_source_drift_rejected`, `test_unsafe_paths`.

New: `test_add_after_hash_enforced`, `test_add_existing_directory_rejected`, `test_add_existing_source_rejected`, `test_add_header_enforced`, `test_add_implicit_directory_rejected`, `test_add_requires_explicit_null`, `test_add_reserved_target_rejected`, `test_add_under_file_rejected`, `test_added_source_twice_reproducible`, `test_replace_cannot_use_null`, `test_unknown_operation_rejected`.

## Checklist (new paths + inherited contracts exercised by harness)

| Check | Result |
| --- | --- |
| Explicit `operation: add` + `before_sha256: null` required | PASS (`test_add_requires_explicit_null`; gate uses default `'missing'` so omitted key fails) |
| Replace cannot use null before | PASS (`test_replace_cannot_use_null`) |
| Safe absent path (no file/dir/implicit-child collision) | PASS (three collision rejects) |
| Parent regular-file collision | PASS (`test_add_under_file_rejected`) |
| Reserved `.php83-experimental` target | PASS |
| Exact `--- /dev/null` / `+++ b/<path>` headers | PASS |
| `after_sha256` after full series | PASS (`test_add_after_hash_enforced` + inherited cross-patch mutate control) |
| New entry mode `0644`, fixed `STAMP`, two-build byte identity, upstream bytes unchanged | PASS (`test_added_source_twice_reproducible`) |
| Unknown operation rejected | PASS |
| Old builder file not modified | PASS (git clean; v2 separate) |
| Hostile-archive resource sandbox beyond trusted signed local inputs | Out of scope (per review brief); not required |

## Code review notes (new paths only)

Direct diff against legacy `build()`: v2 adds `operation` (`replace`\|`add`), reserved-target and non-directory target checks, add collision/parent/header staging, `added_sources` merge into sorted ZIP members with fixed `0o100644`, and `builder_format=2` plus v2 `builder_sha256` in embedded metadata. Replace-default path still stages from upstream and rehashes every output after the whole patch series — same post-series contract as legacy.

No concrete harness failure observed. Negative controls for add collisions, null-before, headers, reserved path, and after-hash are aligned with the gates they name.

Soft observation (not a FAIL): there is no separate test that feeds `operation: add` with a non-null string `before_sha256`; the same gate rejects it, but the named control only deletes the key. Not a silent acceptance path.

## Graph / discovery boundary

This migration worktree is not the indexed packaging project. Sibling index `home-nilton-Projetos-nilton-NOVOS-platform-install-packages` generation `2026-09-25T19:28:02Z` reports legacy and v2 builder paths with `freshness: missing` / recommend read-source. Conclusions use direct file reads only. No graph completeness claim. No reindex (others active; no index/source changes).

## Untested / release gates (explicit non-claims)

- Not a selected cumulative manifest or held XML helper application acceptance
- No real Rigel archive / published bundle / two-build production artifact identity
- No package/CI integration, `.20` write, or cutover approval
- Passing 24 synthetic tests ≠ full application acceptance

## Verdict

**Harness: PASS (24/24, exit 0).** New-file support behaves as documented for synthetic fixtures. Legacy builder untouched. Independent review finds no concrete failure or bad negative control that silently accepts an unsafe add. Remains lab-only builder support, not release evidence.
