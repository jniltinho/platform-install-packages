# Return-contract SQL composition — local preparation

**Latest: primary + actual Claude independent SQL observations completed.
Two cohorts ×91 typed rows per run, exact repeat; no artifact/release selection.**
Ownership is separate from the coordinator's return-contracts native repeat.

## Feasible smallest fixture

Use the known fresh private Unix-socket MariaDB lifecycle on baseline74 and its
copied PHP83 interpreter/modules, after privacy work releases that lab. Native83
has no MariaDB server installed; do not install packages or mutate its runtime.
One fresh synthetic database and one InnoDB table `probe(id INT PRIMARY KEY)` are
sufficient for this focused PDO contract. No AIO/model schema is needed.

Load full real PDO/PropelPDO/KalturaPDO/DebugPDO and selected exp12
KalturaStatement. Compare explicit v3-only prerequisite versus v3+return-family
using fresh strict composition from pinned exp12. Keep original DebugPDO fatal
as the separately recorded native control, not a SQL success. Selected statement
hash and historical harness hashes are in
[evidence](evidence/return-contracts-sql/preparation-identities.json).

Allow only named/hash-pinned seams for KalturaLog, KalturaMonitorClient,
kQueryCache and kApiCache side effects; never replace the five tested classes,
PDO drivers or SQL. Record seam calls without SQL/DSN/password contents. The
logging/monitor/cache seams are a declared boundary, not integration evidence.
KalturaPDO constructor can omit the optional connection-name option and therefore
avoid the DbManager config lookup; do not replace DbManager. Confirm this branch
and actual loaded source identities in the new harness. Disable only optional SQL
comment generation for deterministic fixture statements, reporting that choice.

## Required contracts

- Per real connection class: positive exec zero/one affected rows, invalid exec
  under silent/exception modes, query success/invalid, prepare success/failure,
  fetch scalar and bound typed parameters. Record exact PHP type+value or real
  exception class/code; no integer/bool/string casts to make parity pass.
- Propel-derived classes: nested begin/commit/rollback state, forceRollback and
  no-active transaction errors. Assert database side effects separately from
  return values. PDO is a native reference, not expected to emulate Propel nesting.
- Prepared-statement cache on/off: same-object/different-object identity and raw
  cache attribute return value. No cache backend acceptance claim.
- Real selected KalturaStatement bindValue/execute, missing-table failure in both
  PDO error modes, dry-run write produces no row, dry-run select still returns
  its native scalar. Reset global dry-run in finally. Test KalturaPDO's actual
  statement-class constructor selection rather than only direct setAttribute.
- Preserve all native diagnostics on stderr (error handler returnsfalse), also
  parsed diagnostic records with file/line/source identity. Keep unrelated known
  declaration warnings visible. No deprecation suppression or output hash-only
  evidence when raw fixture diagnostics are safe.

## Historical patterns that must NOT be reused unchanged

Old pdo-return-audit uses exp8 source paths and collector imports, returns true
from its diagnostic handler, and casts fetched scalar/count values. Its limited
side-effect seams omit KalturaPDO constructor monitor methods. It did not test
KalturaPDO/DebugPDO composition. Reusing its successful result or just changing
an archive name would be invalid. New seams, sources, cases, collector and tests
must be explicit and pinned. Existing family/compose tools remain frozen.

## New-runner safeguards and sequencing

1. Prepare new repo-local cohort/source/harness manifests with exact source hashes
   and strict patch replay. Review local tests and safety once as a coherent batch.
2. After named lab handoff, collect fresh source/runtime snapshots, create unique
   owned datadir/unit, verify @@datadir and Unix socket ownership before any DDL.
   Restrict network to AF_UNIX, bind app/cohorts read-only, hide real SQL sockets,
   use private config/cache tmpfs. No existing application config is modified.
3. Persist each process result incrementally, retain failure observations and
   post-failure identity/cleanup. Stop only the exact owned unit, confirm terminal
   server state, do not use broad stop/delete commands or assume rollback cleanup.
4. Initial two-cohort outputs remain observations until exact typed/error/SQL
   effects and expected diagnostic deltas are reviewed. Actual independent repeat
   uses new owned DB and evidence, then the lab is released. Full API/HTTP/cache
   backend/MSSQL and release gates remain open.

This is bounded new SQL work, not permission to resume another worker's stage or
mutate coordinator native-repeat outputs. Rank positive persistence remains in
the separate full-API plan instead of increasing this fixture's scope.

## Implemented and executed bounded phase

The historical plan above led to the new `tools/php83/return-contracts-sql/`
batch, not reuse of old exp8 acceptance. Preparation replays pinned composition
and copies complete class files; the exact38-file map is re-created from the
pinned archive before staging. Separate UUID stages/datadirs/units were used for
primary and independent repeat. The prepared root is read-only and contains all
three source cohorts; only prerequisite/candidate are SQL-executed.

Actual Claude local preparation review timed out180s (exit124), not a pass.
OpenCode free then ran18 local tests and two separate Bash syntax checks (all0)
and reviewed the essential safety boundaries. Its requested real archive/source
join was completed locally before any SQL. Datadirs are deliberately retained
for evidence, not silently deleted; there are four bounded owned datadirs from
this phase and no running corresponding server. Disk reclamation remains an
explicit later maintenance operation, never broad automatic deletion.

Primary Codex execution and actual Claude repeat each returned observer2
(`OBSERVED_NOT_ACCEPTED`), with both PHP83 processes exit0. Source/runtime
pre/post and across-run snapshots are identical. All four exact units stopped
(exit0) and were confirmed inactive; the lab was released before documentation.
The actual interpreter is copied PHP83 on baseline74, not a PHP74 candidate run.
No native83 VM, existing app database, SQL schema, credentials or source was
modified. Only the declared fresh private databases were created/populated.

[Primary](evidence/return-contracts-sql/primary-r1.json),
[independent repeat](evidence/return-contracts-sql/independent-r1.json),
[actual Claude execution report](evidence/return-contracts-sql/repeat-public.json),
[comparison](evidence/return-contracts-sql/comparison-r1.json).

The91-row oracle in `compare.py` explicitly constructs expected operation results,
not a saved successful body used as its own oracle. It covers native PDO's real
nested-transaction exceptions versus Propel-family nesting, exact boolean/int/
false returns, SQLSTATE42S02 failures, prepared-statement classes and scalar types,
cache object identity, transaction writes/rollback, dry-run no-write and SELECT.
Both cohorts match this oracle and each other. Independent bodies, stdout and
stderr are byte-identical per cohort without normalization. Only envelope UUIDs,
command stage paths and snapshot output filenames differ. The typed driver
fetch expectations are scoped to this fixed interpreter/driver configuration.

Diagnostics15→4 are source-declaration observations for this loader, not a promise
that the API's twelve groups/274 events disappear. Four retained controls are
DebugPDOStatement bindValue/execute and DebugPDO exec/query; all stay visible on
native stderr. The explicit diagnostic contract is sampled from retained native
primary records, not a claim to reconstruct an earlier discarded channel. The
comparator checks its exact messages/lines and native stderr representation.
All eight loaded source-file hashes are bound to the prepared cohort manifest.

Thirty-six local tests include adversarial identical-wrong outputs in both
cohorts, float/bool substitutions, missing/duplicate cohorts, missing rows,
extra stderr, dropped warnings, wrong source hashes, runtime drift and cleanup
failures. The first comparator draft incorrectly expected leading newlines in
native stderr; a local self-check rejected it before any acceptance report. Only
the comparator expectation changed to observed native formatting; frozen probe,
runner and actual primary/repeat evidence were not changed.

Four explicit side-effect seams remain. Full logging/monitor/cache backend,
MSSQL, full application/API/auth/performance and release acceptance are open.
The parent's separate native-nine repeat evidence is not owned or modified here.

### Reproduce locally (no VM)

```sh
python3 -m unittest discover -s tools/php83/return-contracts-sql -p 'test_*.py'
python3 tools/php83/return-contracts-sql/compare.py \
 doc/php83/evidence/return-contracts-sql/primary-r1.json \
 doc/php83/evidence/return-contracts-sql/independent-r1.json \
 --diagnostics doc/php83/evidence/return-contracts-sql/diagnostic-contract-r1.json
```

A new runtime repeat requires a named exclusive baseline74 handoff, fresh output
name and the explicit `observe.py --local ... --zip ... --output ...` command
recorded in the independent repeat prompt. No lab slot remains reserved here.

Actual OpenCode independently executed all36 tests and the comparator, returning
bounded PASS; see [public review](evidence/return-contracts-sql/finalreview-public.json).
A final comparator-only hardening phase then pinned the immutable38-file manifest
SHA and required the reported source map/stage pin to match it, preventing a
self-rehashed loaded-source map from authorizing itself. Two adversarial tests
bring the total to38. The prior reviewed comparator/report is preserved; the
[new comparison](evidence/return-contracts-sql/comparison-r2.json) still validates
the same frozen primary/repeat. No PHP probe, source, runner or runtime evidence
changed for this guard phase.
Actual OpenCode guard follow-up also exited0, executed38 tests and reviewed only
the authority-pin delta, finding no blocker:
[guard review](evidence/return-contracts-sql/guardreview-public.json).
Upstream full-source copies preserve their original whitespace; the separate
new harness/Markdown whitespace check is clean, not a claim that copied sources
have been normalized. No global whitespace exemption was added.
