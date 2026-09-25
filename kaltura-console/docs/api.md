# HTTP API reference

[Architecture](architecture.md) · [Operations](operations.md)

This is the embedded SPA's same-origin API, not the Kaltura public API. Route authority: [`internal/server/server.go`](../internal/server/server.go). JSON field definitions: [`auth.go`](../internal/server/auth.go), [`media.go`](../internal/server/media.go). Error bodies use `{"message":"..."}` (currently pt-BR). Do not match localized error strings in integrations.

## Base URL

All paths below are relative to the configured application prefix. With default `server.base_path = ""`, use the paths as written. With `server.base_path = "/console"`, prepend `/console`: login is `/console/api/login`, playback is `/console/media/:id/stream`, and liveness is `/console/healthz`. There are no duplicate root API routes in prefixed mode. Response media URLs include the prefix. Serve flags or `KCONSOLE_SERVER_BASE_PATH` can override the TOML setting.

Use HTTPS directly (`server.https`) or through a trusted TLS-terminating proxy. Cookie Path follows the prefix, or `/` at root; Secure follows direct TLS/trusted forwarded HTTPS. Refer to [TLS/prefix operations](operations.md#standalone-https) for deployment and cookie migration.

## Session contract

`POST /api/login` accepts `{"email":"operator@example.invalid","password":"<supplied securely>","remember":false}`. Success sets `kconsole_session` and returns `{user:{id,name,email,role},csrf,partner_id,version}`. `GET /api/session` returns the same shape. Retain cookies and send the returned `csrf` as `X-CSRF-Token` on authenticated POST/PATCH/DELETE requests, including logout. A fresh unauthenticated login has no CSRF token requirement; a login made with an existing valid session does. Origin checks also apply. No bearer-token or public registration endpoint exists.

Normal sessions expire after configured idle/absolute limits; remembered sessions expire after 30 days. A revoked/expired session returns 401 on protected routes. Five failed logins per normalized email + client IP in 15 minutes trigger 429. Clients must handle 401 by clearing UI state and returning to login.

## Routes

`reader` means either admin or viewer. All `/api` JSON requests have a 1 MiB body limit except the separately bounded multipart upload route.

| Method | Path | Access | Success/result |
|---|---|---|---|
| GET | `/healthz` | Public | 200 plain `ok`; liveness only |
| POST | `/api/login` | Public/origin checked | 200 session object + cookie |
| GET | `/api/session` | Reader | 200 session object |
| POST | `/api/logout` | Reader + CSRF | 204, session deleted/cookie cleared |
| GET | `/api/dashboard` | Reader | 200 `{counts:{total,ready,processing,error},recent:[entry]}` |
| GET | `/api/media?q=...&page=1` | Reader | 200 `{items,total,page,page_size,pages}` |
| GET | `/api/media/:id` | Reader | 200 entry |
| GET | `/api/media/:id/status` | Reader | 200 `{id,status,status_label,status_group,ready,duration,width,height}` |
| GET | `/api/media/:id/flavors` | Reader | 200 array of flavor objects |
| POST | `/api/media` | Admin + CSRF | 201 entry; multipart upload |
| PATCH | `/api/media/:id` | Admin + CSRF | 200 entry; JSON `name`, `description` |
| DELETE | `/api/media/:id` | Admin + CSRF | 204 |
| GET | `/api/users` | Admin | 200 array of `{id,name,email,role}` |
| POST | `/api/users` | Admin + CSRF | 201 user; JSON `name,email,password,role` |
| PATCH | `/api/users/:id` | Admin + CSRF | 200 user; optional `name,role,password` |
| DELETE | `/api/users/:id` | Admin + CSRF | 204 |
| GET | `/api/health` | Reader | 200 array of `{group,name,ok,detail}` |
| GET | `/api/version` | Reader | 200 `{version,commit,build_date}` |
| GET, HEAD | `/media/:id/stream` | Reader | Upstream MP4 response, including 200/206/416 |
| GET, HEAD | `/media/:id/thumbnail` | Reader | Upstream image response |

`/api/health` can return HTTP 200 with individual `ok:false` checks. Inspect the body; do not use its HTTP status alone as readiness. It checks local DB/staging plus Kaltura ping, KS and listing; it does not verify all Kaltura workers.

## Media representation

Entry fields: `id`, `name`, `description`, integer `status`, `status_label`, `status_group`, `duration` (seconds), `created_at`/`updated_at` (Unix seconds), `plays`, `width`, `height`, `thumbnail_url`, `playback_url`. URLs are same-origin proxy paths. IDs match `^[0-9]_[a-z0-9]{8}$`.

Listing is newest first, fixed at 20 items/page. Missing/invalid/nonpositive page becomes 1; `q` searches name and is limited to 100 Unicode characters. `pages` is at least 1, including an empty result.

Entry groups: `ready` = 2; `processing` = 0, 1, 4; `error` = -2, -1; everything else = `other`. Flavor groups differ; see [`status.go`](../internal/kaltura/status.go). A successful upload does **not** imply READY: poll status while conversion runs. Flavor fields are `id,type,status,status_label,status_group,width,height,size_kb,bitrate,format,codec`.

## Multipart upload

Send one `file` part, required `name` (1–255 Unicode characters after trimming), optional `description` (up to 5000). Unknown fields and extra file parts are rejected. Default extension is `.mp4`; minimal ISO-BMFF validation still applies if extension configuration changes. Default file limit is 2048 MiB plus a bounded 64 KiB multipart envelope. Default concurrency is two uploads per process.

Use a client-generated multipart boundary; do not manually set `Content-Type` without it. Browser progress measures browser-to-console intake, not completion of Kaltura upload/conversion. The server returns 201 after `media.addContent`, then removes its local temporary file.

## Important failures and restrictions

- 400: malformed request, invalid numeric user ID, too-long search or unknown upload field.
- 401: invalid credentials or missing/expired session.
- 403: role, CSRF or Origin check failed.
- 404: malformed/unknown media ID (including ownership check failure on detail/proxy).
- 409: duplicate email, last-admin removal/demotion, or self-deletion.
- 413: body/file exceeds limit; 422: invalid upload/metadata.
- 429: login lockout or upload concurrency full; 507: upload admission free-space threshold failed.
- 502: upstream Kaltura failure, disallowed redirect host or unavailable media.

User creation requires an email containing `@`, role `admin`/`viewer`, and a password of at least eight bytes; bcrypt rejects passwords above its supported length. API user updates do not change email. Empty update password means “unchanged.” Password/role changes revoke existing sessions, including the editor's session when editing themselves.

Stream requests forward only `Range` and `If-Range`, not cookies/Authorization. Responses relay `Content-Type`, `Content-Length`, `Content-Range`, `Accept-Ranges`, `ETag`, `Last-Modified`; authenticated responses remain non-cacheable. After stream headers are committed, transmission failures abort the stream rather than return a new JSON error.
