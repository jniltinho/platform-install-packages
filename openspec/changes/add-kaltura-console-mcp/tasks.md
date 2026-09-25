## 1. Foundation

- [ ] 1.1 Add `github.com/modelcontextprotocol/go-sdk` (pinned) and add an `[mcp]` config section: `enabled=false`, `allow_write=false`, `rate_per_minute=60`, `max_results=50`, `caption_max_bytes`. Verify with config tests for defaults, env override and validation.
- [ ] 1.2 Add a migration for `api_tokens` and `mcp_audit`. Verify it is idempotent on SQLite and MariaDB.
- [ ] 1.3 Add the `token add|list|revoke` CLI and a tokens page in the UI (admin; users see their own). Verify with tests:
  - the plaintext token is shown once;
  - only the hash is stored;
  - expiry and revocation work;
  - deleting the user invalidates the token.

## 2. MCP server

- [ ] 2.1 `internal/mcp`: server setup, tool registry with a required role per tool, and the USER KS minting (limited privileges, no `disableentitlement`). Verify with an `httptest` fake `api_v3` that asserts the KS type and privileges.
- [ ] 2.2 Read tools:
  - `search_entries` (eSearch with a `media.list` fallback);
  - `get_entry`, `get_entry_status`, `list_flavors`;
  - `get_playback_urls` (direct and proxied, with the playback scheme);
  - `get_thumbnail_url`, `list_categories`;
  - `list_captions`, `get_caption` (truncated);
  - `get_health`.
  Verify with unit tests per tool: pagination cap, HTTPS scheme, no secret or KS in results or errors.
- [ ] 2.3 Opt-in write tools (`upload_media`, `update_media`, `delete_media`), registered only with `allow_write` and admin only. Verify that `tools/list` without `allow_write` omits them and that a viewer is refused.
- [ ] 2.4 Transports:
  - `kaltura-console mcp` (stdio);
  - `<base_path>/mcp` Streamable HTTP with `auth.RequireBearerToken`, the rate limiter and a body limit.
  Verify with an SDK client test over stdio and over HTTP: initialize, list tools, call a tool, 401 without token, 429 over the limit.
- [ ] 2.5 Audit log. Verify one row per call, with no content, secret or KS columns.

## 3. Validation and docs

- [ ] 3.1 E2E against the .20 AIO (noble): enable MCP, create a viewer token, and from Claude Code (`claude mcp add --transport http`) search, get an entry and get playback URLs for an existing video. Also verify through the Apache `/console` proxy over HTTPS.
- [ ] 3.2 Confirm that each read tool works with a USER KS on CE. Document any tool that needs an admin KS.
- [ ] 3.3 Documentation (`kaltura-console/docs/mcp.md` and README):
  - Claude Code and Codex setup over stdio and HTTP;
  - token management;
  - security notes;
  - no analytics (no DWH).
  Update `config.toml.example`.
- [ ] 3.4 `make lint test build` and the console workflow green. Then review the spec deltas and archive the change.
