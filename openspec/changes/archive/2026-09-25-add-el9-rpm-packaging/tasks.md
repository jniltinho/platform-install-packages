## 1. Rocky Linux 9

- [x] 1.1 EL9 branches in the specs (sphinx 2.2.11, ffmpeg bridges, nginx, server, base). Verify that `el9build` builds the full set.
- [x] 1.2 `rpm/el9/{Vagrantfile,build.sh,install-aio.sh,sanity.sh}` on `bento/rockylinux-9`.
- [x] 1.3 Fixes: php.yml, python2 auto-dependency, Mach-O strip, optional DWH and legacy KMC, stale elastic-populate pid file. Verify that `vagrant provision el9aio` passes sanity with 0 failures.
- [x] 1.4 Clean `vagrant destroy -f el9aio && vagrant up el9aio`. Verify that it exits 0 and sanity reports 0 failures.
- [x] 1.5 Write `doc/install-kaltura-rocky9.md` and add the README link.
