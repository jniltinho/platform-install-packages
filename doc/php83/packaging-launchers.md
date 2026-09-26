# Packaging repository launcher candidates

2026-09-26 — actual repository-local literal inventory, not deployed entrypoint
acceptance or a substitute for the pending original/archive inventory.

The [report](evidence/packaging-launchers/primary-r2.json) inventories **1,085**
tracked members under `deb`, `RPM/SOURCES`, `build` and `.github/workflows`:
**1,045** UTF-8 text files scanned, **36** binary and **4** oversized files
explicitly unscanned. It finds **909 regex candidate rows in 123 files**.
These are not 909 active commands or distinct defects: the legacy PHP package
changelog alone contributes 468 matches. Comments, package names, argument copies,
echo and grep patterns can match; command substitution can be missed.

Every scanned file retains path, current SHA-256, indexed blob and mode; the
working bytes are rehashed after scanning. Commit is context, not a claim that
uncommitted bytes match that commit. Links/special files are not followed and
all member dispositions remain visible. This is literal/configuration inspection,
not a graph-completeness or runtime-reachability conclusion.

Actual OpenCode Muse Spark independently rebuilt the report: byte-identical,
including all file identities and 909 rows. Reusing its output path correctly
failed with `FileExistsError`. [Review](evidence/packaging-launchers/opencode-review.md),
[coordinator comparison](evidence/packaging-launchers/result.json).

The corrected matcher captures the nested variable-PHP launch syntax at
`deb/kaltura-batch/debian/kaltura-batch.init:85`,
`deb/kaltura-elasticsearch/debian/kaltura-elastic-populate.init:65` and
`RPM/SOURCES/kaltura-populate:94`. Their variables remain **unresolved**, not
assumed interpreter paths or active deployed jobs. The review also listed
keyword anchors in grep/echo lines; those remain false-positive candidates,
not startup execution evidence.

## Reproduce

```sh
PYTHONDONTWRITEBYTECODE=1 python3 doc/php83/evidence/packaging-launchers/build.py \
  --output <new-repository-local-path>
```

The builder pins the independently reviewed matcher. It only reads tracked
public repository files and creates the requested report. It does not read
original ZIP/DEB archives, install/execute package hooks, access a VM or retry
the denied external archive operation. The initial report/builder are retained;
`primary-r2.json` is the authoritative reviewed version.

Next: resolve the candidate variables against exact installed configuration and
published payload identities, classify actual supported entrypoints and link
their source diagnostics. None of those joins is inferred from a regex match.
T0-04, full source inventory, application and release acceptance remain open.
