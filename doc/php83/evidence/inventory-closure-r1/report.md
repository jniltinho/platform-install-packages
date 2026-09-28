# Original ZIP extraction and inventory join — bounded task 1.1 delta

Using change `migrate-kaltura-php83`. This implementation fills the original-tree
coverage hole in the prior entrypoint tool, which counted original PHP paths but
only inventoried package entrypoint candidates. It does not adjudicate task 1.3
static findings or claim task 1.1 complete by itself.

The pinned original ZIP was read before/after, path/duplicate/nonregular member
checks passed, and a new exclusive local tree was extracted. All **15,175 regular
files / 186,369,136 bytes** then matched ZIP content hashes. The tree and large
JSON intermediates are ignored; no original application code was executed. The
proof records byte identity, not preservation of ZIP filesystem modes on disk.

Structured rows retain every original file, hash, size, mode, scan disposition,
and candidate classifications. **11,784 PHP-family paths**, **11,840 PHP opening-tag
candidates**, two PHP shebangs and 179 generated-client *path candidates* were
identified. These overlap; none is a distinct executable/reachable endpoint count.
All 14,873 bounded text members were scanned using the pinned existing scanner;
294 binary and eight oversized files remain explicitly unscanned. Its 5,537
invocation candidates contain only source identity, line and classification—no
raw command excerpts/arguments. Regex false positives and dynamic invocation
omissions remain possible.

The historical published-package identity report joins **13,454 PHP files**:
11,782 identical original files, two changed originals and 1,670 package-only
PHP overlays. All package owners remain attached. Every original row has an
explicit `matched_in_packaged_php_index`; false means no match in that *PHP-only*
index, never that non-PHP content is absent from package payloads. The original
package entrypoint report contributes all 18,336 candidate rows, not active paths.
20 vendor attribution rows remain literal historical evidence, not blanket license
or revision resolution. Root's separate license census and reviewer's route ledger
supply additional scopes; do not infer their results from this report.

## Reproduce

```sh
python3 -B tools/php83/inventory-closure-r1/build.py \
  --archive /tmp/kaltura-php83-audit/Rigel-18.20.0.zip \
  --extracted-tree doc/php83/evidence/inventory-closure-r1/.extracted \
  --output /tmp/inventory-closure-repeat.json
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover \
  -s tools/php83/inventory-closure-r1 -p 'test_*.py' -v
```

For a new extraction, choose a nonexistent owned tree and add `--create-new-tree`.
Existing extraction/output paths are never replaced. Trusted local archive scope;
this is not a hostile-archive resource sandbox. Exact input reports/scanner are
pinned in source; `result.json` records output/source hashes and accounting.

Eleven local tests passed. Initial test assumed sorted row index rather than
looking up the source path; it failed and was corrected without changing scanner
semantics. Independent review identified an overbroad non-PHP package-presence
label; the frozen revision uses the explicit PHP-index label above. Independent
rebuild/review result is recorded separately when terminal. No VM, dependency
changes, licenses guessed, task checkboxes changed or publication performed here.

## Supplemental identity join

`join_supplements.py` pins the final census, original-registry report and separate
route-selection report. Its actual join verifies **all4,999 vendor file hashes
and byte counts**, exact scope equality (including IDE root files), and **five
archived route-candidate owner identities**; all13 declared route IDs are unique.
See `supplement-join.json`. This does not turn notice candidates into applicable
licenses or declared build routes into runtime activation. Three extra local
positive/mutation tests pass (14 total). The original 11-test builder remains
unchanged and its independent rebuild matched byte-for-byte; separate reviewer
receipt is `../task11-independent-scope-r1/inventory-independent-result.json`.

## Final scoped component dispositions

`components-r2.json` adds 12 non-vendor directories carrying literal notice files,
37 original files with generated-header declarations, three explicit source-client
scopes (deployment UI client, admin-console JavaScript client, Activiti REST client),
112 package-owned generator PHP source files and all714 broader generated-client
path candidates. Every explicit scope retains archive/package/file identities;
unknown component revision/license is recorded as null with an explicit scoped
unresolved disposition. Notice directories overlap; they are not asserted to be
independent third-party packages or inheritable licensing boundaries. Generated
header matches may be models/examples, and path candidates are not classified as
executed clients. This is reproducible enumeration, not a transitive SBOM.

`maxmind-join.json` proves all35 original MaxMind file identities match the separately
reviewed official-commit comparison, retaining the distinction between byte match,
unique original version and release compliance. `reviewed-notices-join.json` is the
preferred 4,999-file join against the corrected R2 notice census; the original
supplement remains unchanged as historical evidence. Seventeen local tests passed.

The task1.1 acceptance decision should assess extraction/member accounting,
dependency/client/overlay/entrypoint enumeration, recorded scoped metadata and
source-backed selected/historical build paths. It should **not** require runtime
client generation, every static finding adjudicated, all-distro execution or legal
compliance approval. Those later gates remain open. Current source route evidence
includes Noble, Ubuntu26.04 and EL9 workflow selection, not successful distro builds.
No full task checkbox is set by these tools.

## Reproducible checkout inputs and publication boundary

`publish-manifest.json` lists focused candidate files; it does not authorize staging.
Existing tracked package-identities/primary.json, dependency-attribution primary,
and entrypoint scanner are required. The tracked entrypoint inventory is compressed:

```sh
python3 -B - <<'PY'
import gzip, hashlib
from pathlib import Path
root=Path('doc/php83/evidence/entrypoint-inventory/authorized-real-r1')
b=gzip.decompress((root/'inventory.json.gz').read_bytes())
assert hashlib.sha256(b).hexdigest()=='42c3e2411c3973e1f5591d4aacd31d1af2a7a05929af935992ab2ebcdae67501'
with (root/'primary.json').open('xb') as f: f.write(b)
PY
```

If primary.json already exists, verify the same hash rather than overwrite it.
The original ZIP is an external input supplied by the operator and must match
58d534d09b3b75c9a8333957268c884f79032638b2d44a278b1992fda1b0ab28;
no automatic download or application execution is performed. Regenerate
inventory-reviewed.json using a fresh extraction/output as above, or decompress
its deterministic .json.gz and verify 4cd9212e48d806ce7a5cdf852712f4f685cd32182add9a0ec0dacd46567ed162.
Supplement scripts require exactly the report paths listed in their literal pins.
The publish manifest deliberately excludes extraction trees, earlier large JSON
attempts, raw CLI logs, generated runtime configurations and credentials.
