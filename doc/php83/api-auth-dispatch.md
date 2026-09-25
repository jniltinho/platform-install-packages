# Authenticated dispatcher comparison

Date: 2026-09-25. Phase-1 synthetic experiment; **not HTTP/SAPI acceptance**.

## Scope and result

The previous [direct session experiment](api-session.md) is now followed by
real `KalturaDispatcher::dispatch('session', 'get', ...)`: KS parsing,
permission-manager initialization, SQL roles/permissions, action reflection,
service initialization and `KalturaSessionInfo` result assertions. No auth or
permission implementation is mocked. The fixture creates a narrow
`SYNTHETIC_SESSION_READ` permission, granting session.get to synthetic
user/admin roles, plus system.ping to the admin role only. Anonymous permission remains limited to system.getTime.
Both partners 83001 and 83002 exist and are active; cross-partner denial is
therefore not merely a missing-partner result.

[Report](evidence/api-auth-dispatch/report.json): original PHP 7.4 and both
candidates return success and identical normalized stdout. Original PHP 8.3
reproduces the known KalturaPDO declaration fatal. Candidates use only the
previously held KalturaPDO/dateUtils repairs over exp2; **no new application
patch was required**.

| Check | Expected result (both runtimes) |
|---|---|
| User/admin session.get | Correct result class, partner, user and session type |
| Missing session | KalturaAPIException / SERVICE_FORBIDDEN |
| Expired session | kCoreException / INVALID_KS |
| Granted role requesting system.getVersion | KalturaAPIException / SERVICE_FORBIDDEN |
| Admin KS requesting another existing partner | KalturaAPIException / SERVICE_FORBIDDEN |
| Malformed KS | kCoreException / INVALID_KS |
| Valid admin request after each rejection | Correct session info, no poisoned context |

The guest checks exact error class/code, not merely any exception. The host
collector additionally compares against unchanged original 7.4 output. The
prerequisite direct-session assertions (tampering, user-secret escalation,
expiration, fields and duration-format comparison) still run, but their stdout
is buffered: this report compares dispatcher output only, not prerequisite
duration values; the separate session report covers those values.

## Runtime correction and provenance

The first original-7.4 attempt exposed a **harness missing extension**, not an
application incompatibility: request argument deserialization calls iconv.
The auth runner now loads each runtime's own matching iconv extension:

- 7.4 `/usr/lib/php/20190902/iconv.so` SHA256
  `074f0e8478ffbce8dd288f21cb3e9aef664d7df9b661477ab1ed252864b38dd5`.
- 8.3 `/usr/lib/php/20230831/iconv.so`, copied from isolated `.83`, SHA256
  `79ba2593b71ee8277b3a8e2a530c542f901129c78016b7a87d39fe4c2a50ea24`;
  destination hash on `.74` matches. No extension ABI mixing or system PHP
  replacement. Other runtime identities remain in the API/SQL report.

Graph project `kaltura-rigel-18.20.0-full` remains ready at generation
`2026-09-25T12:19:00Z`. Coverage checks for KalturaDispatcher, KalturaBaseService,
SessionService, kCurrentContext and kPermissionManager recorded no issues;
relevant source was read, without making an exhaustive graph claim.

## Reproduce and boundary

Use the disposable DB/runtime setup and finally cleanup documented in
[api-session.md](api-session.md). Copy `api-auth-dispatch.php` and
`run-api-auth-dispatch.sh` beside its prerequisites; add the matching iconv
module. Verify hashes and apply the two held patches to candidate only. Run:

```sh
python3 tools/php83/patch-tests/collect-api-auth-dispatch.py REPORT.json
```

The report records fixture identities, exit status, output and diagnostic
locations/counts, never KS-bearing stack arguments or SQL logs. Diagnostics
remain enabled; existing deprecations are **not waived** by functional success.
Both modified candidate source files were restored and compared to original;
the disposable DB was stopped. The 51 offline tests pass and the new
shell runner passes syntax validation.

HTTP routing/body parsing, front-controller error mapping, JSON serialization,
Apache/FPM, HTTPS, session.start through the dispatcher, cross-runtime token
exchange, media flows and the full three-distro acceptance matrix remain open.
This is one PHP process handling successive dispatches, not separate HTTP
requests. No task checkbox or release gate is complete. `.20`, main, published
packages and the experimental ZIP are unchanged.

## Review hardening

[Claude reviewed the fixture](evidence/api-auth-dispatch/claude-review.txt), not
its execution. The final rerun additionally proves distinct role resolution:
user KS cannot call system.ping; admin KS receives true. An explicit
system.getVersion permission/item exists but is assigned to neither role.
The expired token is separately asserted to return ks::EXPIRED before dispatch.
The missing-KS case explicitly names partner 83001. Remote fixture SHA256 values
are verified against local inputs before collection and included in the report.

Original/candidate nonzero exits already failed comparison; four new offline
tests cover that, output-contract changes and token-free diagnostic summaries.
Existing deprecations remain a migration gate, rather than being silently
accepted or misrepresented as a clean runtime. Same-process order and separate
HTTP request behavior remain limitations. All comparisons were rerun after the
review changes; cleanup was repeated.
