# Loopback HTTP front-controller comparison

Date: 2026-09-25. Bounded phase-1 evidence, **not production web acceptance**.

## Executed path and results

A PHP `cli-server` process and Python HTTP client share a private systemd
network namespace. The server binds only `127.0.0.1:18383`; the client hardcodes
that address, uses no DNS/proxy discovery and rejects redirects. AF_INET is
allowed only inside that isolated namespace; the existing disposable MariaDB
remains AF_UNIX-only. The source trees are read-only, configuration/cache are
verified private tmpfs, and the existing exact datadir guard runs before any
DB reset. The router rejects paths other than `/probe` and non-loopback peers.

The **test adapter**, not `api_v3/web/index.php`, initializes the synthetic DB
and calls real `KalturaFrontController::run()`. That covers request parameter
parsing, dispatcher/session service, KS, permission queries, exception mapping,
JSON serialization and HTTP response headers. The fixture grants session.start
to the anonymous role and session.get to synthetic user/admin roles. It does
not replace application auth, dispatcher or serializer implementations.

[Report](evidence/api-http/report.json): original PHP 7.4 and candidates 7.4/8.3
have matching successful output. Original 8.3 still reproduces the held PDO
signature failure. Candidates retain the same held KalturaPDO/dateUtils repairs
over exp2; there is no new application patch.

- Session.start over form-encoded POST returns a nonempty KS for user/admin.
- Session.get over GET and POST returns KalturaSessionInfo with matching
  partner, user, session type and bounded expiry.
- Exact JSON types preserve the observed original 7.4 contract: partnerId,
  sessionType and expiry are **strings**, not integers. The client asserts
  these types; it does not normalize them to hide runtime differences.
- Missing KS returns SERVICE_FORBIDDEN; malformed/expired KS returns INVALID_KS.
  The expired response must additionally identify EXPIRED in its message.
- Wrong secret and user-secret-to-admin escalation return START_SESSION_ERROR.
- All exercised API results, including API errors, have HTTP 200 and a JSON
  content type, matching the original fixture behavior. Redirects or other
  transport status codes fail the test.
- Each response asserts the expected PHP minor via lab-only X-Probe-PHP and
  X-Probe-SAPI=cli-server headers. Tokens and error messages are not retained
  in committed evidence.

## Diagnostics are still an open migration gate

The first 8.3 attempt executed the action but emitted a dynamic-property
warning from the front-controller constructor before headers. That corrupted
HTTP content type. The adapter now explicitly uses E_ALL, display_errors=0,
log_errors=1 and error_log=/dev/stderr, and asserts the reporting/display/log
settings after bootstrap. This routes diagnostics away from the JSON body;
it does **not fix, suppress via error_reporting, or accept** the warnings.
The collector retains native and application-handler diagnostic locations and
counts. Passing functional assertions is separate from a clean runtime gate.

Full server logs can contain synthetic secrets/KS because the real application
logs request parameters. They pass only through the transient collector's
memory; committed evidence contains location/count summaries and whole-log
hashes, not raw SQL, stack arguments or tokens. The server's private temporary
log is removed by the cleanup trap.

## Fixture limitations and review

The schema is recreated **for every HTTP request**. This tests separate request
process state with deterministic synthetic secrets; it does not establish
persistence, revocation, concurrency or production configuration correctness.
The server is single-worker (`PHP_CLI_SERVER_WORKERS` is unset). APC/APCu must
be absent; application caching is disabled. The private filesystem cache can
retain autoload/reflection/config metadata between requests, not an assertion
of cache-enabled role/permission behavior. Seed/table count assertions run
before the front controller.

[Claude's advisory review](evidence/api-http/claude-review.txt) motivated the
runtime headers, diagnostic-setting assertions, expiry-reason assertion,
single-worker enforcement and seed checks. Diagnostic capture and verified
tmpfs mounts were already in place. Review is not runtime approval.

This adapter does not exercise production web/index.php activation checks or
response-cache lifecycle, Apache/FPM, trusted HTTPS, cross-partner HTTP,
media/upload/worker paths or full installation. No broad OpenSpec checkbox is
complete and no release gate is waived.

## Reproduction and cleanup

Start the disposable DB and apply the two held patches to candidate only as
in [api-session.md](api-session.md). Copy `api-bootstrap.php`, the existing SQL
fixtures, and these files to `/home/vagrant/php-patch-tests/` on `.74`:
`api-http-router.php`, `api-http-client.py`, `api-http-inner.sh`, `run-api-http.sh`.
Use the matching runtime/iconv setup from [api-auth-dispatch.md](api-auth-dispatch.md).

```sh
python3 tools/php83/patch-tests/collect-api-http.py REPORT.json
python3 -m unittest discover -s tools/php83 -p 'test_*.py'
```

The collector verifies remote fixture hashes before execution. Source runtime
and held-patch identities remain those recorded by the prior experiments.
Always restore and compare candidate KalturaPDO/dateUtils from original and
stop kaltura-pdo-mysql-probe in cleanup. Both were done after the final run;
the HTTP service exits with its namespace and no public listener remains.

56 offline tests pass, including fixed loopback targeting, GET encoding,
redirect rejection, content type and safe diagnostic summaries; both shell
scripts pass bash syntax checks. [Regression comparisons](evidence/api-http/regressions.json)
confirm the earlier direct-session and authenticated-dispatch fixtures still
match original 7.4 after adding the HTTP-only bootstrap branch. Historical
reports remain historical, with their own harness hashes.

`.20`, main, production package/CI paths, releases and exp2 ZIP are unchanged.
