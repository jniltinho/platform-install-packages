# Actual exp3 ZIP: isolated SQL / Apache / TLS regression

This is partial T1-01/T1-02 evidence, **not application or release acceptance**.
The exact six-patch exp3 ZIP (`1c64edb5ff34308cedfcea3c7879187c21417b6bd1a8e083d70d580bedc985e3`)
was verified against all 15,183 extracted regular files before execution. The
hardened verifier rejects symlinks and unsafe archive paths; it does not validate
Unix permissions against archive modes.

## Executed matrix

| Source / PHP | Exit | Result |
| --- | --- | --- |
| Original / 7.4 | 0 | Reference HTTP + trusted HTTPS auth/session contracts |
| exp3 / 7.4 | 0 | Same normalized contracts |
| Original / 8.3 | 1 | Expected KalturaPDO query declaration fatal on first HTTP request |
| exp3 / 8.3 | 0 | Same normalized contracts |

Each positive row executes eleven normalized assertions per transport plus
rejection of an untrusted CA. Assertions cover normal/admin session creation,
GET/POST session retrieval and missing/malformed/expired/wrong-secret/escalation
rejection. There are 24 runtime observations per positive row (expired-token
creation adds a request). The failing original-8.3 control never reaches TLS.
Codex and Claude run independently and serially, each against its own database.

The real `api_v3/web/index.php`, bootstrap, SQL/PDO and dispatch run behind a
fixture router. Schema is synthetic and reset **per request**. This does not test
persistent session revocation, production secrets, full AIO installation, FPM,
cache backends, media processing or browser acceptance.

## Isolation and identities

The baseline Noble lab hosts native PHP 7.4 and a separately copied PHP 8.3.6
Apache bundle. This is not a separate-distro acceptance result. Apache uses
loopback HTTP and an ephemeral trusted CA with hostname verification; no TLS
verification bypass is used for the client tests. Existing SSH settings do not
pin host keys, so this is not production transport-hardening evidence.

Every collection creates a new `/tmp/kaltura-pdo-mysql.<random token>` and
matching `php83-exp3-api-<token>` service. The collector knows that identity
before startup, and its finally block stops only that service even on malformed
startup JSON, unexpected identity or startup timeout. Three mocked fault tests
cover those paths. Service lifetime is capped at 600 seconds. Data is retained
for diagnosis; service stop is verified independently of database deletion.
Before schema operations the router requires exact owned `@@datadir` identity.
Private networking, read-only source/runtime binds and inaccessible production
paths protect the existing application. No `.20` change occurred.

Reports include source/fixture/collector/imported-helper SHA256 identities,
normalized outputs, actual runtime observations and sanitized diagnostic
locations/counts. Unknown stdout is redacted and fails validation. Raw
application stderr/KS values are not persisted: only its SHA256 and sanitized
severity/path/line aggregates are retained. Do not replace this with raw logging.

## Diagnostics are NOT accepted exceptions

Candidate 8.3 still emits **41 severity/path/line groups, 1,767 events** in this
bounded matrix. These are not 41 unique defects. The largest group is
`vendor/propel/util/Criteria.php:1375` (694 events), followed by
`criteriaFilter.class.php:51` (132), `KalturaActionReflector.php:129` (74) and
`KalturaLog.php:122` (54). Original 7.4 emits six dateUtils events; exp3 7.4 emits
none in these rows. No diagnostic suppression or blanket casts were added.
`functional_checks_passed` deliberately distinguishes matched functional output
from `application_acceptance`, which remains false.

## Reproduction and review

From the migration worktree, with the existing approved isolated lab/stage:

```sh
# Stage these exact three files in the owned php-exp3-regression/api directory.
# Never point this collector at production or run concurrent VM writers.
python3 tools/php83/exp3-api/collect.py /path/to/new-sanitized-report.json
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tools/php83 -p 'test_*.py'
```

The collector refuses an existing output. Evidence is under
[`evidence/exp3-api/`](evidence/exp3-api/). Initial reports before collector
hardening and the initial faulty unit-test command selector are preserved under
`attempts/`. The selector incorrectly matched the hash-list command instead of
the startup command; it was corrected without weakening assertions.

Claude executed the real matrix and reviewed the collector. Grok timed out
(exit 124); OpenCode Muse Spark Free performed local tests/review as the explicit
fallback, not as Grok. Cursor's first attempt timed out; bounded retries executed
local tests/review. See machine-readable coordination results for exact outcomes.

No full-case checkbox is closed. Next: a minimal, separately tested repair for
the Criteria null-alias diagnostic; expand integrated framework/cache coverage
without treating these probes as complete API, distro or performance acceptance.

### Remaining evidence limits from independent review

The original 7.4 tree and copied 8.3 runtime bundle retain prior provenance but
are **not rehashed by this collector**; current matrix identity is strongest for
the actual exp3 source and fixtures. Runtime observations are not a replacement
for binary identity. Exceptions before report completion stop the known DB unit
but do not emit a structured partial result. `unknown` is accepted as inactive
because transient collected units disappear; neither that state nor successful
stop proves directory removal. Cleanup failure and arbitrary stdout/pass-logic
fault injection are not yet covered by the three new unit tests.

Reviewer prose is advisory: Claude's table described original-8.3 stdout as
matching baseline, but the actual JSON shows **empty stdout**, one runtime
observation and the expected fatal. The collector correctly uses it as a negative
control, not a successful functional comparison. During local review the new
unit-test selector was corrected; final frozen-source reruns supersede the
recorded initial failures. OpenCode's initial mixed old/new hash interpretation
was explicitly corrected by its final hash verification.
