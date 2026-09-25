# Rocky Linux 9 Single-server All-In-One (RPM)

Kaltura CE **Rigel-18.20.0** RPMs for Rocky Linux 9. They also apply to AlmaLinux and RHEL 9 (x86_64). Packages are built and tested with Vagrant/VirtualBox from `rpm/el9/`, using the specs in `RPM/SPECS` (EL9 branches are guarded with `%if 0%{?rhel} >= 9`).

## Stack

| Component | Source |
|---|---|
| PHP 7.4 | remi (`dnf module enable php:remi-7.4`) |
| MariaDB 10.5 | Rocky AppStream |
| Elasticsearch 7.17 | Elastic yum repo (`artifacts.elastic.co/packages/7.x/yum`) |
| ffmpeg, mediainfo | RPM Fusion free / EPEL. `kaltura-ffmpeg` and `kaltura-ffmpeg-aux` are bridge packages. |
| Sphinx 2.2.11 | built from the release tarball (`kaltura-sphinx`) |
| nginx 1.23.0 + vod/secure-token/rtmp/… | built from source (`kaltura-nginx`), linked against the RPM Fusion ffmpeg |

Configuration is done by `kaltura-config-all.sh` with an answers file (`doc/kaltura.template.ans`), not by debconf.

## Build and test with Vagrant

Requirements: VirtualBox, Vagrant and the `bento/rockylinux-9` box. The `generic/rocky9` box hangs `sshd` after its OpenSSL upgrade, so it is not used.

```bash
cd rpm/el9
vagrant up el9build    # builds the RPMs and repodata in rpm/el9/repo/
vagrant up el9aio      # VM at 192.168.56.30: installs from the local repo, configures, runs the sanity checks
vagrant ssh el9aio -c 'sudo bash /vagrant/rpm/el9/sanity.sh'
```

To rebuild only some packages: `vagrant ssh el9build -c 'bash /vagrant/rpm/el9/build.sh kaltura-base'`.

Default access on `el9aio`:

- Service URL: http://192.168.56.30
- Admin Console: `admin@kaltura.local` / `Adm1n#Video`
- MariaDB root password: `kaltura-root`

The test VM sets SELinux to permissive and disables firewalld, as the upstream RPM guide requires.

## Installing on your own server

Follow `rpm/el9/install-aio.sh`: repositories, MariaDB settings, the answers file and `kaltura-config-all.sh`. To use a CI build, point `KALTURA_REPO` at an extracted `kaltura-server-el9-repo.tar.gz` from a `kaltura-server/v*` release:

```bash
KALTURA_REPO=file:///srv/kaltura-el9 HOST_IP=<your ip> bash install-aio.sh
```

## EL9-specific fixes (also documented in the specs)

- **Sphinx.** The 2.2.1 googlecode source is gone, so the 2.2.11 release tarball is used.
- **php.yml.** `kaltura-base` ships `php.yml` without the `log_errors` key. Without this, symfony aborts every alpha request (KMC, playManifest) with "specifies key log_errors which cannot be overrided" (kaltura/server#9492).
- **python2.** The auto-dependency on `/usr/bin/python2` (from a developer utility) is excluded, and a prebuilt iOS demo library that breaks `brp-strip` is removed.
- **Legacy apps.** `kaltura-config-all.sh` skips the DWH, and `kaltura-db-config.sh` skips the legacy Flash KMC, when those packages are not installed.
- **Elastic populate.** The `kaltura-elastic-populate` init script removes a stale pid file. `config-all` configures Elasticsearch before the DB exists, so the first start crashes and leaves one behind.

## Limitations

Same as the Ubuntu packages: no Flash apps, no DWH/pentaho, no player bundler, no live/RTMP, no SSL, no cluster.
