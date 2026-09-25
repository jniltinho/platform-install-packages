## 1. Sources

- [x] 1.1 Check the commit of tag `Rigel-18.20.0-rel` in two forks. Publish `Rigel-18.20.0.zip` (root `server-Rigel-18.20.0/`) and its `.sha256` in release `sources-rigel-18.20.0`. Verify with `curl -I` that the asset returns 200.
- [x] 1.2 Point `KALTURA_CORE_URI` at the mirror and verify the SHA-256 in `build/package_kaltura_core.sh`. Verify that a wrong SHA-256 makes the script fail.

## 2. Build environment

- [x] 2.1 Create `deb/noble/Vagrantfile` (VMs `build` and `aio`, pinned box) and `deb/noble/build.sh`. The script installs the build deps, copies the repo to `~/sources/platform-install-packages`, builds the set in order and runs `dpkg-scanpackages`. Verify with `vagrant up build`.
- [x] 2.2 Ignore the build artifacts (`deb/noble/repo/`, `.vagrant/`) in git. Verify that `git status` is clean after a build.

## 3. Packages

- [x] 3.1 Bridge packages `kaltura-ffmpeg`, `kaltura-ffmpeg-aux` and `kaltura-sphinx` over the distro ffmpeg and sphinxsearch. Verify that the `.deb` files build and install (functional validation is in 4.2).
- [x] 3.2 `kaltura-postinst` 1.0.34 and `kaltura-base` 18.20.0: `php7.4-*` dependencies, upstream SQL fix and generic partner secrets. Verify that `dpkg -c` lists `/opt/kaltura/app`.
- [x] 3.3 `kaltura-front`, `kaltura-batch` and `kaltura-db` 18.20.0: apache2 + libapache2-mod-php7.4, MariaDB, no DWH. Verify that the `.deb` files are built.
- [x] 3.4 Web packages: `kaltura-kmcng` v5.17.0, `kaltura-html5lib` v2.98, `kaltura-html5lib3` 3.8.1, `kaltura-html5-studio` v2.2.3, `kaltura-html5-studio3` v3.18.0 and `kaltura-html5-analytics` v0.3. Verify that they build and do not pull PHP 8.
- [x] 3.5 `kaltura-nginx` 1.23.0 with vod 1.30, secure-token, akamai-token, rtmp and vts, linked against the distro ffmpeg, with `dh_shlibdeps`. Verify with `nginx -t` and that the service is active on the `aio` VM.
- [x] 3.6 `kaltura-elasticsearch` on Elasticsearch 7.17 (ICU plugin, indices created). Verify with `curl :9200/_cat/indices` on the `aio` VM.
- [x] 3.7 Meta package `kaltura-server` 18.20.0, depending on exactly the All-In-One set. Verify that `apt-get install --simulate kaltura-server` resolves on the `aio` VM.

## 4. Install and tests

- [x] 4.1 `deb/noble/install-aio.sh`: ondrej PPA, Elastic repo, local repo, MariaDB, preseed and unattended install. Verify that `vagrant up aio` and then `vagrant provision aio` both exit 0 and keep the same admin secret.
- [x] 4.2 `deb/noble/sanity.sh` checks services, ping, `session.start`, admin_console, kmcng, MP4 upload, entry READY within 10 minutes, and an HLS manifest with a valid segment. Verify that it passes on the `aio` VM and fails when apache2 is stopped.
- [x] 4.3 Run `vagrant reload aio --no-provision`, then the sanity script over `vagrant ssh`. Verify that it passes.

## 5. Review and documentation

- [ ] 5.1 Review the proposal and the implementation with the `codex` CLI and apply the relevant fixes.
- [x] 5.2 Write `doc/install-kaltura-noble.md` (build, install, limitations). Verify with `openspec validate add-noble-deb-packaging --strict`.
- [ ] 5.3 Update `README.md` and the related docs (package list, supported distros, links) for the noble packages.
- [ ] 5.4 Publish the built `.deb` files and `Packages.gz` as release assets. Verify that `apt-get update` works with `deb [trusted=yes] https://github.com/jniltinho/platform-install-packages/releases/download/<tag> ./`.

## 6. End-to-end validation

- [x] 6.1 Download a YouTube video with `yt-dlp` (MP4, 720p or lower) and upload it through the API to the test partner. Verify READY, the flavors and HLS.
- [x] 6.2 Capture screenshots with `agent-browser` of every Admin Console page and the main KMC screens into `doc/prints/`. Verify that none of them shows an error.
- [ ] 6.3 Write `doc/kaltura-api-noble.md` with `curl` examples run on the VM. Verify by re-running the examples.
- [ ] 6.4 Run `criare/kaltura-console` and `criare/kaltura-legacy-gateway` against the AIO and record the outcome in the documentation.
