# Console integration validation

## 2026-09-25 UTC

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

## Remaining gates

- Install and exercise the console RPM after the Rocky server VM is released.
- Validate the integrated server/console branch through both GitHub workflows.
- Record any additional distribution upgrade/remove/purge testing separately;
  a successful fresh install or package build does not imply those checks.
- Merge the integration PR only after the agreed CI and three-distribution
  E2E gates are green. Preserve existing VMs and user data.
