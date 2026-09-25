# Analytics partner-update unit characterization

Date: 2026-09-25. No application repair or endpoint acceptance is claimed.

## Execution boundary

`tools/php83/patch-tests/analytics-partner.php` evaluates exactly three
function-only ranges from the checksum-pinned original
`api_v3/web/analyticsSyncServe.php`:

- `getPartnerVertical`: lines 59–73;
- `getPartnerAccountType`: lines 75–83;
- `getPartnerUpdates`: lines 116–165.

The full file must match SHA256
`b2fe37440f542a49020547bfc6babc76049ab713e65495247b0c6a6eb1f010dc`
before any function is evaluated. No bootstrap, top-level routing, authentication
or other source ranges execute. Graph discovery and coverage were checked in
`kaltura-rigel-18.20.0-full`, generation 2026-09-25T12:19:00Z, metadata match and
no recorded gap; the exact source ranges were read.

Criteria, Partner, PartnerPeer and the statement are **explicit test doubles**.
They do not validate real SQL generation, authorization, model filtering,
database access or exception recovery. The query double returns synthetic rows;
the `SYNTHETIC_NOT_A_SECRET` literal is public test data, not a credential. Runs
use the existing nobody/read-only/no-socket sandbox on `.74` and `.83`.

## Observed behavior

Active rows exercise string, integer and null values for parent-ID/package.
An inactive row, row count, update timestamp and restoration of the criteria
filter flag on the successful path are also checked.

| Input values | Embedded JSON from the real function |
| --- | --- |
| strings `"42"`, `"7"` | `"pp":"42","se":"7"` |
| integers `42`, `7` | `"pp":42,"se":7` |
| null, null | `"pp":null,"se":null` |

Both PHP versions produce identical function output for **the same input shape**.
The function preserves types rather than normalizing those fields. Combined
with the earlier real mysqlnd experiment, this establishes a unit-level consumer
sensitivity to driver result types. It is not proof of an affected deployment or
a completed endpoint test.

Converting both fields unconditionally to strings would change the already-
numeric input contract; converting them unconditionally to integers would
change the string contract and requires explicit null handling. No such patch
was added. Effective connection attributes and downstream analytics expectations
must establish the intended compatibility contract before selecting a repair.

## Reproduction and evidence

```bash
python3 tools/php83/patch-tests/collect.py /tmp/analytics-partner.json \
  --case analytics-partner --mode standard
```

`evidence/analytics-partner/behavior.json` stores runtime identities, harness
hashes, stdout, stderr and comparisons. Both original and exp2 candidate trees
were exercised; analytics source is unchanged in those trees. Passing comparison
means runtime parity **for supplied identical fixture inputs**, not parity of
database-driven end-to-end responses.

All 38 existing offline tests pass. No database process was needed, no live data
was read, no source patch or ZIP was changed, and `.20`/main remain untouched.
Next evidence: reproduce the relevant connection/query path against synthetic
schema/data and establish consumer expectations, including null/zero values,
before claiming or repairing an endpoint contract regression.
