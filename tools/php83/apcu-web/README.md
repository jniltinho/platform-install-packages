# Isolated kApcConf multi-request HTTP experiment

`run-lab.sh 74|83 original|aliases` runs the exact four Rigel configuration-cache
classes read-only from the packaged baseline in the existing isolated lab. The
runner creates a fresh standalone Apache parent with one persistent prefork
worker, a private network namespace and private temporary directories. No live
Apache, configuration, application tree, database or production cache is changed.

The endpoint is available only as `GET /probe` at `127.0.0.1:18383` within that
namespace. The Python client disables proxies and redirects and sends serial
requests with a fresh public 32-hex nonce. It requires exact original source
SHA-256 hashes, PHP 7.4 or 8.3 as selected, `apache2handler`, active APCu, exact
loaded INI and no scanned INI files. Results include PID and runtime identity;
separate HTTP requests demonstrate request-boundary persistence, **not**
cross-worker, cross-host or restart persistence.

## Cases

1. Reject a wrong nonce and an unknown action before cache access.
2. Store a version with `storeKey`, then its map with `store`.
3. A separate request loads the exact version and map, including the nonce.
4. A mismatched version must miss without destroying the valid map.
5. Delete the map; a subsequent request must miss.
6. Replace the version and map; a subsequent request must load the new data.

`original` defines no legacy functions: the APCu-only environment must reproduce
`storeKey = null`, `store = false`, and null reads/deletion. `aliases` installs
**test-only** `apc_fetch`, `apc_store`, and `apc_delete` forwarding to APCu, solely
to exercise this class. No counters, production adapter or application repair
is introduced. E_ALL diagnostics become exceptions and HTTP 500; the client
fails closed on status, schema, source, runtime or exact-value mismatch. No
normalization of false/null or boolean/integer values is allowed.

The synthetic `kEnvironment::get('cache_root_path')` supplies only a fresh
writable temporary directory. Full Kaltura bootstrap is not loaded. A preexisting
reload marker is rejected rather than testing application reload behavior.

## Interface

Server environment: `PHP83_HTTP_NONCE`, `PHP83_EXPECTED_MODE`,
`PHP83_CACHE_DIR` (existing writable directory ending in `/`). Client environment:
`PHP83_HTTP_NONCE`, `PHP83_EXPECTED_MODE`, `PHP83_EXPECTED_RUNTIME` (`74`/`83`),
`PHP83_EXPECTED_INI`. The shell runner supplies all variables; do not invoke the
endpoint on a public server. `client.py` writes one JSON report and exits nonzero
on failure. Source resides at `/audit/app`, fixtures at `/audit/tests`.

## Limits

This is HTTP-only synthetic configuration-cache evidence, not TLS, complete API,
application-reflection/object cache, cache refresh, old serialized-object,
concurrent worker, TTL, reload-marker, database, media or performance acceptance.
It does not repair or waive the previous CLI adapter counter failures. Passing
these cases does not justify integrating the aliases into the application,
changing RPM dependencies, selecting a production provider or publishing a
release. Claude/Grok/Cursor independent execution/review remains separately
recorded in the cycle evidence.
