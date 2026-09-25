## Context

- `deb/<package>/debian/` uses hand-written `rules` (debhelper commands called directly, not `dh $@`). They read versions from `build/sources.rc` and fetch sources through `~/sources/platform-install-packages/build/package_*.sh`, a path that is hard-coded.
- The content was frozen at 16.16.0/focal. The core `postinst` scripts use debconf and the functions shipped by `kaltura-postinst` (`/opt/kaltura/bin/kaltura-functions.rc`).
- External sources, as checked in September 2026:
  - Gone: `kaltura/server` (GitHub returns 404), `installrepo.kaltura.org`, pentaho 4.2.1 on SourceForge, `playkit-js-bundle-builder` (now private), `player-studio-v7`, and the SVN at `kelev.kaltura.com`.
  - The tag `Rigel-18.20.0-rel` (commit `29cf4546`) still exists in public forks, for example `bw-kaltura/server`.
  - Still available: `clients-generator`, kmc-ng, mwEmbed (html5lib), player-studio v2/v3, kaltura-player-js, nginx and its modules, ffmpeg.
- Available on noble:
  - PHP 7.4 in the ondrej PPA, including the memcache, apcu and ssh2 extensions.
  - From the distro: `sphinxsearch` 2.2.11, `mariadb-server` 10.11, `ffmpeg` 6.1, `monit`, `sshpass`, `mediainfo`, `libapache2-mod-xsendfile`, `openjdk-8`.

## Goals / Non-Goals

**Goals:**
- The smallest package set that gives a working All-In-One: API, batch, Admin Console, KMC-ng, player v2 and VOD delivery through nginx.
- Build and test fully automated on Vagrant/VirtualBox (`bento/ubuntu-24.04`).

**Non-Goals:**
- Clusters or multi-server setups, SSL, live streaming (RTMP), red5, DWH/analytics (pentaho), player v3/v7 through the bundler, Flash apps, arm64, GPG signing of the repository.
- Porting Kaltura to PHP 8.

## Decisions

1. **Reuse `deb/<package>/debian` rather than rewriting with `dh $@`.** The diff stays small and the packaging history stays comparable. Only `control`, `changelog`, `rules` and `postinst` change, and only where noble requires it.
2. **Source mirror in this repository's GitHub Releases** (tag `sources-rigel-18.20.0`). Only sources that vanished go there: the server archive, named `Rigel-18.20.0.zip`, with root directory `server-Rigel-18.20.0/`. Everything else still comes from its original URL. Alternative rejected: committing the archives to git, which would add about 90 MB to the history.
3. **PHP 7.4 from the ondrej PPA.** The RPMs use the same version (remi 7.4). Using the native PHP 8.3 would mean porting the server. Dependencies name `php7.4-*` and `libapache2-mod-php7.4` explicitly: any generic `php-*` or `libapache2-mod-php` alternative makes apt pull PHP 8.4 from the PPA.
4. **Distro ffmpeg and sphinx through bridge packages.**
   - The packages keep their old names (`kaltura-ffmpeg`, `kaltura-ffmpeg-aux`, `kaltura-sphinx`) and only create symlinks and init scripts at the paths the core expects (`/opt/kaltura/bin/ffmpeg`, `/opt/kaltura/sphinx/bin/searchd`).
   - Building ffmpeg 4.4 and sphinx 2.2.1 costs hours, and the sphinx source (googlecode) no longer exists.
   - `ffmpeg-aux` (previously 3.4.6) points at the same ffmpeg 6.1. The real check is the upload→transcode→HLS sanity test.
5. **nginx built from source.**
   - It links the distro `libavcodec`/`libavformat`/`libswscale`, which the vod-module needs for thumbnails.
   - `dh_shlibdeps` is enabled, so the ELF dependencies end up in `Depends`.
   - Uses `-Wno-error` because of gcc 13.
   - Validation: `nginx -t` plus a real HLS request.
6. **Elasticsearch 7.17 from the Elastic apt repository.**
   - Uses the `elasticsearch-7` mappings that ship with 18.20, `discovery.type: single-node`, and a 1 GB heap.
   - If the sanity checks show an incompatibility, the proposal is revised. There is no implicit fallback.
7. **MariaDB 10.11 instead of MySQL 8.** Kaltura's SQL relies on the legacy grants and the old `sql_mode`. The RPMs on EL8 also use MariaDB.
8. **Two VMs in one Vagrantfile.** `build` writes to `deb/noble/repo/` (a synced folder), and `aio` consumes `file:/vagrant/deb/noble/repo`.
9. **Idempotency.** Package postinsts run only on first configure. `install-aio.sh` re-runs are safe: they only ensure repositories, packages and services.
10. **RPM impact.** The only shared change is `KALTURA_CORE_URI` in `build/sources.rc`, which now points at the mirror. The old URL returned 404, so the RPM build, already broken, works again with the same archive and root directory.
11. **Flash/DWH/bundler removal.** The dependencies are dropped. The `kaltura-db` postinst no longer needs the DWH.
12. **Unattended configuration.** Answers are preseeded with `debconf-set-selections` before `apt-get install`, in the same order as the legacy all-in-1 installer.
13. **Upstream 18.20.0 fixes applied at package time:**
    - A comma is missing in `app_token` in `01.kaltura_ce_tables.sql`.
    - New partners in `init_data/01.Partner.ini` (for example AUTH_BROKER, USER_PROFILE and KMS) bring new secret placeholders. `kaltura-base` generates a secret for any `@*_SECRET@` left.
15. **Elasticsearch 7 client mode.** Kaltura 18.20 defaults to the ES 5 client (`elasticVersion` = 5), where `hits.total` is an integer. On ES 7 it is an object, and `partner.register` crashes (`Unsupported operand types` in `myPartnerUtils`). The `kaltura-elasticsearch` postinst:
    - sets `elasticVersion = 7` in `elastic.ini` and in the populate config;
    - fills the leftover `@BEACONS_ELASTIC_*@` and `@CURL_TIMEOUT_IN_SEC@` placeholders;
    - uses 0 replicas (single node).
16. **`qt-faststart`.** The ffmpeg conversion engine runs `/opt/kaltura/bin/qt-faststart` after transcoding. Ubuntu ships it in the `ffmpeg` package, so `kaltura-ffmpeg` links it too.
14. **Package distribution.** The built `.deb` files are published as release assets, not committed.

## Risks / Trade-offs

- [ffmpeg 6.1 rejects a flag used by a conversion preset] → The sanity test uploads and transcodes a short video and a real YouTube video. If one fails, `kaltura-ffmpeg` goes back to building 4.4.
- [Some `postinst` step depends on Flash assets that are not installed] → Remove the affected templates, as is already done for `04.dropFolder`.
- [The ondrej PPA stops publishing 7.4 for noble; it is moving to packages.sury.org] → The risk is documented. Mitigation: mirror the PPA packages.
- [The fork used as the server source is not official] → Commit `29cf4546` was checked in two forks, and the mirrored archive is published with a SHA-256 that the build verifies.
- [The admin password rules reject passwords that contain the user's name or e-mail] → The default is `Adm1n#Video`, and the rule is documented.

## Migration Plan

This is a fresh install. There is no upgrade path from focal/16.16. To roll back, run `vagrant destroy aio`.
