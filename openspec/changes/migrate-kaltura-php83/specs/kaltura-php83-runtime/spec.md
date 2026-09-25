## Purpose

Define the runtime compatibility, acceptance and data-preservation contract for migrating the packaged Kaltura CE AIO from PHP 7.4 to PHP 8.3 across supported distributions.

## ADDED Requirements

### Requirement: Consistent PHP runtime
Kaltura web, CLI, cron and background workers SHALL execute under PHP 8.3 with the mandatory extensions enabled for each SAPI. An unavailable compatible provider or extension SHALL block release rather than silently substituting another runtime.

#### Scenario: SAPI verification
- **WHEN** the migrated AIO is installed and restarted
- **THEN** web and CLI diagnostics report PHP 8.3 with their required extensions
- **AND** no active Kaltura worker uses the previous runtime

#### Scenario: Missing extension
- **WHEN** a mandatory extension cannot be installed or loaded for the target runtime
- **THEN** validation fails and no migration release is approved

### Requirement: Reproducible compatibility evidence
The migration SHALL record source and patch identities, a dependency/SAPI inventory and a triaged compatibility report. It SHALL NOT claim compatibility from syntax/static checks alone or hide unresolved runtime errors by disabling diagnostics.

#### Scenario: Upstream source changes
- **WHEN** the source hash or required patch application differs from the reviewed baseline
- **THEN** the build fails pending a new compatibility review

### Requirement: AIO behavior preserved
On Ubuntu 24.04, Ubuntu 26.04 and Rocky Linux 9, the migrated AIO SHALL retain API authentication/authorization and response behavior, Admin Console/KMC access, upload-to-READY processing, search, thumbnails, HTTP/HTTPS HLS delivery and progressive Range playback. Existing Go console media workflows SHALL continue to work without PHP changes to the console.

#### Scenario: Runtime acceptance
- **WHEN** the isolated acceptance suite runs on each supported distribution
- **THEN** API, browser and background-job checks pass without untriaged PHP warnings, fatal/type errors or authorization regressions
- **AND** uploaded Full HD media retains the expected delivered resolution and frame rate where the existing source/profile supports it

### Requirement: Isolated validation before live cutover
Feasibility and acceptance SHALL run in isolated environments. The existing `.20` installation SHALL remain untouched until an operator explicitly approves a live cutover with a maintenance window and verified backups.

#### Scenario: Proposal or feasibility execution
- **WHEN** planning or compatibility experiments run
- **THEN** no package, configuration, database or media changes are made on `.20`

### Requirement: Upgrade and recoverability
The migration SHALL preserve existing data and configuration, rehearse upgrades and matched-state recovery, and quiesce write-producing processes during cutover. Existing published releases SHALL remain immutable. A package downgrade alone SHALL NOT be represented as verified rollback.

#### Scenario: Upgrade and re-provision
- **WHEN** a PHP 7.4 baseline is upgraded in an isolated clone and provisioning is repeated
- **THEN** partner secrets, accounts, existing media and operator configuration remain intact
- **AND** the PHP 8.3 acceptance suite passes

#### Scenario: Failed acceptance
- **WHEN** acceptance fails before reopening write intake
- **THEN** the documented recovery restores matching application packages, runtime, configuration and consistent data/media state
- **AND** baseline authentication and existing-media playback pass again
