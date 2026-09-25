## 1. Ubuntu 26.04

- [x] 1.1 Probe 26.04: PHP 7.4 via packages.sury.org, sphinxsearch 2.2.11, ffmpeg 8.0, MariaDB 11.8, libpcre2. Verify with `apt-cache policy` on `build2604`.
- [x] 1.2 nginx: vod 1.33, `ffmpeg-compat.h`, `-std=gnu17`, vod archive as a prerequisite. Verify that `kaltura-nginx` builds on 26.04.
- [x] 1.3 `deb/ubuntu-26.04/{Vagrantfile,build.sh,install-aio.sh,sanity.sh}`. Verify that `vagrant up build2604` builds 17 packages.
- [x] 1.4 Verify that `vagrant up aio2604` passes sanity with 0 failures.
- [x] 1.5 Rebuild noble with vod 1.33 and re-run the noble sanity before the merge.

## 2. CI and docs

- [x] 2.1 `build.sh` scripts run as root in containers (`SRC`/`REPO`). Verify with a local `docker run ubuntu:26.04` build.
- [x] 2.2 `.github/workflows/kaltura-server-packages.yml`: builds, clean-system checks, release on `kaltura-server/v*`.
- [ ] 2.3 Run the workflow on GitHub (`workflow_dispatch`) after the integration merge. Verify that all jobs are green.
- [x] 2.4 Write `doc/install-kaltura-ubuntu-26.04.md` and add the README link.
