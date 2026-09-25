## Why

The console's default progressive manifest selects a 640×360 rendition at about 400 kbps on the Noble .20 deployment, even when 720p originals are available. Fighting-game motion loses detail; the user requests genuine Full HD and says only .20 remains available.

## What Changes

- Select the highest-resolution ready, browser-compatible MP4/H.264 asset explicitly instead of relying on the default manifest ordering.
- At equal resolution, prefer a compatible original to avoid an unnecessary generation of compression and preserve its frame rate; otherwise prefer higher bitrate.
- Preserve authenticated ownership checks, HTTPS delivery, redirect allowlists and Range streaming.
- Upload an additional genuine 1920×1080/60 fps fight source to .20 and verify the actual delivered resolution/frame rate; retain existing media.
- Document bandwidth trade-offs and the distinction between source resolution and delivered quality. Do not upscale lower-resolution videos or promise removal of compression already present in the source.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `kaltura-console-web`: deterministic high-quality progressive playback selection while retaining the existing proxy security contract.

## Impact

Console Kaltura delivery selection, streaming handler and regression tests; documentation and one additional demo upload on .20. No Kaltura database edits, transcoding-profile changes, other VM operations or new runtime dependencies. Coordinate the code commit with Claude before merging/tagging the release already in progress.
