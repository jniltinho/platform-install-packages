# Disposable PHP 8.3 provider/SAPI probes

**Not an installer for the host, not Kaltura acceptance.** Only run inside a
new disposable Docker container, with no host mounts, published ports, privileged
mode or host networking. The scripts additionally require `/.dockerenv`, root
and `PHP83_DISPOSABLE_CONTAINER=yes`. Do not set those on a live system.

Inputs are four public scripts: `common.sh`, `probe.php`, `ubuntu.sh`, `rocky.sh`.
No application, database, secrets or media are supplied. Run the two Ubuntu
versions and Rocky independently. They install provider packages into their
throwaway filesystems, start private loopback Apache or Apache→Unix-socket FPM,
and check CLI, GET, POST and rejection of invalid POST data. A fresh public
nonce prevents a stale response from counting as success. No TLS acceptance is
claimed by this HTTP-only provider fixture.

## Example: pinned Noble container

```sh
tar -cf /tmp/php83-provider-probes.tar -C tools/php83 provider-probes
docker run --rm -i --name php83-provider-noble-local \
  --cpus=1 --memory=1g --pids-limit=256 \
  -e PHP83_DISPOSABLE_CONTAINER=yes \
  ubuntu@sha256:008173c23f95b170204355c12626cb5a965d779a7e1283b09e9cffbb1bf33ca3 \
  bash -c 'mkdir /tmp/probe; tar -xf - -C /tmp/probe; exec bash /tmp/probe/provider-probes/ubuntu.sh' \
  < /tmp/php83-provider-probes.tar > /tmp/noble.log 2>&1
# Record the docker command exit status before running another command.
```

For Resolute, use the verified image digest
`ubuntu@sha256:da6fc2be547864451aa253836dd926da33623312df4a9a243e35dc877c378a78`
and a separate container name with `ubuntu.sh`. For Rocky use
`rockylinux@sha256:d7be1c094cc5845ee815d4632fe377514ee6ebcf8efaed6892889657e5ddaaa6`
and `rocky.sh`. Do not change suites to get an installation to succeed.
Remove **only your own named container** if the client is interrupted. Never
prune Docker or touch unrelated services. Network repositories can change;
archive package policy/version/signature evidence and exact script hashes.

## Trust and scope

- Noble uses image-configured Ubuntu repositories. Resolute adds exactly
  `https://packages.sury.org/php resolute main`, with `signed-by`. The HTTPS
  keyring DEB is hash-pinned before installation; updating its pin requires
  review. This is HTTPS bootstrap trust, not out-of-band key authentication.
- Remi's release RPM is checked with the explicitly pinned 2021 signing key,
  `rpmkeys --checksig` and `localpkg_gpgcheck=1`; dependency installs keep
  `gpgcheck=1`. EPEL/CRB are disposable-container-only prerequisites. The first
  attempted 2019 key correctly rejected this release RPM; checks were not waived.
- Package origins/signatures/policies and INI/module lists are captured. This
  probe does not programmatically prove a complete supported provider matrix or
  every package ABI constraint. Actual loaded module/function smoke is additional
  evidence, not permission to update production package dependencies.
- The module union includes package-declared extensions plus conservative
  diagnostics (including bcmath and CLI pcntl). It is not a complete application
  use inventory. APCu existence does **not** establish legacy APC compatibility;
  Rocky reports whether the legacy `php-pecl-apc` capability is provided.
- The endpoint throws on PHP warnings, rejects non-8.3 and wrong SAPI/missing
  modules, and runs no DB/SSH/LDAP/memcache network connections. Several smoke
  checks are callable/class availability, not backend service acceptance.

See [provider runtime evidence](../../../doc/php83/provider-runtime.md).
