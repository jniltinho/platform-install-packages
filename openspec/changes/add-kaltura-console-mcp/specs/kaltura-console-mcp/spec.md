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
- **WHEN** a local client starts `kaltura-console mcp --as viewer@example.com --config /etc/kaltura-console/config.toml`, and that user exists
- **THEN** the client can list and call the read-only tools
- **AND** each call is audited as that user
- **AND** no network port is opened

#### Scenario: stdio without identity
- **WHEN** `kaltura-console mcp` runs without `--as`, or with an unknown or disabled user
- **THEN** it exits non-zero before serving any request

### Requirement: Host and Origin validation
The HTTP endpoint SHALL reject with HTTP 403, before authentication, any request that:
- has a `Host` (or trusted forwarded host) not in `[mcp] allowed_hosts`;
- or carries an `Origin` header not in `[mcp] allowed_origins`.

`allowed_origins` SHALL default to empty. The endpoint SHALL refuse plain HTTP unless the listener is bound to loopback only.

#### Scenario: DNS rebinding
- **WHEN** a request with a valid token arrives with `Host: attacker.example`
- **THEN** the response is HTTP 403 and no Kaltura call is made

#### Scenario: Browser origin
- **WHEN** a request carries `Origin: https://evil.example` and `allowed_origins` is empty
- **THEN** the response is HTTP 403

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
Tools SHALL call Kaltura with a short-lived USER KS for the console user, with privileges limited to the method, and SHALL NOT use `disableentitlement`. A tool whose method the USER KS cannot serve SHALL fail closed with an "unavailable" error, or not be registered. It SHALL NOT fall back to an admin KS.

#### Scenario: Read tool session
- **WHEN** a viewer token calls `get_entry`
- **THEN** the Kaltura request uses a USER KS whose privileges do not include `disableentitlement`

#### Scenario: CE refuses the USER KS
- **WHEN** Kaltura rejects a tool's method for the USER KS
- **THEN** the tool returns an "unavailable" error
- **AND** no admin KS is created for that call

### Requirement: Read-only tools
The server SHALL provide these tools:
- `search_entries`: free text, status and paging; eSearch, falling back to `media.list`;
- `get_entry`;
- `get_entry_status`;
- `list_flavors`;
- `get_playback_links`: status, duration, flavors (resolution, bitrate, codec) and the console UI URL of the entry;
- `list_categories`;
- `list_captions`;
- `get_caption`: truncated to a configurable size, with a `truncated` flag;
- `get_health`.

List results SHALL be capped by `max_results`.

#### Scenario: Search
- **WHEN** a viewer token calls `search_entries` with `query = "luta"`
- **THEN** the result lists the matching entries with id, name, status, duration and created date, at most `max_results` items

#### Scenario: Links without credentials
- **WHEN** a client calls `get_playback_links` for a READY entry
- **THEN** the result contains the console entry page URL and flavor metadata
- **AND** no URL contains a KS, a signed query string or the MCP token

### Requirement: Read-only scope
This change SHALL NOT expose any tool that creates, updates or deletes Kaltura objects.

#### Scenario: Tool list
- **WHEN** a client lists the tools
- **THEN** no tool uploads, updates or deletes media

### Requirement: No analytics tools
The server SHALL NOT expose analytics or `report` service tools, because the DWH is not packaged. The documentation SHALL state this.

#### Scenario: Tool list
- **WHEN** a client lists the tools
- **THEN** no tool name starts with `get_analytics`

### Requirement: Rate limit and audit
HTTP calls SHALL be rate-limited per token (default 60/min, configurable). Every tool call SHALL be recorded in `mcp_audit` with these fields: time, transport, user, token prefix (HTTP only), tool, entry id, result, duration. The record SHALL NOT include caption text, file content, secrets or KS values.

#### Scenario: Rate limit
- **WHEN** a token exceeds its per-minute limit
- **THEN** further calls in that minute get HTTP 429

#### Scenario: Audit entry
- **WHEN** a client calls `get_entry` for `0_abc`
- **THEN** `mcp_audit` gains one row with that tool, entry id and result

### Requirement: Client setup documentation
The console documentation SHALL show how to register the server in Claude Code and in Codex:
- stdio on the Kaltura host with `--as`, including its trust boundary: the local operator can read the config and therefore holds the admin secret;
- Streamable HTTP over HTTPS with a bearer token;
- how to create, list and revoke tokens.

#### Scenario: Claude Code over HTTPS
- **WHEN** an operator follows the documented `claude mcp add --transport http` command with a token
- **THEN** Claude Code lists the Kaltura tools
