# exp10 cumulative candidate selection — pending build

This is a **selection proposal for an experimental PHP 8.3-only source ZIP**.
Independent CLI review must complete before creation. At this document's initial
phase, no exp10 ZIP has been built, staged on a VM, integrated into packaging or
accepted for release. Aggregate acceptance gates remain open.

## Exact cumulative selection

The [exp10 manifest](evidence/exp10-candidate/manifest.json) preserves every field
and the order of all **16 exp9 patch entries**, then appends the **43 disjoint
held curly-offset repairs**, for **59 unique application source targets**.
Patch leaf names are also unique. Input provenance pins both prior manifests:

- [Exp9 selection](evidence/exp9-candidate/manifest.json), including the documented
  intentional PDO null-to-bool correction and earlier compatibility repairs.
- [Pure curly-offset held series](../../patches/php83/held/curly-offsets/manifest.json),
  with its [lexical/compile and bounded behavior evidence](curly-offsets.md).

The original ZIP remains pinned to
`58d534d09b3b75c9a8333957268c884f79032638b2d44a278b1992fda1b0ab28`.
No prior ZIP, original source, active exp2 manifest or held alternative changes.
In particular, the older mixed Symfony/Spyc repairs are not silently substituted
or added. Each newly selected patch is precisely the pure curly-offset patch
identified by the held manifest and its hash.

Selection preflight verifies all 59 source-input hashes directly against the
pinned original ZIP and every patch hash against its referenced repository file.
It checks exact first-16 preservation, exact appended-43 correspondence, source
path and patch-leaf uniqueness, source-root identity and provenance hashes. It
**does not** claim that candidate output hashes, cumulative patch application,
archive reproducibility or full runtime behavior have passed before the build.
Those are separate checks below.

The known target remains **PHP 8.3 only**. Original 7.4 is the behavioral reference;
success of selected constituent functions on 7.4 is not whole-candidate 7.4
support. Passing 43 lexical transformations and representative function tests
must not be transferred into a claim that every method/caller or installed AIO
has been exercised. Other compiler failures, diagnostics, caches/frameworks,
licenses/inventory, distros, media/jobs, performance and recovery remain open.

## Reviewable commands — do not execute builds before review

All commands run from the migration worktree. Preflight is read-only:

```sh
python3 tools/php83/exp10-candidate/stage.py \
  --original /tmp/kaltura-php83-audit/Rigel-18.20.0.zip \
  --check-only
```

After independent selection review, stage only the exact manifest/patch bytes
in a **new** temporary directory:

```sh
python3 tools/php83/exp10-candidate/stage.py \
  --original /tmp/kaltura-php83-audit/Rigel-18.20.0.zip \
  --output /tmp/php83-exp10/patches
```

The existing builder refuses existing output directories, enforces unique source
and patch names, checks the original/patch/source hashes, applies patches with
`--fuzz=0`, rejects offsets/fuzz, checks every resulting source hash and unexpected
files, and writes deterministic archive metadata. Create two distinct builds:

```sh
base=/home/nilton/Projetos/nilton/NOVOS/platform-install-packages-php83-artifacts
python3 tools/php83/build-experimental-zip.py \
  --patch-dir /tmp/php83-exp10/patches \
  /tmp/kaltura-php83-audit/Rigel-18.20.0.zip "$base/exp10"
python3 tools/php83/build-experimental-zip.py \
  --patch-dir /tmp/php83-exp10/patches \
  /tmp/kaltura-php83-audit/Rigel-18.20.0.zip "$base/exp10-repeat"
```

Expected distinct filenames:

```text
platform-install-packages-php83-artifacts/exp10/Rigel-18.20.0-php83-experimental.exp10.zip
platform-install-packages-php83-artifacts/exp10-repeat/Rigel-18.20.0-php83-experimental.exp10.zip
```

Verify exact original-to-candidate content changes and repeated-build identity
with a fresh report output path (the existing verifier itself does not refuse
report overwrite):

```sh
test ! -e doc/php83/evidence/exp10-candidate/verification.json
python3 tools/php83/verify-experimental-zip.py \
  /tmp/kaltura-php83-audit/Rigel-18.20.0.zip \
  "$base/exp10/Rigel-18.20.0-php83-experimental.exp10.zip" \
  "$base/exp10-repeat/Rigel-18.20.0-php83-experimental.exp10.zip" \
  doc/php83/evidence/exp10-candidate/manifest.json \
  doc/php83/evidence/exp10-candidate/verification.json
```

If any named output already exists, stop and inspect it rather than deleting or
replacing historical evidence. A review-approved revision needs a new location
or a documented separate phase.

## Post-build requirements

Verify the exact application-byte delta against exp9 is **only the 43 newly
selected targets**, with all 16 prior source results preserved. Then run the
paired full syntax selection, artifact-based CLI/API/SQL/HTTP/trusted-TLS
regressions and relevant actual-function controls on the built ZIP, using
exclusive lab ownership and independent executors. Remaining diagnostics or
compiler failures stay visible; no expected count is a measured result until
that run completes. No package/CI/main/release or `.20` authorization follows
from this selection or a successful experimental build.

## Selection-helper local controls

Ten synthetic tests pass without executing patches or creating an experimental
candidate: exact 16+43 preservation, cumulative omission, prior-entry reorder,
source overlap, patch-leaf collision, patch drift, upstream-target hash drift,
provenance drift, archive drift and unsafe source-patch paths. Their synthetic
ZIP is an input fixture only, not an exp10 build.

```sh
python3 -m unittest discover -s tools/php83/exp10-candidate -p 'test_*.py'
```

These tests validate staging/selection guards; they do not replace independent
selection review, the existing builder tests or the two real builds and archive
verification after review.

## Actual artifact execution (after selection review)

The primary and repeat builds now exist and are **byte-identical**, SHA-256:

```text
de177e6cbaedf3a3207661c2325f466cce37febb73190f3a49d31f24b740c053
```

The unchanged archive verifier confirms exactly59 modified source files versus
upstream and61 additional metadata files; all other upstream entry bytes remain
identical. The independent exp9→exp10 comparison confirms exactly43 new source
changes, preservation of the prior16 source results/selection entries, and no
added or removed non-metadata files. There are15,236 regular files and18,088 ZIP
entries. Original and previous artifacts are preserved.

Actual Cursor CLI independently runs the archive verifier with **byte-identical
verification report**, and separately recomputes the exp9→exp10 delta. Its first
inline delta-report attempt failed on stdin's `__file__`; the corrected attempt
is reported separately, not counted as an initial pass. See
[build result](evidence/exp10-candidate/build-result.json),
[primary verification](evidence/exp10-candidate/verification.json),
[Cursor verification](evidence/exp10-candidate/cursor-verification.json),
[delta](evidence/exp10-candidate/delta.json), and
[review phases](evidence/exp10-candidate/review-notes.md).

This closes only reproducible experimental assembly. The manifest's original
pending-review/build status records the selection phase and is not rewritten
inside an already hashed archive. Subsequent execution evidence is authoritative
for later phases. Whole-source syntax and actual artifact API/CLI regression
are tracked separately; no production/package/release gate is implied.
