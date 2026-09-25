## MODIFIED Requirements

### Requirement: Unattended AIO on Rocky Linux 9
`vagrant up el9aio` SHALL install `kaltura-server` with PHP 8.3 from one verified EL9 AppStream or Remi stream with matching extensions, selected in the reviewed provider manifest and configure it with `kaltura-config-all.sh` and an answers file, with no prompt. It SHALL pass the sanity checks.

#### Scenario: Clean install
- **WHEN** the operator runs `vagrant up el9aio` after a successful build
- **THEN** the sanity script reports 0 failures: services, ping, session, Admin Console, KMC, upload → READY, HLS manifest and segment
- **AND** provisioning exits 0

#### Scenario: Re-provisioning
- **WHEN** `vagrant provision el9aio` runs on an installed VM
- **THEN** the configuration is not re-run and the sanity checks still pass
