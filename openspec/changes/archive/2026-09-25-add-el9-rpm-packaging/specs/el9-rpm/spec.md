## Purpose

Build the Kaltura CE 18.20.0 All-In-One RPM set on Rocky Linux 9 and install it unattended, verified by the same sanity checks as the Ubuntu packages.

## ADDED Requirements

### Requirement: Build on Rocky Linux 9
`vagrant up el9build` in `rpm/el9/` SHALL build every RPM of the All-In-One set into `rpm/el9/repo/` with repodata.

#### Scenario: Full build
- **WHEN** the operator runs `vagrant up el9build` on a clean VM
- **THEN** provisioning exits 0
- **AND** `rpm/el9/repo/` contains the RPMs and `repodata/`

### Requirement: Unattended AIO on Rocky Linux 9
`vagrant up el9aio` SHALL install `kaltura-server` with PHP 7.4 from remi and configure it with `kaltura-config-all.sh` and an answers file, with no prompt. It SHALL pass the sanity checks.

#### Scenario: Clean install
- **WHEN** the operator runs `vagrant up el9aio` after a successful build
- **THEN** the sanity script reports 0 failures: services, ping, session, Admin Console, KMC, upload → READY, HLS manifest and segment
- **AND** provisioning exits 0

#### Scenario: Re-provisioning
- **WHEN** `vagrant provision el9aio` runs on an installed VM
- **THEN** the configuration is not re-run and the sanity checks still pass
