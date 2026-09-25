## MODIFIED Requirements

### Requirement: Package quality
Every built `.deb` SHALL install on Ubuntu 24.04 without unmet dependencies, using only these repositories:
- the distro repositories (main, universe and multiverse);
- the `ondrej/php` PPA;
- the Elastic 7.x apt repository (version 7.17);
- the local repository.

For the PHP 8.3 migration release, the selected CLI/web runtimes and mandatory extensions SHALL belong to the verified PHP 8.3 stack. Package resolution SHALL reject 7.4, other PHP minor runtimes and mismatched extension ABIs. Additional runtime repositories require an explicitly reviewed suite-compatible provider manifest before use.

#### Scenario: Dependency resolution
- **WHEN** `apt-get install --simulate kaltura-server` runs with those repositories configured
- **THEN** apt resolves every dependency without errors
- **AND** the PHP runtime selected is 8.3 and every mandatory extension resolves for that runtime
