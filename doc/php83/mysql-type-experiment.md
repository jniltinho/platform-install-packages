# Isolated PDO MySQL type experiment

Date: 2026-09-25. Experimental v2 remains held. No application configuration,
database, published artifact, main branch or `.20` change was made.

## Design and provenance

A separate MariaDB 10.11.14 process ran on the synthetic `.74` baseline VM, with
a fresh `/tmp/kaltura-pdo-mysql.*` datadir, `--no-defaults`, `--skip-networking`,
AF_UNIX-only sockets and a ten-minute systemd runtime limit. Its socket is not
the installed application's socket. Bootstrap used socket authentication for
the lab OS user `vagrant`; no password, production credentials or application
database was read. Queries select synthetic literals only; no fixture table
or application schema is needed.

Both PHP versions ran against **the same disposable database on `.74`**. The
PHP8.3 executable and three modules were copied from `.83`, not installed and
not selected as the system interpreter. Tests use `-n` and explicit matching
mysqlnd/PDO/pdo_mysql modules. This is a paired driver experiment, not the full
`.83` SAPI or application acceptance suite. The copied binary uses `.74` system
libraries, recorded by ldd, rather than proving every `.83` library identical.

Input hashes and provenance are under `evidence/debug-pdo/mysql-types/`:
`runtime-inputs.txt`, `origin83-hashes.txt`, `behavior.json`, `cleanup.txt`.
The PHP8.3 executable/module hashes match their origin. The source candidate
is the unchanged held `DebugPDO-query-v2` output. Diagnostics are retained.

## Results

Tests cover direct and prepared SELECTs, integer parameter binding, integer,
DECIMAL, floating-point, text and NULL results. Each runtime explicitly tests
both values of emulate-prepares and stringify-fetches; no default is inferred.

| Emulated prepares | Stringify fetches | Patched 8.3 matches original 7.4 fixture |
| --- | --- | --- |
| false | false | yes |
| false | true | yes |
| true | false | **no: integer/float values change from strings to numbers** |
| true | true | yes |

All four original/patched 7.4 result matrices match. Within each exercised
runtime/configuration, DebugPDO matches native PDO exactly. Original 8.3 still
fails on the incompatible query declaration; patched 8.3 executes the matrix.
DECIMAL remains a string and NULL remains null in the recorded rows.

Thus a driver/runtime type difference also occurs with pdo_mysql in this
synthetic MariaDB test. It is not solely a SQLite observation. It does **not**
justify changing emulate-prepares or stringify-fetches globally: effective
application connection attributes, ORM hydration, strict comparisons and API
JSON contracts still need testing. The default application contract is not
proven by selecting the passing matrix rows.

## Reproduction outline (disposable `.74` only)

Copy `.83`'s `/usr/bin/php8.3` and `/usr/lib/php/20230831/{pdo,mysqlnd,pdo_mysql}.so`
to `/home/vagrant/php-mysql-probe/runtime83/`, verify the recorded hashes, and
copy `mysql-types.php` / `run-mysql-types.sh` to the existing lab harness folder.
Make the copied executable executable. Apply held v2 to the candidate only.

```bash
# On kaltura-php74-baseline only; never point these commands at an existing DB.
d=$(mktemp -d /tmp/kaltura-pdo-mysql.XXXXXXXX)
mariadb-install-db --no-defaults --datadir="$d/data" \
  --auth-root-authentication-method=socket --auth-root-socket-user=vagrant \
  --skip-test-db > "$d/bootstrap.log" 2>&1
sudo systemd-run --quiet --unit=kaltura-pdo-mysql-probe \
  -p User=vagrant -p Group=vagrant -p PrivateNetwork=yes \
  -p RestrictAddressFamilies=AF_UNIX -p ProtectSystem=strict \
  -p ReadWritePaths="$d" -p MemoryMax=1G -p RuntimeMaxSec=600 \
  /usr/sbin/mariadbd --no-defaults --datadir="$d/data" --tmpdir="$d" \
  --socket="$d/mysql.sock" --skip-networking --pid-file="$d/server.pid" \
  --log-error="$d/server.log"
# Wait for readiness; wrapper refuses a missing socket or unexpected path.
bash /home/vagrant/php-patch-tests/run-mysql-types.sh 74 original "$d"
bash /home/vagrant/php-patch-tests/run-mysql-types.sh 74 candidate "$d"
bash /home/vagrant/php-patch-tests/run-mysql-types.sh 83 original "$d" # expected fatal
bash /home/vagrant/php-patch-tests/run-mysql-types.sh 83 candidate "$d"
sudo systemctl stop kaltura-pdo-mysql-probe
```

The wrapper runs with a private network, AF_UNIX only, read-only binds and denies
the application tree, installed database directory/socket and root home. The
initial bootstrap attempt needed an explicit temporary directory inside the
writable probe directory; this was fixed without widening filesystem access.
The final report reflects successful PHP execution, not the earlier wrapper
failure to resolve the bind-mounted executable before entering the namespace.

After collection the dedicated server was stopped and candidate DebugPDO was
restored to its original hash. Synthetic scratch data remains in the private
temporary directory for inspection; it is not shipped in any ZIP.

## Outstanding review

Grok's v2 review arrived and is retained in `evidence/debug-pdo/v2/grok-review.txt`.
It identifies another untested boundary: naming `fetchMode:` without supplying
the required SQL query can inject the override's optional null default rather
than producing native PDO's missing-argument error. Reproduce this before any
promotion. No review or successful matrix cell closes the migration gate.
