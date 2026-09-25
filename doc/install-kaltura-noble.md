# Ubuntu Noble (24.04) Single-server All-In-One

Kaltura CE **Rigel-18.20.0** `.deb` packages for Ubuntu 24.04 (amd64). They are built and tested with Vagrant/VirtualBox from `deb/noble/`.

## Stack

| Component | Source |
|---|---|
| PHP 7.4 | `ondrej/php` PPA (Kaltura 18.20 does not run on PHP 8) |
| MariaDB 10.11 | Ubuntu |
| Elasticsearch 7.17 | Elastic apt repo (`artifacts.elastic.co/packages/7.x`) |
| ffmpeg 6.1, sphinxsearch 2.2.11 | Ubuntu, via the bridge packages `kaltura-ffmpeg`, `kaltura-ffmpeg-aux` and `kaltura-sphinx` |
| nginx 1.23.0 + vod/secure-token/akamai-token/rtmp/vts | built from source (`kaltura-nginx`) |

Packages: `kaltura-postinst`, `kaltura-base`, `kaltura-front`, `kaltura-batch`, `kaltura-db`, `kaltura-server`, `kaltura-ffmpeg`, `kaltura-ffmpeg-aux`, `kaltura-sphinx`, `kaltura-nginx`, `kaltura-elasticsearch`, `kaltura-kmcng`, `kaltura-html5lib`, `kaltura-html5lib3`, `kaltura-html5-studio`, `kaltura-html5-studio3`, `kaltura-html5-analytics`.

## Build and test with Vagrant

Requirements: VirtualBox, Vagrant and the `bento/ubuntu-24.04` box.

```bash
cd deb/noble
vagrant up build   # builds the .deb files and the apt index in deb/noble/repo/
vagrant up aio     # VM at 192.168.56.20: installs from the local repo, configures, runs the sanity checks
vagrant provision aio --provision-with shell   # re-runs the install (idempotent)
vagrant ssh aio -c 'sudo bash /vagrant/deb/noble/sanity.sh'
```

To rebuild only some packages: `vagrant ssh build -c 'bash /vagrant/deb/noble/build.sh kaltura-base kaltura-db'`.

Default access on the `aio` VM. You can override these with the environment variables in `install-aio.sh`.

| | |
|---|---|
| Service URL | http://192.168.56.20 |
| Admin Console | http://192.168.56.20/admin_console/ (`admin@kaltura.local` / `Adm1n#Video`) |
| KMC | http://192.168.56.20/index.php/kmcng/ |
| MariaDB root | `kaltura-root` |

The admin password must be 8 to 14 characters long and include a digit, a lowercase letter and a symbol. It **must not contain parts of the user's name or e-mail**, which is why `Kaltura1!` is rejected for `admin@kaltura.local`.

## Installing on your own server

Prebuilt packages are published in the GitHub release [`noble-deb-18.20.0-1`](https://github.com/jniltinho/platform-install-packages/releases/tag/noble-deb-18.20.0-1). The release is a flat apt repository, so it can be used directly:

```bash
echo "deb [trusted=yes] https://github.com/jniltinho/platform-install-packages/releases/download/noble-deb-18.20.0-1 ./" > /etc/apt/sources.list.d/kaltura.list
```

To build the packages yourself, use `vagrant up build` as above. The remaining steps are the same in both cases:

```bash
add-apt-repository -y multiverse
add-apt-repository -y ppa:ondrej/php
curl -fsSL https://artifacts.elastic.co/GPG-KEY-elasticsearch | gpg --dearmor -o /usr/share/keyrings/elastic.gpg
echo "deb [signed-by=/usr/share/keyrings/elastic.gpg] https://artifacts.elastic.co/packages/7.x/apt stable main" > /etc/apt/sources.list.d/elastic-7.x.list
apt-get update
```

Then follow `deb/noble/install-aio.sh`, or run it directly with `KALTURA_APT=https://github.com/jniltinho/platform-install-packages/releases/download/noble-deb-18.20.0-1 HOST_IP=<your ip> bash install-aio.sh`. It is the reference procedure for the MariaDB settings, the debconf answers and the install order. Order matters: `kaltura-db` needs the front and Sphinx to be up before it runs.

## Sources

The `kaltura/server` repository is gone from GitHub. The archive of tag `Rigel-18.20.0-rel` (commit `29cf4546`) is mirrored in release [`sources-rigel-18.20.0`](https://github.com/jniltinho/platform-install-packages/releases/tag/sources-rigel-18.20.0). The build verifies its SHA-256 against `KALTURA_CORE_SHA256` in `build/sources.rc`.

## Limitations

- Out of scope: Flash apps (KDP, KCW, legacy KMC…), DWH/pentaho, player v3/v7 through `playkit-bundler`, live/RTMP, SSL and clusters. The sources of the first three are no longer public.
- `kaltura-html5lib3` ships without the private plugins `kaltura-interactive-player` and `brand3d`. To include them, set `GITHUB_TOKEN`/`BITBUCKET_TOKEN` in `build/packager.rc`.
- The `ondrej/php` PPA is moving to `packages.sury.org`. If PHP 7.4 is dropped from the PPA, switch to the new repository.
