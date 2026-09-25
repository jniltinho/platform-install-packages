# Real web entrypoint, Apache and trusted HTTPS

Date: 2026-09-25. Synthetic phase-1 experiment, **not full installed AIO acceptance**.

## What changed from the previous HTTP test

The new `api-web-router.php` prepares only native PDO synthetic data and private
configuration, then requires the **unmodified** `api_v3/web/index.php` without
preloading any Kaltura class/bootstrap. That entrypoint now executes its own
response-cache check, bootstrap, DbManager initialization from db.ini,
ActKeyUtils call, front controller, monitoring and response finalization.
The pinned CE `ActKeyUtils::checkCurrent()` body is empty: this is not a claim
of testing a licensing/activation implementation.

The adapter verifies UID and cache/config tmpfs mounts before writing. It
retains the exact disposable MariaDB datadir check before resetting its owned
`php83_api_probe` schema. Synthetic schema/seeds are rebuilt per request;
this remains a stateless session/auth probe, not persistence/revocation testing.
Application caches are disabled/without a backend, while autoload/config cache
metadata may persist inside the private tmpfs.

## SAPI and transport matrix

Both candidates use only the previously held KalturaPDO/dateUtils repairs over
exp2. No additional application patch was needed.

| SAPI/transport | Original 7.4 | Candidate 7.4 | Original 8.3 | Candidate 8.3 |
|---|---|---|---|---|
| cli-server HTTP | Pass | Matches baseline | Known PDO signature fatal | Matches baseline |
| Apache mod_php HTTP | Pass | Matches baseline | Known PDO signature fatal | Matches baseline |
| Apache mod_php trusted HTTPS | Pass | Matches baseline | Blocked at preceding HTTP check | Matches baseline |

Evidence: [cli-server](evidence/api-web/cli-server.json),
[Apache](evidence/api-web/apache.json), [identities](evidence/api-web/identities.json).
Original 8.3 is not represented as having separately reached TLS tests.

The Apache runner starts a separate unprivileged process with its own config,
PID/runtime paths and single prefork worker. It does not restart/reconfigure
the installed Apache. The 8.3 mod_php module is copied from `.83` into the
private runtime bundle on `.74`, with matching source/destination SHA256:
`836620e8b0733c288ab323f3c341855066a8a91e774e82c9fc059adea257d8d5`.
It uses matching 8.3 extensions and a private INI with an empty scan directory,
not PHP7 extension binaries. This tests the module under the shared Noble
Apache host, not an independently installed full `.83` AIO.

HTTP and HTTPS bind only private-netns loopback on ports 18383/18443. Each run
creates an ephemeral RSA CA and a separately signed server certificate with
IP SAN 127.0.0.1 and serverAuth usage. Python uses create_default_context with
the generated CA; hostname verification is not disabled. A separate connection
without that CA **must** fail certificate verification. No external endpoint,
DNS/proxy discovery or redirect following is used. Keys/certs remain in private
runtime storage and are removed during cleanup, never committed.

The same 11 normalized assertions run over HTTP and HTTPS: session.start for
user/admin, session.get over GET/POST, exact JSON string fields, bounded expiry,
and rejection of missing/malformed/expired KS, wrong secret and escalation.
The client checks PHP minor and SAPI (apache2handler versus cli-server) on every
response. Existing [HTTP limitations](api-http.md) still apply.

## Diagnostics and cleanup correction

E_ALL diagnostics remain enabled and display_errors remains off for clean JSON.
For mod_php, php://stderr was insufficient to reliably recover application logs
from worker shutdown. The adapter instead writes both PHP and Kaltura logs to
`/audit/app/cache/probe-diagnostics.log` in the verified private tmpfs.

Apache is started with `setsid`: without its own process group, shutdown could
terminate the shell before its cleanup trap exported diagnostics. Final evidence
was rerun after fixing this harness issue. Cleanup now stops/waits for Apache,
exports logs to the collector, deletes temporary TLS/config material, and the
namespace disappears on service completion. Only diagnostic locations/counts
and whole-log hashes are committed, not raw token-bearing logs.

Candidate 8.3 has diagnostics at 43 recorded severity/path/line combinations in
this bounded run. These are not 43 unique bugs, not a full inventory and **not
accepted warnings**. Functional success does not satisfy the clean-runtime gate.
The source files were restored and compared to original after the final runs,
and the dedicated DB service was stopped. `.20`, installed Apache, main,
production package/CI files, releases and exp2 remain unchanged.

## Reproduce

Use the disposable DB and held-patch procedure in [api-session.md](api-session.md).
Copy the new web/router/runner files beside the existing schema fixtures and
updated HTTP client. Copy verified libphp8.3.so from `.83` into runtime83.

```sh
python3 tools/php83/patch-tests/collect-api-web.py CLI_REPORT.json
python3 tools/php83/patch-tests/collect-api-apache.py APACHE_REPORT.json
python3 -m unittest discover -s tools/php83 -p 'test_*.py'
```

Both collectors verify remote fixture identities before execution. Finally
restore candidate KalturaPDO/dateUtils and stop the disposable DB regardless of
success. 60 offline tests pass, covering fixed targets, redirects, explicit CA
loading, missing CA rejection and runtime/SAPI mismatches. Shell syntax checks
pass for both runners/inner scripts.

Graph project `kaltura-rigel-18.20.0-full` was ready at generation
2026-09-25T12:19:00Z. Coverage for web/index.php, KalturaResponseCacher, kConf and
ActKeyUtils recorded no issues; exact source was also read. No exhaustive
coverage claim is made.

Still open: FPM/Rocky, full distro installation/reboot/upgrade/rollback, real
cache-enabled behavior, uploads/workers/media, performance, diagnostic fixes
and release approval. No broad OpenSpec checkbox is complete.

## Independent review and final rerun

[Claude's advisory review](evidence/api-web/claude-review.txt) prompted further
harness hardening before the final reports: remove the artificial STDERR
constant, close/unset setup variables before entering the application, verify
the exact mountpoint field and reject shared propagation, explicitly request
MountFlags=private, restrict Apache document access to the probe location,
verify the child is alive, and assert a fresh per-run response nonce. The
stronger mount guard initially rejected systemd's shared-marked tmpfs; the
explicit private propagation setting corrected the runner, not the application.

Each run truncates only its fresh tmpfs diagnostic file. Apache requests assert
the exact private php.ini and absence of scanned INI files; reports record
runtime version, SAPI and loaded extensions without exposing config contents.
For this Apache test the 7.4 module set is a subset of 8.3, whose additional
built-in module is random. That is observed parity of this minimal probe's
module set, not proof of the full mandatory extension matrix.

Diagnostics remain a separate unresolved migration gate; synthetic schema reset
and cache-disabled behavior are explicit limitations, not silent exceptions.
Final CLI-server/Apache comparisons were rerun after all these changes, and
candidate restoration plus DB shutdown were repeated successfully.
