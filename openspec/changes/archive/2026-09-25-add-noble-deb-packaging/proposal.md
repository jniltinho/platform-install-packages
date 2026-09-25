## Why

The `.deb` packaging in this repository stopped at 16.16.0 (Ubuntu focal/xenial), while the RPMs are already on Rigel-18.20.0. Kaltura CE 18.20.0 therefore cannot be installed on Ubuntu 24.04 LTS (noble). Several sources the build depends on are also gone:

- The `kaltura/server` repository was removed from GitHub.
- `installrepo.kaltura.org` no longer responds.
- pentaho on SourceForge returns 404.
- The Flash apps come from an unreachable internal SVN.

As a result, the current build cannot be reproduced.

## What Changes

- Update the recipes in `deb/` to Rigel-18.20.0 for Ubuntu 24.04 (noble), amd64, as a **Single-server All-In-One** install.
- Runtime stack:
  - PHP 7.4 from the `ondrej/php` PPA. Kaltura 18.20 does not support PHP 8.x.
  - MariaDB 10.11 from the distro.
  - Elasticsearch 7.17 from the Elastic apt repository.
- `kaltura-ffmpeg`, `kaltura-ffmpeg-aux` and `kaltura-sphinx` become thin bridge packages over the distro `ffmpeg` 6.1 and `sphinxsearch` 2.2.11. They keep the same `/opt/kaltura` paths.
- `kaltura-nginx` is built from source again: nginx 1.23.0 plus the vod, secure-token, akamai-token, rtmp and vts modules, linked against the distro ffmpeg.
- Sources that disappeared are mirrored as GitHub Release assets of this repository (`jniltinho/platform-install-packages`). `build/sources.rc` points to the mirror.
- New reproducible environment in `deb/noble/`:
  - `Vagrantfile` with a `build` VM, which builds the `.deb` files and a local apt repository, and an `aio` VM, which installs from it, configures unattended and runs the sanity checks.
  - Scripts `build.sh`, `install-aio.sh` and `sanity.sh`.
- **BREAKING**: on noble, `kaltura-server` no longer depends on the following, because none of them has a public source anymore:
  - The Flash packages: `kaltura-widgets`, kdp, kcw, kupload, kvpm, kclip, flexwrapper and legacy kmc.
  - `kaltura-dwh` and `kaltura-pentaho`.
  - `kaltura-playkit-bundler`.
- End-to-end validation:
  - Upload a real YouTube video (fetched with `yt-dlp`) through the API and the UI.
  - Screenshots of the whole administration interface (Admin Console and KMC), taken with `agent-browser` and saved in `doc/prints/`.
  - Check that the `criare/kaltura-console` and `criare/kaltura-legacy-gateway` clients can talk to this install's API.
- Documentation, all in English:
  - `doc/install-kaltura-noble.md`.
  - `doc/kaltura-api-noble.md`: session, upload, entries and playManifest, with `curl` examples validated on the VM.
  - Update `README.md` and the related docs for the new packages.
- Built packages are published as GitHub Release assets rather than committed to git. A flat apt repository can point at the release URL.

## Capabilities

### New Capabilities
- `noble-deb-build`: reproducible build of the Kaltura 18.20.0 `.deb` packages for Ubuntu 24.04, with resolvable sources and a local apt repository.
- `noble-aio-install`: unattended install and configuration of a Single-server All-In-One on Ubuntu 24.04 from those packages, verified by automated sanity checks.
- `noble-aio-validation`: validation evidence for the AIO:
  - a real video uploaded and processed;
  - screenshots of the administration interface;
  - API documentation;
  - interoperability with the `criare` clients.

### Modified Capabilities
<!-- none: there are no previous specs in openspec/specs -->

## Impact

- Code: `deb/*/debian/{control,rules,postinst,changelog}`, `build/sources.rc`, `build/package_*.sh`, the new `deb/noble/`, `doc/` and `README.md`.
- External dependencies:
  - The `ondrej/php` PPA.
  - The Elastic 7.x apt repository.
  - This repository's GitHub Releases, used as the source mirror and for package downloads.
- RPM: only `KALTURA_CORE_URI` changes. It replaces a URL that returned 404 with the mirror, which serves the same content. The RPM specs do not change.
