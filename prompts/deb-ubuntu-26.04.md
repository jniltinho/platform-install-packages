# Agent prompt: Kaltura CE 18.20.0 .deb packages for Ubuntu 26.04

Run this from a dedicated worktree so the agent does not collide with the noble work:

```bash
git worktree add ../platform-install-packages-2604 -b ubuntu-2604-deb-packaging noble-deb-packaging
cd ../platform-install-packages-2604
grok < prompts/deb-ubuntu-26.04.md     # or the equivalent non-interactive invocation of your agent CLI
```

---

All repository content must be in English: code, comments, docs and commit-ready text. Stay inside this git worktree. Do NOT run `git commit` or `git push`; a human reviews and commits.

## Goal

Build, install and test the Kaltura CE **Rigel-18.20.0** Single-server All-In-One as `.deb` packages for **Ubuntu 26.04 LTS** (amd64), using Vagrant/VirtualBox. This extends the Ubuntu 24.04 (noble) work. Read these first:

- `openspec/changes/add-noble-deb-packaging/`: proposal, design, specs, tasks. The design lists every decision and upstream fix.
- `deb/noble/Vagrantfile`, `deb/noble/build.sh`, `deb/noble/install-aio.sh`, `deb/noble/sanity.sh`
- `doc/install-kaltura-noble.md`
- `deb/<package>/debian/*`, the shared packaging recipes. They are already updated for noble.

Start by creating an OpenSpec change `add-ubuntu-2604-deb-packaging` with `openspec new change add-ubuntu-2604-deb-packaging`. It is a delta over the noble change and only needs to describe what differs on 26.04. Keep it valid with `openspec validate add-ubuntu-2604-deb-packaging --strict`.

## Constraints

- **Do not break noble.** The `deb/<package>/debian` recipes are shared between releases. If 26.04 needs something different, prefer changes that work on both releases: dependency alternatives in `control`, or runtime detection in `postinst`. If a recipe cannot serve both, add a small per-release override and explain why in `design.md`.
- **Separate VMs.** Put the new environment in `deb/ubuntu-26.04/` with box `bento/ubuntu-26.04`:
  - VM `build2604`: 8 GB RAM, 8 CPUs.
  - VM `aio2604`: 8 GB RAM, 4 CPUs, `private_network` IP `192.168.56.40`, `autostart: false`.
  - The repo output goes to `deb/ubuntu-26.04/repo/`. Add it to `.gitignore`.
- **Leave the noble VMs alone.** Never touch the VMs `build` and `aio` (IP 192.168.56.20), or `deb/noble/repo/`.

## Already solved on noble (reuse)

- **Server source.** `kaltura/server` is gone from GitHub. `KALTURA_CORE_URI` points to the mirror release `sources-rigel-18.20.0`, and its SHA-256 is verified.
- **Flash and DWH removed.** The Flash apps, DWH/pentaho and playkit-bundler are out of scope; their sources are gone.
- **Distro binaries.** `kaltura-ffmpeg`, `kaltura-ffmpeg-aux` and `kaltura-sphinx` are bridge packages over distro binaries.
- **nginx.** `kaltura-nginx` is built from source with `--with-cc-opt=-Wno-error` and `dh_shlibdeps`, linking the distro libav*.
- **Upstream 18.20.0 fixes.** Already applied:
  - `app_token` comma in the SQL;
  - generic `@*_SECRET@` fill in `kaltura-base` postinst;
  - `mysql -N` for `USER_EXISTS` in `kaltura-db` postinst;
  - nginx upstream host without a scheme;
  - ES 7.17 `elasticsearch-7` mappings with `single-node` and a 1 GB heap;
  - admin password `Adm1n#Video`.
- **PHP.** Dependencies are pinned to `php7.4-*` and `libapache2-mod-php7.4`. Any generic `php-*` or `libapache2-mod-php` alternative pulls PHP 8 and breaks Kaltura: PHP 8 fails with `KalturaPDO::query()` signature errors.

## Things to verify first on 26.04 (they drive the decisions)

1. **PHP 7.4.** The `ondrej/php` PPA says Resolute is served from `https://packages.sury.org/php/`. Check that `php7.4-{cli,xml,curl,mysql,mbstring,gd,gmp,ldap,memcache,zip,intl,xsl,apcu,ssh2}` and `libapache2-mod-php7.4` exist for 26.04 and install cleanly. If PHP 7.4 is not available for 26.04, stop and document it as a blocker in the OpenSpec change. Do not port Kaltura to PHP 8 without a human decision.
2. **Sphinx.** Check whether `sphinxsearch` still exists in 26.04 universe. If it does not, decide between building Sphinx 2.2.11 from source (for example the `sphinxsearch/sphinx` GitHub tag `2.2.11-release`) or another compatible option, and record the decision.
3. **ffmpeg.** Note the ffmpeg version. `nginx-vod-module` 1.30 may not compile against ffmpeg ≥ 7 because of the thumbnail/avcodec API. If it fails, try a newer vod-module release first, then building without thumbnail capture, and document the trade-off. Also re-check that the Kaltura conversion presets still work: the upload → READY sanity check covers this.
4. **MariaDB version.** Check that the Kaltura SQL still loads, with `lower_case_table_names=1` and `sql_mode=NO_ENGINE_SUBSTITUTION`.
5. **Elasticsearch.** Check that the Elastic 7.x apt repository still installs 7.17 on 26.04.
6. **Library renames.** Check the dependencies listed by `dh_shlibdeps` and any hard-coded library package names (for example t64 renames).

## Deliverables

- `deb/ubuntu-26.04/{Vagrantfile,build.sh,install-aio.sh,sanity.sh}`. Adapt them from `deb/noble/` with minimal differences, and keep `sanity.sh` behavior identical.
- Changelog entries for release 26.04 where the packages differ. A version suffix such as `~2604` is fine if both releases need to coexist in one repository.
- `doc/install-kaltura-ubuntu-26.04.md`, and a link in `README.md`.
- A final summary:
  - what works and what failed;
  - exact commands to reproduce;
  - the list of `.deb` files with versions;
  - any change to shared recipes, with proof that noble still builds: run `vagrant up build` in `deb/noble/`, or explain why you could not.

## Definition of done

- `vagrant up build2604` exits 0, and every package of the set is in `deb/ubuntu-26.04/repo/`.
- `vagrant up aio2604` exits 0, and the sanity checks pass: services, ping, `session.start`, admin_console 200, kmcng 200, MP4 upload READY within 10 minutes, HLS manifest plus one segment.
- `vagrant provision aio2604` passes again.
- After `vagrant reload aio2604 --no-provision`, the sanity checks pass over SSH.

Iterate until the definition of done is met, or until a blocker needs a human decision (for example PHP 7.4 unavailable). In that case, record the exact failing command, the log excerpt and the options you considered. Only destroy the VMs `build2604` and `aio2604`.
