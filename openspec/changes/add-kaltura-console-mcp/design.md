## Context

`kaltura-console` is a single Go binary. It uses Echo v5, Cobra, Viper and GORM, with SQLite or MariaDB. It holds the partner `admin_secret` in `/etc/kaltura-console/config.toml` (mode 0640) and talks to `api_v3` through `internal/kaltura`. Local users have the roles `admin` or `viewer`. It can run standalone over TLS, or behind Apache under `base_path = "/console"`.

## Goals / Non-Goals

**Goals:**
- MCP access to this installation's media for AI clients, with no new runtime.
- The admin secret never leaves the server.
- Least privilege by default, and every call auditable.

**Non-Goals:**
- analytics (the DWH is not packaged);
- an OAuth authorization server;
- multi-partner support;
- replacing the KMC or the Admin Console.

## Decisions

1. **In-process, same binary.** MCP lives in `internal/mcp` and reuses `internal/kaltura`, config, auth and the database.
   - A separate binary would duplicate config, secrets and packaging.
   - Alternative rejected: running upstream Python `kaltura-mcp` as a sidecar (secret-leaking JWT, no DWH).

2. **SDK:** `github.com/modelcontextprotocol/go-sdk`.
   - It is the official SDK and supports Go ≥ 1.25; the console uses 1.27.
   - It provides `mcp.StdioTransport`, the Streamable HTTP handler and `auth.RequireBearerToken`.
   - Pin the version and review its changelog on upgrades.
   - `mark3labs/mcp-go` was considered. It is not used: the official SDK now covers what this change needs.

3. **Transports.**
   - **stdio (`kaltura-console mcp`):**
     - For a client on the same host. It reads the local `config.toml`, so it needs read access to the config. By default it runs as the `viewer` role. It acts as `admin` only with `--as <email>` naming an existing admin user.
     - It opens no port.
   - **Streamable HTTP:**
     - Mounted by `serve` at `<base_path>/mcp` when `[mcp] enabled = true` (default `false`).
     - It gets TLS, `base_path` and proxy trust the same way as the rest of the console.
     - It ignores session cookies and accepts bearer tokens only, so no CSRF surface is added.

4. **Tokens.**
   - Created by `token add --user <email> [--expires 90d] [--name]` or by the UI. The plaintext is shown once.
   - Format: `kc_<random 32 bytes base64url>`.
   - Only the SHA-256 is stored, in table `api_tokens` with columns: id, user_id, name, hash, prefix, created_at, last_used_at, expires_at, revoked_at.
   - The verifier looks the token up by hash and checks the user, revocation and expiry. It returns `auth.TokenInfo` carrying the user and role.
   - Revoking the token, deleting the user or changing the user's role takes effect on the next call.

5. **Authorization.**
   - Each tool declares a required role.
   - Read tools: `viewer` or `admin`.
   - Write tools: registered only when `[mcp] allow_write = true`, and `admin` only.
   - A denied call returns an MCP tool error without calling Kaltura.

6. **Kaltura session.**
   - Read tools use a KS minted by the console for that call:
     - type USER, `userId` = console user email;
     - short expiry;
     - privileges limited to the call, e.g. `sview:*` for playback URLs;
     - never `disableentitlement`.
   - Write tools reuse the existing admin KS path, only for admin tokens with `allow_write`.
   - Integration testing verifies that the USER KS is enough for each read tool on the CE install. A tool that needs ADMIN is documented as admin-only.

7. **Tool results.**
   - Tools return structured JSON with a small text summary.
   - Lists are paginated with a hard `max_results` (default 50).
   - Captions are truncated with a `truncated` flag.
   - URLs are built by the existing `PlaybackURL` and `ThumbnailURL`, which keep the `playback_host` scheme.
   - For internal hosts, `get_playback_urls` returns console-proxied URLs so the client needs no direct access to Kaltura delivery.

8. **Abuse controls.**
   - Per-token rate limit (default 60 calls/min).
   - Request body limit.
   - Per-tool timeout from `kaltura.http_timeout`.
   - Table `mcp_audit` records: time, token prefix, user, tool, entry id, result, duration. Arguments are recorded without caption or upload content.

## Risks / Trade-offs

- **A leaked token gives read access to the media metadata.** Mitigations: hash-only storage, expiry, revocation, rate limit, audit, endpoint disabled by default, and TLS required unless the host is loopback.
- **SDK churn.** The MCP spec still evolves. Mitigation: pinned version and a transport conformance test in CI.
- **USER KS limits on CE.** Some list calls may need ADMIN privileges on CE. The fallback is an admin KS for that read tool, marked in docs, still only for the authenticated console user.

## Migration Plan

One additive migration (`api_tokens`, `mcp_audit`). The endpoint is disabled by default, so upgrades do not change behavior. Rollback: set `enabled = false`, or install the previous package; the extra tables are ignored.

## Open Questions

- Should `get_playback_urls` return direct Kaltura URLs, console-proxied URLs, or both? Proposed: both, labeled.
- Should the stdio mode require `--as` for any use? Proposed: no, default viewer.
