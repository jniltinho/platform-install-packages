# exp13 paired whole-artifact compiler — preparation

**Executed and independently repeated: bounded compiler nonregression passes.
Seven historical rejections and application/release gates remain open.**
No original74 baseline is needed for this native83 compiler comparison.

The exp12 scanner cannot be used unchanged by arguments: it hardcodes exp11/12,
three targets and equal11784 inventories, and drops raw stdout/stderr. The thin
adapter retains its byte-identical `frozen-core.py` (SHAfd98fdb4…e48f3e), importing
only archive inventory, hashing, summary and equality helpers. New code handles
12 changed sources plus exactly one added source, explicit11784→11785 selection,
retained native stdout/stderr, derived path-normalized diagnostics and fresh
runtime/source/harness pre/post identities. No old harness is edited.

`input-contract.json` takes13 exact source deltas from exp13 proposed composition;
the coordinator-approved75-target selected artifact must be built/verified before
its ZIP pin is supplied. The sole new source is
`infra/general/kXmlEntityLoaderPolicy.php`. The seven historical compiler rejects
must remain the same paths, not be waived. All changed/added targets must compile;
unchanged PHP-family source bytes and outcomes/diagnostics must remain exact.
Diagnostics for all13 delta sources are retained before/after, not presumed equal
or silently suppressed. No source inclusion, SQL or app boot is performed.

Extension selection is case-insensitive `.php`, `.phtml`, `.inc`, `.php5`. Entire
ZIP/source inventories are byte-checked, including nonselected files. Runtime
uses native `/usr/bin/php8.3 -n -l` with E_ALL/short tags, no networking and read-only
source/tools mounts. Independent comparison permits only duration_ns differences;
raw stdout/stderr, source/runtime/harness identities and exact target changes must
match. Compiler acceptance is not application or package/release acceptance.

## Historical planned commands — executed after coordinator authorization

Archive inputs:
- exp12: `../platform-install-packages-php83-artifacts/exp12/Rigel-18.20.0-php83-experimental.exp12.zip`,
  SHA `de5e61a1b54f472e605ef2e87669302a3915616fd85378e0f05706fcb06a7e8b`.
- exp13: `../platform-install-packages-php83-artifacts/exp13/Rigel-18.20.0-php83-experimental.exp13.zip`,
  SHA `6d0bc4947207e6c5457b7843948d263aa8d5f251480e58cbf9086c0add79a944`.

New native83 stage: `/home/vagrant/php-candidate-syntax-exp13`.
Copy only the two verified ZIPs as exp12.zip/exp13.zip and the five `scan.FILES`
into stage/tools; neither reuse nor overwrite an old stage. Then, under an
explicit native83 ownership grant:

```sh
ssh -F /tmp/kaltura-php83-ssh.conf php83 \
 'python3 -B /home/vagrant/php-candidate-syntax-exp13/tools/stage.py'
ssh -F /tmp/kaltura-php83-ssh.conf php83 \
 'bash /home/vagrant/php-candidate-syntax-exp13/tools/run.sh' \
 > doc/php83/evidence/exp13-syntax/primary.json \
 2> doc/php83/evidence/exp13-syntax/primary.stderr
# Capture actual status immediately as primary.exit; do not infer from JSON.
```

Actual Claude repeats the same frozen runner, synchronously, into distinct
`claude-repeat.json/.stderr/.exit`; then local comparison:

```sh
python3 tools/php83/exp13-syntax/compare.py \
 doc/php83/evidence/exp13-syntax/primary.json \
 doc/php83/evidence/exp13-syntax/claude-repeat.json \
 doc/php83/evidence/exp13-syntax/comparison.json
```

The migration worktree is not indexed by the packaging sibling's graph;
exp12 scanner/stager/runner/comparator were directly read completely before reuse.
No graph absence or complete impact claim follows. Native83 execution was held until the exact artifact pin, coherent local
tests/review and named handoff; that sequence is now complete.

## Actual primary and independent execution

Codex primary and actual Claude each executed23,569 PHP8.3 compile processes.
No application code was included or executed. Both runner exits are0, but bounded
acceptance also requires the explicit path/hash/outcome/runtime contracts.

| Result | exp12 | exp13 |
|---|---:|---:|
| Selected PHP-family files |11784|11785|
| Compiler accepted |11777|11778|
| Compiler rejected |7|7|
| Diagnostic files |73|72|
| Accepted with diagnostics |66|65|
| Incomplete subprocesses |0|0|

Twelve modified sources and the one added XML policy helper compile. Every
unchanged selected source preserves exact outcome/derived diagnostic text. The
only diagnostic change is removal of the KalturaAPIException `__wakeup` return
warning. All seven rejected paths are identical, including six unsubstituted
Symfony templates and the old Riak alias source; none is waived.

[Primary summary](evidence/exp13-syntax/primary-summary.json),
[independent comparison](evidence/exp13-syntax/comparison.json),
[actual Claude execution report](evidence/exp13-syntax/claude-public.json).

Raw stdout, stderr, command, exit and source hash remain in every scan record.
Both full ZIP/source maps and runtime/harness identities are exact before/after.
Primary/independent reports match with only duration_ns removed; no diagnostics,
UUID or source-path fields are normalized during independent comparison. The
per-row derived diagnostic strips only its own known audit source prefix, while
raw channels remain intact. Codex separately reran the comparator; output bytes
match Claude's final comparison. Native83 was released immediately upon CLI
termination, before this documentation/checkpoint.

Actual OpenCode preparation review ran22 local tests plus shell syntax and found
no blocker. Actual Claude reran22 tests after its native repeat. The first local
test draft indexed sorted diagnostic deltas incorrectly; that failed test output
is preserved and corrected by matching the explicit target path, without changing
scanner behavior. Frozen runtime tool hashes remained unchanged throughout.

Claude reported creating its first derived comparison from another working
directory, then deleting that self-created output and regenerating it using the
requested input paths. The raw primary/repeat scans are untouched, but the first
derived output is not retained; that provenance limitation is disclosed rather
than claiming all intermediate attempts were preserved. The final comparator was
independently reproduced by Codex into a new file without overwriting it.

This is not all-files compiler acceptance, API/runtime/MSSQL validation, package
qualification, performance proof or production/release authorization.
