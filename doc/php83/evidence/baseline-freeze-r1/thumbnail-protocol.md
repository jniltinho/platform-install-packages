# Same-entry thumbnail: bounded new probe

This is a new functional observation, not a repeat of the successful HLS case.
The root coordinator alone may execute it after independent review. No native
thumbnail result or golden dimensions/size are claimed by these synthetic tests.

The existing root-owned USER-session, original/source fixture checks, target
identity, immutable stage, CA-pinned API8443 transport, both TLS log adapters,
finite same-original-start privacy scans and common-end convergence remain.
The new workload makes thumbasset/list and getUrl, then at most one HTTPS443 GET.
It selects exactly one READY thumbnail owned by entry 0_wzmt2sfy/partner102;
returned version and dimensions are validated, not inferred from the video asset.
Multiple READY rows or unsupported metadata fail closed rather than choose one.

Source: original checksum-verified archive, ThumbAssetService.php lines1020–1039
requires thumbnail type, existing entry, READY and access control before getUrl.
thumbAsset.php lines25–43 builds the exact serve/thumbAssetId path, conditionally
v (>1), pv and ev. Lines55–75 invoke getDownloadUrl(true), with possible edge
routing; asset.php's download helper can mint a KS. Those variants are NOT
implicitly authorized: every returned URL is enrolled before any guard failure,
current secret/KS markers are checked first and queries, auth paths, unknown
suffixes, alternate origin and encodings are rejected. No rewriting or redirects.
The three exact thumbnail PHP files are pinned before auth and at postcheck.
Existing asset.php source pin remains enforced by the inherited source guard.

GET is bounded to1MiB, identity encoding, one JPEG Content-Type and JPEG framing.
Pinned ffprobe/ffmpeg read the private sealed bytes with mjpeg input and only
file protocol; one MJPEG frame must match the API width/height, each<=4096 and
product<=4Mi pixels. Full image decode must return zero with no stderr. Executable
hashes are the root-observed binaries; dynamic library cohort is not attested.
No image bytes, URL, token, private output or image hash is exported.

New stage /var/lib/kaltura-baseline-thumbnail-r1; prior successful HLS unit
baseline-freeze-b93f7882 must be inactive. Use run_thumbnail.py with the same
externally pinned actual context-reconciliation receipt and existing strict SSH
configuration, first --check and then one actual execution with new output.
No failed stage reuse or automatic workload retry. Exact CLI flags are preserved
from the reviewed HLS runner. The historical profile mutation remains failed;
context reconciliation does not relabel it atomic or eliminate recovery limits.

Independent Claude source-only review completed (no CLI test execution). Its
suggestion to guard before URL enrollment was rejected because rejected URLs
must still be covered by privacy scanning. Its corruption-concealment concern
was addressed with explicit `-err_detect explode` before MJPEG input in both
ffprobe and ffmpeg, preserving fail-closed exit/stderr checks. The focused argv
regression and full 330-test local suite passed after this minimal delta.
