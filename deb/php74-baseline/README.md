# Isolated PHP 7.4 reference

Fresh Ubuntu 24.04 at `192.168.56.74`, hostname `kaltura-php74-baseline`,
4 vCPU / 8 GiB RAM, same pinned box as the PHP 8.3 lab. No shared host mounts,
production database, credentials or user media. Run `vagrant up baseline74` in
this directory. The bootstrap refuses an existing application/database and is
not a recovery or reprovisioning script.

It downloads the checksum-pinned published Noble server repository and installer
and installs the original PHP 7.4 AIO, not candidate PHP 8.3 packages. Credentials
are random and stored only in `/root/kaltura-baseline-private/` in the guest.
Never copy those files into git or reports. `.20` is blocked by a guest OUTPUT
rule during bootstrap; that transient rule must be restored after reboot before
any testing (do not treat it as persistent network isolation).

Provisioning verifies basic services/API only. It does not claim full baseline,
HTTPS, browser, upload, timing or recovery acceptance. The synthetic workload
protocol in the migration design must be completed before task 1.2 is checked.

## Guarded HTTP smoke test

From the migration worktree on the host, after successful provisioning:

```sh
git show kaltura-server/v18.20.0-1:deb/noble/sanity.sh > /tmp/php74-baseline-sanity.sh
cd deb/php74-baseline
vagrant ssh-config baseline74 > /tmp/kaltura-php74-ssh.conf
chmod 600 /tmp/kaltura-php74-ssh.conf
scp -F /tmp/kaltura-php74-ssh.conf /tmp/php74-baseline-sanity.sh smoke.sh baseline74:/tmp/
ssh -F /tmp/kaltura-php74-ssh.conf baseline74 'sudo bash /tmp/smoke.sh'
```

The wrapper checks the script hash and guest identity and temporarily blocks
new outbound connections except loopback/`.74`. It creates synthetic partner
and media data in this lab. It restores its temporary firewall chain on exit;
never run this wrapper on an arbitrary host. These are functional smoke checks,
not the full repeated performance, HTTPS, browser or recovery matrix.
