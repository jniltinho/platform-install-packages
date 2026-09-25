## Purpose

Record verifiable evidence that the Kaltura CE 18.20.0 All-In-One on Ubuntu 24.04 works for real use:

- a real video is processed;
- the administration interface can be navigated;
- the API is documented;
- external clients (`criare`) interoperate with it.

## ADDED Requirements

### Requirement: Real test video
The validation SHALL upload to the AIO a real video obtained from YouTube with `yt-dlp` (MP4, up to 720p). It SHALL verify that the video becomes READY and plays through HLS.

#### Scenario: Upload through the API
- **WHEN** the downloaded video is uploaded with `uploadToken.add`, then `uploadToken.upload`, then `media.addContent` (or `baseEntry.addFromUploadedFile`)
- **THEN** the entry reaches status READY
- **AND** it has at least one flavor besides the source
- **AND** the entry's HLS manifest returns valid segments

#### Scenario: Visible in the UI
- **WHEN** the operator opens the KMC as the test partner
- **THEN** the entry appears in the entries list, with a thumbnail

### Requirement: Administration interface screenshots
The validation SHALL capture screenshots with `agent-browser` of:
- every navigable section of the Admin Console, including login and every menu tab and page;
- the main KMC screens: login, entries, entry details with the player, upload and settings.

The screenshots SHALL be stored in `doc/prints/` with descriptive names.

#### Scenario: Screenshot set
- **WHEN** the screenshot run finishes
- **THEN** `doc/prints/` contains one PNG per visited screen
- **AND** none of them shows an error page (HTTP 4xx/5xx or a PHP exception)

### Requirement: API documentation
The repository SHALL contain `doc/kaltura-api-noble.md` with `curl` examples, run against the AIO, for:
- `system.ping` and `session.start`;
- partner creation;
- `uploadToken.add` and `uploadToken.upload`;
- `media.addContent` or `baseEntry.addFromUploadedFile`;
- `baseEntry.get`, `baseEntry.list` and `flavorAsset.list`;
- `playManifest` (HLS).

#### Scenario: Runnable examples
- **WHEN** an example from the document is run against the AIO with the documented variables
- **THEN** the response matches the one described in the document

### Requirement: Interoperability with the criare clients
The `criare/kaltura-console` and `criare/kaltura-legacy-gateway` projects SHALL be run against the AIO. The outcome SHALL be recorded in the documentation: works or does not work, and why.

#### Scenario: Connected client
- **WHEN** a client is configured with the AIO service URL and credentials
- **AND** it performs a basic operation (authenticate and list entries)
- **THEN** either the operation returns the AIO data, or the incompatibility is documented together with its cause
