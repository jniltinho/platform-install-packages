# Entrypoint candidate inventory — prepared, no real-input execution

Status: **PREPARED / NOT_EXECUTED_REAL_INPUTS**. T0-04 remains incomplete.
The first OpenCode attempt encountered an external-directory permission denial
while requesting a copy/control-archive inspection under `/tmp`. That operation
was not retried with another tool or path. The separate repository-only author
attempt timed out (exit124); it is not a successful execution or review.

## Exact prepared scope

`tools/php83/entrypoint-inventory/build.py` accepts the pinned published Noble
bundle and original ZIP. It is intended to inspect DEB control/data tar streams
without installing packages, executing hooks or extracting archive member paths.
Only mocked/synthetic archives have been executed in this phase.

- Package control: maintainer scripts, full member metadata, regular file hashes,
  line-numbered invocation candidates with source hash and package owner identity.
- Package data: PHP-family files, shell scripts, executable and extensionless
  candidates, etc/systemd and application-configuration path candidates. Every
  selected bounded text is scanned, not merely etc configuration files.
- Absolute literal PHP target tokens are distinguished from relative targets,
  option-led invocations and variable/dynamic interpreters. These are regex
  candidates, **not shell parsing or proof of execution**. Comments, strings and
  package names may overmatch. Unusual command construction can still be missed.
- Links are recorded but never followed; all data member types are counted.
  Each regular member receives a candidate, oversize-unscanned or excluded
  disposition. The2MiB scan limit and per-suffix exclusions remain visible.
- **The original ZIP contributes a PHP-family file count only.** This is not an
  inventory of original-tree entrypoints or a source/package reachability join.
  Existing ledger/source-map/payload-report hashes identify context; their owner
  records are not semantically reconciled by this prepared tool.

Traversal and duplicate normalized paths are rejected. The outer bundle,
original ZIP and inner DEB checksums are checked; member paths never become
extraction destinations. Temporary DEB/tar byte streams stay in repository-owned
scratch and are removed. Output is exclusive-create and cannot overwrite an
existing report. The scope is trusted pinned inputs, not a hostile-archive
resource-exhaustion sandbox or proof of absence of executable content.

## Review and corrections

Initial local execution had12 tests with3 failures/errors; that evidence and
source are preserved. Corrections retained normal root-tar directory handling,
fixed synthetic scratch containment and fully mocked the negative package test.
Actual Claude then ran12 passing tests but rejected the prepared tool because
shell/template invocations and variable interpreters were missed and the prose
overstated the source scope. The rejected review is retained.

The next revision scans shell/configuration/extensionless candidates, records
variable interpreters as unresolved, distinguishes relative/option targets,
retains invocation source hashes and control metadata, and avoids labeling every
extensionless executable as PHP. Four added tests cover those findings. The
expanded16-test synthetic suite passes locally; independent re-review is pending.
No test outcome closes real-input execution, owner/source reconciliation,
original-tree entrypoint discovery, active-path classification or T0-04.

```sh
mkdir -p tools/php83/entrypoint-inventory/.tmp-test-scope
TMPDIR="$PWD/tools/php83/entrypoint-inventory/.tmp-test-scope" \
  python3 -m unittest discover -s tools/php83/entrypoint-inventory -p 'test_*.py'
```

Evidence: [local attempts and reviews](evidence/entrypoint-inventory/).
No application, VM, performance, packaging or release acceptance is claimed.
