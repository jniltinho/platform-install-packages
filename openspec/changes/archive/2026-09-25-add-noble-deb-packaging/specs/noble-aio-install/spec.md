## Purpose

Ensure that a Kaltura CE 18.20.0 Single-server All-In-One can be installed and configured unattended on Ubuntu 24.04 (noble), and that the result is functional and checked by an automated sanity script.

## ADDED Requirements

### Requirement: Unattended All-In-One install
The install SHALL complete without any prompt when the configuration answers are provided upfront (debconf preseed).

#### Scenario: Test VM provisioning
- **WHEN** the operator runs `vagrant up aio` in `deb/noble/` after a successful build
- **THEN** `kaltura-server` and its dependencies are installed from the local repository
- **AND** the database, Sphinx, Elasticsearch, nginx and Apache are configured and running
- **AND** provisioning exits with code 0

### Requirement: Working API
After the install, the Kaltura API SHALL respond.

#### Scenario: API ping
- **WHEN** `GET http://<host>/api_v3/index.php?service=system&action=ping` is requested
- **THEN** the response is HTTP 200 and the body contains `true`

#### Scenario: Admin session
- **WHEN** a session is started (`session.start`) for partner -2 with the admin secret generated during the install
- **THEN** the API returns a valid KS

### Requirement: Web interfaces reachable
The host SHALL serve the Admin Console and the KMC (kmc-ng).

#### Scenario: Admin Console
- **WHEN** `GET http://<host>/admin_console/` is requested, following redirects
- **THEN** the final response is HTTP 200

#### Scenario: KMC
- **WHEN** `GET http://<host>/index.php/kmcng/` is requested
- **THEN** the response is HTTP 200

### Requirement: Transcoding and VOD delivery
The All-In-One SHALL transcode an uploaded video and deliver it through nginx VOD.

#### Scenario: Upload and transcoding
- **WHEN** the sanity script uploads a short MP4 to a test partner through the API
- **THEN** the entry reaches status READY (2) within 10 minutes

#### Scenario: HLS manifest
- **WHEN** the HLS manifest of the converted entry is requested, following redirects, at `/p/<pid>/sp/<pid>00/playManifest/entryId/<id>/format/applehttp/protocol/http/a.m3u8`
- **THEN** the response is a valid m3u8
- **AND** its first `.ts` segment returns HTTP 200 with a non-empty body

### Requirement: Idempotent re-provisioning
Re-running the install on the same VM SHALL NOT recreate the database or change secrets already generated.

#### Scenario: Second provisioning
- **WHEN** the operator runs `vagrant provision aio` on an installed VM
- **THEN** provisioning exits with code 0
- **AND** the sanity checks pass with the same admin secret

### Requirement: Persistent services
The All-In-One services SHALL start on their own after a reboot.

#### Scenario: Reboot
- **WHEN** the `aio` VM is rebooted without provisioning (`vagrant reload aio --no-provision`)
- **THEN** the sanity script, run over SSH, passes again with no manual intervention

### Requirement: Automated sanity checks
The environment SHALL provide a sanity script that checks the requirements above. It SHALL exit non-zero if any check fails.

#### Scenario: Failure detected
- **WHEN** an essential service is stopped, for example apache2
- **THEN** the sanity script reports the failed check
- **AND** it exits non-zero
