# Inventory evidence ledger: bounded T0-04 prerequisite

This is a deterministic, offline accounting join, **not completed inventory,
semantic adjudication, runtime acceptance or permission for package integration**.
The original source ZIP, experimental exp9 ZIP and existing reports are read
only. No VM, network, application service or source code analysis is performed.
Cursor independently executed the eight local tests and rebuilt the ledger;
its output is byte-identical. Its review confirms the bounded accounting scope.

## Recorded scope

The [machine-readable ledger](evidence/inventory-ledger/ledger.json) joins:

- [Raw static candidates](evidence/source-audit/static-findings.csv): 1,901 rows.
- [Packaged static candidates](evidence/source-audit/packaged-static-findings.csv):
  2,810 rows. Together these are **4,711 report rows, not 4,711 distinct defects**;
  overlapping raw/package findings are deliberately retained with their provenance.
- [Raw syntax](evidence/source-audit/syntax-findings.json) and
  [packaged syntax](evidence/source-audit/packaged-syntax-findings.json): 126 and
  149 diagnostic-file records respectively. These are not independent incident
  counts and overlap static findings.
- [Compiler differential](evidence/source-audit/php74-vs-php83-compile.json):
  72 new PHP 8.3 compiler rejections and 7 retained baseline rejections. These
  observed compiler classifications do not establish runtime reachability.
- [Current experimental selection](evidence/exp9-candidate/manifest.json): all
  16 selected source targets are checked against original/candidate ZIP bytes,
  their before/after hashes and local patch hashes. Unexpected application deltas
  fail the join. This is a byte-level check, not independent patch application.
- [Exp9 API evidence](evidence/exp9-api/codex.json): 18 observed diagnostic groups /
  503 events linked to exact candidate file hashes. Runtime observations are
  limited to that recorded workload; they do not adjudicate similarly located
  static findings or prove all callers exercised.
- [Archive inventory](evidence/source-audit/archive-inventory.json) and
  [package overlay map](evidence/source-audit/source-to-package-map.json).

Every imported report has a SHA-256 and byte count under `inputs`. Each finding
retains its report-relative path and zero-based record index. File keys include
scope, path and exact source hash; unresolved keys explicitly say `unresolved`.
Runtime records are kept separately because their candidate bytes may differ
from historical static inputs. No source-code graph conclusion is made.

## Honest unknowns

There are 1,530 file-identity records in the finding/runtime join (including five runtime-only file records). **792 packaged-file
records lack exact hashes in these imported reports**. Raw ZIP hashes are never
silently substituted for missing packaged identities; even an aggregate claim
of unchanged upstream files is insufficient for a file-level assertion.

The inventory lists 20 vendor directories. All 20 remain without completed
version attribution and license attribution in this ledger. Candidate license
paths/hashes merely identify files for review: directory nesting does not prove
which license applies, and this is not a complete transitive SBOM.

All 1,530 finding/runtime-file records have unresolved active-entrypoint status in this
join. Existing focused runtime evidence does not establish exhaustive reachability.
All 4,711 static rows remain unverified. A file matching a selected patch does
**not** mean its findings are fixed; the tool resolves zero semantic findings.
Historical known runtime defects have not been converted into blanket static
findings classifications. Existing evidence should support individual future
adjudications with exact identities and scope.

The package overlay input records two changed upstream PHP files and 1,670
additional packaged PHP files. The latter is not a file-level complete hash or
entrypoint inventory; attribution remains outstanding. Analyzer pins/manual
blind spots, generated clients, cron/install/plugin entrypoints and a candidate
whole-tree syntax/static rerun remain separate gaps. **T0-04 stays open.**

## Reproduction and validation

From the migration worktree, with both documented archives already local:

```sh
python3 tools/php83/inventory-ledger/build.py \
  --original /tmp/kaltura-php83-audit/Rigel-18.20.0.zip \
  --candidate /home/nilton/Projetos/nilton/NOVOS/platform-install-packages-php83-artifacts/exp9/Rigel-18.20.0-php83-experimental.exp9.zip \
  --output /tmp/php83-inventory-ledger-new.json
python3 -m unittest discover -s tools/php83/inventory-ledger -p 'test_*.py'
```

Outputs must not exist; reports are not overwritten. Two primary executions
produced byte-identical ledgers. Eight local tests pass: archive identity,
wrong hash, traversal, wrong root, duplicate entry, package-extra mapping,
explicit unknown identity, and evidence-reference/count validation. These
nested tests are **not** included by the older top-level unittest discovery
command; execute the explicit command above. The duplicate-entry fixture emits
an expected Python ZIP warning during construction before rejection is tested.

[Local test output](evidence/inventory-ledger/local-tests.stderr),
[exit status](evidence/inventory-ledger/local-tests.exit) and
[identity/result record](evidence/inventory-ledger/result.json) are retained.
The byte verifier is for trusted local immutable inputs, not hostile archive
resource limits or a filesystem race sandbox. It does not extract archive files.

## Next runnable inventory case

Obtain exact file hashes from the checksum-verified published baseline package
payloads, read-only, and join the 792 unresolved records without inferring hashes
from paths. Then independently verify the full component/version/license and
entrypoint ledger, prioritizing compiler-rejected files over repeatedly fixing
one observed warning at a time. Keep each unverified finding and manual analyzer
gap visible; no classification should be invented merely to close a task.

## Baseline execution warning

Do not execute `/tmp/php74-baseline-sanity.sh` unmodified. Inspection found its
protected `.20` default and `curl -L` redirects without per-hop target validation.
The historical [network guard record](evidence/noble-baseline/network-guard.txt)
says the temporary smoke chain was removed. A future T0-05 driver must freeze
explicit baseline74 identity, owned synthetic state and guarded destinations
before any full-service upload or benchmark run. This ledger performs none.

## Independent verification

[Cursor execution/review](evidence/inventory-ledger/cursor.json) reports exit 0
for the eight tests, standalone build and byte comparison. The independent
output is 3,909,779 bytes with SHA-256
`33977fe50b11cf851bee4ccd7a5d1e33bcfdb9653c07f413b108b8ed69edddea`.
The review correctly distinguishes sixteen validated manifest targets from
fourteen joined file records carrying a selected-patch field: two selected
targets have no finding/differential/runtime row in this join. No patch is omitted
from archive validation, and no finding is marked resolved. Its reference to a
"committed ledger" described the working-tree ledger; verification occurred
before its first commit.

The next package-identity input is already available locally: published Noble
repository tarball SHA-256
`91629580441f6a896ebf9e51f0256532221715bee57a3e5a64c66ff0c4e3127b`,
matching `/tmp/kaltura-php83-audit/release/SHA256SUMS` on recheck. That checksum
match alone does not yet fill missing file identities; the next case must inspect
verified DEB payload bytes without installing packages or running their scripts.
