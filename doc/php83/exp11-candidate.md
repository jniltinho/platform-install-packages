# exp11 preparation — not selected or built

Status: **PREPARED_NOT_SELECTED**. This is a reviewable cumulative experimental
selection proposal, not permission to build, integrate or publish a new ZIP.
No exp11 archive or VM deployment was created by this preparation. Independent
actual CLI review and selection approval remain pending; ongoing autoload
composition testing must not be inferred to have passed from this manifest.

## Exact 59 + 4 selection

The [manifest](evidence/exp11-candidate/manifest.json) retains every field and
the order of all **59 exp10 entries**, then proposes four unique new targets:

| Order | Target | Existing held input |
|---|---|---|
| 60 | `alpha/apps/kaltura/lib/baseObjectUtils.class.php` | `patches/php83/held/base-object-ternary/base-object-ternary.patch` |
| 61 | `vendor/htmlpurifier/library/HTMLPurifier.autoload.php` | `patches/php83/held/autoload83/HTMLPurifier-autoload.patch` |
| 62 | `vendor/symfony-data/bin/symfony.php` | `patches/php83/held/autoload83/symfony-cli-autoload.patch` |
| 63 | `vendor/symfony/util/sfCore.class.php` | **Reuse exactly once:** `patches/php83/held/sfCore.class.php.patch` |

All 63 source paths and patch leaf names are unique. The sfCore patch is the
previous held repair, not a newly authored duplicate; its metadata remains in
`patches/php83/held/symfony-bootstrap.json`. Other mixed Symfony/bootstrap or
Spyc alternatives in that metadata document are not silently selected. The
ternary manifest's unchanged helper files remain provenance checks, not seven
additional patches.

The upstream source ZIP stays pinned to
`58d534d09b3b75c9a8333957268c884f79032638b2d44a278b1992fda1b0ab28`.
The exact prior exp10 manifest is pinned to
`db4c2b6dfff31f9fd64e05f29e0ccd79b2049e85e7c27ee29b2783605db387aa`.
The manifest and preparer also pin all four held metadata documents, rather
than accepting a new self-declared checksum as provenance. Existing manifests,
patches, original source and exp10 ZIP remain unchanged.

## What the preparation actually verified

[Final preflight](evidence/exp11-candidate/preflight-final.json), exit 0:

- exact prior-59 field/order preservation and normalized four-entry metadata
  joins, including unique source/patch names;
- pinned bytes for all five metadata inputs and the original archive;
- original source and referenced patch hashes for all 63 targets;
- original-byte hashes for the ternary manifest's unchanged helper inputs;
- strict single-file patch headers and exact GNU patch application to temporary
  private copies, rejecting offsets, fuzz, reversed/skipped hunks, unexpected
  files and mismatched resulting source hashes;
- a second whole-series resulting-file identity check after all applications.

The checker does not run PHP, invoke application code, construct a ZIP or modify
the originals. Its successful outcome remains `selection_approved=false`,
`zip_built=false`, `runtime_executed=false`, `application_acceptance=false`.
It fails if the manifest tries to claim a selected status at this phase.

**23 local synthetic tests pass**, including valid 59+4 replay, prior/addition
reordering, omissions/extra fields, target/leaf collisions, patch/metadata/source
drift, invalid after hashes, wrong target headers, forbidden symlink/traversal,
non-exact offset application, invalid sfCore metadata and unexpected changes
to helpers. These are preflight tests, not 23 application cases. The source
author's tests do not substitute for independent CLI execution/review.

`preflight.json` is retained as the first preparation run. Its later replacement
`preflight-final.json` reflects a wording-only limitation update: composition
evidence is now under review instead of implying that no other worker has run
it. Patch bytes, target selection and tool code did not change between these
preflights. Use the final report for the current manifest identity.

## Reproduce preparation only

From the migration worktree, without VMs or network services:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover \
  -s tools/php83/exp11-candidate -p 'test_*.py' -v
PYTHONDONTWRITEBYTECODE=1 python3 tools/php83/exp11-candidate/stage.py \
  --original /tmp/kaltura-php83-audit/Rigel-18.20.0.zip \
  --check-only
```

An optional `--report NEW_PATH` writes a new preflight report and refuses to
overwrite evidence. The alternate `--output NEW_DIRECTORY` stages only the
same manifest and explicit patch bytes for later inspection; it is not a ZIP
builder or selection-approval command. No staged output directory was created
in this preparation cycle. Do not pass these inputs to the ZIP builder until
the coordinator completes the independent review and approves that separate
experiment. Future artifact construction still requires two reproducible
builds, exact exp10-to-exp11 deltas, original preservation and execution from
the newly built artifact—not an unrelated manually patched tree.

## Evidence limits that remain visible

The ternary repair preserves PHP 7.4 left association, including legacy output
quirks. Existing evidence has **130 fixed expected cases plus 17 native-baseline
parity cases**, not 147 independent golden expectations. See the source repair's
own retained evidence and [Cursor's accounting](evidence/autoload83/cursor-notes.md).

[Autoload repairs](autoload83.md) preserve existing SPL branches and introduce
an explicitly documented appended callback for the CLI; this is not universal
PHP 7.4 composition parity. Positive configured task listing and the retained
empty-project failures must remain separate. Extended composition/exception/
duplicate-loader results require their own completed review before selection;
this proposal neither waives nor marks those cases successful.

No whole-candidate PHP 7.4 support is implied: the target remains PHP 8.3 and
original PHP 7.4 is the behavioral reference. Other compiler rejections, six
template-generation paths, runtime diagnostics, caches, frameworks, dependencies,
licenses, distro installation, media/workers/UI, performance and recovery remain
requirements. No package/CI integration, `main` merge, release publication or
`.20` cutover permission follows from a prepared selection.

## Structural verification scope

Graph freshness was checked: `kaltura-rigel-18.20.0-full` remained ready at
generation `2026-09-25T12:19:00Z`, 231,336 nodes and 800,641 edges. The four new
targets have [matching coverage metadata with no recorded gaps](evidence/exp11-candidate/coverage.json).
Relevant immutable-source hunks were read directly; the autoload call-context
audit is [retained separately](evidence/autoload83/audit-graph.json). No new broad
call-graph conclusion is made for the prior 59 files: their exact manifest and
archive/patch byte identities, rather than a graph completeness assertion,
establish preservation. Coverage remains best effort, not proof of runtime
reachability or exhaustive application compatibility.

## Separately authorized lab build phase

The coordinator subsequently authorized exactly the reviewed 59+4 source targets
for an experimental lab artifact, not production, packaging, publishing or full
application acceptance. The original `manifest.json` and preparation/review
reports remain unchanged and retain their historical `PREPARED_NOT_SELECTED`
status. `evidence/exp11-candidate/selected-manifest.json` is a separate selection,
bound to prepared SHA `dd9243b654a98385a30dd87a3bbf6e20a3034c9106311d135b57bc9f35696eb2`.
Its 63 patch entries are identical to those reviewed.

`tools/php83/exp11-candidate/selected.py` first repeats the strict original-ZIP
63-patch preflight, then stages the separately validated selected manifest and
patch bytes in a fresh directory. The existing audited generic builder is not
modified. `delta.py` independently checks the complete exp10/exp11 entry-byte
difference: only the four newly selected application targets, changed embedded
manifest and four new patch metadata entries are allowed. All 59 earlier target
bytes must retain their exact after-hashes. The generic ZIP verifier separately
checks original-source deltas, selected metadata and two-build reproducibility.

Local selection/delta tests are recorded as `artifact-tests.*`; these are harness
checks, not application execution. Actual build and verification results are
recorded separately in `build*`, `verification.*` and `delta.*`. Artifact-based
PHP compiler/runtime testing remains a distinct subsequent phase.

Build result: both fresh output directories, `exp11` and `exp11-repeat`, contain
byte-identical `Rigel-18.20.0-php83-experimental.exp11.zip` with SHA-256
`f2474f5b951bfd2d121291025c8dd4554697fb5bb4024e132987643dab6144a7`.
Original-versus-candidate verification found 63 changed source entries and 65
added metadata entries; exp10-versus-exp11 found exactly four changed source
entries, one changed metadata manifest and four added patch entries. The 59
prior targets and every other shared entry retain their original exp10 bytes.

Reproduction (use **new, nonexistent** output paths):

```bash
original=/tmp/kaltura-php83-audit/Rigel-18.20.0.zip
artifacts=/home/nilton/Projetos/nilton/NOVOS/platform-install-packages-php83-artifacts
stage=$(mktemp -d)
python3 tools/php83/exp11-candidate/selected.py --original "$original" --output "$stage/patches"
python3 tools/php83/build-experimental-zip.py "$original" "$artifacts/exp11-new" --patch-dir "$stage/patches"
python3 tools/php83/build-experimental-zip.py "$original" "$artifacts/exp11-new-repeat" --patch-dir "$stage/patches"
python3 tools/php83/verify-experimental-zip.py "$original" \
  "$artifacts/exp11-new/Rigel-18.20.0-php83-experimental.exp11.zip" \
  "$artifacts/exp11-new-repeat/Rigel-18.20.0-php83-experimental.exp11.zip" \
  doc/php83/evidence/exp11-candidate/selected-manifest.json "$stage/verification.json"
python3 tools/php83/exp11-candidate/delta.py \
  "$artifacts/exp10/Rigel-18.20.0-php83-experimental.exp10.zip" \
  "$artifacts/exp11-new/Rigel-18.20.0-php83-experimental.exp11.zip" "$stage/delta.json"
```

Prepared metadata is historical: its original “proposals, not implicitly
promoted” wording is retained; the selected manifest's explicit authorization is
only for this experimental artifact. No active/default patch manifest changed.

Independent actual OpenCode (Muse Spark 1.3 Free) subsequently executed the same
37 local tests with exit 0 and reviewed selected/delta tooling and repository
reports, with no reported permission/tool failures. This was explicitly
**repository-only review, not independent ZIP replay**. See
`opencode-artifact-public.txt`, `opencode-artifact-tests.*`, terminal
`opencode-artifact.exit`, and `artifact-result.json`. Reviewed tool/manifest
identities were unchanged through that review.
