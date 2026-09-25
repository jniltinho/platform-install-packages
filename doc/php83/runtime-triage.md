# PHP 8.3 runtime triage — phase 1, 2026-09-25

**No-go for an unchanged-runtime switch.** This is a partial investigation, not
the final feasibility gate or authorization to patch dependencies. No claim is
made that all findings have been triaged.

## Reproducible differential

The same versioned harness ran 15 fixed probes over extracted public packages
in the independent PHP 7.4 and PHP 8.3 labs. All 15 matched expected output and
exited zero under 7.4; five
failed under 8.3. Both runs passed the sandbox preflight (UID 65534, read-only
payload, protected directories inaccessible, AF_INET/AF_INET6/AF_UNIX socket creation denied).
No database connection or application configuration was used. Reports include
module lists, harness hashes and per-process diagnostics/public inclusion hashes.

| Finding | Demonstrated evidence | Reachability / pending work |
|---|---|---|
| Zend Registry | `Registry.php:206`: `array_key_exists` on an object throws TypeError in set/get probe | File included during baseline Admin login; exact application method coverage pending |
| Legacy Services_JSON | `Services_JSON.class.php:176`: removed offset syntax rejects inclusion | Fixed synthetic encode probe; broader first-party usage pending |
| Zend JSON fallback encoder | `Zend/Json/Encoder.php:557`: removed offset syntax rejects inclusion | Forced fallback fails; default ext/json encode/decode succeeds |
| Zend JSON fallback decoder | `Zend/Json/Decoder.php:324`: removed offset syntax rejects inclusion | Forced fallback fails; default ext/json encode/decode succeeds |
| Propel DebugPDO | `DebugPDO.php:330`: `query()` declaration incompatible with PDO | Autoload-only class probe fails without a DB connection; configured driver reachability pending |
| Symfony KMC files | PHP 8.3 compiler rejects `sfRouting.class.php`, `UrlHelper.php`, `sfCore.class.php` | All three included in baseline KMC shell; PHP 8.3 HTTP application bootstrap not yet run |

The DebugPDO declaration failure is additional runtime evidence beyond syntax
checking. Loading the base PropelPDO class succeeds, so its success must not be
used to infer that every subclass or database path is compatible.

## Successful probes are bounded

Empty-options Zend Application, simple Zend Config, base PropelPDO discovery,
DebugPDOStatement, PropelConfigurationIterator, Criteria, BasePeer, BaseObject,
PropelPager and default Zend JSON completed their fixed operations on PHP 8.3.
Return-type and other deprecation diagnostics remain in the reports; exit zero
is not a waiver or a full functional compatibility assertion. In particular,
class discovery does not exercise SQL operations, transactions or error handlers.

## Repair investigation order (not approved patches)

1. Establish exercised KMC syntax repairs and focused regression expectations.
2. Characterize Zend Registry key-existence behavior before choosing a fix;
   preserve absent versus null-valued keys and ArrayObject semantics.
3. Inventory Propel/PDO override signatures and active driver/debug settings;
   preserve argument handling and return behavior, not merely declaration load.
4. Track forced JSON fallback paths separately from native JSON; no blanket
   exclusion based only on the default probe passing.
5. Continue full static triage, license/source inventory, extensions/SAPIs,
   controlled baseline timings and browser/worker coverage before go/no-go.

The graph indexes the packaging repository, not the downloaded application.
Coverage checks reported missing records for the Zend JSON and Propel source;
these observations rely on direct verified-source reads and executed probes,
not on a graph absence claim.

## Independent CLI review follow-up

Claude reviewed the first expanded harness and supplied reports without tools.
Its useful corrections were applied before the final rerun: expected-output
checks and summary, absolute PHP paths, explicit include paths, INI file lists,
wrapper hash, distinct absent/denied path results, a 600-second service limit
covering the per-probe budgets, and denial checks for Unix/IPv4/IPv6 socket
creation. Duplicate PHP log emission is disabled while E_ALL diagnostics remain.
These checks attest only their measured properties, not full sandbox security.
Runner exit zero remains collection success by design, explicitly not acceptance.
Timeouts are incomplete evidence and currently omit partial captured output.
Reports are content-hashed and committed with the harness; no pre-existing commit
identity or equivalence to the production `.20` runtime is claimed.

## Evidence

- [Expanded baseline](evidence/runtime-probes/sandbox-v2/php74.json)
- [Expanded candidate](evidence/runtime-probes/sandbox-v2/php83.json)
- [Exit comparison](evidence/runtime-probes/sandbox-v2/comparison.json)
- [Baseline HTTP inclusion summary](evidence/runtime-probes/include-summary.json)
- [Harness and isolation instructions](../../tools/php83/README.md)

The first wrapper attempt rejected mismatched assumed VM hostnames before any
probe. The corrected candidate attempt then failed mount setup because the
protected `/opt/kaltura` path does not exist there. Marking that inaccessible
path optional when absent resolved setup; it remains hidden when present on the
baseline. Neither setup failure is an application compatibility defect.
