# Synthetic session-service and KS comparison

Date: 2026-09-25. This is bounded phase-1 evidence, **not HTTP or full
application acceptance**. See [API/SQL setup](api-mysql.md).

## What ran

The dedicated AF_UNIX-only MariaDB probe on `.74`, never its installed Kaltura
DB, was recreated through the existing datadir guard. Both PHP binaries ran
unprivileged in a private network namespace, with read-only application trees
and private configuration/cache tmpfs. PHP 8.3 is the copied `.83` executable
and matching modules, not the system interpreter on `.74`. Runtime identities
are unchanged from [the SQL experiment](evidence/api-mysql/identities.json).

The fixture runs the previous anonymous dispatcher/permission checks, then
calls real `SessionService::startAction()` directly. It uses synthetic partner
83001 and public test-only secrets, real partner SQL lookup, signing, parsing
and `ks::isValid()`. No authentication implementation is mocked. The added
`invalid_session` table is copied from pinned source lines 1261–1271; see
`tools/php83/patch-tests/session-schema-provenance.json` for identities.

The private cache mapping points `partnerSecrets` at an undefined
`disabledProbe` section: real cache code returns null and uses the database
fallback. Query-cache invalidation is likewise unavailable; validation queries
the synthetic `invalid_session` table. This is **not cache acceptance**.

Checks cover user/admin sessions, decoded partner/user/type, successful
validation, rejection of another partner, another user, tampered token,
expired session and wrong partner secret. Tokens are never included in stdout.
The collector retains only stderr diagnostic locations/counts and a whole-log
hash, not SQL, token fragments, stack arguments or token hashes. Expected
signature-mismatch logs from tampering are not treated as an application crash.
Diagnostic summaries are not a complete warning triage or full sanitized logs.

## Results and minimal repair

[Report](evidence/api-session/report.json): original PHP 7.4, candidate 7.4 and
candidate 8.3 return success and identical normalized stdout. Original 8.3
still fails at the previously documented `KalturaPDO::query()` declaration.

With only the held KalturaPDO repair, session validation reaches a new fatal:
`dateUtils.class.php:100`, an unparenthesized nested ternary. The new held
`patches/php83/held/dateUtils-ternary.patch` adds parentheses preserving **PHP
7.4 left association**. It deliberately does not fix unrelated legacy format
quirks: e.g. 11 hours formats as `011:00:00.0`. Nine duration inputs (including
10/11 hours and a negative value) match original 7.4. Removing only this repair
reproduces the fatal: [counterfactual](evidence/api-session/date-counterfactual.json).
Source/patch before/after hashes are in its adjacent JSON metadata.

Graph verification used `kaltura-rigel-18.20.0-full`, generation
`2026-09-25T12:19:00Z`, with coverage checks for SessionService, kSessionUtils,
kSessionBase, kCacheManager and dateUtils: no recorded issues, not proof of
completeness. The SQL block was read directly; the full SQL index is partial.

## Reproduce and cleanup

1. Prepare the disposable DB and copied runtime as in `api-mysql.md`.
2. Copy the new `api-session.php`, `api-session-schema.sql` and
   `run-api-session.sh` beside the existing guest fixture files.
3. Verify original hashes, then apply the held KalturaPDO and dateUtils repairs
   to **candidate only**, with zero fuzz/offset. Do not alter the original tree.
4. Run `python3 tools/php83/patch-tests/collect-api-session.py REPORT.json`.
5. In a finally/cleanup path, restore both candidate files from the verified
   original tree, compare them, and stop `kaltura-pdo-mysql-probe`.

Both files were restored and the disposable DB stopped after this run.
47 offline Python tests pass; the shell wrapper passes `bash -n`.

## Still open

The session action bypasses dispatcher initialization: authenticated dispatch,
HTTP/HTTPS, Apache/FPM, KS v2, cross-runtime token exchange, session revocation,
cache-enabled validation, media permissions and full installation remain open.
Many existing deprecations remain in the report (including reflection parsing,
PDO signatures and dynamic properties); passing assertions do **not** waive
these diagnostics. No broad task is complete. No change to `.20`, `main`,
production packaging, CI or release. Both repairs remain held; exp2 still
contains only its three JSON patches.

## Independent review follow-up

[Claude's advisory review](evidence/api-session/claude-review.txt) caught a real
fixture error: admin must be `SessionType::ADMIN` (2), not 1. The final fixture
uses the source constants and additionally rejects user-secret-to-admin
escalation; the four-tree report was rerun after this correction. Comparison
against original 7.4 is enforced by the collector, not the guest shell runner.
The cache file is private tmpfs (verified before bootstrap), so it does not
persist in host configuration. The added schema creates only invalid_session,
not partner. Wrong-type validation and cache-enabled coverage remain open;
review suggestions are not evidence that those paths passed.
