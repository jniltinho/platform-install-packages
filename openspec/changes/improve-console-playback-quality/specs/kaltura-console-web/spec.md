## MODIFIED Requirements

### Requirement: Playback and thumbnail proxy
The console SHALL serve `/media/{id}/stream` and `/media/{id}/thumbnail` (GET and HEAD) by streaming from the Kaltura delivery host. It SHALL do so only for valid entry IDs of the configured partner, and SHALL follow redirects only to allow-listed hosts. It SHALL forward the `Range` header and relay the status code, `Content-Type`, `Content-Length`, `Content-Range` and `Accept-Ranges`. The browser SHALL never receive a KS or the partner secret.

#### Scenario: Seek
- **WHEN** the browser requests `Range: bytes=1000000-`
- **THEN** the console answers HTTP 206 with the matching `Content-Range`

#### Scenario: Unsatisfiable range
- **WHEN** the browser requests a range beyond the file size
- **THEN** the console relays HTTP 416

#### Scenario: Redirect outside the allowlist
- **WHEN** the manifest redirects to a host that is not allow-listed
- **THEN** the console answers HTTP 502 without contacting that host

#### Scenario: Upstream down
- **WHEN** the Kaltura delivery host is unreachable
- **THEN** the console answers HTTP 502 without leaking upstream details

The console SHALL explicitly choose the highest-resolution ready MP4/H.264 asset owned by the requested entry. At equal resolution it SHALL prefer a compatible original; otherwise it SHALL prefer the higher bitrate. Selection SHALL NOT request upscaling or silently use an unready/incompatible asset. If no compatible asset is ready, playback SHALL return a controlled unavailable response without weakening proxy security.

#### Scenario: High-resolution asset available
- **WHEN** an entry has ready 360p and 1080p compatible assets
- **THEN** progressive playback delivers the 1080p asset rather than the default low-quality rendition

#### Scenario: Preserve a compatible original
- **WHEN** a ready original is MP4/H.264 at 1080p60 and a derived asset has the same resolution
- **THEN** playback chooses the original and preserves its frame rate without another transcode

#### Scenario: Unsafe or unavailable asset
- **WHEN** an asset belongs to another entry, has an invalid identifier, is not ready or uses an unsupported format/codec
- **THEN** it is excluded from selection
- **AND** no compatible candidate results in a controlled unavailable response
