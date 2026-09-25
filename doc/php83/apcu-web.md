# Original configuration cache across Apache requests

2026-09-25 — partial T1-03/5.9 and T4-01/5.16 evidence, not application acceptance.
The previous [counter experiment](apcu-cache.md) remains rejected; this does not
repair it or approve a production compatibility shim.

## Executed matrix

| Original runtime | APCu | Mode | Result | Independent executor |
|---|---|---|---|---|
| PHP 7.4.33 | 5.1.28 | Original kApcConf | PASS, disabled-cache control | Claude |
| PHP 7.4.33 | 5.1.28 | Three fixture-only aliases | PASS, serial request persistence | Claude |
| PHP 8.3.6 | 5.1.22 | Original kApcConf | PASS, disabled-cache control | Cursor |
| PHP 8.3.6 | 5.1.22 | Three fixture-only aliases | PASS, serial request persistence | Cursor |

Codex ran all four rows first. Independent reruns use fresh Apache parents and
fresh nonces. This is **four logical rows**, not eight different test cases.
All rows exited zero; stderr contained only Apache configuration `Syntax OK`.
Each row has ten responses: rejected nonce (403), rejected phase (400), then
store, read, version mismatch, read after mismatch, delete, miss, replace and
read-new. The eight successful requests have one stable worker PID and exact
runtime/source/INI identities.

In original mode, APCu is enabled but legacy `apc_fetch` is absent: stores do not
persist and reads return null. This reproduces the disabled path under the
**explicit minimal test INI** on both versions. It is not proof of the deployed
baseline application's complete web configuration or bootstrap.

With only test-local fetch/store/delete aliases, real APCu preserves the nonce,
version and typed nested payload across separate requests. A wrong version
returns null without destroying the valid map; deletion produces a miss; a new
version stores and reads revision 2. False/null and booleans/integers are not
normalized. No application source was edited and no alias was installed.

## Exact scope and safeguards

The endpoint loads unchanged `kApcConf`, `kBaseConfCache`, `kMapCacheInterface`
and `kKeyCacheInterface` from the packaged application, with all four original
SHA256 identities checked by the client. `kEnvironment` is a **synthetic stub**
providing only a fresh temporary cache directory; full Kaltura bootstrap is not
loaded. No configuration fallback layer or reflection consumer is substituted
for these four original classes, but those broader paths remain untested.

Each runner selects only its existing synthetic lab through fixed loopback SSH
ports and a hostname guard. A transient systemd service runs an unprivileged
standalone Apache inside private network/mount/tmp namespaces with read-only
application files, no production app or DB paths, no privilege escalation,
256 MiB memory and a 60-second limit. The installed Apache service/configuration
is untouched. The private listener is only 127.0.0.1:18383; client proxy and
redirect handling fail closed. Cache keys and the global version key exist only
inside that fresh Apache parent. Cleanup removes owned processes/directories.

The test deliberately uses one persistent prefork worker, APCu plus required
JSON support, no scanned INI files, and an exact temporary INI path. This is
not a full-extension SAPI acceptance or the production configuration. HTTP only;
no TLS, FPM, multi-worker sharing/concurrency, restart/TTL/reload-marker behavior,
old serialized application objects, performance or whole-service claims.
Existing laboratory SSH host keys are not pinned; loopback/hostname checks are
not a substitute for production transport authentication.

## Reproduction and review

```sh
tools/php83/apcu-web/run-lab.sh 74 original
tools/php83/apcu-web/run-lab.sh 74 aliases
tools/php83/apcu-web/run-lab.sh 83 original
tools/php83/apcu-web/run-lab.sh 83 aliases
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tools/php83 -p 'test_*.py'
```

[Fixture interface](../../tools/php83/apcu-web/README.md),
[evidence](evidence/apcu-web/result.json). Per-command nanosecond durations are
retained for operational accounting, **not a performance comparison**.

Claude and Cursor reviewed the harness and independently reran their matrix
rows. Grok timed out at 120 seconds (exit 124, no final JSON), so its attempt is
not credited as execution. Authorized OpenCode Muse Spark Free provides the
fallback review/local-suite role; see its actual terminal outcome in the record.
Ten new client unit tests include malformed identity/schema, missing persistence,
PID drift, booleans versus integers, duplicate JSON and redirect rejection.
They use mocked responses and are **not** ten new application runtime tests.

## Next integration step

Move existing demonstrated JSON/PDO/date/parser repairs into a separately
identified six-patch **exp3 experiment**, preserving exp2 and original artifacts.
Test the built archive rather than ad-hoc patched files. Cache activation remains
separate: counter semantics, bootstrap placement, actual configuration/reflection
consumers, management/opcode paths and concurrency still need decisions/tests.
None of these results close the original acceptance tasks or authorize packaging,
release, or `.20` cutover.
