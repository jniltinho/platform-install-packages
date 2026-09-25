# Ubuntu 26.04 (resolute) Single-server All-In-One

For prebuilt packages, start with the [quick install guide](quick-install-ubuntu-26.04.md).

Kaltura CE **Rigel-18.20.0** `.deb` packages for Ubuntu 26.04 LTS (amd64). They use the same recipes as [Ubuntu 24.04](install-kaltura-noble.md); this page covers only what differs. They are built and tested with Vagrant/VirtualBox from `deb/ubuntu-26.04/`.

## Differences from noble

| Item | noble (24.04) | resolute (26.04) |
|---|---|---|
| PHP 7.4 | PPA `ondrej/php` | `packages.sury.org/php` (the PPA does not serve resolute) |
| ffmpeg (distro) | 6.1 | 8.0 |
| MariaDB | 10.11 | 11.8 (`/usr/bin/mysql` is still shipped) |
| PCRE for nginx | libpcre3 | libpcre2 (libpcre3 was removed) |
| gcc | 13 | 15 (C23 by default) |

`kaltura-nginx` needs two build changes on 26.04. Both are harmless on noble:

- **nginx-vod-module 1.33.** Version 1.30 uses the FFmpeg channel-layout API that was removed in FFmpeg 7.
- **`debian/ffmpeg-compat.h`.** It is force-included and maps `avcodec_close()`, which was removed in FFmpeg 8 (libavcodec 62), to `avcodec_free_context()`. The build also passes `-std=gnu17` because gcc 15 defaults to C23.

## Build and test with Vagrant

Requirements: VirtualBox, Vagrant and the `bento/ubuntu-26.04` box.

```bash
cd deb/ubuntu-26.04
vagrant up build2604   # builds the .deb files and the apt index in deb/ubuntu-26.04/repo/
vagrant up aio2604     # VM at 192.168.56.40: installs from the local repo, configures, runs the sanity checks
vagrant ssh aio2604 -c 'sudo bash /vagrant/deb/ubuntu-26.04/sanity.sh'
```

The VM names and IP differ from the noble VMs (`build`, `aio`, 192.168.56.20), so both environments can run side by side.

Default access on `aio2604`:

- Service URL: http://192.168.56.40
- Admin Console: `admin@kaltura.local` / `Adm1n#Video`
- MariaDB root password: `kaltura-root`

## Installing on your own server

```bash
add-apt-repository -y multiverse
curl -fsSL https://packages.sury.org/php/apt.gpg | gpg --dearmor -o /usr/share/keyrings/sury-php.gpg
echo "deb [signed-by=/usr/share/keyrings/sury-php.gpg] https://packages.sury.org/php/ resolute main" > /etc/apt/sources.list.d/sury-php.list
curl -fsSL https://artifacts.elastic.co/GPG-KEY-elasticsearch | gpg --dearmor -o /usr/share/keyrings/elastic.gpg
echo "deb [signed-by=/usr/share/keyrings/elastic.gpg] https://artifacts.elastic.co/packages/7.x/apt stable main" > /etc/apt/sources.list.d/elastic-7.x.list
echo "deb [trusted=yes] file:/path/to/repo ./" > /etc/apt/sources.list.d/kaltura.list
apt-get update
```

Then follow `deb/ubuntu-26.04/install-aio.sh`, or run it with `KALTURA_APT=<repo URL or file:path> HOST_IP=<your ip>`.

Packages built by CI are attached to the `kaltura-server/v*` releases as `kaltura-server-ubuntu-26.04-repo.tar.gz`. See `.github/workflows/kaltura-server-packages.yml`.

## Limitations

Same as noble: no Flash apps, no DWH/pentaho, no player bundler, no live/RTMP, no SSL, no cluster.
