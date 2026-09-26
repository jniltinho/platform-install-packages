# Baseline source fixtures and guarded-client preparation

**Current result: two synthetic source fixtures generated and independently
validated. No installed-AIO upload, READY, delivery or benchmark acceptance.**

The approved Decision7 source pair now exists under the sibling artifact directory
`platform-install-packages-php83-artifacts/baseline-media-r1/`. Media bytes are
not committed to Git. Reuse these exact bytes in both labs; do not regenerate a
nominally similar file for the candidate.

| File | Source | Decoded video frames | Bytes | SHA256 |
|---|---|---:|---:|---|
| short360.mp4 | 10s, 640×360, 25fps, H.264/AAC | 250 | 1511134 | `612d179c75f8f2374b7ac59c2dd7edba65e38eb357b870e8ad8c2e83d63b5473` |
| fullhd60.mp4 | 60s, 1920×1080, 60fps, H.264/AAC | 3600 | 117210794 | `611e3644fb56fc1f12ddccd1d889258d249e36a4eca445451c16d13f5c5f5b07` |

Audio is AAC 48kHz stereo. Actual video/audio/container durations equal10/60s.
The predeclared tolerance was one video frame plus one AAC1024-sample frame.
Full commands, encoder/prober executable hashes, versions, native output and
validation are in [generation manifest](evidence/baseline-protocol/media-generation-r1-manifest.json).
Single-threaded settings do not establish cross-build byte reproducibility.
Linked-library attestation was not performed.

## Independent execution

Actual Cursor CLI completed exit0, independently hashed media and tool binaries,
then ran native ffprobe on each file (both exit0), checking exact frame counts,
format/rate/duration and audio. See [machine report](evidence/baseline-protocol/media-independent.json)
and [public report](evidence/baseline-protocol/media-independent.md). It did not
regenerate media or touch a VM. This uses the same validation expectations with
a separate executor, not an independent generation build.

## Client preparation and review outcomes

The GET-only guarded client fixes a literal lab IP, scheme and port, rejects
redirects/proxies and invalid nested targets, requires explicit pinned private
CA material and bounds response bytes. OpenCode Muse independently identified
two exception-normalization defects; corrected code maps malformed CA and native
HTTP read failures to sanitized errors. Fifteen guard tests passed independently.

Nine media-preparation tests bring the root-owned local total to24. A second Muse
review incorrectly alleged the existing-output check reached a later finally.
The source actually raises before entering that try. Sentinel regression tests
and actual independent Cursor review disproved the finding without rewriting
correct source. The original review and adjudication are retained. A separate
deadline transport is being developed; do not infer its acceptance from this page.

## Remaining baseline gate

Source fixtures do not establish delivered profiles, preservation of1080p60,
upload-to-READY, thumbnails, HLS, byte-range streaming, TLS/API/UI acceptance or
timing. No real workload request was sent by this client preparation. Hard total
deadlines, transport integration, private credentials and lab origin guards,
exact profile selection, coherent baseline preservation, independently validated
HTTP/HTTPS rehearsal and the full frozen repetition protocol remain required.
All corresponding broad and detailed task checkboxes stay open.
