## 1. Foundation

- [ ] 1.1 Add `github.com/modelcontextprotocol/go-sdk` (pinned) and add an `[mcp]` config section: `enabled=false`, `allowed_hosts`, `allowed_origins=[]`, `rate_per_minute=60`, `max_results=50`, `caption_max_bytes`. Verify with config tests for defaults, env override and validation.
- [ ] 1.2 Add a migration for `api_tokens` and `mcp_audit`. Verify it is idempotent on SQLite and MariaDB.
- [ ] 1.3 Add the `token add|list|revoke` CLI and a tokens page in the UI (admin; users see their own). Verify with tests:
  - the plaintext token is shown once;
  - only the hash is stored;
  - expiry and revocation work;
  - deleting the user invalidates the token.

## 2. MCP server

- [ ] 2.1 `internal/mcp`: server setup, read-only tool registry, and USER KS minting (limited privileges, no `disableentitlement`, no admin fallback). Verify with an `httptest` fake `api_v3` that asserts the KS type and privileges and the fail-closed error.
- [ ] 2.2 Read tools:
  - `search_entries` (eSearch with a `media.list` fallback);
  - `get_entry`, `get_entry_status`, `list_flavors`;
  - `get_playback_links` (metadata plus the console UI URL; no KS, signed URL or token);
  - `list_categories`, `list_captions`, `get_caption` (truncated);
  - `get_health`.
  Verify with unit tests per tool: pagination cap, no secret, KS or token in results or errors.
- [ ] 2.3 Transports:
  - `kaltura-console mcp --as <email>` (stdio), which exits non-zero without a valid user;
  - `<base_path>/mcp` Streamable HTTP with `auth.RequireBearerToken`, Host/Origin allow lists, the rate limiter and a body limit, and plain HTTP refused unless loopback.
  Verify with SDK client tests over stdio and HTTP:
  - initialize, list tools, call a tool;
  - 401 without a token;
  - 403 for a bad Host or Origin;
  - 429 over the limit;
  - through `base_path` and a trusted proxy with TLS.
- [ ] 2.4 Audit log (transport, user, token prefix). Verify one row per call, with no content, secret, KS or token columns.

## 3. Validation and docs

- [ ] 3.1 Privilege matrix on the .20 AIO (noble): for each tool, check the Kaltura method with a USER KS on CE. Record the result in `kaltura-console/docs/mcp.md`. Drop or disable (fail closed) any tool CE refuses.
- [ ] 3.2 E2E on .20: enable MCP, create a viewer token, and from Claude Code (`claude mcp add --transport http`) search, get an entry and get playback links for an existing video. Also run it over stdio with `--as`.
- [ ] 3.3 Documentation (`kaltura-console/docs/mcp.md` and README):
  - Claude Code and Codex setup over stdio (`--as`, with its trust boundary) and HTTP;
  - `allowed_hosts` and `allowed_origins`;
  - token management;
  - security notes;
  - no analytics (no DWH).
  Update `config.toml.example`.
- [ ] 3.4 `make lint test build` and the console workflow green. Then review the spec deltas and archive the change.
