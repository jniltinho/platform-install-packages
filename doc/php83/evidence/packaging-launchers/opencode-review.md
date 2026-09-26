# OpenCode independent validation — packaging-launchers literal inventory (repeat)

Executor: OpenCode (Muse Spark `opencode/muse-spark-1.3-contributor-free`), worktree only.
Reviewer: OpenCode self-check against `primary-r2.json` (independent re-execution, not author review).
Date (UTC): 2026-09-26. AGENTS.md read: coordination rules acknowledged
(Claude/Cursor/OpenCode CLIs, Codex coordinates, Grok deprioritized, no production/`.20`/publish scope).

Scope: DISTINCT repository-tracked public configuration literal inventory ONLY.
Denied operation NOT retried: no `/tmp` archive access, no archives/DEBs/VM/network,
no member extraction, no install, no secret access. No source/index edits
(`build.py`, helper, index untouched); only new outputs in
`doc/php83/evidence/packaging-launchers/` (`opencode-repeat.json`, this file).
Other workers active in worktree — untracked files observed, not touched.

## Actual commands and exits

1. `ls -l doc/php83/evidence/packaging-launchers/` + summary dump of `primary-r2.json`
   + `git rev-parse HEAD` + `git status --short` — exit 0.
   - `primary-r2.json` summary: tracked 1085, text_scanned 1045, binary 36,
     oversize 4, candidates 909, files_with_candidates 123.
   - HEAD `e5a586a4b1319a5fd4e74ae1432855211a7b3f44` == primary-r2 commit context.
2. `PYTHONDONTWRITEBYTECODE=1 python3 doc/php83/evidence/packaging-launchers/build.py --output doc/php83/evidence/packaging-launchers/opencode-repeat.json` — exit 0,
   stdout `{"candidate_rows": 909, "dispositions": {"binary_unscanned": 36, "oversize_unscanned": 4, "text_scanned": 1045}, "files_with_candidates": 123, "tracked_members": 1085}`.
3. Comparison script (primary-r2.json vs opencode-repeat.json) — exit 0:
   commit equal True; schema/status/scopes/listing_sha256/builder_sha256/matcher/
   summary/archive_access/application_execution/active_entrypoint_proven/
   T0_04_complete/limitations ALL EQUAL; `files` EQUAL; `candidate_rows` EQUAL.
4. Exclusivity re-run, same `--output` path — exit 1, `FileExistsError`
   (`open('x')` exclusive-create), confirming existing output must fail. No overwrite.
5. Anchor/hash/scope probes (python + grep, no archive I/O) — exit 0 (details below).
6. `sha256sum tools/php83/entrypoint-inventory/build.py` → `d2ed28e1...3702b3202`,
   matches pinned `HELPER_SHA`. `git status --short doc/php83/evidence/packaging-launchers/`
   shows the evidence dir untracked (new outputs only).

Limits: wall-clock foreground < 120 s; no broad code audit; no graph claims
(configuration-literal matches only); byte-compare of full JSON, not sampling.

## Results

- PASS — repeat reproduces `primary-r2.json` exactly: 1085 tracked members
  (1045 text scanned, 36 binary unscanned, 4 oversize unscanned), 909 regex
  candidate rows across 123 files. `files[]` rows (paths, git modes, blobs,
  sizes, sha256) and all `candidate_rows[]` byte-identical. Only allowable
  header variance (`repository_commit_context`) did not occur here (HEAD
  unchanged); no other-worker change was masked — `listing_sha256` equal proves
  the tracked listing is identical.
- PASS — tracked selected-roots read-only text scope: scopes
  `deb`, `RPM/SOURCES`, `build`, `.github/workflows` via `git ls-files -s -z`;
  `lstat` (no symlink follow; non-regular → `nonregular_not_followed`);
  2 MiB cap (`oversize_unscanned`); NUL → `binary_unscanned`; non-UTF8 →
  `nonutf8_unscanned`; unsafe/duplicate/unmerged members raise; re-hash guard
  aborts on mid-scan change. No link-following, member extraction, install, or
  secret access in `build.py` (grep: only `git ls-files`/`rev-parse` subprocess).
- PASS — reviewed matcher hash pin: `tools/php83/entrypoint-inventory/build.py`
  sha256 `d2ed28e1...3702b3202` verified pre-scan; mismatch raises
  `Reviewed literal matcher changed`.
- PASS — three real nested-variable launcher anchors exist with retained source
  hashes (owner `working_tree_sha256` == `files[]` sha256; 0 mismatches over 909):
  `RPM/SOURCES/kaltura-batch:55` (+ deb init mirror) `KP=...php [K]GenericBatchMgr.class.php...$1`;
  `RPM/SOURCES/kaltura-elastic-populate:65` `su $OS_KALTURA_USER -c "$PHP_BIN $ES_PLUGIN_SCRIPT..."`;
  `RPM/SOURCES/kaltura-populate:92` `echo "$PHP_BIN $SCRIPTEXE ..."`.
  (Shell-variable launchers of PHP; keyword hits: batch 12 / elastic 4 / populate 11 rows.)
- Explicit — false positives / unknowns / no archive-owner join: rows carry ONLY
  `interpreter/line/line_excerpt/owners/source_path/target/target_class` — no
  verdict/confidence/owner-join fields. Top hit source is
  `deb/kaltura-php/debian/changelog` (468 rows): literal regex matches in
  changelogs, NOT active paths. Flags: `archive_access False`,
  `application_execution False`, `active_entrypoint_proven False`,
  `T0_04_complete False`; limitations state regex overmatch, commit-as-context,
  no archive input, and no deployed-path/source-target/package-owner/
  reachability join.
- PASS — existing-output-must-fail confirmed (second run exit 1, FileExistsError).

Untested scope: denied `/tmp` archive operation (not retried per instruction);
deployed-path reachability; shell-execution semantics; release/acceptance gates.
Passing repeat ≠ application acceptance.
