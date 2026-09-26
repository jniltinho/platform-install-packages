# exp13 source composition — proposed, not selected

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
