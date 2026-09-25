# Console integration validation

## Initial validation — 2026-09-25 UTC

Source commit: `582a7f2888afe6e94581c48672be0db5593fd2d2`.
Console package: `0.1.0~rc3` (built from the same source before that commit;
the embedded commit therefore identifies the earlier repository base).

| Target | Install/service | Browser integration | Upgrade |
| --- | --- | --- | --- |
| Ubuntu 24.04 Noble `aio` | DEB installed, service active | Passed again after the server nginx/VOD 1.33 update | rc1 → rc2 preserved config checksum, user and authenticated session; rc3 active |
| Ubuntu 26.04 `aio2604` | Fresh DEB install, migration and service startup passed | Passed | Not tested |
| Rocky Linux 9 `el9aio` | RPM built, real installation pending server VM readiness | Pending | Not tested |

Both successful browser runs used `tests/e2e.sh` against actual Kaltura servers
with partner 102. They covered login, both upload transfer phases, processing
until READY, HTML5 playback, HTTP 206/Content-Range and a 1024-byte response,
metadata edit/delete, user creation/role/password/delete, health, English and
Portuguese navigation, zero border radius, 360-pixel layouts and logout.
Each run deleted only its generated media and user records. The temporary
Ubuntu 26.04 E2E login was removed after provisioning an operator account.
Credentials are not part of this repository.

Local checks passed: Go lint; CGO-disabled tests; race tests; TypeScript/ESLint
and radius lint; production frontend build; 11 Vitest tests. An isolated
MariaDB last-admin concurrency integration test passed five repetitions;
its temporary database/user were subsequently removed.

GitHub build run: [36089313085](https://github.com/jniltinho/platform-install-packages/actions/runs/36089313085).
Result: **success**. The build job passed lint, CGO-disabled tests, race tests,
11 Vitest tests, packaging and artifact upload. The release job was correctly
skipped on the branch push. Local `act` validation also passed. No release tag
was created.

## Follow-up validation — 2026-09-25 UTC

Source: `deabdc85` (includes TLS/base-path `8e606ef7` and navigation `63eff68b`).
Local packages: `0.1.0~rc8`, built from the same working source before the
commit; the embedded commit identifies the earlier base.

- Noble `.20` and Ubuntu 26.04 `.40`: rc8 DEB upgrades and full browser E2E passed.
- Rocky `.30`: RPM install and rc6 → rc7 → rc8 upgrades passed. rc8 full browser
  E2E passed at root and behind a real Apache HTTPS proxy at `/console`.
  The temporary test listener, services and secret-bearing proxy config were
  removed afterward; the main console and user media were preserved.
- PHP-FPM initially discarded chunked multipart uploads: setting the exact
  Content-Length fixed this without buffering the video in memory or changing
  Kaltura workers. The fake upstream tests reject chunked uploads.
- Standalone TLS on Rocky: curl with the generated CA certificate returned
  HTTP 200 at `/console/healthz`; private key mode 0600 and certificate reuse
  across restarts were verified. No upstream TLS verification was disabled.
- rc8 browser navigation regression passed: 150ms out-in fade, stable card/footer,
  rapid navigation, reduced-motion preference and logout.
- CGO-disabled Go tests, race tests, Go lint, frontend lint and all 13 Vitest tests passed.
- Prefix-specific session cookie names prevent a remaining root cookie from
  reauthenticating a prefixed deployment after logout; regression test passed.

## HTTPS upstream acceptance — 2026-09-25 UTC

- Source `d69201e1`, package `0.1.0~rc9`: Noble `.21` fresh rc8 install and
  rc9 upgrade passed. Full browser E2E passed at `https://192.168.56.21/console`
  with both the API and delivery upstream using HTTPS.
- The first test exposed a hardcoded HTTP progressive-playback redirect. rc9
  selects the manifest protocol from the configured playback host; regression
  tests cover HTTP and HTTPS. Playback now passes in the browser and returns
  HTTP 206 with the requested 1024 bytes.
- The VM trusts its Kaltura certificate through the OS CA store; Go upstream
  TLS verification remained enabled. Host curl/HTTP probes used an explicit CA
  certificate. Only the isolated test browser bypassed self-signed warnings.
- Requested demo videos are preserved: three matches on `.20` and `.30`, and
  one on `.21`, all READY with successful Range playback checks. Test-created
  E2E media/users were deleted by the test cleanup, not these demos.
- Console workflow [36095934196](https://github.com/jniltinho/platform-install-packages/actions/runs/36095934196)
  passed on `d69201e1`; downloaded DEB, RPM and tar.gz artifacts matched
  all three SHA256SUMS entries. Integrated console workflow
  [36096306963](https://github.com/jniltinho/platform-install-packages/actions/runs/36096306963)
  passed on `dab5b916`. These are build validations, not published releases.

## Remaining integration/release gates

- Validate the integrated server/console branch through both GitHub workflows.
- Record any additional distribution upgrade/remove/purge testing separately;
  a successful fresh install or package build does not imply those checks.
- Merge the integration PR only after the agreed CI and three-distribution
  E2E gates are green. Preserve existing VMs and user data.
