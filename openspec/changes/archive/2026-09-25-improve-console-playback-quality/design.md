## Context

See proposal.md for the observed 360p/400 kbps default. The existing authenticated proxy already validates entry ownership and controls redirect hosts. The new source was downloaded without re-encoding and ffprobe reports 1920×1080, 60000/1001 fps and about 5.66 Mbps video bitrate.

## Goals / Non-Goals

Deliver existing source detail through the current progressive player. Do not add adaptive HLS, a manual quality selector, transcoding profiles, upscaling or a new player dependency in this patch. Do not access retired VMs.

## Decisions

- List entry flavors after ownership validation and select only ready MP4/H.264 assets with a valid ID, matching entry ID and positive dimensions. Rank by pixel area, then compatible original, then bitrate, with a deterministic ID tie-break. Prefer an original at equal resolution to preserve source frame rate rather than a re-encoded rendition with a larger nominal bitrate.
- Pass the selected flavor ID explicitly to the progressive manifest; preserve the existing HTTP/HTTPS choice and redirect allowlist. Do not trust an arbitrary browser-supplied URL or flavor ID.
- Return controlled unavailable/upstream errors when listing fails or no supported candidate exists. Falling back silently would recreate the reported low-quality behavior.
- Keep the old media. Upload the new source as a separately labelled Full HD demo only after code approval; verify the actual stream with ffprobe and browser playback, not just entry metadata.

## Risks / Trade-offs

- Higher bandwidth → document that best-quality progressive playback is not adaptive; no guarantee of smooth playback on slow links.
- Extra upstream list call for Range requests → start without caching to avoid stale ownership/readiness; evaluate measured load later.
- Codec metadata variation → fixtures must cover known avc1/h264 representations and reject unknown codecs rather than assuming browser compatibility.
- Concurrent release → coordinate a separate branch/PR from main with Claude; do not modify already published tags.

## Migration Plan

After approval, implement regression tests, build/install on .20 preserving config/users/media, upload the Full HD source and verify delivered resolution/frame rate, Range and HTTPS URL regression. Roll back only the console package if needed; no data/schema migration. Update docs/changelog, synchronize specs and archive after validation.
