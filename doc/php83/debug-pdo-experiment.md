# DebugPDO signature experiment — held

Date: 2026-09-25. Scope: OpenSpec `migrate-kaltura-php83`, task 1.6
(partial). This is not application acceptance or a deployment artifact.

## Change and result

`patches/php83/held/DebugPDO-query.patch` changes only the declaration from
`query()` to `query($query = null, ...$fetchModeArgs)`. The original body,
argument forwarding, logging and query accounting remain unchanged.
Hashes are recorded in the adjacent JSON. It is **not** in the active manifest.

| Runtime/tree | Execution | Strict stdout parity with original 7.4 |
| --- | --- | --- |
| PHP 7.4.33 original | passes | baseline |
| PHP 7.4.33 candidate | passes | passes |
| PHP 8.3.6 original | fatal incompatible query declaration | fails |
| PHP 8.3.6 candidate | passes fixture execution | **fails** |

In this SQLite fixture, 7.4 returns selected numeric values as strings and
8.3 as integers. An independent native PDO `SELECT 1` control reproduces the
difference; DebugPDO matches native PDO strictly within each runtime. This
isolates a driver/runtime difference in this test, **not** a finding about the
production MySQL configuration. No normalization or application setting was
added to make the gate pass.

Coverage: default/associative/column/class fetches (including constructor
argument forwarding), custom DebugPDOStatement, prepared binding/execution,
query count and last-query text, rollback, exception-mode error and silent-mode
error. Logging is disabled through synthetic Propel configuration. Return-type
and `parent`-callable deprecations remain visible in captured stderr.

## Safety and reproduction

Only disposable `.74`/`.83` copies were patched. `php7.4-sqlite3` and
`php8.3-sqlite3` were downloaded via each lab's existing apt sources and extracted
with `dpkg-deb -x`; **not installed**, no INI/service changes. Package versions,
package/module hashes and tested candidate hashes are in
`evidence/debug-pdo/php74-inputs.txt` and `php83-inputs.txt`.

Place the extracted module at
`/home/vagrant/php-patch-tests/sqlite/extracted/usr/lib/php/<ABI>/pdo_sqlite.so`
(ABI 20190902 for 7.4, 20230831 for 8.3), copy the harness files, and apply the
held patch only to the candidate tree. The wrapper loads that module per
invocation and runs as nobody with a read-only tree, no sockets/private network
and SQLite `:memory:`. It does not load application configuration or credentials.

```bash
python3 tools/php83/patch-tests/collect.py /tmp/debug-pdo.json \
  --case debug-pdo --mode standard
# Exit 1 is expected: the PHP8.3 strict parity gate currently fails.
```

`behavior.json` includes outputs, diagnostics and fixture hashes. Its environment
records describe the standard PHP process; the extra SQLite module is loaded
only for `debug-pdo`, with provenance recorded separately. After collection,
DebugPDO in both candidate trees was restored from the original packaged copy,
leaving the exp2 JSON-only candidate state. The exp2 ZIP was not rebuilt.

## Reviews and next gates

Claude and Grok were asked to review the patch and initial fixture using their
CLIs with tools disabled. Their opinions are advisory, not test evidence. The
native-PDO control was added after submitting the review input.

Claude identified a possible named-argument loss: `fetchMode:` lands in the
variadic parameter but the old body forwards `func_get_args()`. This requires
an explicit PHP8-only test before any promotion. Also pending: explicit null
fetch mode, missing arguments, FETCH_INTO/PROPS_LATE, enabled logging, subclass
overrides, and real isolated MySQL tests. A stringify-fetches variant may be
useful diagnostically but must not replace the failing default comparison.

All 27 offline Python tests pass; all eight JSON-only differential comparisons
still pass (see `json-regression.json`). Neither result closes the migration's
broader gates. `.20`, main, releases and the active patch manifest are unchanged.
