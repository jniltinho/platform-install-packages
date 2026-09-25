# Agent prompt: Kaltura CE 18.20.0 RPMs for Rocky Linux 9

How to run it, from a dedicated worktree so the agent does not collide with the noble work:

```bash
git worktree add ../platform-install-packages-el9 -b el9-rpm-packaging noble-deb-packaging
cd ../platform-install-packages-el9
codex exec --sandbox danger-full-access - < prompts/rpm-rocky9.md
```

---

Write everything you add to the repository in English: code, comments, docs, commit-ready text. Work only in this git worktree. Do NOT run `git commit` or `git push`; a human reviews and commits.

## Goal

Build, install and test the Kaltura CE **Rigel-18.20.0** Single-server All-In-One as `.rpm` packages for **Rocky Linux 9** (EL9, x86_64), using Vagrant/VirtualBox. Use the Ubuntu 24.04 work as your reference for approach and scope. Read these first:

- `openspec/changes/add-noble-deb-packaging/` (proposal, design, specs, tasks)
- `deb/noble/Vagrantfile`, `deb/noble/build.sh`, `deb/noble/install-aio.sh`, `deb/noble/sanity.sh`
- `doc/install-kaltura-noble.md`
- `RPM/SPECS/*.spec`, `RPM/scripts/postinst/*` (current RPM packaging, last built for EL8)

Start by creating an OpenSpec change `add-el9-rpm-packaging` (`openspec new change add-el9-rpm-packaging`) that mirrors the noble one. Keep it valid with `openspec validate add-el9-rpm-packaging --strict`.

## Already solved (reuse, do not redo)

- **Server source.** `kaltura/server` is gone from GitHub. `build/sources.rc` points `KALTURA_CORE_URI` at the mirror `https://github.com/jniltinho/platform-install-packages/releases/download/sources-rigel-18.20.0/Rigel-18.20.0.zip`, and `KALTURA_CORE_SHA256` is verified by `build/package_kaltura_core.sh`.
- **Dead sources.** `installrepo.kaltura.org` is dead. The internal SVN (Flash apps) and `playkit-js-bundle-builder` (private) are unreachable. `pentaho` 4.2.1 is 404 on SourceForge.
- **Scope.** Same set as noble: `kaltura-postinst`, `kaltura-base`, `kaltura-front`, `kaltura-batch`, `kaltura-server`, `kaltura-ffmpeg`, `kaltura-ffmpeg-aux`, `kaltura-sphinx`, `kaltura-nginx`, `kaltura-elasticsearch`, `kaltura-kmcng`, `kaltura-html5lib`, `kaltura-html5lib3`, `kaltura-html5-studio`, `kaltura-html5-studio3`, `kaltura-html5-analytics`, plus `kaltura-monit` or `kaltura-mysql-config` if the specs need them.
  - For EL9, drop Flash, DWH/pentaho, `kaltura-playkit-bundler` and `kaltura-widgets` from the `kaltura-server` meta package.
  - `kaltura-html5lib3` must skip the private plugins when no token is set. `build/package_kaltura_html5lib3.sh` already does this.
- **Upstream 18.20.0 bugs.** These also hit the RPM path, so apply them in the spec or config scripts:
  1. `deployment/base/sql/01.kaltura_ce_tables.sql` is missing a comma before ``KEY `partner_id_status` `` in `app_token`. See the `perl -0pi` line in `deb/kaltura-base/debian/rules`.
  2. `deployment/base/scripts/init_data/01.Partner.ini` has new secret placeholders that `RPM/scripts/postinst/kaltura-base-config.sh` does not substitute: `@AUTH_BROKER_*@`, `@USER_PROFILE_*@`, `@KMS_*_SECRET@` and others. After the existing seds, generate one secret per remaining `@*_SECRET@` placeholder and reuse it across files. See the `NEW_SECRETS` loop in `deb/kaltura-base/debian/postinst`.
  3. The admin password must not contain the user's name or e-mail. Use `Adm1n#Video` for `admin@kaltura.local`.
  4. Elasticsearch 7.17 must use the mappings in `configurations/elastic/mapping/elasticsearch-7/` and `plugins/beacon/config/mapping/elasticsearch-7/`, with `discovery.type: single-node` and a 1 GB heap (`/etc/elasticsearch/jvm.options.d/`). Use `elasticsearch-plugin install --batch analysis-icu`.
  5. The kaltura-nginx upstream host must be a bare host, not a URL. Strip `http(s)://` from the service URL.
  6. The DB config scripts query `mysql.user` without `-N`, so `USER_EXISTS` is never `1` on re-runs. Use `mysql -N`.
- **EL9 stack.**
  - PHP 7.4 from remi: `dnf module reset php && dnf module enable php:remi-7.4`. Make sure nothing pulls PHP 8.
  - MariaDB from the distro. Put this in a `/etc/my.cnf.d/` drop-in, because the `sed` on `my.cnf` does nothing there:
    ```
    lower_case_table_names=1
    innodb_file_per_table
    innodb_log_file_size=32M
    open_files_limit=20000
    max_allowed_packet=16M
    sql_mode=NO_ENGINE_SUBSTITUTION
    ```
    If root is set up with unix_socket auth, give it a password usable over TCP from `127.0.0.1`.
  - Elasticsearch 7.17 from `artifacts.elastic.co/packages/7.x/yum`.
  - EPEL and RPM Fusion for `ffmpeg`, `sphinx`, `mediainfo` and `sshpass`. Prefer thin bridge RPMs, which symlink into `/opt/kaltura/bin` and `/opt/kaltura/sphinx/bin` as the noble `debian/links` files do, over building ffmpeg or sphinx from source.
  - `kaltura-nginx` must be built from source with `nginx-vod-module` and must link the distro ffmpeg libraries.
  - SELinux: set permissive in the test VM and document it.

## Deliverables (all under `rpm/el9/` unless noted)

- `Vagrantfile`, box `generic/rocky9`:
  - VM `el9build` (8 GB RAM, 8 CPUs) builds every RPM into `rpm/el9/repo/` and runs `createrepo_c`.
  - VM `el9aio` (8 GB RAM, 4 CPUs, `private_network` IP `192.168.56.30`, `autostart: false`) installs from the local repo, configures unattended with an answer file for `kaltura-config-all.sh`, and runs the sanity script.
  - Use VM names and IPs distinct from the noble VMs (`build`, `aio`, `192.168.56.20`). Never touch the noble VMs or `deb/noble/`.
- `build.sh`, `install-aio.sh`, `sanity.sh`:
  - `install-aio.sh` must be idempotent: re-running it must not recreate the DB or change secrets.
  - `sanity.sh` runs the same checks as `deb/noble/sanity.sh`: services, `system.ping`, `session.start`, admin_console 200, kmcng 200, MP4 upload → READY within 10 minutes, and an HLS m3u8 plus one segment.
- Minimal edits to `RPM/SPECS/*.spec` and `RPM/scripts/postinst/*` for EL9. Keep the EL8 behavior where possible.
- Add `rpm/el9/repo/` to `.gitignore` (`.vagrant/` is already there).
- `doc/install-kaltura-rocky9.md`, and a link in `README.md`.
- A final summary:
  - what works and what failed;
  - exact commands to reproduce;
  - the list of RPMs built, with versions;
  - the OpenSpec tasks checked off.

## Definition of done

- `vagrant up el9build` exits 0 with every RPM of the set in `rpm/el9/repo/`.
- `vagrant up el9aio` exits 0 and the sanity script passes.
- `vagrant provision el9aio` passes a second time.
- `vagrant reload el9aio --no-provision`, followed by the sanity script over SSH, also passes.

Iterate until the definition of done is met. If you run out of reasonable options, document the exact blocker: the failing command, the log excerpt, and what you tried. Only destroy the VMs `el9build` and `el9aio`.
