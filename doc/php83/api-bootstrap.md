# API bootstrap and dispatch preflight

## Result and boundary

Real `api_v3/bootstrap.php` completes on PHP 7.4 and 8.3 using explicitly synthetic
configuration. The actual autoloader loads `KalturaFrontController`,
`KalturaDispatcher` and `SystemService`. Both candidate comparisons match original
7.4; no new application patch is needed for these operations. This is **CLI
bootstrap/class-loading evidence, not a working HTTP API**.

An anonymous call through the real dispatcher to `system.getTime` proceeds to
permission prefetch, then fails on both runtimes because datasource `propel` has
no configured connection. No mock replaces reflection, permission handling or
DB access; the failure remains a failed process, not an accepted test. A
configured synthetic database/application environment is now the next prerequisite
for this path. This common setup failure does not prove later SQL/API compatibility.

## Fixture and isolation

`tools/php83/patch-tests/api-bootstrap.php` supplies only synthetic server values,
UTC, disabled query/application cache flags, and a real Zend stderr logger with a
simple formatter. The API bootstrap, configuration reader, autoloader and classes
are real. No live configuration, credentials, KS, media or DB are copied.

The existing hostname-guarded unprivileged runner mounts new private tmpfs cache
and configuration directories for these API cases. The fixture checks its fixed
`/audit/app` root, UID 65534 and both tmpfs mounts before writing synthetic INIs.
The source payload remains read-only; socket creation stays denied, and live
`/opt/kaltura` remains inaccessible. No host service or cache is altered. These
fixtures are not HTTP SAPI or network acceptance and do not exercise the web
entrypoint's database initialization.

Initial setup attempts exposed a missing timezone and missing logger formatter
in the synthetic configuration, on both PHPs. Those fixture prerequisites were
supplied, not patched in application code. `dispatch-initial.json` records the
older formatter failure; `dispatch.json` is the current datasource failure.
Remaining memcache-configuration messages and PHP 8.3 deprecations are retained,
not waived or hidden. Exit zero from bootstrap alone does not clear diagnostics.

## Reproduction and evidence

Sync the versioned PHP fixture, behavior dispatcher and runner into each lab's
`/home/vagrant/php-patch-tests/`, then run from this worktree:

```sh
python3 tools/php83/patch-tests/collect.py /tmp/api-bootstrap.json --case api-bootstrap --mode standard
# Expected nonzero until a separate synthetic DB environment is configured:
python3 tools/php83/patch-tests/collect-api-dispatch.py /tmp/api-dispatch.json
python3 -m unittest discover -s tools/php83 -p 'test_*.py'
```

Reports under `evidence/api-bootstrap/` retain process outcomes, diagnostics and
current harness hashes. Two bootstrap comparisons and eight JSON regression
comparisons pass; 41 offline tests pass, including three checks that failed
dispatch collection cannot become a passing result. No held Registry, DebugPDO
or Symfony patch was applied during this experiment. The active exp2 ZIP and
`.20`, main, release artifacts and CI remain unchanged.

Graph generation `2026-09-25T12:19:00Z` reported ready. Exact entrypoint,
bootstrap, autoloader, dispatcher and configuration-reader paths were checked
for coverage; conclusions are bounded to source reads and executed operations.
No exhaustive application compatibility or authenticated API claim is made.
