## 1. Baseline and feasibility gate

- [ ] 1.1 Extract the checksum-verified pinned Kaltura archive and enumerate bundled dependencies, generated clients, packaging overlays and PHP entrypoints; verify a reproducible inventory records revisions, licenses and active versus historical build paths.
- [ ] 1.2 Reproduce the PHP 7.4 baseline in an isolated lab, never `.20`; verify API/UI/upload/worker/playback checks and save sanitized runtime, extension and timing reports.
- [ ] 1.3 Run PHP 8.3 syntax checks and a pinned compatibility analyzer against the exact packaged application, clients and installer PHP; verify every reported finding is classified with a source location and evidence, including manual checks the analyzer cannot cover.
- [ ] 1.4 Produce the three-distro provider/extension/SAPI matrix; verify signed suite-compatible PHP 8.3 package resolution and loaded modules in clean test environments, without mixing unsupported distro packages or extension ABIs.
- [ ] 1.5 Write a go/no-go feasibility report with bounded repairs, upstream references and blockers; verify operator approval before runtime/package implementation, stopping for a revised proposal if a framework/Kaltura upgrade is needed.

## 2. Compatibility patches and packaging

- [ ] 2.1 Fix confirmed core/API compatibility issues in a reviewed patch series; verify focused PHP 8.3 tests cover each changed behavior and the patch series applies to the pinned archive without fuzz or rejected hunks.
- [ ] 2.2 Fix confirmed worker/CLI, bundled-library and generated-client issues without an unpinned dependency upgrade; verify focused execution tests, attribution and hashes for every dependency/source change.
- [ ] 2.3 Wire a common reproducible patch application step into DEB/RPM builds; verify identical patched PHP sources are packaged on all three targets and a deliberate source/patch mismatch fails the build.
- [ ] 2.4 Update Ubuntu package dependencies and web/CLI configuration to the verified 8.3 stack; verify clean dependency resolution, matching CLI/Apache modules and configuration-preserving upgrade behavior on both Ubuntu versions.
- [ ] 2.5 Update EL9 dependencies, runtime stream and FPM/CLI configuration; verify 8.3 version-family selection, mandatory extensions, pool/service configuration and no old-runtime Kaltura workers after restart.
- [ ] 2.6 Replace PHP-8-rejection CI checks with positive exact-family and extension assertions; verify fixtures reject 7.4, 8.2/8.4, absent modules and misleading RPM release strings, while accepting the intended 8.3 transaction.

## 3. Isolated runtime acceptance

- [ ] 3.1 Run fresh install, repeated provisioning and reboot acceptance on an isolated Ubuntu 24.04 lab; verify no data/secret reset and zero functional sanity failures with web/CLI PHP 8.3 evidence.
- [ ] 3.2 Repeat the same acceptance on isolated Ubuntu 26.04 and save provider/module evidence; verify no fallback to another PHP minor or unsupported distro packages.
- [ ] 3.3 Repeat the same acceptance on isolated Rocky 9 with FPM; verify request-body handling, worker processing and modules rather than relying on dependency simulation alone.
- [ ] 3.4 Run API authentication/permission/JSON-contract, eSearch and Admin Console/KMC browser regression tests across the matrix; verify unauthorized calls still fail, UI flows succeed and logs contain no untriaged runtime failures.
- [ ] 3.5 Run short deterministic and Full HD/60 fps upload fixtures across HTTP and trusted HTTPS API/delivery; verify READY, thumbnails/flavors, HLS manifest/segment, progressive resolution/frame rate/Range and existing Go console E2E behavior.
- [ ] 3.6 Compare repeated baseline/candidate workload timings and error logs; verify the design's performance gate and triage all exercised-path warnings without blanket suppression.

## 4. Upgrade, recovery and release gate

- [ ] 4.1 Rehearse 7.4-to-8.3 upgrade with representative existing data in an isolated clone; verify accounts, partner secrets, media, configuration and job state are preserved without schema/engine changes.
- [ ] 4.2 Rehearse failed-cutover recovery from a coherent restricted snapshot; verify matched application/runtime/config/DB/media restoration and baseline login/playback, documenting the maintenance/write-freeze boundary.
- [ ] 4.3 Write migration, provider-update, rollback and limitations documentation with the evidence matrix; verify commands/links and re-check PHP 8.3 security-support dates before proposing a release candidate.
- [ ] 4.4 Obtain release approval only after all distro, runtime and recovery gates pass; verify uniquely versioned DEB/RPM artifacts and checksums, leaving old releases unchanged. Any actual `.20` cutover requires separate explicit target/window/backup approval.
