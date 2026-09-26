# Entrypoint candidate inventory — actual authorized archive checkpoint


## Current checkpoint: actual inputs, independently repeated

After the operator explicitly released the requested accesses, the previously
reviewed unchanged builder executed against the pinned public Noble repository
bundle and original Rigel ZIP. Codex primary and actual Claude CLI repeat both
exited0; the reports are byte-identical and builder/bundle/ZIP identities remained
unchanged. No package installation, maintainer hook, extracted-member execution,
VM or production operation occurred. The earlier denial is preserved below as
history, not silently relabeled successful.

- 17 packages;73 control members;43,782 payload members.
- 37,149 regular payload files:18,335 candidate-scanned,18,813 excluded by the
  visible policy,1 oversize-unscanned. Links6 and directories6,627 are separate.
- 18,336 candidate records, including the oversize record; **not18,336 active
  PHP entrypoints**. Executable/non-PHP text can be a candidate.
- 5,489 invocation regex rows:8 literal PHP targets,5,481 unresolved
  (5,355 dynamic,69 relative,57 option-led). These are not confirmed defects.
- Original ZIP contributes11,784 PHP-family files, still only a count.

[Result and storage identities](evidence/entrypoint-inventory/authorized-real-r1/result.json)
record raw report SHA256
`42c3e2411c3973e1f5591d4aacd31d1af2a7a05929af935992ab2ebcdae67501`.
The byte-identical37,082,593-byte reports are stored once as deterministic gzip
(`inventory.json.gz`,2,674,735bytes); decompression was checked byte-exact. Raw
local primary/repeat copies are ignored, not omitted from the reproducible inputs.
[Claude public execution](evidence/entrypoint-inventory/authorized-real-r1/claude-public.json)
retains tool commands/results and the scoped conclusion. This is independent
execution of the same builder, not an independent semantic classifier.

**T0-04 remains incomplete:** original-tree entrypoint discovery, source/package
owner reconciliation, active-path classification and finding triage remain open.
Command-substitution misses, regex false positives, exclusions and2MiB limit are
unchanged. No application/runtime/performance/package/release acceptance follows.

## Historical preparation before access confirmation

Status: **PREPARED / NOT_EXECUTED_REAL_INPUTS**. T0-04 remains incomplete.
The first OpenCode attempt encountered an external-directory permission denial
while requesting a copy/control-archive inspection under `/tmp`. That operation
was not retried with another tool or path. The separate repository-only author
attempt timed out (exit 124); it is not a successful execution or review.

## Exact prepared scope

`tools/php83/entrypoint-inventory/build.py` accepts the pinned published Noble
bundle and original ZIP. It is intended to inspect DEB control/data tar streams
without installing packages, executing hooks or extracting archive member paths.
Only mocked/synthetic archives have been executed in this phase.

- Package control: maintainer scripts, full member metadata, regular file hashes,
  line-numbered invocation candidates with source hash and package owner identity.
- Package data: PHP-family files, shell scripts, executable and extensionless
  candidates, cron/init/default/web/php etc paths, systemd and application-configuration path candidates. Every
  selected bounded text is scanned, not merely etc configuration files.
- Absolute literal PHP target tokens are distinguished from relative targets,
  option-led invocations and variable/dynamic interpreters. These are regex
  candidates, **not shell parsing or proof of execution**. Comments, strings and
  package names may overmatch. Unusual command construction can still be missed.
- Links are recorded but never followed; all data member types are counted.
  Each regular member receives a candidate, oversize-unscanned or excluded
  disposition. The 2 MiB scan limit and per-suffix exclusions remain visible.
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

Initial local execution had 12 tests with 3 failures/errors; that evidence and
source are preserved. Corrections retained normal root-tar directory handling,
fixed synthetic scratch containment and fully mocked the negative package test.
Actual Claude then ran 12 passing tests but rejected the prepared tool because
shell/template invocations and variable interpreters were missed and the prose
overstated the source scope. The rejected review is retained.

The next revision scans shell/configuration/extensionless candidates, records
variable interpreters as unresolved, distinguishes relative/option targets,
retains invocation source hashes and control metadata, and avoids labeling every
extensionless executable as PHP. Five added tests cover those findings, including the actual nested `su ... -c`
variable-interpreter idiom that the second independent review found was missed.
The repaired matcher does not consume later variables and also recognizes quoted
and default-valued PHP variables. Both rejected reviews remain preserved. The
expanded 17-test synthetic suite passes locally; actual Claude independently reran all 17 tests and validated the tracked daemon
launch idioms. [Final targeted review](evidence/entrypoint-inventory/claude-r3-review.md)
approves prepared candidate discovery only.
No test outcome closes real-input execution, owner/source reconciliation,
original-tree entrypoint discovery, active-path classification or T0-04.

```sh
mkdir -p tools/php83/entrypoint-inventory/.tmp-test-scope
TMPDIR="$PWD/tools/php83/entrypoint-inventory/.tmp-test-scope" \
  python3 -m unittest discover -s tools/php83/entrypoint-inventory -p 'test_*.py'
```

Evidence: [local attempts and reviews](evidence/entrypoint-inventory/).
No application, VM, performance, packaging or release acceptance is claimed.

Known discovery limitation: command-substitution interpreters such as
`$(which php) script` are not recognized; argument copies/comments may produce
extra candidate rows. Neither a match nor its absence proves active execution.
