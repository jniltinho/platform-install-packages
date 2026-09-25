# Experimental PHP 8.3 source ZIP — exp2

**Lab source artifact only. Do not deploy it to `.20`.** The original PHP 7.4
archive and releases remain unchanged. No DEB/RPM/CI source pointer is changed.

## Artifact

`Rigel-18.20.0-php83-experimental.exp2.zip`

SHA-256: `99233ac6638f02072b3394159340edd1e2388b243bafadca3fe33b6bbafa97a0`

The two independent local builds produced identical ZIP hashes. Verification
compared all 18,027 original ZIP entries: only three source files have different
bytes, none are missing, and five experimental metadata entries were added.
Timestamps and permission modes are intentionally normalized for reproducibility;
this is not a byte-identical rearchive of original ZIP metadata.

The patched files are Services_JSON, Zend JSON Encoder and Zend JSON Decoder.
All 54 replacements are curly-brace to square-bracket string offset syntax.
There is no framework version upgrade, no Registry/Propel/Symfony repair, and no
performance improvement claim in this artifact.

[Patch series and build instructions](../../patches/php83/README.md).
[Manifest](../../patches/php83/manifest.json).
[ZIP verification](evidence/experimental-zip/exp2/archive-verification.json).
[Build toolchain report](evidence/experimental-zip/exp2/build-report.json).
[Checksum file](evidence/experimental-zip/exp2/SHA256SUMS).

The source archive is not itself the complete installed package payload; build
overlays and generated extras must still be reconciled before package integration.

## Executed checks

- All three patched files pass PHP 7.4.33 and PHP 8.3.6 compiler checks; the
  original files fail on 8.3. Changed lab file hashes match the manifest/ZIP.
- Eight behavioral comparisons pass: two JSON codecs × two PHP candidate
  versions × two INI modes, against the matching unpatched 7.4 baseline.
- Standard INI loads mbstring/iconv; minimal INI has neither. Reports verify
  those module states rather than assuming flags worked.
- Each codec exercises 13 roundtrip values: scalar/null/boolean/numeric,
  punctuation and escapes, control characters, two-/three-byte Unicode, empty
  arrays, nested arrays and nullable members. Encoded and decoded output must
  exactly match the baseline, not just return exit zero.
- Runs use the existing unprivileged, read-only bind-mounted lab sandbox with
  socket creation denied. No configured Kaltura tree, DB or `.20` is involved.
- The builder's offline tests cover repeatability, preservation, source/patch
  drift, output hash mismatch, existing output refusal and unsafe archive paths.

[Behavior and retained diagnostics](evidence/experimental-zip/exp2/behavior.json).
[Source hashes and compiler results](evidence/experimental-zip/exp2/source-lint.json).

This corpus does **not** cover malformed JSON, surrogate pairs, all legacy UTF
branches, HTTP behavior, API authorization, workers or full application bootstrap.
It does not establish JSON standards compliance beyond baseline parity.

## Diagnostics and held changes

Deprecations are recorded, not suppressed or accepted as harmless. Examples:
Services_JSON's dynamic `$use` property, Zend decoder's dynamic `$_tokenValue`,
and old Services_JSON_Error constructor declarations on the 7.4 baseline. Output
parity does not waive these diagnostics; production error-handler behavior remains
part of the full acceptance gate.

The first Registry experiments are held after expanded property fixtures exposed
behavior differences. The earlier four-file `exp1` scratch ZIP was never approved
or published; do not use it. `exp2` explicitly excludes Registry rather than
silently marking its failing tests passed. Its original PHP 8.3 blocker remains.

Independent Claude/Grok review of the syntax patches found the offset changes
bounded but identified coverage gaps. The corpus was extended to run without
mbstring/iconv and include Registry property writes; that extension is what
caught the held Registry difference. Reviewer opinions are not operator release
approval or a substitute for runtime evidence.

## Reproduction of the behavioral corpus

Prepare candidate copies from the verified public package payload on `.74` and
`.83` (not `/opt/kaltura/app`), apply only the three active patches, and verify
before/after hashes from the manifest. Place `behavior.php` and `run-one.sh` from
`tools/php83/patch-tests/` in each guest's `/home/vagrant/php-patch-tests/`.
The candidate app copy must be `/home/vagrant/php-patch-tests/candidate`.
Then, with the existing host SSH configs for the two disposable VMs:

```sh
python3 tools/php83/patch-tests/collect.py report.json --case legacy-json --case zend-json
python3 -m unittest discover -s tools/php83 -p 'test_*.py'
```

The collector exits nonzero on a comparison failure and retains stderr. Omitting
`--case` also runs Registry, which is expected to fail on the unchanged 8.3 source;
that full set is intentionally not the acceptance criterion for this JSON-only
patch batch. Remaining migration tasks and the final release gate stay open.

## Builder review and local artifact location

Claude's independent review identified builder issues which were corrected before
these final hashes were generated: hash a single immutable input byte snapshot,
check every output after the complete patch series, reject reversed/offset patches,
reject metadata-name collisions, preserve ZIP comments and executable intent,
and set the directory attribute explicitly. Tests include cross-patch mutation,
symlinks, reserved metadata, offset application, executable modes and comments.
No distribution was made from the earlier scratch hashes.

The completed lab artifact is stored locally at:

```text
/home/nilton/Projetos/nilton/NOVOS/platform-install-packages-php83-artifacts/exp2/
```

This directory contains the ZIP, `SHA256SUMS`, the build report and an explicit
not-for-deployment note. The ZIP is not committed to Git and no GitHub release,
tag or main-branch merge was created.

Re-run full archive verification with the committed verifier:

```sh
python3 tools/php83/verify-experimental-zip.py ORIGINAL.zip FIRST.zip SECOND.zip \
  patches/php83/manifest.json verification.json
```
