## Why

AI assistants (Claude Code, Codex, Hermes and other MCP clients) cannot query or manage the Kaltura media of this installation today. They would need raw `api_v3` calls and the partner admin secret.

The existing [zoharbabin/kaltura-mcp](https://github.com/zoharbabin/kaltura-mcp) was reviewed at commit `567f016`, dated 2025-07-01. It is Python, about 5.6k lines, and depends on `mcp`, `KalturaApiClient` 19 and FastAPI. It does not fit this installation:

- **Analytics needs DWH.** Its analytics tools use the `report` service, which needs the DWH. The DWH is not part of the Kaltura CE packages built here, so those tools would fail.
- **Secrets leak.** Its remote mode puts `kaltura_credentials`, including `admin_secret`, inside an HS256 JWT. Such a JWT is signed but not encrypted, so any token holder can read the secret. It also defaults `JWT_SECRET_KEY` to `"your-secret-key-change-this"`.
- **Too much privilege.** It always starts an ADMIN KS with `disableentitlement`, even for read-only tools.
- **Another runtime.** It adds a Python stack to hosts that otherwise run only the static `kaltura-console` binary.

`kaltura-console` already has a tested Go Kaltura client, local users with roles, TLS, `base_path` and packaging. The official Go MCP SDK, [`github.com/modelcontextprotocol/go-sdk`](https://github.com/modelcontextprotocol/go-sdk) (v1.8.0), provides a stdio transport, a Streamable HTTP handler, and bearer-token middleware (`auth.RequireBearerToken`). An MCP server inside the console reuses all of this.

## What Changes

- **MCP server in the console binary** (capability `kaltura-console-mcp`):
  - `kaltura-console mcp`: stdio transport, for local clients on the Kaltura host.
  - `<base_path>/mcp`: Streamable HTTP endpoint, served by `serve` when `[mcp] enabled = true`. It respects `base_path`, TLS, `trusted_proxies` and the Apache `/console` proxy.
- **Read-only tools in the MVP:**
  - `search_entries`: eSearch, with a fallback to `media.list`;
  - `get_entry`;
  - `get_entry_status`: transcoding status;
  - `list_flavors`;
  - `get_playback_links`: links to the entry in the console UI, which the user opens with an explicit browser login;
  - `get_thumbnail_url`;
  - `list_categories`;
  - `list_captions` and `get_caption`;
  - `get_health`: ping plus counters.
- **No write tools in this change.** Upload, update and delete through MCP are left for a separate change, with its own review.
- **Authentication:**
  - Per-user API tokens managed by the new `kaltura-console token add|list|revoke` command and a UI page.
  - Tokens are stored only as hashes, can expire, and are scoped to the user's role.
  - The Kaltura admin secret never leaves the server.
  - Every call is recorded in an audit log.
  - HTTP calls are rate-limited per token.
- **Least privilege.**
  - Read tools use a USER KS whose privileges are limited to the call. Entitlement is never disabled.
  - A tool the USER KS cannot serve on CE fails closed. There is no silent fallback to an admin KS.
- **stdio identity.** The stdio mode requires `--as <email>` naming an existing console user. That user becomes the identity for roles and audit.
- **HTTP hardening.** The HTTP endpoint validates `Origin` and `Host` against configured allow lists, to block DNS rebinding.
- **Documentation:** how to register the server in Claude Code (`claude mcp add`) and in Codex, locally over stdio and remotely over HTTPS with a bearer token.

Out of scope:
- analytics or `report` tools (no DWH);
- live streaming;
- write tools (upload, update, delete);
- media streaming through MCP, or signed media URLs;
- OAuth authorization server flows (bearer tokens only);
- changes to the Kaltura server packages.

## Impact

- **Code:** `kaltura-console/` gains `internal/mcp` and the `cmd` subcommands `mcp` and `token`. It adds one migration (`api_tokens`, `mcp_audit`), a UI page for tokens, `[mcp]` config keys (including `allowed_origins` and `allowed_hosts`), and one dependency (`github.com/modelcontextprotocol/go-sdk`).
- **Specs:**
  - new `kaltura-console-mcp`;
  - `kaltura-console-ops` CLI requirement modified: new `mcp` and `token` commands.
- **Security surface:** a new authenticated HTTP endpoint, disabled by default.
- **Packaging:** unchanged. The same binary and units; `config.toml.example` gains an `[mcp]` section.
