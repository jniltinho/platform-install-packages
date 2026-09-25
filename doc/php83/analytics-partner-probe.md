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

## Real-driver integration follow-up

`analytics-mysql.php` now connects the exact functions to actual PDO statements
obtained through the bundled Propel connection factory and held DebugPDO v3.
It uses the dedicated socket-only MariaDB from the type experiments. The
Criteria and PartnerPeer layers are still **test adapters**: they return a real
statement for a synthetic literal SELECT/UNION rather than generating the
production query. No endpoint bootstrap, authentication, real partner table or
application credentials are loaded. This narrows the driver-to-function gap,
but is not full endpoint or real-schema acceptance.

Nine combinations cover positive, zero and NULL parent/package values, each
with unspecified attributes, explicit native prepares or explicit stringify.
Every SQL result flows through the original `getPartnerUpdates` function. A
separate fetch checks that the output pp/se types match the actual driver input.
The inactive-partner result, count, timestamp and successful-path filter reset
are asserted again.

Results in `evidence/analytics-partner/mysql/behavior.json`:

- Original/patched 7.4 match in all nine combinations.
- Patched 8.3 differs from original 7.4 for **positive and zero** values with
  unspecified connection attributes: quoted numbers become JSON numbers.
- NULL values match; all explicit-native and explicit-stringify cases match.
- Original 8.3 still fails at the unpatched DebugPDO declaration.
- Existing function-only comparisons still pass, as expected for identical
  supplied input shapes (`unit-regression.json`). All 38 offline tests pass.

With the existing guarded, disposable server prepared, invoke:

```bash
bash /home/vagrant/php-patch-tests/run-mysql-types.sh 74 original "$d" analytics
bash /home/vagrant/php-patch-tests/run-mysql-types.sh 74 candidate "$d" analytics
bash /home/vagrant/php-patch-tests/run-mysql-types.sh 83 candidate "$d" analytics
```

Both PHP binaries run on the isolated baseline VM with previously recorded
binary/module provenance. Hashes of the integration harness are in the report.
The dedicated database service was stopped and candidate DebugPDO restored
after collection. No new source patch or global PDO setting was selected.

Claude's unit-methodology review is saved as advisory text. Its request for
real-driver evidence motivated this bounded integration. Its opinions about
whether a downstream consumer must fail before a repair is warranted, or where
a repair must live, are not acceptance decisions: the proposal still requires
preserved API contracts and review of configuration side effects. Effective
deployed attributes, real query/schema execution, downstream readers and the
full authenticated endpoint remain unverified.
