# exp5 isolated artifact regression

Revision-pinned follow-up to exp4. See `doc/php83/exp5-null-batch.md` for identities,
results and remaining gates. Original and earlier candidates must be preserved.

`stage.sh 74` / `stage.sh 83` create a new stage and refuse an existing directory.
They transfer the source ZIP, unchanged API fixtures and exp5 CLI runners. The
first baseline74 extraction printed a stale EXP4 label; SHA/content checks were
for exp5 throughout. The label was fixed before staging83; no tested source changed.

The extra null-probe requires separate staging in the new exp5 directory:

```sh
# Only with these existing approved isolated lab aliases/configs:
ssh -T -F /tmp/kaltura-php74-ssh.conf baseline74 'mkdir /home/vagrant/php-exp5-regression/null-probe'
scp -F /tmp/kaltura-php74-ssh.conf tools/php83/null-probe/{probe.php,run.sh,dependencies.php,run-dependencies.sh} baseline74:/home/vagrant/php-exp5-regression/null-probe/
ssh -T -F /tmp/kaltura-php83-ssh.conf php83 'mkdir /home/vagrant/php-exp5-regression/null-probe'
scp -F /tmp/kaltura-php83-ssh.conf tools/php83/null-probe/{probe.php,run.sh} php83:/home/vagrant/php-exp5-regression/null-probe/
```

Collectors refuse existing output reports. API and dependency SQL collectors
must run serially with one baseline74 writer. Their private synthetic DB service
is stopped afterward; datadirs remain for diagnosis. Never use the legacy
`current-path` DB service or an installed database for these tests.

The class-only probe uses private temporary config/cache and no DB or networking;
it saves synthetic bootstrap diagnostics and fake input values only. Do not
introduce real credentials/KS or live user data into it. API/SQL collectors keep
only sanitized diagnostics and stderr hashes. This remains lab-only evidence.
