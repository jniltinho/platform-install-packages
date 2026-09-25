# ubuntu-2604-deb Specification

## Purpose
Build the Kaltura CE 18.20.0 All-In-One `.deb` set on Ubuntu 26.04 and install it unattended, verified by the same sanity checks as noble.

## Requirements

### Requirement: Build on Ubuntu 26.04
`vagrant up build2604` in `deb/ubuntu-26.04/` SHALL build every package of the noble All-In-One set into `deb/ubuntu-26.04/repo/` with an apt index.

#### Scenario: Full build
- **WHEN** the operator runs `vagrant up build2604` on a clean VM
- **THEN** provisioning exits 0
- **AND** 17 `.deb` files and `Packages.gz` exist in `deb/ubuntu-26.04/repo/`

### Requirement: Unattended AIO on Ubuntu 26.04
`vagrant up aio2604` SHALL install the packages with PHP 7.4 from packages.sury.org, configure the AIO unattended, and pass the sanity checks. The checks are: services up, API ping, admin session, Admin Console and KMC reachable, and an upload that reaches READY and plays over HLS.

#### Scenario: Clean install
- **WHEN** the operator runs `vagrant up aio2604` after a successful build
- **THEN** the sanity script reports 0 failures
- **AND** provisioning exits 0

### Requirement: CI packages
The `kaltura-server-packages` workflow SHALL build the noble, ubuntu-26.04 and el9 packages in containers. It SHALL resolve `kaltura-server` on a clean container of each distro, failing if PHP 8 would be installed. On tags `kaltura-server/v*` it SHALL publish one repository tarball per distro plus `SHA256SUMS`.

#### Scenario: Tag pushed
- **WHEN** `kaltura-server/v18.20.0-2` is pushed
- **THEN** the release contains `kaltura-server-noble-repo.tar.gz`, `kaltura-server-ubuntu-26.04-repo.tar.gz`, `kaltura-server-el9-repo.tar.gz` and `SHA256SUMS`
