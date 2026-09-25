# exp3 experimental API web candidate selection

Date: 2026-09-25. **Selection reviewed for an isolated experiment by Cursor CLI.**
Construction results are recorded below when verified; no execution of the built
artifact or successful application acceptance is inferred from selection.
The user-authorized purpose is to assemble the best already exercised repair
combination into a reproducible artifact and test that artifact as a whole.
Full application acceptance is not a prerequisite for building this isolated
experiment; it remains a prerequisite for declaring the migration successful.

## Scope and selected inputs

The separate [exp3 manifest](evidence/exp3-candidate/manifest.json) pins the
original ZIP SHA256, exact ordered patch bytes and original/resulting file
hashes. It does not replace `patches/php83/manifest.json`, which remains exp2,
or rewrite the historical inventory/disposition ledger. No production package
or CI source pointer changes. The exp2 ZIP is never overwritten.

| Order | Exact repository patch path | Selection rationale |
|---|---|---|
| 1 | `patches/php83/0002-Services_JSON.class.patch` | Existing exp2 JSON offset syntax repair; no algorithm change. |
| 2 | `patches/php83/0003-Encoder.patch` | Existing exp2 Zend JSON encoder offset repair. |
| 3 | `patches/php83/0004-Decoder.patch` | Existing exp2 Zend JSON decoder offset repair. |
| 4 | `patches/php83/held/KalturaPDO-query.patch` | Removes the PHP 8.3 PDO declaration fatal; direct argument forwarding preserves bounded native controls and tested API behavior. |
| 5 | `patches/php83/held/dateUtils-ternary.patch` | Removes the session-path nested-ternary fatal while preserving PHP 7.4 left association and legacy formatting quirks. |
| 6 | `patches/php83/held/doc-comment-property.patch` | Declares the existing public property without changing parser logic, eliminating selected dynamic-property diagnostics in the tested web path. |

The first five reproduce the functional candidate in [api-web.md](api-web.md):
real `api_v3/web/index.php`, synthetic SQL/session/authorization checks, Apache
HTTP and trusted HTTPS. The sixth was subsequently exercised with the same
harness in [doc-comment-property.md](doc-comment-property.md). The retained
[comparator](evidence/doc-comment/comparison.json) reports unchanged stdout and
harness hashes, with selected diagnostic occurrences reduced from 4,408 to zero.
This does **not** mean every diagnostic disappeared.

[api-mysql.md](api-mysql.md) records PDO forwarding/native controls;
[api-session.md](api-session.md) records nine duration cases and the fatal
counterfactual when only the date repair is removed.
[doc-comment-consumer.md](doc-comment-consumer.md) covers six complete original
PHP 7.4 parser-object serializations and the actual annotation/deserialization
consumer. These are bounded prior results on lab trees, not evidence that a
new exp3 ZIP has been executed or that every application path works.

## Explicit exclusions, not forgotten work

- The seven Symfony repairs and `core_compile.yml.patch` are a separate next
  integration expansion. [The ordering follow-up](symfony-bootstrap.md#follow-up-duplicate-class-blocker-resolved)
  records successful bounded bootstrap/decorator parity. They are not required
  by the already demonstrated API web path; they must still be integrated and
  tested for the full migration, not indefinitely held pending full acceptance.
- DebugPDO alternatives are never stacked. V3 has the strongest forwarding
  evidence, but numeric/API compatibility remains open. It is not the
  `KalturaPDO` class required by this path; see [DebugPDO](debug-pdo-experiment.md).
- `Registry-properties.patch` is rejected. `Registry-cast.patch` has unresolved
  flag 2/3 property semantics. Exclusion leaves a known compatibility blocker,
  not a claim that Registry is unneeded by the whole application.
- The [APCu experiment](apcu-cache.md) failed counter assertions and is not
  selected. Real cache-enabled persistence/invalidation and separate legacy
  opcode/upload-progress capabilities remain unresolved.

## Staging and build recipe — independent selection review completed

Run from the migration worktree. Requires Python 3 and GNU patch. Set
`ORIGINAL_ZIP` to the pinned original public ZIP, `BUILD_A` and `BUILD_B` to two
different, **nonexistent** output directories outside the repository/source
tree, and `REPORT` to a new verification report path. Neither output is the
existing exp2 directory. No package installation, VM operation or deployment is
part of these commands.

The builder requires leaf patch names beside its input manifest. Staging copies
only the six explicit paths from the manifest, verifies their recorded hashes,
and normalizes no source bytes. The manifest's `source_patch` field retains
repository provenance; its `patch` field is the builder's leaf name. Held
metadata's `patch_sha256` was mapped to the builder's `sha256` field without
modifying the original metadata.

```sh
set -eu
: "${ORIGINAL_ZIP:?set original ZIP path}"
: "${BUILD_A:?set first new output directory}"
: "${BUILD_B:?set second new output directory}"
: "${REPORT:?set new verification report path}"
test "$BUILD_A" != "$BUILD_B"
test ! -e "$BUILD_A"
test ! -e "$BUILD_B"
test ! -e "$REPORT"
stage=$(mktemp -d /tmp/php83-exp3-patches.XXXXXXXX)
trap 'rm -rf -- "$stage"' EXIT
python3 - "$stage" <<'PY'
import hashlib
import json
from pathlib import Path
import sys

manifest = Path('doc/php83/evidence/exp3-candidate/manifest.json')
data = manifest.read_bytes()
selection = json.loads(data)
stage = Path(sys.argv[1])
for entry in selection['patches']:
    patch = Path(entry['source_patch']).read_bytes()
    if hashlib.sha256(patch).hexdigest() != entry['sha256']:
        raise ValueError('Source patch checksum mismatch: ' + entry['source_patch'])
    name = entry['patch']
    if Path(name).name != name or not name.endswith('.patch'):
        raise ValueError('Expected leaf patch name')
    with (stage / name).open('xb') as out:
        out.write(patch)
with (stage / 'manifest.json').open('xb') as out:
    out.write(data)
PY
python3 tools/php83/build-experimental-zip.py "$ORIGINAL_ZIP" "$BUILD_A" \
  --patch-dir "$stage"
python3 tools/php83/build-experimental-zip.py "$ORIGINAL_ZIP" "$BUILD_B" \
  --patch-dir "$stage"
python3 tools/php83/verify-experimental-zip.py "$ORIGINAL_ZIP" \
  "$BUILD_A/Rigel-18.20.0-php83-experimental.exp3.zip" \
  "$BUILD_B/Rigel-18.20.0-php83-experimental.exp3.zip" \
  "$stage/manifest.json" "$REPORT"
```

Expected and subsequently observed by the construction verifier below: identical repeated ZIP hashes, all original
entries retained, exactly six changed source files and eight added metadata
entries (manifest, README and six patches), and identical bytes for every other
original entry. Retain builder/verifier identities and Python/zlib versions.
Report any failure; do not alter expected deltas to make verification pass.

## Execution required after construction

Extract the verified built artifact into a fresh owned lab candidate. Do not
substitute another manually patched tree and call it ZIP acceptance. Rerun
original PHP 7.4 versus candidate PHP 7.4/8.3 comparisons for JSON, native PDO
forwarding/date cases, parser serialization/consumer and actual Apache
HTTP/trusted-HTTPS session/authorization behavior. Preserve original PHP 8.3
counterfactual failures where the fixtures require them. Record artifact,
source/patch/harness/runtime identities, executor/reviewer, exits, diagnostics
and cleanup. Follow the canonical actual Claude/Grok/Cursor CLI coordination
rule and report any authorized OpenCode fallback under its own identity.

Real cache-enabled behavior, clean-runtime diagnostics, full dependency/license
inventory, three-distro installed services, uploads/media/workers/UI,
performance and upgrade/recovery are still separate migration requirements.
Building or passing this experiment grants no production package/CI integration,
release publication, `main` merge or `.20` deployment approval. Preserve the
feasibility, release and explicit target/window/backup cutover gates.

## Observed construction — 2026-09-25

Codex built the selected manifest twice in separate new artifact directories.
Both ZIPs have SHA256:

`1c64edb5ff34308cedfcea3c7879187c21417b6bd1a8e083d70d580bedc985e3`

The [exact-delta verifier](evidence/exp3-candidate/verification.json) reports six
changed source files, eight metadata additions, all 18,027 original entries
retained and every other original entry byte unchanged. Builder/verifier/input
identities and Python/zlib versions are retained in the reports.

Artifact location: `platform-install-packages-php83-artifacts/exp3/` beside this
worktree; repeat in `exp3-repeat/`. The ZIP was extracted separately under
`exp3-extracted/server-Rigel-18.20.0` for the next regression cycle, with the six
after-hashes checked. This is source staging, **not PHP execution evidence**.

Cursor independently reviewed the selection and verified all six patch hashes
and original/result metadata before construction. Claude's separate document
review timed out at 120 seconds with no final result; no approval is attributed
to that attempt. Independent artifact verification is recorded separately.
Full integrated runtime tests of the extracted ZIP remain the next action.

Cursor also independently executed the exact ZIP verifier (exit 0); its report
matches the primary report field-for-field. It verified the original and exp2
SHA256 values are unchanged. [Structured result](evidence/exp3-candidate/result.json)
and [current experimental disposition ledger](evidence/exp3-candidate/selection-ledger.json)
retain the six selected, one rejected and twelve deferred decisions. The earlier
batch-2 ledger remains historical, not silently rewritten.

## Subsequent artifact-based execution

The [first focused CLI regression](exp3-runtime.md) now executes this ZIP's
extracted files on 7.4 and 8.3 with independent reruns. All candidate rows return
zero and typed-output/parser-entry parity holds, but deprecations remain. This
supersedes the earlier NOT_RUN staging status only for that bounded matrix;
PDO/date SQL/session, Apache/TLS and wider application gates remain open.
