## Purpose

Web console for managing the media of one Kaltura partner: authentication, dashboard, media library, upload, entry management, playback through the console, and health. It is delivered as a single Go binary with an embedded Vue SPA.

## ADDED Requirements

### Requirement: Authentication
The console SHALL require login with a local e-mail and password for every page and API route except `/login`, static assets and `/healthz`. Sessions SHALL be server-side and revocable. Logout SHALL invalidate the session immediately.

#### Scenario: Successful login
- **WHEN** a user submits valid credentials
- **THEN** a session cookie (`HttpOnly`, `SameSite=Lax`, `Secure` over HTTPS) is set
- **AND** the user is redirected to the dashboard

#### Scenario: Brute force
- **WHEN** 5 failed logins happen for the same e-mail and IP within 15 minutes
- **THEN** further attempts are rejected for the rest of the window without checking the password

#### Scenario: CSRF
- **WHEN** an authenticated `PATCH /api/media/{id}` arrives without a valid `X-CSRF-Token`
- **THEN** the response is HTTP 403
- **AND** no Kaltura call is made

#### Scenario: Revocation
- **WHEN** an admin resets another user's password
- **THEN** every existing session of that user stops working immediately

#### Scenario: Return to requested page
- **WHEN** an anonymous user opens `/media/0_abcdefgh` and then logs in
- **THEN** they land on `/media/0_abcdefgh`

#### Scenario: Unauthenticated access
- **WHEN** an anonymous request hits `/api/media`
- **THEN** the response is HTTP 401

### Requirement: Roles
Users SHALL have role `admin` or `viewer`. Only `admin` SHALL upload, edit or delete entries and manage users.

#### Scenario: Viewer tries to delete
- **WHEN** a `viewer` calls `DELETE /api/media/{id}`
- **THEN** the response is HTTP 403
- **AND** no Kaltura call is made

### Requirement: Dashboard
The dashboard SHALL show:
- the total number of entries;
- counts of ready (2), processing (0, 1, 4) and error (-2, -1) entries, using the Kaltura 18.20 `entryStatus` enum;
- the 8 most recent entries with thumbnail, name, status badge and creation date.

#### Scenario: Counters
- **WHEN** the partner has 7 entries, 6 ready and 1 converting
- **THEN** the dashboard shows total 7, ready 6, processing 1, error 0

### Requirement: Media library
The library SHALL list the partner's entries, newest first, 20 per page, with a name search (`nameLike`). Each row SHALL show thumbnail, name, entry ID, status badge, duration (`m:ss`) and creation date.

#### Scenario: Search
- **WHEN** the user searches "Bunny"
- **THEN** only entries whose name contains "Bunny" are listed
- **AND** pagination reflects the filtered total

### Requirement: Upload
An `admin` SHALL upload an MP4 file (other containers only when `allowed_ext` enables them) with a name and an optional description. The upload SHALL show three phases: sending to the console (byte progress), sending to Kaltura, and processing. Success SHALL be reported only after the content is attached. The console SHALL create the entry with `media.add`, `uploadToken.add`, `uploadToken.upload` and `media.addContent`. It SHALL reject:
- files above the configured size, before reading the body;
- files that are not valid ISO-BMFF;
- uploads beyond the concurrency limit (HTTP 429).

If a step fails after the entry was created, the console SHALL delete that entry. Each step's failure SHALL be reported with a distinct message.

#### Scenario: Successful upload
- **WHEN** an admin uploads a 80 MB MP4
- **THEN** a progress bar reaches 100%
- **AND** the user lands on the entry details page with status "Processando"

#### Scenario: Oversized file
- **WHEN** the file exceeds `max_upload_mb`
- **THEN** the upload is rejected with HTTP 413
- **AND** no Kaltura entry is created

### Requirement: Entry details
The details page SHALL show:
- a player when the entry is ready, a processing indicator while converting, and an error state;
- entry info: ID, status, duration, creation date, dimensions;
- an edit form for name (≤255 characters) and description (≤5000 characters);
- a delete action with confirmation;
- the flavors table: type, status, resolution, size, bitrate, format. If only `flavorAsset.list` fails, the rest of the page SHALL still render, with a notice in place of the table.

While the entry is processing, the page SHALL poll its status every 5 seconds, at most 240 times, and stop when the entry is ready or in error.

#### Scenario: Becomes ready while open
- **WHEN** the entry changes from status 1 to 2 while the page is open
- **THEN** the page replaces the processing indicator with the player without a reload

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

### Requirement: User management
An `admin` SHALL list, add, change the role of, reset the password of, and delete console users. E-mails SHALL be unique. The last admin SHALL NOT be deleted or demoted, and admins SHALL NOT delete themselves.

#### Scenario: Last admin
- **WHEN** the only admin tries to change their own role to `viewer`
- **THEN** the change is rejected with a clear message

### Requirement: Health page
The health page SHALL report, as ok or fail with a fixed message and no secrets or stack traces:
- the console DB;
- storage;
- whether the partner is configured;
- the upload endpoint;
- `system.ping`;
- whether an admin KS can be obtained;
- `media.list`.

#### Scenario: Kaltura down
- **WHEN** `system.ping` fails
- **THEN** that check is shown as failed and the other checks still render

### Requirement: painel-golang look and feel
The UI SHALL reproduce the painel-golang `criarenet` theme:
- the brand palette tokens (navy `#113058` and the derived tones, orange accent `#F58322`, light backgrounds `#E7ECEF`, `#D9E6F3` and `#EAF0F6`, borders `#b9c9dc`);
- the Inter font;
- a centered container on a dotted light-blue background;
- square top-level tabs with a navy sub-menu band;
- a navy info bar;
- a content card with a navy footer showing the version;
- a right "Ajuda" help column;
- tables with a navy header and zebra rows.

No element SHALL have rounded corners.

#### Scenario: No rounded corners
- **WHEN** any page is rendered
- **THEN** the computed `border-radius` of every element is `0px`

#### Scenario: Active navigation
- **WHEN** the user is on Mídia → Upload
- **THEN** the "Mídia" tab is shown as active
- **AND** the sub-menu band shows "Biblioteca" and "Upload", with "Upload" active

### Requirement: Responsive UI with modern feedback
The UI SHALL:
- be usable from 360 px wide;
- show toasts for success and errors;
- be in pt-BR by default with an English option.

#### Scenario: Mobile width
- **WHEN** the viewport is 360 px wide
- **THEN** the tabs wrap
- **AND** the help column moves below the content
- **AND** tables scroll horizontally without breaking the layout
