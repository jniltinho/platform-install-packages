# Published package payload identities

This offline identity audit resolves the inventory ledger's **792 missing
packaged-file hashes** without inferring bytes from upstream paths. It preserves
all **149 already-known packaged hashes**, leaving zero missing packaged-file
identities within that ledger's 941 packaged records. This is not dependency
attribution, semantic classification, runtime acceptance or T0-04 completion.

## Pinned inputs and result

- Published Noble bundle: SHA-256
  `91629580441f6a896ebf9e51f0256532221715bee57a3e5a64c66ff0c4e3127b`.
- Original Rigel ZIP: SHA-256
  `58d534d09b3b75c9a8333957268c884f79032638b2d44a278b1992fda1b0ab28`.
- [Prior inventory ledger](evidence/inventory-ledger/ledger.json) remains unchanged;
  joins reference its original file keys and preserve semantic classifications.
- [Historical source/package map](evidence/source-audit/source-to-package-map.json)
  also remains unchanged. Its counts, exact changed-file identities and complete
  extra-path grouping reconcile against the package payloads.

The [primary report](evidence/package-identities/primary.json) verifies the outer
bundle and its inner `SHA256SUMS`: exact coverage and hashes of **17 DEBs**.
Every selected PHP-family file records its exact payload hash, type, size,
mode, UID/GID and owner package filename/hash. Package filename plus content
hash identifies the exact owner artifact; it is not a separate assertion about
control-file package/version fields or publisher signatures.

Results:

| Identity dimension | Result |
|---|---:|
| Unique selected package payload paths | 13,454 |
| Selected payload occurrences across DEBs | 13,454 |
| Duplicate selected paths across packages | 0 |
| Selected symlink/hardlink/nonregular entries | 0 |
| Original selected source files | 11,784 |
| Byte-identical upstream/package files | 11,782 |
| Changed upstream/package files | 2 |
| Missing upstream paths | 0 |
| Extra packaged selected files | 1,670 |
| Missing ledger hashes resolved | 792 |
| Previously known ledger hashes preserved | 149 |
| Semantic findings resolved | 0 |

The two changed upstream files are
`infra/cdl/kdl/KDLOperatorFfmpeg1_1_1.php` and `start/index.php`; their before/after
identities agree with the historical map. This is overlay identity evidence,
not a claim that these changes are correct, active or compatible with PHP 8.3.

## Scope and fail-closed handling

The selected suffixes are **`.php`, `.phtml`, `.inc`, `.php5`, case-insensitive**,
matching the established lint scope. The original ZIP has 11,619 `.php` and
165 `.phtml` files. Every other non-directory member is counted by its final
suffix, or `(extensionless)`, per package. Those counts expose exclusions; they
are not content inspection or an inventory of every executable PHP entrypoint.
PHP embedded in other extensions, extensionless/shebang programs, shell/Python
launchers, generated runtime files and active configuration remain separate work.

- Reject wrong archive hashes, checksum/package-set mismatch, unsafe member
  names, duplicate normalized names inside a package and incorrect known hashes.
- PHP symlinks, hardlinks and special files are **rejected**, not followed,
  resolved from the host filesystem or silently counted as regular bytes.
  Non-PHP links are outside the hashed selection and are never followed.
- Identical cross-package paths retain **all** owner identities. Differences in
  bytes, type, size, mode or UID/GID fail rather than selecting an arbitrary owner.
- Exact historical extra-path groups must form a complete, non-overlapping
  partition; mismatches fail.
- Existing output paths are rejected. No prior ledger is modified.

The builder copies each checksum-verified DEB to a generated private temporary
filename, runs **`dpkg-deb --fsys-tarfile`**, and reads the resulting tar stream.
It does not install packages, execute maintainer scripts, extract member paths,
follow archive links, contact networks or access a VM. Temporary DEB/tar byte
streams are cleaned up. The `dpkg-deb` binary hash/version is recorded. This is a
trusted-local-input audit, not hostile-archive resource-limit enforcement or
fresh signature verification. The source ZIP and package bundle stay read-only.

## Reproduction

From the migration worktree:

```sh
python3 tools/php83/package-identities/build.py \
  --bundle /tmp/kaltura-php83-audit/release/kaltura-server-noble-repo.tar.gz \
  --original /tmp/kaltura-php83-audit/Rigel-18.20.0.zip \
  --output /tmp/php83-package-identities-new.json
python3 -m unittest discover -s tools/php83/package-identities -p 'test_*.py'
```

The nested suite has **18 passing tests**, including malformed/duplicate
checksums, traversal, all selected nonregular member types, intra-package
collisions, cross-package identical-owner retention and content/metadata
conflicts, missing/known hash joins, missing payloads, historical-map mismatch
and incomplete extra-path partitions. It is not automatically included by the
older top-level unittest discovery command. These are local synthetic tests,
not additional PHP application acceptance cases.

[Primary test output](evidence/package-identities/primary-tests.stderr),
[exit status](evidence/package-identities/primary-tests.exit),
[repeated report](evidence/package-identities/primary-repeat.json) and
[primary result/identities](evidence/package-identities/primary-result.json)
are retained. The earlier
[initial report](evidence/package-identities/primary-initial.json) predates only
excluded-suffix accounting and has its earlier builder hash; use the final
primary report for the frozen tool version. Independent CLI review/execution
is coordinated separately and must not be inferred from this primary result.

## Next gate

Use the exact package/file identities to attach dependency/version/license and
entrypoint evidence to unresolved findings. Do not relabel static findings as
fixed merely because their file hashes are now known. No package mutation,
provider selection, deployment, performance claim or release gate is approved.
For full-service baseline execution, retain the
[unsafe temporary-script warning](inventory-ledger.md#baseline-execution-warning):
the old script defaults to protected `.20` and follows unvalidated redirects.

## Independent executions and review follow-up

Claude independently rebuilds the full inventory from both pinned archives.
Its report, the primary and the primary repeat are byte-identical (SHA-256
`9e76e1f9664527102528ea2eb46aae38a0d06d441cf270dc48724086af1515c9`).
The [comparison verifier](evidence/package-identities/compare.py) also checks
current input hashes and all 941 owner/hash joins; see
[comparison result](evidence/package-identities/comparison.json).
Claude executes the original 18 tests; Cursor independently executes those 18
plus eight ledger tests and checks joins against the old ledger. Both review the
actual builder. Their final CLI reports are retained under
[evidence/package-identities/agents](evidence/package-identities/agents/).

The reviewers identify missing orchestration fault-path tests. Seven new tests
now exercise the actual `build()` function with synthetic inputs: successful
end-to-end joins, wrong outer hash, inner checksum mismatch, wrong original ZIP
hash, nonregular DEB, checksum/package set mismatch and failed `dpkg-deb`.
This increases the separate suite to **25 passing local tests**. The external
payload command is mocked in these controls; the three real inventory builds
provide distinct actual `dpkg-deb` execution evidence. The builder and real
reports are unchanged. Old 18-test source/results are retained, and the new
phase is identified in [orchestration result](evidence/package-identities/primary-orchestration-result.json).

Grok's initial successful eight-test execution/review concerned the old ledger
and identity contract, not this then-unfinished builder; it must not be presented
as a review of the final implementation. A separate final follow-up is tracked
independently. Non-DEB bundle members are not interpreted as package payloads,
non-PHP links are not followed, and the zero nonregular-PHP count in a successful
report reflects rejection of such entries rather than their acceptance.

The final Grok attempt timed out at 120 seconds (exit 124); it supplies no
completed final-builder review. The authorized OpenCode Zen fallback used
`opencode/muse-spark-1.3-contributor-free`, independently ran the expanded 25
package tests and 11 syntax tests (both exit 0), and reviewed the actual builder,
scanner and comparison reports. Its final claim that actual builder/VM evidence
is missing because Grok timed out is incorrect: Claude's real rebuild and real
lab compiler repeat are recorded separately. Only Grok's own final contribution
is missing. Preserve that distinction rather than turning a CLI timeout into a
false pass or discarding another executor's genuine evidence.
