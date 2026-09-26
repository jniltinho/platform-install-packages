# exp13 experimental source artifact — reproduced, runtime pending

## Current selected-r1 result

Coordinator authorized laboratory selection after SQL gate commit `004b75da`:
91 typed rows per cohort, exact primary/Claude repeat, 15→4 warnings retained.
The proposal below is preserved unchanged in its historical phase. New
[selected-r1 manifest](evidence/exp13-candidate/selected-r1/manifest.json) has SHA256
`4414dee2337cd2858e0553ce73cd9809975d69326be56033bf88bd3599ce81ba`.
Selection is explicitly **not** application, package, production or release approval.
Actual Claude selection review completed exit0 and independently ran 4 selection
and 9 preparation tests; no blocking defect for the authorized lab builds.

Codex built primary once; actual Claude CLI independently executed a second build
and verifier (both exit0). ZIP bytes, build reports and SHA256SUMS are identical.
Final artifact in sibling `platform-install-packages-php83-artifacts/exp13/`:
`Rigel-18.20.0-php83-experimental.exp13.zip`, **91,210,445 bytes**, SHA256:
`6d0bc4947207e6c5457b7843948d263aa8d5f251480e58cbf9086c0add79a944`.

[Verification](evidence/exp13-candidate/verification.json) and
[actual Claude build/review](evidence/exp13-candidate/claude-build-review.json)
confirm original and exp12 hashes unchanged, 75 cumulative targets, 62 preserved
exp12 entries, 12 modifications plus one added helper, and PHP-family count
11,784→11,785. Every source member is checked, not merely the changed-file list.
Four further author verifier tests passed, including retained actual artifacts and
negative controls; Claude did not execute those additional four tests.

Verifier limitations remain visible: some report counts are literals, but Claude
independently recomputed them; builder pin and build-report/SHA256SUMS equality
were checked separately by Claude. This proves reproducibility on the same local
toolchain, not cross-toolchain determinism. No artifact PHP/compiler/runtime has
been executed by this task. Parent coordinates subsequent lab acceptance matrices.
AWS mixed-version cache and recovery gates remain open. No VM/package/CI/tag or
production operation was performed. Historical patch whitespace warnings are
preserved, not suppressed or silently reformatted.

## Historical proposed-r1 phase

This is a **local source-patch proposal**, not a built ZIP, a PHP execution, or a
release decision. Exp12 remains unchanged. Real SQL validation and independent
repeat of the return-contract family are pending; only the coordinator may
select this composition and authorize a future two-build artifact experiment.
Privacy changes are deliberately absent.

## Inventory and order

[Proposed manifest](evidence/exp13-candidate/proposed-r1/manifest.json) and
[composition proof](evidence/exp13-candidate/proposed-r1/composition.json):

- Start from the exact selected exp12's **65 upstream-relative target patches**.
  Replay all 65 against pinned original ZIP members and compare bytes with exp12.
- Preserve **62 entries exactly**. Replace three entries cumulatively, never stack
  duplicate targets: KalturaFrontController retains its null-user repair before
  the hierarchy-wide dynamic-property attribute; KalturaPDO retains query repair;
  PropelPDO retains bool-setAttribute before their return-contract deltas.
- Add ten unique targets, giving **75 total (74 replacements + one addition)**.
  XML: kConf, kSoapClient, and new `infra/general/kXmlEntityLoaderPolicy.php`.
  AWS: Credentials, NullCredentials, AbstractCredentialsDecorator, FileCache.
  Returns: PropelConfiguration, KalturaAPIException, DebugPDO.
- DebugPDO combines query-v3 with return typing. Exact strict replay verifies both
  orders yield `8f800a0146345f05a71950e3785e442d4aee351184309246cb28159a2afe2ea0`.
  Never select old query-v1/v2 or silently omit the v3 prerequisite.
- Every changed entry keeps prior/exp12/final hashes and the ordered held patch
  chain; superseded selected entries remain in the proposal and proof.

Only one new source file is required. The expected `.php`/`.phtml` compiler
inventory becomes **11,785**, subject to the actual built-artifact inventory.
The XML helper requires native loader getter support (PHP8.2+); this artifact is
explicitly PHP8.3, not a PHP7.4-compatible replacement.

## Builder and gates

Reuse unchanged `tools/php83/zip-builder-v2/build.py`, whose identity is pinned in
`tools/php83/exp13-candidate/inputs.json`. Its explicit add operation checks
`before_sha256:null`, upstream absence/collisions and exact null-source headers.
Do not invoke the builder on this **unselected** proposal. The generic builder
itself is not a policy-enforcement selection gate; a future coordinator-reviewed
selection transition must validate the frozen proposal before any build.

Source replay does not establish composed runtime behavior. Required future gates:
SQL primary/repeat, coordinator selection, two reproducible builds and exact delta,
whole artifact compiler scan, API/CLI/XML/serialization regressions, and broader
application/package/release acceptance. XML preserves synchronous owned loader
and wrapper boundaries; it does not claim fiber-wide isolation. AWS C→O remains
incompatible with old readers: draining workers, isolated cache and snapshot-based
rollback/recovery must be selected and rehearsed. This proposal does not waive it.

## Reproduction (local source only)

```sh
python3 tools/php83/exp13-candidate/test_prepare.py
python3 tools/php83/exp13-candidate/prepare.py \
  --original /tmp/kaltura-php83-audit/Rigel-18.20.0.zip \
  --exp12 ../platform-install-packages-php83-artifacts/exp12/Rigel-18.20.0-php83-experimental.exp12.zip \
  --output "$PWD/doc/php83/evidence/exp13-candidate/proposed-NEW"
```

Output must not exist. No PHP/application body is executed, no VM is accessed,
no dependencies upgraded, and no ZIP is created. Repository metadata/hash/patch
inspection does not assert new structural graph conclusions.

## Independent proposal review

Actual Claude CLI completed exit 0, ran all nine local guards successfully, and
verified all 75 patch hashes, 62 preserved entries and composition metadata.
[Review](evidence/exp13-candidate/claude-review.json): no blocking defect for the
**proposal stage**. It did not re-read/replay archives or execute PHP. Low-risk
limitations remain: end-to-end preparer replay is author evidence rather than a
separate reviewer run; selection enforcement must be implemented in the future
coordinator-approved transition. No build or runtime approval follows from this.

Checkpoint format-check warnings are retained in `checkpoint-format.stdout`:
patch files preserve historical whitespace/CRLF and context indentation. They
are hash-pinned evidence, not reformatted source. This is not a global clean
`git diff --check` claim; no whitespace suppression attributes were added.

## Deferred execution sequence (not run)

1. Wait for SQL independent repeat and coordinator selection authorization.
2. Create a **new named selected phase**, deriving a separate selected manifest
   from frozen proposed manifest SHA256
   `b6ec7cc58a1828611d9c4558a8557eaa6fbf57ea72a40ef02e2095d9af177b17`.
   Preserve every patch row/hash; record authorization and SQL evidence pins.
   The transition must fail closed on unexpected status, bytes or missing gates.
3. Stage this selected manifest/patch set into a fresh directory, then run the
   unchanged v2 builder twice against the pinned original ZIP, with two distinct
   nonexistent output directories. No overwriting historical artifacts.
4. Verify byte-identical ZIPs, every original member/patch/addition hash, unchanged
   exp12 repair preservation, and exact 13-target delta (12 modifications + one
   addition). Record tool identities and output checksums.
5. Only after explicit lab allocation run built-artifact compiler/runtime matrices;
   do not reinterpret source-stage evidence as artifact execution or acceptance.

The selection adapter and actual output locations are intentionally not supplied
as an executable command until the coordinator authorizes that named phase.
