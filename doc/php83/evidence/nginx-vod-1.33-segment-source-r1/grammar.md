# Tagged nginx-vod-module 1.33: narrow TS segment route evidence

## Provenance and limits

The official GitHub tag `1.33` resolved through the HTTPS Git-ref API to commit `1750eb08021e362859887fdfe842ed6a4997f576`. Each saved source was downloaded from that **commit**, capped at 1 MiB, SHA256-recorded, and its Git blob SHA1 recomputed and matched against the commit tree. The tree was not truncated. `source-pins.json` records exact URLs and hashes. This is public upstream source identity, not a signed release attestation or proof that the installed binary was built from these exact bytes. No source was executed, compiled or installed; no VM/API request was made.

Packaging `build/sources.rc:154–155` selects 1.33; `deb/kaltura-nginx/debian/rules:19,91` selects that module archive. Their current SHA256 values are respectively `84b0535bc1d93d06f1196e22b3cfb35a75244f5d7fe6958f67e4e01d80c19505` and `8edcc518531853886970f04ba71494ffea14b5f8daa7b76f992bfc90e94bc708`. Graph coverage was checked: sibling project generation 2026-09-25T19:28:02Z, both paths freshness `not_tracked`; conclusions use direct source reads, not graph completeness.

## Producer and parser

- [m3u8_builder.c](https://github.com/kaltura/nginx-vod-module/blob/1750eb08021e362859887fdfe842ed6a4997f576/vod/hls/m3u8_builder.c), lines117–130: segment name = selected base URL + configured prefix + hyphen + decimal `(segment_index + 1)` + track suffix. Lines70/428 select `.ts` for MPEG-TS. Lines442–447 build the track suffix; lines713/720 emit segment references.
- [manifest_utils.c](https://github.com/kaltura/nginx-vod-module/blob/1750eb08021e362859887fdfe842ed6a4997f576/vod/manifest_utils.c), lines352–400: each video/audio track contributes `-v`/`-a` plus one-based track index. Multi-sequence mode can add `-fN` or `-sID`; those forms are outside the proposed narrow guard.
- [ngx_http_vod_hls.c](https://github.com/kaltura/nginx-vod-module/blob/1750eb08021e362859887fdfe842ed6a4997f576/ngx_http_vod_hls.c), lines1132/1139: defaults enable absolute index URLs and use segment prefix `seg`. Lines1215–1221 recognize prefix + `.ts` and require segment index parsing.
- [ngx_http_vod_request_parse.c](https://github.com/kaltura/nginx-vod-module/blob/1750eb08021e362859887fdfe842ed6a4997f576/ngx_http_vod_request_parse.c), lines249–263: positive segment index is required and converted to zero-based internally. The server accepts more forms than the proposed client guard; do not inherit its entire grammar.

## Same-parent URL binding

HLS source lines422–445 derive the segment base from the current request unless an explicit segment-base override exists. [ngx_http_vod_utils.c](https://github.com/kaltura/nginx-vod-module/blob/1750eb08021e362859887fdfe842ed6a4997f576/ngx_http_vod_utils.c), lines181–285, derives the default scheme from the TLS connection, uses the request Host and retains the URI through its last slash. Config overrides can change this; therefore source defaults alone never authorize another host/path.

The next guard can require the already validated exact HTTPS8444 origin and exact owned `index.m3u8` parent, then only `seg-N-v1-a1.ts` for this deliberately narrow first-video/first-audio case. Match actual references privately; do not synthesize replacement URLs. Unknown tracks, multi-sequence selectors, different parent, percent escapes, credentials, query/fragment, alternative extensions or protocols fail closed. The actual five-reference counter does **not** yet prove any of these filename properties.

## Media playlist contract

`m3u8_builder.c:11–14` emits the target duration, fixed `ALLOW-CACHE:YES`, and VOD/event type. Lines592–599 choose VOD for a VOD media set. Lines660–664 emit version and one-based first media sequence. Lines1520–1535 use version3 for default unencrypted/key-format-empty mode; encryption/key formats may require version5, and fMP4 uses version6. A TS-only unencrypted narrow guard should reject these other modes rather than reinterpret them.

Lines132–140 generate EXTINF durations; lines684–720 emit ranges in order and skip zero-duration ranges. Thus a universal consecutive-index assumption is not justified. For this specific five-segment fixture, requiring five consecutive positive indices starting at the declared media sequence is a conservative supported subset, not a general producer invariant. Lines728–731 emit ENDLIST only when presentation ends. Numeric duration/sequence/target values must be validated from the actual bounded playlist, not invented from tag counts.

No segment GET or decoding acceptance is established by this report. Existing runtime/proof/tenant/asset/version/TLS/privacy gates remain required, including the actual context-pair receipt and stored-split reconciliation rather than an atomic-mutation success claim.
