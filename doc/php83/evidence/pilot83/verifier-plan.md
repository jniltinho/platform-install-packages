# Independent private-DEB verifier — prepared, not executed against builds

CLI: `python3 tools/php83/pilot83/verify-private-debs.py BUILD_A BUILD_B --inputs CONTRACT_JSON --inputs-sha256 REVIEWED_SHA256 --output FRESH_REPORT_JSON`.

Contract schema1: `inputs` exact keys bundle/published/payload/controls/hooks/privacy_contract, each `{path,sha256}`; `new_helpers` exactly two reviewed kaltura-postinst source files with package/path/source_path/before_sha256:null/after_sha256/mode:420/uid:0/gid:0. Contract is an independently reviewed/pinned input, never inferred from a builder report. Final hookR2 contract remains pending; no placeholder acceptance.

Read-only `dpkg-deb --fsys-tarfile`/`--ctrl-tarfile`, no extraction or hook execution. Original17DEBs joined to published immutable bundle; actual new inventories exact except78source targets, named hooks, controls, reached installer helper and2newhelpers. Replacement metadata preserved. New XML/helper metadata explicit. md5sums recomputed against every regular data member; old md5sums metadata preserved or new root0644. Other bytes/type/link/mode/numeric UID/GID/PAX fields unchanged; only tar mtime/order/textual owner names are nonsemantic normalization ignored. Existing pinned inventory has37149regular/6610directories/6symlinks/nohardlinks. Unknown special members rejected; no broad tar extraction.

Both actual output directories must contain exactly expected17DEBfilenames and identical complete DEB bytes. Each is parsed and compared independently. Source-policy7helpers+3evidence references rehashed; private5output hashes joined. Build reports are not trusted as proof; APT origins/resolution, native installation, hook confidentiality and application acceptance remain NOT_VERIFIED. Failures raise nonzero and do not write a PASS report. The caller must retain failed command outputs in a distinct attempt.

22synthetic guard tests passed author-local: unchanged/added/removed/changed data, hash drift, links, metadata and boolean misuse, tar duplicates/traversal/special/PAX, permittedmtime, md5 inventory/duplicates/content and full synthetic package comparator. This is not a real DEBbuild or independentreview; actual runs wait final inputs and two builder directories.

## Actual R2 build verification

Codex independently executed the frozen verifier against `pilot83-private-r2`
and `pilot83-private-repeat-r2`: exit0, stderr empty. All17DEBs (177120680bytes per
build) match byte-for-byte and pass actual control/data comparisons against the
published originals, with81expecteddata rows/43control rows (including unchanged
named hooks). Report `verifier-actual-r2.json` SHA256
`796472e7920b8390610e4bb5207f7e5560cb26f23ae2db5e6a1befb5c9e5129b`.
The22guards and14independent reviewer metadata mutants passed; source freeze
remains exact. This does not execute hooks, resolve APT or install the app.

The first candidate-authored R1 verification failed `MD5SUMS_LINE`: builder had
written a lone newline for empty-payload packages. That failure remains in the
candidate's `private-debs-verification-r1.*` evidence. Builder was corrected to
write an empty file and both builds were repeated in fresh R2directories. The
verifier was **not relaxed**. Final source hashes still match verifier-freeze-r1.
