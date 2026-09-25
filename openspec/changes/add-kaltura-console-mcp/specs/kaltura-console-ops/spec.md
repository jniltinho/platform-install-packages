## MODIFIED Requirements

### Requirement: CLI
The binary SHALL provide these Cobra commands:
- `serve`;
- `migrate`;
- `user add|passwd|list|delete`;
- `token add|list|revoke`, for MCP API tokens;
- `mcp --as <email>`, which serves MCP over stdio as an existing console user;
- `config init`;
- `version`, which prints the version, commit and build date injected at build time.

#### Scenario: First admin
- **WHEN** the operator runs `kaltura-console user add --email a@b.c --role admin` and enters a password
- **THEN** the user can log in to the web console

#### Scenario: Create an MCP token
- **WHEN** the operator runs `kaltura-console token add --user a@b.c --expires 90d`
- **THEN** the token is printed once
- **AND** `token list` shows only its prefix, owner and expiry
