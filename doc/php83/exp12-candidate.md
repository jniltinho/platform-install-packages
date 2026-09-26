# exp12 cumulative draft — not selected or built

Status: **DRAFT_PENDING_CRITERIA_COMPOSITION_NOT_SELECTED**.
No exp12 ZIP, VM execution, package selection or publication is authorized by this
preparation. Criteria composition review/native tests and coordinator approval
remain prerequisites, then independent exp12 input review before any build.

## Exact proposed 65 source targets

The [draft manifest](evidence/exp12-candidate/draft-manifest-r3.json) derives from the
**selected** exp11 manifest, SHA256
`99f87bf705b0a9c419229fc5c1484919e6de4ebc24dabcccb359b5bb762af2ff`.
It is not derived from the historical prepared exp11 manifest.

- 62 prior entries retain every field and their order exactly.
- One explicit replacement at the original Criteria position combines the selected
  native-return changes with the class-level AllowDynamicProperties attribute.
  The complete old entry remains recorded as superseded provenance; it is not
  applied twice. The original selected Criteria patch bytes and strict replay are
  also verified separately, not just its supersedes filename. Candidate source after SHA256
  `f8f726443dbc3af363f6c08db2d6baa92591b37bb14abd104ac6a5951b5f6d8d`.
- Two unique targets are appended: held Pake relative-path closure, and held
  sfPakeGenerator numeric DEBUG token repair. DEBUG's explicit Pake prerequisite
  must match the appended source hash.

All65 source paths and patch basenames are unique. Patch inputs/metadata/upstream
ZIP identities are pinned; original source hashes and strict private-copy replay
verify all65 targets without offsets/fuzz. Nineteen local tests cover prior omission,
wrong prior selection, cumulative hash drift, unauthorized promotion, prerequisite
mismatch and actual65 replay. No native runtime is invoked.

[Preflight](evidence/exp12-candidate/preflight-r3.json) is preparation evidence only.
The copied Criteria patch is a reviewable exact pending input, not a selection.
Its cross-engine serialized layout difference remains a known baseline failure;
no cache or backend acceptance transfers. Pake/DEBUG source-stage proofs do not
become exp12 artifact proof until an approved ZIP exists and is tested.

## Reproduce draft in fresh output files

```sh
python3 tools/php83/exp12-candidate/prepare.py \
  --original /tmp/kaltura-php83-audit/Rigel-18.20.0.zip \
  --manifest /tmp/exp12-draft-manifest.json \
  --report /tmp/exp12-draft-preflight.json
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover \
  -s tools/php83/exp12-candidate -p 'test_*.py' -v
```

The preparer refuses existing outputs and has no ZIP build or approval option.
After explicit approval, a separately reviewed selected manifest and fresh patch
stage should feed the existing deterministic builder twice in distinct exp12 and
exp12-repeat artifact directories. Verify65 source repairs and original metadata,
then exact exp11→exp12 delta of3 source files (Criteria replacement + two additions).
Do not create those artifacts or rename the draft to selected before approval.

## Review checkpoint (draft history retained)

Actual Claude independently executed19 local tests, verified7 frozen inputs, and
replayed the65 patches into a fresh private temporary tree; both manifest and
preflight exactly match retainedr3. It also checked metadata mutation guards and
old/new Criteria bytes: removing the single27-byte class attribute from the new
source reproduces every selected exp11 Criteria byte. See
[public review](evidence/exp12-candidate/claude-r3-public.json).

The earlier pending-Criteria status is retained in the frozen draft as historical
preparation state. The coordinator subsequently received actual primary and Cursor
composition repetition in commit c7cf5fb4; that bounded evidence does not waive the
known cross-engine layout failure. Selection/build still require explicit approval.
No artifact has been created by this draft. Additional negative tests and exact
message assertions remain coverage improvements noted by the reviewer; no guard
failure was observed. The test suite deliberately requires the pinned local ZIP.

## Authorized lab-only selection and reproducible artifact

The coordinator explicitly approved a separate selected manifest after the reviewed
65-target input and independently repeated Criteria/DEBUG bounded evidence. The
frozen drafts are unchanged. [Selected manifest](evidence/exp12-candidate/selected-manifest.json)
records the exact authorized metadata transition, deliberate hierarchy-wide Criteria
exemption and retained strict cache-layout FAIL. It authorizes neither production,
publication, packages nor artifact runtime acceptance.

Actual Claude prebuild review executed25 tests and8 checksum checks, reviewed the
fresh stager and unchanged generic builder/verifier, and found no blocking defect.
Both fresh builds and actual verification completed exit0:

- Artifact: `platform-install-packages-php83-artifacts/exp12/Rigel-18.20.0-php83-experimental.exp12.zip`
- Repeat: same filename under `exp12-repeat/`.
- Both SHA256: `de5e61a1b54f472e605ef2e87669302a3915616fd85378e0f05706fcb06a7e8b`.
- [Verification](evidence/exp12-candidate/verification.json):65 changed source files
  against pinned original, reproducible ZIP bytes and exact selected metadata.
- [Delta](evidence/exp12-candidate/delta.json): exactly3 changed source files versus
  exp11 (Criteria, pakeApp, sfPakeGenerator),62 prior targets unchanged. Three patch
  metadata additions, one superseded Criteria metadata removal and changed manifest;
  every other shared entry retains identical bytes.
- Original ZIP and every prior artifact listed before the build retain their hashes.

The selected manifest's inherited `zip_built:false` describes its prebuild
provenance; actual build result is recorded here and in verification evidence.
Artifact syntax/API/CLI/additions and generator/Criteria regressions remain pending.
This is an experimental source artifact, **not a release**.

Reproduce with fresh paths only:

```sh
python3 tools/php83/exp12-candidate/selected.py --original ORIGINAL.zip --output NEW_STAGE
python3 tools/php83/build-experimental-zip.py ORIGINAL.zip NEW_ARTIFACT_DIR --patch-dir NEW_STAGE
python3 tools/php83/build-experimental-zip.py ORIGINAL.zip NEW_REPEAT_DIR --patch-dir NEW_STAGE
python3 tools/php83/verify-experimental-zip.py ORIGINAL.zip EXP12.zip EXP12_REPEAT.zip \
  doc/php83/evidence/exp12-candidate/selected-manifest.json NEW_VERIFICATION.json
python3 tools/php83/exp12-candidate/delta.py EXP11.zip EXP12.zip NEW_DELTA.json
```
