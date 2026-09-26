# Entrypoint-candidate inventory

Status: **PREPARED, NOT_EXECUTED_REAL_INPUTS**. Independent review pending.

This is a synthetic-only implementation. The builder accepts user-provided
published-bundle and original-ZIP paths, but it was **not executed on real
inputs** in this session. The prior permission denial for archive
copy/control extraction under `/tmp`
(`evidence/entrypoint-inventory/attempt1.json`) is retained and not a pass.
That denied operation was not retried through another tool or path.

## What the builder does

`tools/php83/entrypoint-inventory/build.py` performs an offline deterministic
candidate inventory:

- Verifies the outer bundle hash against the existing exact pin
  `91629580441f6a896ebf9e51f0256532221715bee57a3e5a64c66ff0c4e3127b`
  and the original ZIP hash against
  `58d534d09b3b75c9a8333957268c884f79032638b2d44a278b1992fda1b0ab28`.
- Verifies the inner `SHA256SUMS` manifest: exact coverage of all `.deb`
  members, exact per-package hashes, regular-file DEB members only.
- Reads regular DEB control and data metadata only through
  `dpkg-deb --ctrl-tarfile` and `dpkg-deb --fsys-tarfile`. It records the
  `dpkg-deb` binary hash/version and both invocations. No package is
  installed, no maintainer script is executed, no member path is extracted,
  and no link is followed. All private DEB/tar scratch files live in a
  repository-owned directory and are removed afterwards.
- Inventories exact control members, maintainer scripts
  (`preinst`, `postinst`, `prerm`, `postrm`, `config`), cron/systemd/init/web
  configuration paths, literal PHP invocations, executable/shebang/
  extensionless-PHP candidates, PHP symlink/hardlink candidates, and
  generated-client path candidates.
- Records path, content hash (where inspected), owner package filename/hash,
  and line evidence for PHP invocations. Dynamic interpreter targets
  (`$var`, `${...}`, `$(...)`, backticks, globs) are classified
  `unresolved_dynamic`, never resolved from the host.
- Reports full denominators (control/data member totals, regular/directory/
  link counts, upstream PHP count) and exclusion counts (per-suffix skips,
  oversize-skipped, nonregular kinds). Oversize regular files above 2 MiB are
  counted but not content-inspected.

Safe-parsing patterns (path normalization, traversal/absolute-path rejection,
duplicate detection, checksum-manifest validation, hash helpers) mirror
`tools/php83/package-identities/build.py`.

## Explicit non-claims

- No active-runtime behavior, reachability, exploitability, or
  exhaustive-entrypoint claim. Candidates are static inventory rows, not proof
  that a path is reachable, served, scheduled, or compatible with PHP 8.3.
- No semantic finding is resolved. No ledger, package, configuration, or
  deployment change is approved.
- This is a trusted-local-input auditor, not a hostile-archive resource
  sandbox: no CPU/memory/output quotas beyond fixed subprocess timeouts, no
  signature verification beyond the pinned hashes, and no decompression-bomb
  defense beyond the documented scan-size limit.

## Synthetic verification only

Tests use synthetic tar/ZIP bytes and a mocked `dpkg-deb` subprocess inside a
repository-owned scope (`tools/php83/entrypoint-inventory/.tmp-test-scope`).
No real archive or DEB is read or executed. Cases cover path traversal,
intra-package duplicates, symlink/hardlink recording, maintainer-script line
evidence, literal versus dynamic interpreter targets, denominator/exclusion
accounting, oversize handling, repo-owned scratch enforcement, synthetic
end-to-end orchestration, and inner-hash fail-closed behavior.

```sh
mkdir -p tools/php83/entrypoint-inventory/.tmp-run-scope
TMPDIR="$PWD/tools/php83/entrypoint-inventory/.tmp-run-scope" \
  python3 -m unittest discover -s tools/php83/entrypoint-inventory -p 'test_*.py'
```

Local synthetic evidence is retained under
`doc/php83/evidence/entrypoint-inventory/local-*`. Real-input execution,
comparison against `package-identities/primary.json` owners, and independent
review remain open.
