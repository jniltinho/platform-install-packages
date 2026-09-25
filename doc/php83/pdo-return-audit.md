# Real SQL audit before native PDO return repairs

This cycle **measures existing defects**, not a fixed candidate. Adding `: bool`
blindly would turn implicit null returns into TypeErrors; casting null to false
would incorrectly report successful work as failure. No application patch or
experimental ZIP changes here. The exp8 API residual remains 21 groups / 571 events.

## Actual results on PHP 7.4.33 and 8.3.6

Codex and Claude independently execute nineteen rows per runtime on a new,
uniquely owned socket-only MariaDB instance. Observed values are identical across
these runtimes, but this is **not** native-contract compatibility:

| Operation | Native PDO | Existing wrapper | Required repair constraint |
| --- | --- | --- | --- |
| Supported setAttribute | true | PropelPDO null | Propagate native success, not a cast |
| Unsupported attribute 987654 | false | PropelPDO null | Preserve false, never unconditional true |
| Custom prepare-cache attribute | not a PDO feature | value stored, null return | Specify custom setter success while preserving cached-value behavior |
| Successful bound statement | true, SELECT 17 | KalturaStatement null, SELECT 17 | Preserve native result and data |
| Failed statement, ERRMODE_SILENT | false, SQLSTATE 42S02 | null, same SQLSTATE | Propagate failure distinctly from success |
| Failed statement, ERRMODE_EXCEPTION | PDOException/42S02 | same exception/state | Do not swallow or rewrite PDO errors |
| Dry-run write | no native equivalent | null, zero inserted rows | Preserve no-write behavior and explicitly specify simulation return |
| Dry-run SELECT | no native equivalent | null, SELECT 19 | Preserve actual read and native execution result |

Cache enabled returns the identical prepared-statement object for the same SQL;
disabled returns distinct objects. Nested commits preserve transaction depth,
physical transaction state and committed row count. Nested rollback makes final
commit throw PropelException until forceRollBack; the rolled-back insert does not
persist. Existing Propel commit/rollback without an active transaction returns
true—intentional wrapper behavior, **not** native PDO equivalence. Those semantics
must not be “fixed” merely to look like native PDO. The explicit transaction and
dry-run data invariants are asserted, not inferred from warning counts.

PHP 8.3 records eight deprecation locations in PropelPDO and KalturaStatement;
PHP 7.4 records none. This audit records severity/file/line rather than message
text, and correlates the source with previously measured native tentative return
contracts. It does not establish resolution of any deprecation.

[Primary](evidence/pdo-return-audit/codex.json),
[independent](evidence/pdo-return-audit/claude.json),
[comparison](evidence/pdo-return-audit/comparison.json).
`audit_executed:true` means the observation experiment completed, **not** that
its observed null/native-bool divergence is acceptable.

## Source, inheritance and fixture boundaries

The loaded PropelException, PropelPDO and KalturaStatement bytes from exp8 are
identical to the pinned original source. [Identity](evidence/pdo-return-audit/loaded-source-identity.json).
These unchanged classes can be exercised under 7.4; the whole exp8 artifact is
still PHP 8.3-only. The fixture does not load KalturaPDO or full application bootstrap.

Graph INHERITS tracing identifies KalturaPDO, DebugPDO, MssqlPropelPDO and
MssqlDebugPDO below PropelPDO. All exact inspected paths have matching coverage
metadata at generation `2026-09-25T12:19:00Z`, best effort. Source declarations
show overrides in subclasses: return declarations cannot be added to the parent
without checking the corresponding child signatures. KalturaStatement has no
descendant in that bounded graph trace, not proof of absence outside the tree.
[Coverage](evidence/pdo-return-audit/coverage.json),
[source inventory](evidence/pdo-return-audit/source-inspection.json).

PDO, PropelPDO and KalturaStatement execute real MariaDB statements. Only logging,
query-cache status, API-cache side effect and database monitoring dependencies
are fixture stubs. Bind uses an explicit integer PDO type; default/null binding,
input-parameter arrays, warning error mode, emulation-off paths, cache option
keys, repeated placeholder/multi-row failure and full logging/cache/monitor
behavior remain untested. This is not a claim of all PDO driver behavior or MSSQL
runtime validation. Actual get_class observations and direct per-process source
hashes should be added for the repaired-candidate matrix; current identity comes
from pinned class loading and entire artifact verification.

## Safe database lifecycle and reproduction

The runner requires baseline74 hostname, validated owned datadir/socket and no
symlink redirects. It uses the original 7.4 binary or copied 8.3 runtime, minimal
explicit MySQL modules, private network with AF_UNIX only, read-only application
and fixtures, and inaccessible production DB/application paths. Before any schema
DROP/CREATE, native PDO must report exactly the expected owned `@@datadir`.
Both runtimes reset only the fixed synthetic schema on that fresh private server.
The known random unit is stopped in finally, even after startup identity failures.

```sh
# After first staging probe.php/run.sh at /home/vagrant/php-pdo-return-audit:
python3 tools/php83/pdo-return-audit/collect.py /path/to/new-report.json
python3 doc/php83/evidence/pdo-return-audit/compare.py
```

The complete exp8 source is verified before/after. Native errors are reduced to
exception class/SQLSTATE; error messages, passwords and arbitrary failed-process
stdout are not saved. Logs/monitor stubs do not emit SQL. Reports include owned
unit **and datadir**. Datadirs are intentionally retained, not deleted, and are
not proof of running services. Exceptions may leave no complete partial report;
existing host keys and runtime binaries are not revalidated by this collector.

## Independent roles and next repair gate

Claude independently repeats the two real SQL variants and reviews cleanup,
source and observed values. Cursor executes 136 local tests and reviews original
class/override/return behavior. Grok times out at 120 seconds (exit 124); after its
termination, OpenCode Zen Muse Spark 1.3 Free executes 136 local tests and reviews
both runtime reports and the proposed repair constraints. The local suite does
not exercise this new live fixture or supply new mocked collector coverage.

Advisory corrections: OpenCode's “124s” means exit 124, not the configured 120-second
bound. Claude's assertion that retained datadirs lack report registration is
incorrect: both are explicitly in `db.datadir`; its broader count of historical
directories is not a deletion request. Nested transaction behavior is deliberately
not native-equivalent. Source declarations alone cannot prove dropped results;
method bodies plus observed real SQL establish the finding. Independent reruns
share a harness, so separate code review remains necessary.

Next: develop minimal held repairs that propagate native true/false, specify
custom-cache/dry-run success explicitly, and retain exception, row, transaction
and cache effects. This intentionally changes defective public null returns;
it must be called out and tested at callers, not described as exact return-value
parity. Review subclass declarations before adding types, expand binding/prepare
and dry-run controls, then exercise real KalturaPDO/bootstrap and the artifact
API/SQL/HTTPS matrix. No diagnostic is waived, no acceptance task closes, and no
package/CI, release or `.20` gate is crossed by these observations.
