# Patch and baseline identity audit (T0-02)

Date: 2026-09-25. This historical audit covers the 19-patch repository snapshot, not runtime
compatibility, provider support or promotion of a complete PHP 8.3 candidate.

## Inputs and results

- Raw source ZIP: `58d534d09b3b75c9a8333957268c884f79032638b2d44a278b1992fda1b0ab28`.
  All **15,175 files** in the immutable `server-Rigel-18.20.0` directory match
  their archive bytes; no extra or missing files. **18,027 archive entries**
  includes directories. The graph view is not used as the original reference.
- Published Noble baseline tarball:
  `91629580441f6a896ebf9e51f0256532221715bee57a3e5a64c66ff0c4e3127b`.
  All **17 embedded DEB hashes** match its checksum manifest. Checks read tar
  members as streams: no filesystem extraction, hooks or installation.
  Provenance is the previously pinned local release checksum, not a fresh
  publisher-signature or network verification. Other distro baseline bundles
  are not claimed verified by this case.
- **19 patch files** have exactly one metadata record each: **3 active, 16 held**.
  Patch, original and resulting source hashes match. Each applies exactly to a
  private original-file copy without offsets/fuzz/reversal or unexpected files.
  Alternatives are applied independently, never stacked.
- exp2 ZIP retains SHA256
  `99233ac6638f02072b3394159340edd1e2388b243bafadca3fe33b6bbafa97a0`.
  Cursor reran the archive verifier against the original and the retained second
  build: all original entries retained, exactly 3 source changes and 5 metadata
  additions; all other entry bytes match. This does not constitute a new build.

[Source-tree evidence](evidence/batch2-inventory/source-tree.json),
[baseline package hashes](evidence/batch2-inventory/baseline-packages.json),
[patch application report](evidence/batch2-inventory/patches.json), and
[current disposition ledger](evidence/batch2-inventory/selection-ledger.json).

## Explicit disposition; no silent omissions

| Files | Count | Current decision / reason |
|---|---:|---|
| Services_JSON, Zend JSON Encoder/Decoder offset patches | 3 | Selected for **exp2 only**, in manifest order; not a full candidate. |
| Registry-properties | 1 | Rejected: baseline changes and failed parity. |
| Registry-cast | 1 | Deferred: unresolved ArrayObject property semantics. Metadata lacks a status field; the ledger supplies this documented disposition without rewriting original metadata. |
| DebugPDO-query v1/v2/v3 | 3 | Deferred: standalone alternatives, earlier forwarding defects and unresolved type/API/diagnostic acceptance. |
| KalturaPDO-query, dateUtils-ternary, doc-comment-property | 3 | Deferred: bounded integration/cache evidence is not full acceptance. |
| Seven bootstrap-path repairs and core_compile ordering | 8 | Deferred: bounded bootstrap evidence, not complete application acceptance. |

Each ledger row pins its patch hash and links the supporting existing experiment.
Passing application/hash verification does not change a rejection/defer decision.
A future integrated candidate needs its own reviewed selection and regression
run; no claim is made that all held patches should be included. Registry and
DebugPDO alternative groups deliberately share original source hashes.

## Reproduction

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tools/php83 -p 'test_*.py'
PYTHONDONTWRITEBYTECODE=1 python3 tools/php83/audit-patch-inventory.py \
  --source-root /path/to/server-Rigel-18.20.0 \
  --output /tmp/patch-inventory.json
```

The tool audits all metadata formats present in this repository, rejects uncovered/multiply-covered patches,
SHA drift, traversal/symlink escapes, bad patch headers and non-exact application.
It rejects outputs in audited source/patch directories. It creates only private
copies and its report, with no changes to originals. Twelve new unit tests cover
normal and rejection paths; the full local suite now contains **80 tests**.
These are offline harness tests, not additional PHP runtime tests. The local
input must not be concurrently replaced; this is not a hostile-filesystem sandbox.

Exact [source-tree verifier](evidence/batch2-inventory/verify-source-tree.txt) and
[baseline verifier](evidence/batch2-inventory/verify-baseline.txt) are retained for
reproduction using the documented local public-artifact paths. Their assertions
must run with ordinary Python (no `-O`). Original files/archives are read only.

## Scope still open

This inventory closes neither original task 1.1 (complete dependency/license and
entrypoint audit) nor 1.6 (full experimental repair program). Existing syntax
findings, Registry parity, integrated diagnostics, generated extras, full service
workloads, three-distro providers and upgrade/recovery remain separate gates.
Only current identity/disposition accounting is in scope here.

## Independent execution and review

Cursor executed the 19-patch audit and exp2 archive verification. Claude
independently reran the patch, raw-tree and baseline audits and the 80-test
harness; reports match the primary run. Claude and Cursor reviewed the final
disposition/coverage documents without blocking findings. See the
[batch record](evidence/batch2-inventory/result.json). The first Cursor Ask-mode
attempt refused report writing; the same authorized command then succeeded in
Agent mode. That initial refusal is not reported as an execution pass.

## Subsequent experimental selection: exp3

The table and linked batch-2 ledger above are the immutable historical selection
at that audit. A separate [six-patch exp3 manifest](exp3-candidate.md) now selects
the existing JSON repairs plus KalturaPDO query, date ternary and parser property
for a reproducible **lab experiment**, following Cursor CLI review. Their original
held files/metadata and exp2 manifest remain unchanged. This is not production
promotion or a claim that broad runtime acceptance must precede experimentation.
Other alternatives remain explicitly excluded, with reasons in the exp3 record.

## Subsequent Criteria experiment

The held Criteria null-alias experiment adds a twentieth patch (3 active in the
unchanged exp2 manifest, 17 held). The new strict identity/application audit is
[`criteria-null/patch-inventory.json`](evidence/criteria-null/patch-inventory.json).
The historical 19-row disposition ledger above remains unchanged; later exp3
selection is recorded separately in `exp3-candidate.md`. Criteria is not selected
into exp3 and has only focused runtime approval, not SQL/application acceptance.
See [Criteria experiment](criteria-null-alias.md).

The subsequent exp5 null-only batch adds five explicitly reviewed experiments:
25 total patches, 3 active in unchanged exp2 / 22 held; strict identity/application
audit at [`null-batch/patch-inventory.json`](evidence/null-batch/patch-inventory.json).
The separate exp5 manifest selects twelve patches for isolated integration, not
production acceptance. See [exp5 evidence](exp5-null-batch.md).
