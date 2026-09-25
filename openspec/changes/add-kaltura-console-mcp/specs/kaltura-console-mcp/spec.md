## ADDED Requirements

### Requirement: MCP transports
The console SHALL serve the Model Context Protocol over stdio, with `kaltura-console mcp`, and over Streamable HTTP at `<base_path>/mcp`, using `github.com/modelcontextprotocol/go-sdk`. The HTTP endpoint SHALL be disabled unless `[mcp] enabled = true`. It SHALL honor `base_path`, TLS and `trusted_proxies` like the rest of the console.

#### Scenario: Endpoint disabled by default
- **WHEN** `serve` runs with no `[mcp]` section
- **THEN** `<base_path>/mcp` returns HTTP 404

#### Scenario: Behind the Apache /console proxy
- **WHEN** `enabled = true`, `base_path = "/console"`, and an MCP client posts an `initialize` request to `https://<host>/console/mcp` with a valid token
- **THEN** the server answers with its name, version and tool list

#### Scenario: stdio
- **WHEN** a local client starts `kaltura-console mcp --config /etc/kaltura-console/config.toml`
- **THEN** the client can list and call the read-only tools
- **AND** no network port is opened

### Requirement: Bearer token authentication
The HTTP endpoint SHALL accept only `Authorization: Bearer` API tokens and SHALL ignore session cookies. Tokens SHALL be generated with at least 32 random bytes, shown once, and stored only as a SHA-256 hash with a short display prefix. A token SHALL be rejected when it is unknown, revoked or expired, or when its user is deleted.

#### Scenario: Missing token
- **WHEN** a request to `/mcp` has no bearer token
- **THEN** the response is HTTP 401 and no Kaltura call is made

#### Scenario: Revoked token
- **WHEN** an admin revokes a token with `kaltura-console token revoke <id>`
- **THEN** the next call with that token gets HTTP 401

#### Scenario: Token never stored in plaintext
- **WHEN** the `api_tokens` table is inspected after `token add`
- **THEN** it contains the hash and prefix only, and no column holds the plaintext token

### Requirement: Secret confinement
The Kaltura `admin_secret` and any KS SHALL NOT appear in MCP responses, tool errors, tokens, logs or the audit table.

#### Scenario: Error from Kaltura
- **WHEN** a tool call fails because Kaltura rejects the session
- **THEN** the tool error names the failure class
- **AND** it contains no secret, KS or signed URL query string

### Requirement: Least-privilege Kaltura sessions
Read tools SHALL call Kaltura with a short-lived USER KS for the console user, with privileges limited to the call. Read tools SHALL NOT use `disableentitlement`. Write tools SHALL use an admin KS only for admin tokens with writes enabled.

#### Scenario: Read tool session
- **WHEN** a viewer token calls `get_entry`
- **THEN** the Kaltura request uses a USER KS whose privileges do not include `disableentitlement`

### Requirement: Read-only tools
The server SHALL provide these tools:
- `search_entries`: free text, status and paging; eSearch, falling back to `media.list`;
- `get_entry`;
- `get_entry_status`;
- `list_flavors`;
- `get_playback_urls`: HLS and MP4, using the `playback_host` scheme;
- `get_thumbnail_url`;
- `list_categories`;
- `list_captions`;
- `get_caption`: truncated to a configurable size, with a `truncated` flag;
- `get_health`.

List results SHALL be capped by `max_results`.

#### Scenario: Search
- **WHEN** a viewer token calls `search_entries` with `query = "luta"`
- **THEN** the result lists the matching entries with id, name, status, duration and created date, at most `max_results` items

#### Scenario: HTTPS playback URLs
- **WHEN** `playback_host` is `https://media.example.com` and a client calls `get_playback_urls` for a READY entry
- **THEN** every returned URL uses `https`

### Requirement: Opt-in write tools
`upload_media`, `update_media` and `delete_media` SHALL be registered only when `[mcp] allow_write = true`, and SHALL be callable only with an admin token.

#### Scenario: Writes disabled
- **WHEN** `allow_write` is false
- **THEN** `tools/list` does not include the write tools

#### Scenario: Viewer tries to delete
- **WHEN** `allow_write` is true and a viewer token calls `delete_media`
- **THEN** the call returns a permission error and no Kaltura call is made

### Requirement: No analytics tools
The server SHALL NOT expose analytics or `report` service tools, because the DWH is not packaged. The documentation SHALL state this.

#### Scenario: Tool list
- **WHEN** a client lists the tools
- **THEN** no tool name starts with `get_analytics`

### Requirement: Rate limit and audit
HTTP calls SHALL be rate-limited per token (default 60/min, configurable). Every tool call SHALL be recorded in `mcp_audit` with these fields: time, token prefix, user, tool, entry id, result, duration. The record SHALL NOT include caption text, file content, secrets or KS values.

#### Scenario: Rate limit
- **WHEN** a token exceeds its per-minute limit
- **THEN** further calls in that minute get HTTP 429

#### Scenario: Audit entry
- **WHEN** a client calls `get_entry` for `0_abc`
- **THEN** `mcp_audit` gains one row with that tool, entry id and result

### Requirement: Client setup documentation
The console documentation SHALL show how to register the server in Claude Code and in Codex:
- stdio on the Kaltura host;
- Streamable HTTP over HTTPS with a bearer token;
- how to create, list and revoke tokens.

#### Scenario: Claude Code over HTTPS
- **WHEN** an operator follows the documented `claude mcp add --transport http` command with a token
- **THEN** Claude Code lists the Kaltura tools
