[![License](https://img.shields.io/badge/license-AGPLv3-blue.svg)](http://www.gnu.org/licenses/agpl-3.0.html)
[![Kaltura server packages](https://github.com/jniltinho/platform-install-packages/actions/workflows/kaltura-server-packages.yml/badge.svg)](https://github.com/jniltinho/platform-install-packages/actions/workflows/kaltura-server-packages.yml)
[![Kaltura Console](https://github.com/jniltinho/platform-install-packages/actions/workflows/kaltura-console-release.yml/badge.svg)](https://github.com/jniltinho/platform-install-packages/actions/workflows/kaltura-console-release.yml)

# Kaltura Installation Packages Project

Native OS packages (`.deb` and `.rpm`) for the Kaltura Video Platform Community Edition.

This fork packages **Kaltura CE Rigel-18.20.0** for current distributions, as a **Single-server All-In-One** install. It also ships **Kaltura Console**, a new media console written in Go. GitHub Actions build every package, and each one is installed and tested in Vagrant VMs.

## Supported platforms

| Distribution | Format | PHP | Database | Guide |
|---|---|---|---|---|
| Ubuntu 24.04 (noble) | `.deb` | 7.4 (ondrej PPA) | MariaDB 10.11 | [install-kaltura-noble.md](doc/install-kaltura-noble.md) |
| Ubuntu 26.04 (resolute) | `.deb` | 7.4 (packages.sury.org) | MariaDB 11.8 | [install-kaltura-ubuntu-26.04.md](doc/install-kaltura-ubuntu-26.04.md) |
| Rocky Linux / AlmaLinux / RHEL 9 | `.rpm` | 7.4 (remi) | MariaDB 10.5 | [install-kaltura-rocky9.md](doc/install-kaltura-rocky9.md) |

All three use Elasticsearch 7.17, the distribution ffmpeg (through small bridge packages), Sphinx 2.2.11, and nginx 1.23.0 with nginx-vod-module 1.33.

## Releases

Prebuilt packages are on the [Releases page](https://github.com/jniltinho/platform-install-packages/releases):

| Tag | Contents |
|---|---|
| `kaltura-server/v*` | `kaltura-server-noble-repo.tar.gz`, `kaltura-server-ubuntu-26.04-repo.tar.gz`, `kaltura-server-el9-repo.tar.gz` (one local repository per distribution), plus `SHA256SUMS` |
| `kaltura-console/v*` | Kaltura Console binary, `.deb` and `.rpm` |
| `sources-rigel-18.20.0` | Mirror of the Kaltura server source archive. The upstream `kaltura/server` repository is gone from GitHub. |

## Quick start

Extract the repository tarball for your distribution, then run the All-In-One installer from a checkout of this repository:

```bash
# Ubuntu 24.04
mkdir -p /srv/kaltura && tar -C /srv/kaltura -xzf kaltura-server-noble-repo.tar.gz
KALTURA_APT=file:/srv/kaltura HOST_IP=<server ip> bash deb/noble/install-aio.sh

# Rocky Linux 9 (Kaltura does not support SELinux enforcing: set it to permissive first,
# or pass RELAX_HOST_SECURITY=1 to let the installer do it and stop firewalld)
mkdir -p /srv/kaltura && tar -C /srv/kaltura -xzf kaltura-server-el9-repo.tar.gz
KALTURA_REPO=file:///srv/kaltura HOST_IP=<server ip> bash rpm/el9/install-aio.sh
```

On Ubuntu 26.04, use `deb/ubuntu-26.04/install-aio.sh` in the same way. The installers:

1. add the PHP, Elasticsearch and ffmpeg repositories;
2. configure MariaDB;
3. answer the package questions (debconf, or the RPM answers file);
4. install in the required order;
5. start all services.

The distribution guides explain each step for a manual install. Run `sanity.sh` next to the installer to check the result: services, API, KMC, upload, transcoding and HLS playback.

For HTTPS on Ubuntu 24.04, add `SSL=1` (optionally with `SSL_CERT`/`SSL_KEY`). See [HTTPS, Let's Encrypt and the Kaltura Console at /console](doc/kaltura-ssl-and-console.md).

## Kaltura Console

[Kaltura Console](kaltura-console/README.md) is a single Go binary with an embedded Vue UI and local user management (SQLite or MariaDB). It talks directly to the Kaltura `api_v3` for upload, transcoding status, playback, and media edit and delete. It complements the KMC and the Admin Console; it does not replace them. It runs:

- behind the Kaltura Apache at `https://<host>/console` (see the [HTTPS guide](doc/kaltura-ssl-and-console.md));
- or standalone, over HTTP or HTTPS (its own or an auto-generated certificate), at the root or under a prefix.

## Build and test

Each target has a Vagrant setup that builds the packages in a clean VM and installs them in another:

| Target | Directory | VMs |
|---|---|---|
| Ubuntu 24.04 | `deb/noble/` | `build`, `aio` (192.168.56.20), `aiossl` (192.168.56.21, HTTPS) |
| Ubuntu 26.04 | `deb/ubuntu-26.04/` | `build2604`, `aio2604` (192.168.56.40) |
| Rocky Linux 9 | `rpm/el9/` | `el9build`, `el9aio` (192.168.56.30) |

```bash
cd deb/noble && vagrant up build && vagrant up aio
```

In GitHub Actions:
- [`kaltura-server-packages.yml`](.github/workflows/kaltura-server-packages.yml) builds the three distributions in containers and checks that `kaltura-server` resolves from the result, with PHP 7.4 and no PHP 8.
- A `kaltura-server/v*` tag publishes the repositories as a release.
- [`kaltura-console-release.yml`](.github/workflows/kaltura-console-release.yml) does the same for the console, on `kaltura-console/v*` tags.

Changes are specified with [OpenSpec](openspec/): the current specs are in `openspec/specs/`, and the completed proposals are in `openspec/changes/archive/`.

## Repository layout

| Path | Contents |
|---|---|
| `deb/<package>/debian` | Debian packaging of each Kaltura component |
| `deb/noble`, `deb/ubuntu-26.04` | Build scripts, installers, sanity tests and Vagrantfiles for Ubuntu |
| `RPM/SPECS`, `RPM/scripts` | RPM specs and post-install configuration scripts |
| `rpm/el9` | Build script, installer, sanity test and Vagrantfile for Rocky Linux 9 |
| `build/` | Source download and packaging helpers (`sources.rc` pins versions and checksums) |
| `kaltura-console/` | Kaltura Console (Go + Vue) |
| `doc/` | Guides; `doc/kaltura-api-noble.md` documents the API calls used for validation, and `doc/prints/` holds admin UI screenshots |
| `openspec/` | Specifications and change history |

## Limitations

Out of scope for these packages:

- Flash-based apps and the legacy KMC;
- DWH/Pentaho analytics;
- the player bundler;
- live streaming/RTMP;
- cluster deployments.

HTTPS is validated on Ubuntu 24.04. The Rocky Linux 9 HTTPS settings are documented but not yet tested in a VM.

## Documentation

* [Ubuntu 24.04 installation](doc/install-kaltura-noble.md)
* [Ubuntu 26.04 installation](doc/install-kaltura-ubuntu-26.04.md)
* [Rocky Linux 9 installation](doc/install-kaltura-rocky9.md)
* [HTTPS, Let's Encrypt and the Kaltura Console at /console](doc/kaltura-ssl-and-console.md)
* [nginx VOD over SSL](doc/nginx-ssl-config.md)
* [Kaltura API used by the validation](doc/kaltura-api-noble.md)
* [Kaltura Console](kaltura-console/README.md)
* [Required open ports](doc/kaltura-required-ports.md)
* [Frequently Asked Questions](doc/kaltura-packages-faq.md)

Upstream guides for older releases and distributions (not maintained in this fork):
* [RedHat based distros](doc/install-kaltura-redhat-based.md)
* [deb based distros (Debian 8, Ubuntu 14.04)](doc/install-kaltura-deb-based.md)
* [Ubuntu 16.04](doc/install-kaltura-xenial.md)
* [Ubuntu 20.04](doc/install-kaltura-focal.md)
* [Docker](doc/install-docker.md)
* [Cluster (RPM)](doc/rpm-cluster-deployment-instructions.md)
* [Cluster (deb)](doc/deb-cluster-deployment-instructions.md)
* [Chef (RPM)](doc/rpm-chef-cluster-deployment.md)
* [Platform monitoring](doc/platform-monitors.md)
* [Offline install from a local RPM repository](doc/deploy-local-rpm-repo-offline-install.md)

## License and Copyright Information
All code in this project is released under the [AGPLv3 license](http://www.gnu.org/licenses/agpl-3.0.html) unless a different license for a particular library is specified in the applicable library path.

Copyright © Kaltura Inc. All rights reserved.

Authors [@jessp01](https://github.com/jessp01), [@zoharbabin](https://github.com/zoharbabin) and many others.

Contributors: [@DBezemer](https://github.com/DBezemer), [@fugazi73](https://github.com/fugazi73), [@blackyboy](https://github.com/blackyboy), [@Ronileco](https://github.com/Ronileco), [@jpluijmers](https://github.com/jpluijmers), [@smartdrive](https://github.com/smartdrive), [@baiyou2014](https://github.com/baiyou2014), [@krarey](https://github.com/krarey), [@nzimas](https://github.com/nzimas), [@nshulakov](https://github.com/nshulakov), [@joerace](https://github.com/joerace), [@iddrew](https://github.com/iddrew), [@ironsizide](https://github.com/ironsizide), [@angober](https://github.com/angober), [@nviera777](https://github.com/nviera777), [@bnelson796](https://github.com/bnelson796), [@cschaub](https://github.com/cschaub), [@mobcdi](https://github.com/mobcdi), [@flipmcf](https://github.com/flipmcf), [@dudyk](https://github.com/dudyk), [@vadimtar](https://github.com/vadimtar), [@corematter](https://github.com/corematter), [@visomar](https://github.com/visomar), [@AquileaSFX](https://github.com/AquileaSFX), [@carise](https://github.com/carise), [@shojikajita](https://github.com/shojikajita), [@suhastnex](https://github.com/suhastnex), [@ElGabbu](https://github.com/ElGabbu), [@OriHoch](https://github.com/OriHoch), [@tan-tan-kanarek](https://github.com/tan-tan-kanarek), [@kobimichaeli](https://github.com/kobimichaeli), [@leosuncin](https://github.com/leosuncin), [@wzur](https://github.com/wzur)

Rigel-18.20.0 packaging for Ubuntu 24.04/26.04 and Rocky Linux 9, and the Kaltura Console: [@jniltinho](https://github.com/jniltinho).
