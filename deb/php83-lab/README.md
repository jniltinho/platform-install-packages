# PHP 8.3 feasibility lab (Ubuntu 24.04)

This is **not a Kaltura PHP 8.3 installer**. It provisions only a clean, isolated
PHP 8.3 CLI/Apache environment and the candidate extension set from Ubuntu's
signed Noble repositories. No application compatibility is claimed.

```sh
cd deb/php83-lab
vagrant up php83
vagrant ssh php83
# Later, preserve the guest disk but power it off:
vagrant halt php83
```

- VM: `kaltura-php83-noble-lab`, Vagrant target `php83`.
- Private IP: `192.168.56.83` (reserve this address before starting).
- Box: `bento/ubuntu-24.04`, version `202510.26.0`; 4 CPUs / 8 GiB RAM.
- No shared host folders, copied production data, partner secrets or test media.
- Existing Noble `.20` remains PHP 7.4. Never run this bootstrap there.
- Do not install the released Kaltura DEBs here: they require PHP 7.4.
- Provisioning checks the OS and lab hostname, rejects existing Kaltura/MySQL
  state, and fails if the PHP minor version or required CLI/web modules differ.
- Apache's temporary runtime probe permits loopback clients only and is removed
  after the test. There is no persistent public `phpinfo()` page.
- Runtime/package/provider reports: `/var/lib/kaltura-php83-lab/` in the guest.
- Provisioning uses current signed Noble security updates, not a frozen apt
  snapshot. The recorded package versions identify each actual run.

Next: audit the checksum-pinned Kaltura archive, packaging overlays and clients;
create an isolated PHP 7.4 application baseline; run syntax/compatibility and
runtime probes, classify findings, and obtain the feasibility go/no-go decision.
Starting on Noble does not waive the proposal's eventual Ubuntu 26.04/EL9,
upgrade, rollback or release gates.

See [proposal](../../openspec/changes/migrate-kaltura-php83/proposal.md) and
[tasks](../../openspec/changes/migrate-kaltura-php83/tasks.md). Lab preparation
alone does not complete any broad compatibility task.
