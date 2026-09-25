## MODIFIED Requirements

### Requirement: Unattended AIO on Ubuntu 26.04
`vagrant up aio2604` SHALL install the packages with PHP 8.3 from a verified, signed, suite-compatible provider, configure the AIO unattended, and pass the sanity checks. The checks are: services up, API ping, admin session, Admin Console and KMC reachable, and an upload that reaches READY and plays over HLS.

#### Scenario: Clean install
- **WHEN** the operator runs `vagrant up aio2604` after a successful build
- **THEN** the sanity script reports 0 failures
- **AND** provisioning exits 0

### Requirement: CI packages
The `kaltura-server-packages` workflow SHALL build the noble, ubuntu-26.04 and el9 packages in containers. It SHALL resolve `kaltura-server` on a clean container of each distro, failing unless the selected Kaltura CLI/web runtimes and required extension ABIs are consistently PHP 8.3; selecting 7.4 or another minor version SHALL fail. No migration tag SHALL be created before the approved three-distro runtime/recovery release gate. On approved migration tags `kaltura-server/v*` it SHALL publish one repository tarball per distro, the accepted versioned PHP 8.3 source ZIP, its source/patch manifest, installation instructions and `SHA256SUMS`, all in the same GitHub release.

#### Scenario: Tag pushed
- **WHEN** a new, unused `kaltura-server/v*` migration release tag is pushed
- **THEN** the release contains `kaltura-server-noble-repo.tar.gz`, `kaltura-server-ubuntu-26.04-repo.tar.gz`, `kaltura-server-el9-repo.tar.gz` and `SHA256SUMS`
- **AND** that same release contains the accepted versioned PHP 8.3 source ZIP, its source/patch manifest and installation instructions
- **AND** downloaded ZIP, manifest and package bundles match `SHA256SUMS` and the accepted source/patch identities, without overwriting any original ZIP or prior release
