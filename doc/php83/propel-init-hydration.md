# Propel initialization and bounded entry hydration probe

Date: 2026-09-25. Phase-1 experiment, not API acceptance.

## Source path verified

The shared Rigel graph (`kaltura-rigel-18.20.0-full`, generation
2026-09-25T12:19:00Z) located `Propel::initConnection` and `Baseentry::hydrate`.
Exact source reads confirmed the relevant behavior; graph call edges were used
only for discovery, not assumed to resolve dynamic classes correctly.
Coverage checks returned metadata-match/no-recorded-gap for:

- `vendor/propel/Propel.php`: lines 584–684 choose/construct the configured class,
  set exception mode, process optional connection attributes, then call the
  adapter initializer. Lines 696–719 resolve configured PDO constant names.
- `vendor/propel/adapter/DBAdapter.php`: lines 98–110 apply charset and configured
  initialization queries. `DBMySQL.php` supplies the real MySQL adapter.
- `alpha/lib/model/om/Baseentry.php`: lines 2830–2906 explicitly cast selected
  columns, then reset modification state and mark the object non-new.
- `vendor/propel/om/BaseObject.php` and `om/Persistent.php`: the real base class
  and interface used by the fixture, not substitutes.

These bounded checks do not prove exhaustive inheritance/caller coverage or
the effective configuration of a deployed application. No configured credentials
or runtime connection files were inspected.

## Executed fixture

`tools/php83/patch-tests/mysql-init.php` loads the actual bundled classes and
calls `Propel::initConnection` with synthetic parameters. The real DBMySQL
adapter initializes utf8mb4. No attribute changes are made outside the fixture
connections. Four cases run on original/patched 7.4 and patched 8.3:

1. No explicit emulate/stringify option.
2. Native prepares specified through constructor `options` using a qualified
   PDO constant name.
3. Native prepares specified through post-construction `attributes` using an
   unqualified constant name.
4. Stringify specified through post-construction `attributes`.

For this synthetic setup, case 1 reports emulation enabled in both runtimes.
Its raw integer/float results differ across PHP versions. Cases 2–4 return
matching raw rows. Exception mode and charset initialization pass in all cases.
This identifies a possible application risk; it does not establish that a live
deployment uses case 1 or authorize changing its connection defaults.

PDO 7.4 here rejects readback of `ATTR_STRINGIFY_FETCHES` with SQLSTATE IM001.
The fixture records this as unsupported/null, not false. It checks the actual
stringified values for case 4. Other readback errors are rethrown. PHP8.3 permits
readback. This readback difference is not a failure to set the attribute.

## Generated hydration result

A concrete test subclass extends the actual abstract Baseentry without
overriding its constructor or hydrate method. The fixture passes a synthetic
53-column row with a fixed entry ID and uses the SQL integer result for `views`
and `partner_id`. Other columns are null. Assertions verify:

- hydrate returns the expected end column 53;
- ID is the expected string, views and partner ID are integer 42, name is null;
- the hydrated object is non-new and unmodified.

All selected hydrated values match original 7.4 across the four cases. This
demonstrates normalization for these generated integer fields, not all Kaltura
models, temporal/decimal values, rehydration, business-class hooks or API
serialization. No full API JSON-contract claim is made.

## Evidence and reproduction

Report: `evidence/debug-pdo/mysql-init/behavior.json`, including captured stderr,
fixture hashes and separate raw/hydrated comparisons. Original 8.3 still fails
at the unpatched DebugPDO declaration; the candidate uses held v3 only.
Use the disposable MariaDB setup in [mysql-type-experiment.md](mysql-type-experiment.md)
and invoke the same guarded wrapper with an additional `init` argument:

```bash
bash /home/vagrant/php-patch-tests/run-mysql-types.sh 74 original "$d" init
bash /home/vagrant/php-patch-tests/run-mysql-types.sh 74 candidate "$d" init
bash /home/vagrant/php-patch-tests/run-mysql-types.sh 83 original "$d" init
bash /home/vagrant/php-patch-tests/run-mysql-types.sh 83 candidate "$d" init
```

Both binaries run on the disposable baseline VM against one dedicated,
socket-only database, not the installed application database. The PHP8.3
binary/modules are copied from `.83`; provenance and limitations are those of
the previous type probe. The temporary DB service was stopped and candidate
DebugPDO restored after collection. `.20`, main, active patch manifest and exp2
ZIP are unchanged. Remaining diagnostics and API/raw-query consumers still
block promotion; no migration task is marked complete.

## Follow-up: actual JSON serializer

The fixture now invokes the bundled `KalturaSerializer` and
`KalturaJsonSerializer` on **plain synthetic objects** constructed from the raw
row and the selected hydrated fields. It does not construct a full Kaltura API
object, invoke authentication or execute an endpoint. Both serializer files
were source-read and coverage checked with the same graph generation and
metadata-match/no-recorded-gap result.

New report: `evidence/debug-pdo/mysql-serializer/behavior.json` (the earlier
hydration report remains unchanged). With unspecified connection attributes:

```json
{"n":"42","f":"1.25","charset":"utf8mb4"}
```

is the original 7.4 raw-object JSON, while patched 8.3 produces:

```json
{"n":42,"f":1.25,"charset":"utf8mb4"}
```

The selected hydrated object produces identical JSON on both runtimes in all
four configurations. The real serializer's removal of null properties is also
asserted. Constructor/attribute native-prepares and explicit stringify cases
retain raw JSON parity in this fixture, not necessarily across the whole API.

Run the prepared, dedicated probe with:

```bash
python3 tools/php83/patch-tests/collect-mysql-init.py /tmp/mysql-init.json
```

The collector's success means the recorded characterization was reproduced,
**not that raw JSON parity passed**: its report explicitly retains the known
false comparison. Five offline tests verify that the mismatch remains visible
and that hydration regressions, missing cases, candidate failures and unrelated
original failures fail collection. All 38 offline tests pass.

### Direct-consumer triage (source only)

- `api_v3/web/analyticsSyncServe.php`, `getPartnerUpdates`, lines 132–151:
  fetches associative rows, copies parent-ID/package columns into a structure
  and calls `json_encode` without explicit casts for those columns. This is a
  candidate JSON-contract risk inferred from source, **not an executed endpoint
  regression**. The script was not loaded or run; it includes sensitive-data
  processing paths and must only be tested later with isolated synthetic data.
- `alpha/lib/model/PartnerLoadPeer.php`, `getPartnerLoads`, lines 110–132:
  consumes associative rows then passes values through generated model setters.
  That is a different path from direct JSON emission. Setter behavior and the
  complete batch workflow were not tested in this step.

Both files were coverage checked and relevant source ranges read. This is not
an exhaustive raw-query inventory or evidence that deployed connections use
the synthetic unspecified configuration. Broad API acceptance remains open.
The probe DB was stopped and original candidate source restored after this run.
