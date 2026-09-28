# Bounded short delivery, separate local candidate

`delivery.py` is pure orchestration/validation, not a standalone network executor. The caller MUST inject pinned-CA HTTPS transport for exactly .74:8443, proxies/redirects disabled, a <=30-second wall-clock request deadline and body cap, all inside saved complete TLS log/journal privacy windows. A flow-wide <=180-second deadline is required for HLS integration. No credentials appear in URL output, errors, hashes or receipts. Returned bodies/URLs are private in-memory objects; publish only the closed report.

`native_url(call)` uses native flavorasset/getUrl for original0_ewuu0o46. Source `FlavorAssetService.php` lines609–667 checks entitlement/ready status and selects getServeFlavorUrl or getDownloadUrl. Returned HTTP URLs are rejected, NOT upgraded silently; any scheme/port discrepancy needs separate native delivery configuration evidence. No speculative HLS URL builder is included: `flavorAsset::getPlayManifestUrl` source generates format/url, not proof of applehttp delivery. HLS URL must be independently source/identity joined by integration.

`progressive` does a full <=2MiB 200 fetch, verifies exact 1511134-byte original SHA612d...b5473, then first and last1024-byte requests, requiring206/exact Content-Range/body equality. No transcoded asset can be substituted. MIME alone cannot pass. This is delivery, not decoding.

`hls` tests only a bounded VOD MPEG-TS subset: one master, first variant only, one media playlist, <=32segments, <=120seconds declared duration, <=2MiB total fetched bytes. Unknown tags/encryption/byteranges/fMP4/external origins/nested masters fail closed. TS sync framing is checked but NOT semantic decode. Unsupported valid HLS is unresolved, not a product defect or passing stream. Reports expressly decoded=false; unselected variants remain untested.

`probe_projection` validates <=32KiB strict duplicate-free/nonfinite-free ffprobe JSON, one H264 video with bounded dimensions and at most one AAC audio stream. It does NOT execute ffprobe/ffmpeg, attest binary identity, establish duration or prove full decode. A future reviewed decoder must use pinned binary, private bounded bytes, disabled network protocols, bounded CPU/output/wall-clock and actual exit0/full decode semantics. Do not infer decoded playback from probe metadata.

Author combined suite19tests exit0, ten delivery tests plus nine metadata tests, synthetic transport only. Independent actual Claude review pending until terminal. No VM/API/service changes. Original metadata freeze retained.

## R2 parser correction
Actual Claude CLI terminal0 ran19tests plus reported12 adversarial probes. It correctly blocked R1 on malformed header-name bypass and non-HLS splitlines delimiters. R1 source/hash/review preserved. R2 validates HTTP token header names; splits only LF with optional final CR and rejects other controls/Unicode separators. Two new tests cover those negatives and CRLF positive;21 combined author tests PASS. Independent delta review required. Other limitations unchanged; no new native acceptance claim.

Independent Codex delta reviewer reran21 combined tests and approved R2 parser changes. Native request wrapper still needs its own review.

## Native route and credential follow-up
`KalturaFlavorAssetStatus.php` SHA8e0f1c8846eb9966b6f2e1aefcd1b0e38a3fc540f28e00fff20e153b002870d9 line9 defines NOT_APPLICABLE=4; no reason is inferred from that enum. Root separately observed source/transcoded statuses; this local module did not execute API.

Additional exact archive source hashes in delivery-route-source-pins.json. `myPartnerUtils::getUrlForPartner` lines37–39 renders /p/{partner}/sp/{subpartner}; playManifestAction279–287 accepts flavorId,1240–1246 protocol/format. PlaybackProtocol line11 defines APPLE_HTTP='applehttp'. Candidate HLS path can use those source-defined fields after actual delivery-profile/rewriter join; this is not proof of working HLS or permission to bypass entitlement. Do not assume subpartner solely from multiplication when native stored context differs.

IMPORTANT: getUrl can generate a NEW private credential. asset::getDownloadUrlWithExpiry595–607 calls startKSession with partner secret;615–616 appends the minted /ks/ token. Normal serveFlavor goes through kAssetUtils::getAssetUrl97–124 and configured delivery signing. The API's existing USER KS is not necessarily the new token. First progressive integration should accept only a proven token-free fixed route (reject query and KS/KT paths), or explicitly enroll native response-derived credentials in memory before GET and scan saved pre-getUrl windows as well. No raw URL/credential/request digest may be exported. The pure module does not implement credential extraction or scanner enrollment; caller must not treat target-origin validation as that proof.

kAssetUtils116–132 obtains request protocol, but explicitly falls back to HTTP if the selected profile does not support it. An HTTP response therefore remains a clear blocked observation, never an implicit HTTPS rewrite.
