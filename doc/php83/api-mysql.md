# Real API dispatch over isolated MariaDB

## Result

Real `DbManager` initialization, `KalturaPDO` connection, Propel permission queries
and `KalturaDispatcher::dispatch('system', 'getTime')` now complete on PHP 7.4
and PHP 8.3 in the bounded synthetic fixture. `system.getVersion`, deliberately
not granted to the anonymous role, is rejected with `SERVICE_FORBIDDEN` on both.
No authorization method, database peer, reflection or dispatcher is mocked.

The original PHP 8.3 tree fails while `DbManager::setConfig` reflects
`KalturaPDO`: its no-argument `query()` declaration is incompatible with PDO.
This is a distinct class from the previously investigated DebugPDO. The held
`KalturaPDO-query.patch` removes this fatal; both candidate stdout comparisons
match the unchanged 7.4 baseline. Original 8.3 failure is retained and asserted.

**This remains CLI integration evidence**, not HTTP/FPM/Apache, authenticated KS,
full install, tenant isolation, upload/worker/playback or performance acceptance.
The synthetic database is a six-table subset, not a complete Kaltura instance.

## Repair and preserved behavior

The patch changes `query()` to `query(...$args)`, forwards arguments directly to
`parent::query(...$args)` and recognizes named `query` for logging. No SQL values
are coerced or global PDO attributes changed. Constructor, prepared statements,
transaction handling and other methods are unchanged. Original code computes a
comment-prefixed SQL string for monitoring but forwards the original arguments;
this unrelated quirk is intentionally preserved, not silently repaired.

Four native-PDO controls on 7.4 and seven on 8.3 pass: associative/column fetches,
FETCH_CLASS constructor arguments, missing SQL, and 8.3 named/unknown-name cases.
Invalid-call results are compared **within** each runtime and recorded separately:
missing SQL returns false on this 7.4 build but throws ArgumentCountError on 8.3.
The first diagnostic attempt accidentally called fetchAll on false and observed
an unrelated Error; the final fixture explicitly records false without calling a
method on it. No cross-version equivalence of invalid-call diagnostics is claimed.

The candidate's missing-SQL path also removes the legacy undefined-index notice
through `?? null`; that diagnostic difference is not a global waiver. Remaining
PDO return-type, dynamic-property, null-argument and other deprecations are kept
in stderr. The earlier raw numeric JSON-contract issue remains unresolved.
Claude's review is advisory and saved; its suggestion of return-type suppression
was not applied. The patch remains outside the active ZIP pending broader tests.

## Synthetic data and isolation

- Real table definitions for partner, kuser, user_role, permission,
  permission_item and permission_to_permission_item are extracted byte-for-byte
  from pinned public deployment SQL. Provenance records source and block hashes.
- Synthetic records provide global partner 0 and an anonymous role granting only
  `system.getTime`; no users or real secrets/KS are present. The negative action
  verifies that the narrow grant does not permit every system action.
- Before each run, only `php83_api_probe` is recreated on the dedicated disposable
  server. Both the socket path and `@@datadir` are checked against the runner's
  exact expected disposable path before destructive setup SQL executes.
- The runner is guarded to `kaltura-php74-baseline`, uses a private network and
  AF_UNIX only, hides live application/default MySQL paths, and mounts source
  read-only with ephemeral cache/config tmpfs. It runs as vagrant (UID 1000) for
  socket authentication; the PHP fixture checks that UID and the tmpfs mounts.
- Both binaries execute on `.74` against the same MariaDB 10.11.14 probe server.
  PHP 8.3 executable/PDO modules are the prior verified copies from `.83`; posix
  and ctype modules were additionally copied and hashes matched to `.83`.
  Nothing is installed or selected as the system interpreter. This is not a
  claim of independent full-service `.83` acceptance.

The disposable server was stopped and the candidate KalturaPDO restored to its
original hash after collection. No `.20`, live lab DB/config, main, CI, release
asset or exp2 ZIP was changed.

## Reproduction

Use the existing disposable MariaDB lifecycle in `mysql-type-experiment.md`.
Sync the new runner, behavior/API fixture and SQL fixture to `.74`; ensure the
copied 8.3 posix/ctype modules match their `.83` origins. Apply only the
hash-verified held KalturaPDO patch to the candidate tree, then:

```sh
python3 tools/php83/patch-tests/collect-api-mysql.py /tmp/api-mysql.json
```

The runner reads the existing private `current-path` file, never a production
DSN. Restore the candidate file and stop `kaltura-pdo-mysql-probe` in cleanup.
Do not run this destructive fixture against any other database. Evidence in
`evidence/api-mysql/` includes comparisons, all diagnostics, source/runtime/schema
identities and restoration. Bootstrap-only and existing JSON regressions are
rerun separately with the database stopped.

Initial failures for missing pool settings, schema tables, role/permission and
partner rows were fixture setup gaps reproduced on 7.4, not source fixes. The
only application change in this experiment is the held KalturaPDO query patch.
Next: establish a configured synthetic HTTP application and authenticated API
fixtures; these successful direct-dispatch checks do not replace that gate.
