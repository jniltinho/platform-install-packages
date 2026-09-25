# Real bootstrap PDO boolean probe

This is a **synthetic integration test, not application acceptance**. It runs
PHP 8.3 against immutable exp8 and exp9 sources on the disposable baseline74 VM.
The existing API bootstrap guards the private MariaDB datadir before recreating
`php83_api_probe`. Never point this harness at a shared SQL server.

The 23 strict cases per artifact cover actual `KalturaPDO`/`KalturaStatement`,
custom preparation-cache setters and identity, supported/unsupported native
attributes, integer binding and input-array writes, native/wrapped silent failure
and exceptions, and dry-run INSERT/SELECT with actual Kaltura comment prefixes.
Exp8 null results deliberately differ from exp9 bool results. All other expected
case values are identical. Logging, monitor and query/API cache classes are real
artifact classes, not stubs; their source hashes are checked against the ZIP.
External monitoring/cache services are not configured or claimed tested.

The runner allows only baseline74, the two selected source trees and a guarded
owned Unix socket. Source/config isolation uses systemd read-only binds and
private tmpfs, network and devices. It retains the owned datadir but stops its
unit in `finally`. Full extracted-source verification is repeated after execution.
The collector refuses prior output paths and accepts only exact case values,
known fields and verified source identities. It stores stderr hashes and diagnostic
locations/counts, never raw SQL/application logs. Warnings are not suppressed.
An exception during validation/SSH can stop before writing the final report;
absence of a report is not a pass. SSH host-key policy and copied-runtime
provenance are inherited from the earlier lab, not strengthened by this probe.

Run only after obtaining the coordinator's **exclusive baseline74 ownership**:

```bash
ssh -F /tmp/kaltura-php74-ssh.conf baseline74 \
  'mkdir /home/vagrant/php-pdo-bootstrap'
scp -F /tmp/kaltura-php74-ssh.conf tools/php83/pdo-bootstrap/{probe.php,run.sh} \
  baseline74:/home/vagrant/php-pdo-bootstrap/
python3 tools/php83/pdo-bootstrap/collect.py NEW_REPORT.json
```

The exp8/exp9 stages must already exist, including exp9's unchanged bootstrap
and permission schema. Do not overwrite a previous staging directory silently.
Local positive, negative and static regression tests (no SQL/SSH):

```bash
python3 tools/php83/pdo-bootstrap/test_collect.py
```

Remaining gaps include ERRMODE_WARNING, default/null bindings, emulation off,
custom cache values other than bool, unusual whitespace/comments, persistent
sessions, external monitoring/cache behavior, concurrent callers, all other PDO
return contracts and full application workflows. Passing this probe does not
close those gates or authorize packages, release, main merge or production work.
