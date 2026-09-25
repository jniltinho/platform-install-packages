# noble-deb-build Specification

## Purpose
Ensure the Kaltura CE Rigel-18.20.0 `.deb` packages for Ubuntu 24.04 (noble) can be built repeatably on a clean VM, from publicly resolvable sources.

## Requirements

### Requirement: Repeatable build on a clean VM
The build SHALL produce every `.deb` of the All-In-One set on a clean Ubuntu 24.04 VM, using the `bento/ubuntu-24.04` box pinned in the Vagrantfile. It SHALL run from a single command with no manual steps.

"Repeatable" means functional repeatability: two clean builds produce the same set of packages and versions. It does not mean bit-for-bit reproducibility.

The All-In-One set is:
- core: `kaltura-postinst`, `kaltura-base`, `kaltura-front`, `kaltura-batch`, `kaltura-db`, `kaltura-server`;
- media and search: `kaltura-ffmpeg`, `kaltura-ffmpeg-aux`, `kaltura-sphinx`, `kaltura-nginx`, `kaltura-elasticsearch`;
- web apps: `kaltura-kmcng`, `kaltura-html5lib`, `kaltura-html5lib3`, `kaltura-html5-studio`, `kaltura-html5-studio3`, `kaltura-html5-analytics`.

#### Scenario: Full build
- **WHEN** the operator runs `vagrant up build` in `deb/noble/`
- **THEN** provisioning exits with code 0
- **AND** `deb/noble/repo/` contains a `.deb` for every package of the All-In-One set

#### Scenario: A package failure stops the build
- **WHEN** building any package of the set fails
- **THEN** the build exits non-zero and reports which package failed

### Requirement: Versions aligned with RPM 18.20.0
The core packages (`kaltura-base`, `kaltura-front`, `kaltura-batch`, `kaltura-db`, `kaltura-server`) SHALL be versioned `18.20.0`. They SHALL ship the Kaltura server code from commit `29cf45469c1e210498087942f5b76b5c706e4cda`, which is tag `Rigel-18.20.0-rel` (its `VERSION.txt` reads `Rigel-18.20.0`).

#### Scenario: Core version
- **WHEN** `dpkg-deb -f kaltura-base_*.deb Version` is inspected
- **THEN** the value starts with `18.20.0`

### Requirement: Resolvable sources
Every source the build uses SHALL be downloadable from a public URL. When the original location of a source no longer exists, its URL SHALL be permanently replaced by a mirror the project controls, published together with its SHA-256. The mirror is a GitHub Release asset of this repository. There is no build-time fallback: each source has exactly one URL.

#### Scenario: Mirrored source
- **WHEN** the build downloads the server code
- **THEN** it uses the project mirror URL
- **AND** the SHA-256 of the downloaded file matches the published one, otherwise the build fails

### Requirement: Local apt repository
The build SHALL publish the resulting `.deb` files as an apt repository usable via `deb [trusted=yes] file:<dir> ./`.

#### Scenario: Repository index
- **WHEN** the build finishes
- **THEN** `deb/noble/repo/Packages.gz` exists and lists every built package

### Requirement: Package quality
Every built `.deb` SHALL install on Ubuntu 24.04 without unmet dependencies, using only these repositories:
- the distro repositories (main, universe and multiverse);
- the `ondrej/php` PPA;
- the Elastic 7.x apt repository (version 7.17);
- the local repository.

Installing the set SHALL NOT pull any PHP version other than 7.4.

#### Scenario: Dependency resolution
- **WHEN** `apt-get install --simulate kaltura-server` runs with those repositories configured
- **THEN** apt resolves every dependency without errors
- **AND** no `php8.*` package is selected
