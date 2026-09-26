# Experimental ZIP builder v2 — explicit new-file support

Prepared and tested with synthetic local inputs only. No new Rigel ZIP, selected
manifest, package integration or release is produced by this work. The legacy
`tools/php83/build-experimental-zip.py` and all historical manifests/artifacts
remain unchanged.

The held XML lifecycle repair needs the new
`infra/general/kXmlEntityLoaderPolicy.php` helper. The old builder stages only
existing ZIP members; it cannot represent a genuinely absent source file.
A separately versioned builder supports an explicit manifest row:

```json
{
  "operation": "add",
  "path": "infra/general/kXmlEntityLoaderPolicy.php",
  "patch": "reviewed-helper.patch",
  "sha256": "<exact patch SHA-256>",
  "before_sha256": null,
  "after_sha256": "<exact helper SHA-256>"
}
```

This example is not a selected patch or executable manifest. Existing entries
remain replacements when `operation` is omitted; deletion is unsupported.
An addition requires explicit null-before, an absent path, no collision with
an explicit/implicit directory or parent file, a non-reserved safe path, and
exact `/dev/null` to `b/<path>` patch headers. New source content comes only
from reviewed, checksum-pinned patches and is rehashed after the entire series.
All staged output paths must match the manifest; patch offsets/fuzz fail.

The v2 ZIP retains deterministic sorted entries, fixed timestamps, source
comments and existing executable bits; new source files are regular 0644.
Its embedded metadata declares builder format 2 and hashes the new builder.
Thus v2 output is not expected to be byte-identical to an older builder's ZIP,
even for a replacement-only manifest. Reproducibility means two builds with
identical v2 inputs, not relabeling or overwriting historical artifacts.

## Validation scope

24 synthetic tests pass locally: 13 inherited legacy controls plus 11 addition
controls. They execute real GNU patch on repository-local synthetic ZIPs,
including two-build identity, preserved original bytes, new-file hashes/mode/time,
source/patch drift, collisions, missing/null before identities, unknown operation,
reserved paths and exact headers. No original Rigel archive or published bundle
is read; the previously denied external inventory operation is not retried.

```sh
mkdir -p tools/php83/zip-builder-v2/.scratch
TMPDIR="$PWD/tools/php83/zip-builder-v2/.scratch" PYTHONDONTWRITEBYTECODE=1 \
  python3 -m unittest discover -s tools/php83/zip-builder-v2 -p 'test_*.py' -v
```

Actual Cursor independently executed all 24 tests and reviewed the new paths;
[review](evidence/zip-builder-v2/cursor-review.md) reports no concrete failure.
The reviewed legacy builder and its tests remained unchanged. Application-level helper acceptance, selected
cumulative manifest, real two-build artifact identities and actual-artifact
regression remain separate prerequisites. This is not production packaging code.

## Discovery boundary

The available packaging graph indexes the sibling main worktree, not this
migration worktree. Its generation 2026-09-25T19:28:02Z is ready, but searches
returned no builder nodes and exact coverage marked the legacy builder/test
paths missing. Conclusions above therefore rely on direct reads of the complete
legacy files and the explicit diff/tests, not absence of graph edges.
