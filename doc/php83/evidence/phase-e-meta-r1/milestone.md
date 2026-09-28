# Actual E meta-package installation

2026-09-28. Coordinator executed the reviewed fresh E executor after a successful
read-only guard and matched pre-E snapshot. Normal offline APT installed exactly
`kaltura-server 18.20.0-1+php83lab1` (all), SHA256
`e53154baff6e5f091a0ee876e558e0469ff38e06f7b4ab5b4207d29573c1b387`.
Its authenticated control archive has no maintainer hooks and its data archive
contains only the root directory. No service-start command was executed.

Execution exited 0 and all four terminal checks passed: exact package observation,
unchanged runtime/private metadata, input-canary scan and generated-secret audit.
The actual installed Kaltura cohort now contains 17 packages. Apache, Monit,
MariaDB and Elasticsearch remained active; nginx remained stopped and workers
remained held. The D3 configuration, private safe logs and listeners were checked
unchanged. See `actual-execution.json` and `contract.json` for bounded results and
cohort identities. No raw runtime log or configuration was exported.

Author, coordinator and independent Codex reviewer executed the six local tests,
including actual inspection of the pinned hookless DEB. The reviewed final
executor SHA256 is `d63af73cd1620cedf491b2105b553e9880b9bdd170bfceec3bcb3c4008fb8230`.
The independent reviewer confirmed the sole final helper-path correction and
reviewed the sanitized actual receipt. These tests are not full application
acceptance. Existing external CLI limitations are preserved in the D3 milestone.

This finishes the planned incremental package-install sequence in this Noble lab,
not the migration or a deployable release. Continuous nginx operation, full seed
persistence/authorization, API/UI, upload-to-READY, background jobs, search/media,
TLS/HLS/progressive playback, all-distro and recovery/performance acceptance remain
open. Do not release workers or RTMP publishing merely because the meta-package
is installed. OpenSpec remains 4/51; no new task-completion email was warranted.
