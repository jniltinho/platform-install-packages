# Five guarded HLS segments and private decode

This derivative follows the actual successful two-manifest observation, not the earlier failed attempts. It retains the exact successful protocol-selection receipt and recovery history. No profile or delivery configuration is changed.

Primary nginx-vod-module tag 1.33 source (commit `1750eb08021e362859887fdfe842ed6a4997f576`) supports the same-parent TS segment builder, default `seg` prefix, one-based sequence, and `-v1-a1.ts` for the first video/audio tracks. See the separately authenticated source report. This does **not** prove installed binary/build correspondence or that all native playlists use consecutive indices. The permitted observation is deliberately narrower: exactly five consecutive segments 1–5, the already owned `index.m3u8` parent on HTTPS8444, VOD/version3/ALLOW-CACHE:YES/MEDIA-SEQUENCE1, ENDLIST and roughly ten seconds. Zero-duration skips, other tracks, multi-sequence routes, unknown tags, extra URL components and signers fail rather than being normalized.

All five URIs are checked before the first segment GET. Closed booleans record parent/sequence/track matches without raw URLs. Existing context/master/media guards and conservative candidate enrollment remain before these checks. GETs retain pinned CA, no proxy/redirect, private bounded memory, and total manifest-plus-segment bytes <=2MiB. TS framing is separate from the decoder proof.

The decoder reuses the previously reviewed sealed-executable/memfd runner. Root independently observed matching native `/usr/bin/ffmpeg` and `/usr/bin/ffprobe` hashes; new pre/post source guards check exact metadata and bytes. The fixed MPEG-TS demuxer, file-only protocol whitelist, selected video/audio maps, -xerror, resource limits, 30-second wall limits and private capped outputs prohibit external/network media input. Full decode requires exit0 and no stderr/stdout. Only bounded numeric video/audio metadata is exported. It is **observed metadata**, not an invented 640x360 transcoding golden or dynamic-library cohort attestation. New unit tests mock subprocess completion and do not themselves prove native downloaded-byte decode.

All existing finite privacy gates, original boundaries, whole-batch common-end convergence and both TLS-log adapters remain. No API/GET is retried by audit convergence. The new host projection is exercised end-to-end with success and missing/drift/private-field negatives, and the actual generated new dependency loop is executed in tests.

Root protocol after independent review:
- `run_hls_delivery8444.py --split-proof <actual delivery-context-reconciliation-native-r2.json> --split-proof-sha256 <exact hash> --check`
- Same arguments with `--output <new exclusive local artifact directory>`.
- Prior successful unit `baseline-freeze-6b33c740.service` must be inactive; stage `/var/lib/kaltura-baseline-hls-delivery8444-r1` must not exist.

No upload, unrelated media, profile change, production access, measured benchmark or full task-1.2 acceptance follows from this bounded probe.
