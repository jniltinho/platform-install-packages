## Why

The Kaltura CE 18.20.0 `.deb` packages exist for Ubuntu 24.04 (`add-noble-deb-packaging`). Ubuntu 26.04 LTS (resolute) is the current LTS, but it breaks several build assumptions:

- FFmpeg 8 removed APIs that nginx-vod-module 1.30 uses.
- libpcre3 is gone.
- gcc 15 defaults to C23.
- The `ondrej/php` PPA does not serve resolute, so PHP 7.4 is not available from it.

## What Changes

- New Vagrant environment `deb/ubuntu-26.04/`:
  - VMs `build2604` and `aio2604` (192.168.56.40);
  - `build.sh`, `install-aio.sh` (PHP 7.4 from packages.sury.org) and `sanity.sh`.
- `kaltura-nginx`:
  - nginx-vod-module 1.30 → 1.33;
  - force-included `debian/ffmpeg-compat.h` (maps `avcodec_close` to `avcodec_free_context` on libavcodec ≥ 62);
  - `-std=gnu17`;
  - the vod module archive becomes an explicit build prerequisite.

  The recipes stay shared with noble.
- The `build.sh` scripts accept `SRC`/`REPO` and run as root without `sudo`, so CI containers can use them.
- New GitHub workflow `.github/workflows/kaltura-server-packages.yml`:
  - builds deb noble, deb ubuntu-26.04 and rpm el9 in containers;
  - checks dependency resolution on clean containers;
  - publishes on tags `kaltura-server/v*`.
- Docs: `doc/install-kaltura-ubuntu-26.04.md` and a README link.

## Capabilities

### New Capabilities
- `ubuntu-2604-deb`: build and unattended AIO install of the Kaltura 18.20.0 `.deb` set on Ubuntu 26.04.

### Modified Capabilities
<!-- noble behavior is unchanged; its build recipes gain compatibility flags only -->

## Impact

- Code: `deb/kaltura-nginx/debian/{rules,ffmpeg-compat.h}`, `build/sources.rc` (vod version), `deb/noble/build.sh`, the new `deb/ubuntu-26.04/`, `.github/workflows/`, `doc/`, `README.md`.
- noble must be rebuilt and re-validated with vod 1.33 before merge.
