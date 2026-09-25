## Context

`kaltura-console` is a single Go binary. It uses Echo v5, Cobra, Viper and GORM, with SQLite or MariaDB. It holds the partner `admin_secret` in `/etc/kaltura-console/config.toml` (mode 0640) and talks to `api_v3` through `internal/kaltura`. Local users have the roles `admin` or `viewer`. It can run standalone over TLS, or behind Apache under `base_path = "/console"`. Its media proxy authenticates with the browser session cookie.

## Goals / Non-Goals

**Goals:**
- Read-only MCP access to this installation's media metadata for AI clients, with no new runtime.
- The admin secret never leaves the server, and no Kaltura privilege is elevated silently.
- Every call is authenticated with a named console user, authorized by that user's role, and audited.

**Non-Goals:**
- write tools (upload, update, delete); these need a separate change;
- streaming media through MCP, or handing out KS-bearing or token-bearing media URLs;
- analytics (the DWH is not packaged);
- an OAuth authorization server;
- multi-partner support.

## Decisions

1. **In-process, same binary.** MCP lives in `internal/mcp` and reuses `internal/kaltura`, config, auth and the database. A separate binary would duplicate config, secrets and packaging. Rejected: running upstream Python `kaltura-mcp` as a sidecar, because of its secret-bearing JWT, its always-admin KS and its dependence on the DWH.

2. **SDK:** `github.com/modelcontextprotocol/go-sdk`, pinned.
   - It is the official SDK; v1.8.0 requires Go ≥ 1.25, and the console uses 1.27.
   - It provides `mcp.StdioTransport`, the Streamable HTTP handler and `auth.RequireBearerToken`.
   - A transport conformance test runs in CI.

3. **Transports and identity.**
   - **stdio (`kaltura-console mcp --as <email>`):**
     - `--as` is required and must name an existing, active console user. That user is the identity for role checks and audit rows.
     - There is no implicit identity and no default admin.
     - Trust boundary, documented plainly: whoever can run this command can already read `config.toml`, and therefore holds the admin secret. stdio is for a trusted local operator. `--as` gives accountability and role limits; it is not protection against that operator.
     - It opens no port.
   - **Streamable HTTP:**
     - Mounted by `serve` at `<base_path>/mcp` only when `[mcp] enabled = true` (default `false`).
     - It gets TLS, `base_path` and `trusted_proxies` handling the same way as the rest of the console.
     - It accepts only bearer tokens and ignores session cookies, so there is no CSRF surface.

4. **Origin and Host validation.** A bearer token does not stop DNS rebinding against a loopback or LAN listener, so the endpoint also checks two headers:
   - The `Host` header (or the trusted forwarded host) must be in `[mcp] allowed_hosts`. The default is the console's configured host names.
   - When an `Origin` header is present, it must be in `[mcp] allowed_origins`. The default is empty, so browser origins are refused.

   Requests failing either check get HTTP 403 before authentication. Plain HTTP is refused unless the listener is loopback-only.

5. **Tokens.**
   - Created by `token add --user <email> [--expires 90d] [--name]` or by the UI. The plaintext is shown once.
   - Format: `kc_<random 32 bytes base64url>`.
   - Only the SHA-256 is stored, in table `api_tokens` with columns: id, user_id, name, hash, prefix, created_at, last_used_at, expires_at, revoked_at.
   - The verifier checks the user, revocation and expiry on every call. Revoking the token, deleting the user or changing the user's role takes effect on the next call.

6. **Authorization and Kaltura sessions: fail closed.**
   - All tools in this change are read-only and allowed for `viewer` and `admin`.
   - Each tool calls Kaltura with a KS minted for that call:
     - type USER, `userId` = console user email;
     - short expiry;
     - privileges limited to what the method needs;
     - never `disableentitlement`.
   - A privilege matrix (tool → Kaltura method → required KS type and privileges) is part of the implementation, and a test verifies it against the CE install.
   - If CE refuses a method with a USER KS, that tool is not shipped, or it returns a clear "unavailable" error. It never falls back to an admin KS silently. Any later decision to use an admin KS for a specific read tool is a documented spec change.

7. **Links, not media.**
   - `get_playback_links` returns metadata:
     - status, duration and flavors (resolution, bitrate, codec);
     - the URL of the entry page in the console UI.
   - The user opens that URL in a browser and logs in normally.
   - No tool returns KS-bearing URLs, signed delivery URLs or anything carrying the MCP token.
   - The media proxy keeps cookie authentication only. Extending it to bearer tokens needs its own spec and tests.

8. **Results.**
   - Tools return structured JSON with a short text summary.
   - Lists are capped by `max_results` (default 50).
   - Captions are truncated to `caption_max_bytes`, with a `truncated` flag.

9. **Abuse controls and audit.**
   - Per-token rate limit (default 60 calls/min).
   - Request body limit.
   - Per-tool timeout from `kaltura.http_timeout`.
   - Table `mcp_audit` records: time, transport, user, token prefix (HTTP), tool, entry id, result, duration. It never records caption text, secrets, KS or tokens.

## Risks / Trade-offs

- **A leaked token gives read access to the media metadata.** Mitigations: hash-only storage, expiry, revocation, rate limit, audit, endpoint disabled by default, Host and Origin checks, and TLS unless loopback.
- **Some read methods may need ADMIN on CE.** Those tools are dropped or disabled rather than given an admin KS. The MVP may therefore ship fewer tools than listed; the tasks record the matrix result.
- **SDK churn.** The MCP spec still evolves. Mitigations: pinned version and the conformance test.

## Migration Plan

One additive migration (`api_tokens`, `mcp_audit`). The endpoint is disabled by default, so upgrades do not change behavior. Rollback: set `enabled = false`, or install the previous package; the extra tables are ignored.
