# exp4: integrated Criteria null-alias experiment

Separate seven-patch ZIP, not a release or full PHP 8.3 acceptance result.
It includes the exact exp3 selection plus the reviewed one-line Criteria
null-alias repair. Original, exp2 and exp3 archives remain unchanged.

## Artifact identities

- Upstream: `58d534d09b3b75c9a8333957268c884f79032638b2d44a278b1992fda1b0ab28`.
- exp4 ZIP: `a1ce4c46792667b07a733e622a3ee71dd01c87a94f7841edfc72d58746ab9d08`.
- Local artifact: sibling `platform-install-packages-php83-artifacts/exp4/`
  `Rigel-18.20.0-php83-experimental.exp4.zip`.
- Second build: sibling `exp4-repeat/`, byte-identical ZIP.
- [Ordered manifest](evidence/exp4-candidate/manifest.json) pins seven patches,
  before/after file hashes and their repository source paths.
- [Exact-delta verification](evidence/exp4-candidate/verification.json) checks
  every original entry: seven source files changed, nine metadata additions,
  other bytes unchanged. No runtime data, secrets or installed configuration.

The exp2 active manifest is not changed. Selection is explicit, not wildcard
promotion of held experiments. Remaining patches/cache work are still separate.

## Actual ZIP SQL / HTTP / TLS results

The full extracted source is verified against the ZIP before running the real
`api_v3/web/index.php` through the existing synthetic SQL/session fixture. The
same collection includes exp3 as a contemporaneous counterfactual, not merely a
historical warning-count comparison.

| PHP | Original | exp3 | exp4 |
| --- | --- | --- | --- |
| 7.4.33 | Functional baseline, six dateUtils events | Matches baseline, no events | Matches baseline, no events |
| 8.3.6 | Expected PDO declaration fatal at first HTTP request | Matches baseline; 41 groups / 1,767 events | Matches baseline; 40 groups / 1,073 events |

Each positive row checks eleven normalized session/auth assertions per transport,
HTTP and trusted HTTPS, and rejects an untrusted CA. Raw KS-bearing application
logs are not persisted. Both candidate versions match original-7.4 normalized
output, including denied malformed/expired/missing sessions and privilege
escalation attempts. No new allowlist exclusion or diagnostic suppression.

Exactly the **694 Criteria.php:1375 events disappear**. All other sanitized
severity/path/line counts are unchanged between exp3 and exp4. This is a
compatibility improvement, **not measured performance improvement** and not
acceptance of the remaining 1,073 events.

[Primary report](evidence/exp4-api/codex.json),
[diagnostic delta](evidence/exp4-api/diagnostic-delta.json), and
[independent execution](evidence/exp4-api/claude.json).

## Isolation, reproduction and limits

`tools/php83/exp4-api/stage.sh 74` creates a new owned lab staging directory and
refuses an existing one. The collector uses its own random private synthetic DB,
checks fixture/source hashes, serializes all six rows and stops its unit in a
finally block. Only the existing disposable baseline VM is used; the separate
PHP 8.3 bundle is not installed as the system runtime. Source/scripts/binaries
are read-only binds, network is private, installed production paths inaccessible.
The `.20` server is not touched.

```sh
# Run after the one-time stage, with no other writer on baseline74.
python3 tools/php83/exp4-api/collect.py /path/to/new-report.json
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tools/php83 -p 'test_*.py'
```

The [exp3 API fixture boundaries](exp3-api.md) still apply: schema reset per
request, not persistent sessions/revocation; no full AIO/FPM/distro installation,
media jobs/playback/browser/load/upgrade/recovery acceptance. Existing SSH host
keys are not pinned. Original baseline files and copied PHP binaries have prior
provenance but are not rehashed this collection. DB data is retained after service
stop. Exceptions can leave no structured partial report; this is not a production
gate. The new verifier refuses optimized Python before its assertions.

The focused CLI matrix was also rerun on actual exp4 bytes in both labs:
48 rows, 44 zero exits and four expected original-8.3 JSON syntax controls;
all 24 candidate rows exit zero. Twenty typed JSON/serialized-entry comparisons
match original 7.4 (environment rows are recorded, not treated as functional
parity). This is new exp4 execution, not inferred from historical exp3 tests.
See [`exp4-runtime/parity.json`](evidence/exp4-runtime/parity.json). Diagnostics
remain recorded, including dynamic-property/interface warnings. The CLI batch
inherits assertion-based guards and must not run with Python optimization;
replace guards before using it as a production gate.
No full-case checkbox or release gate is closed. Independent CLI results and
explicit failures/timeouts are tracked in `evidence/exp4-api/result.json`.

## Independent execution and review

Cursor independently verified the exact ZIP delta/repeat build. Claude reran the
six-row real API matrix; OpenCode Muse Spark Free and Cursor independently
reviewed the counterfactual reports. Grok timed out at 120 seconds (exit 124),
so its attempt is not counted as successful execution. The authorized fallback
ran the 122 local tests and checked the API evidence explicitly.

Claude reran the 24 CLI rows on 7.4 and Cursor reran the 24 rows on 8.3, in parallel
on separate VMs. Codex verified both normalized independent reports against the
primary executions and checked every recorded fixture hash against the local
files. Local Python suite: 122 tests, unchanged count; these are not tests of the
new exp4 collector itself. Raw executor/reviewer final responses are retained.

Claude noted a missing stage script inside `exp4-regression/`; staging actually
lives in [`exp4-api/stage.sh`](../../tools/php83/exp4-api/stage.sh), documented in
its [README](../../tools/php83/exp4-api/README.md). The first run copied CLI runners
separately; the final stage script includes them for clean reproduction. This
post-execution setup-documentation change did not modify the tested runners.
