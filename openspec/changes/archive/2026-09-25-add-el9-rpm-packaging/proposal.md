## Why

The RPM specs in `RPM/SPECS` target EL8 and cannot be built from public sources anymore: `kaltura/server` and the googlecode Sphinx are gone. Rocky Linux 9 has no Kaltura CE 18.20.0 packages.

## What Changes

- EL9 branches in `RPM/SPECS` (guarded by `%if 0%{?rhel} >= 9`):
  - `kaltura-sphinx` 2.2.11 from the release tarball;
  - bridge `kaltura-ffmpeg`/`kaltura-ffmpeg-aux` over the RPM Fusion ffmpeg (`rpm/el9/SPECS`);
  - `kaltura-nginx` linked against the distro ffmpeg;
  - `kaltura-server` without DWH/widgets;
  - `kaltura-base` with EL9 dependencies and its python2 auto-dependency excluded.
- Upstream 18.20.0 fixes applied at package time, matching the noble ones:
  - `app_token` SQL comma;
  - generic partner secrets;
  - `appVersions.ini`;
  - Audit plugin;
  - Elasticsearch 7 client mode;
  - nginx upstream host.
- EL9-only fixes:
  - `php.yml` without `log_errors` (kaltura/server#9492);
  - optional DWH and legacy KMC in the config scripts;
  - a stale pid file in `kaltura-elastic-populate`.
- Vagrant environment `rpm/el9/` (VMs `el9build` and `el9aio`, box `bento/rockylinux-9`): `build.sh`, `install-aio.sh` (answers file + `kaltura-config-all.sh`) and `sanity.sh`.
- Docs: `doc/install-kaltura-rocky9.md` and a README link.

## Capabilities

### New Capabilities
- `el9-rpm`: build and unattended AIO install of the Kaltura 18.20.0 RPM set on Rocky Linux 9.

### Modified Capabilities
<!-- EL8 spec paths are unchanged (guarded by %if) -->

## Impact

- `RPM/SPECS/*.spec`, `RPM/SOURCES/{php.yml,kaltura-elastic-populate}`, `RPM/scripts/postinst/*`, the new `rpm/el9/`, `deb/kaltura-elasticsearch/debian/kaltura-elastic-populate.init` (same pid fix), `doc/`, `README.md`.
- The CI build and release are part of `.github/workflows/kaltura-server-packages.yml` (change `add-ubuntu-2604-deb-packaging`).
