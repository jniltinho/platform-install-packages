# Exp12 return-contract family: held local preparation

**Latest: nine native83 observations independently repeated by actual Claude
after explicit operator access confirmation. Not selected, not a release.**
Historical local-preparation phase: five delta patches against
pinned exp12 change eleven native return declarations and add exactly three
method-level ReturnTypeWillChange attributes. No body, cast, parameter, default,
logging, cache, SQL or serialization change. Ten local builder tests pass; they
prove guards/byte transformation, not runtime behavior.

See [manifest](../../patches/php83/held/return-contracts/manifest.json),
[preparation](evidence/return-contracts/preparation.json) and
[diagnostic plan](exp12-diagnostic-families.md). This is a delta against exp12,
not a cumulative patch against upstream; stacking it incorrectly must be rejected.

## Concrete scope

- KalturaPDO: exec `int|false`, query/prepare `PDOStatement|false`.
- PropelPDO: getAttribute `mixed`, prepare `PDOStatement|false`.
- PropelConfiguration: ArrayAccess exists/set/get/unset `bool/void/mixed/void`.
- KalturaAPIException: __wakeup `void`.
- DebugPDO: prepare `PDOStatement|false`, required by the typed userland parent.
- PropelPDO only: beginTransaction/commit/rollBack get scoped attributes instead
  of a native bool type. Both MSSQL subclasses remain byte-identical.

[PHP's official ReturnTypeWillChange documentation](https://www.php.net/returntypewillchange)
supports a method-level temporary exception when an overriding return is
incompatible. Here both real MSSQL implementations return exec's int|false on
outer operations, true on nested/no-op operations. Forcing bool would alter their
observable values; declaring int|bool under a bool userland parent would be invalid.
Three parent attributes avoid adding a userland return constraint. This defers
full transaction typing; **it does not repair the MSSQL return API**. No blanket
error-level suppression or attribute on an entire hierarchy is introduced.

## Inheritance audit and blockers

Graph INHERITS yielded four edges: KalturaPDO→PropelPDO, DebugPDO→PropelPDO,
MssqlPropelPDO→PropelPDO, MssqlDebugPDO→DebugPDO. A follow-up for the two MSSQL
classes returned no edges, which is not a proof of complete dynamic inheritance.
Exact seven-file coverage is recorded; all seven complete bodies were read from
the exp12 ZIP. Wider graph scopes contain parse gaps; no broad absence claim is
made. Before acceptance, a pinned full-source token-level declaration inventory
and all discovered class load combinations must supplement graph findings.

**DebugPDO remains blocked before and after this preparation:** its selected
exp12 query declaration is still the original no-parameter signature. The held
v3 forwarding repair is not silently included. [Prior v3 proof](debug-pdo-experiment.md)
records separate PHP74/83/SQL experiments and an old review; that is not a current
exp12 composition proof. Explicitly review its pinned patch, decide prerequisite
selection, then stage prior-with-prerequisite and candidate-with-prerequisite
controls plus untouched-exp12 expected-failure control. No patch can be promoted
by treating this class load failure as a pass.

## Execution plan (not yet run)

1. Fresh independently reviewed source staging, all source/patch/harness/runtime
   hashes before and after. Confirm native PDO/ArrayAccess/Exception tentative
   signatures and exact declaration diagnostic messages in a secret-free process.
2. Real full classes, positive and negative load tests. Preserve original DebugPDO
   fatal as a separate expected negative, never an accepted class hierarchy.
3. Three independently isolated focused corpora: real SQL PDO transactions/cache/
   failure modes; ArrayAccess typed values and existing typo warnings; exception
   legacy serialization/wakeup. Reuse the prior SQL audit's owned socket/datadir
   safeguards, but update runtime identities and exact selected exp12 bytes.
4. Attribute controls: inspect attributes on exactly three methods; retain an
   unrelated deprecation to prove no blanket suppression. Exercise unchanged
   MSSQL source with explicit synthetic exec seams separately if the real MSSQL
   driver is unavailable; label seams, and keep real backend acceptance open.
5. Primary plus actual independent repeat of full API/CLI/addition corpora. Predict
   only the twelve confirmed groups/274 events disappear; do not enforce the
   prediction before native attribution confirms it. Full-source native83 compile,
   typed values/errors/cache format and all other diagnostics remain controlled.

No VM ownership has been acquired for this family. PHP8 union/mixed types mean
candidate74 is unsupported; original74 helper cohorts are historical controls.

## Reproduce preparation

```sh
python3 -m unittest discover -s tools/php83/return-contracts -p 'test_*.py' -v
python3 tools/php83/return-contracts/build.py \
  --zip ../platform-install-packages-php83-artifacts/exp12/Rigel-18.20.0-php83-experimental.exp12.zip \
  --output /tmp/php83-return-contracts-new-unique-directory
```

The builder refuses existing output directories, source/ZIP/selection hash drift,
missing/duplicate declarations and candidate collisions. Reverse substitutions
must reproduce original bytes. Actual PHP token validation, strict patch replay,
full-source runtime and independent patch review remain prerequisites.

## Explicit prerequisite composition follow-up

After initial review, the coordinator authorized including held DebugPDO v3 as an
explicit experimental prerequisite (not artifact selection). `compose.py` now
constructs three seven-file cohorts from the pinned full exp12 ZIP: untouched,
v3-only and v3+return-family. Strict zero-fuzz/no-offset patch replay and independent
order reversal prove the v3 forwarding edit commutes with the prepare declaration.
[Composition identities](evidence/return-contracts/composition-preparation-r2.json)
record every cohort/source SHA. No whole archive is rebuilt or promoted.

Actual OpenCode Muse free ran the initial ten builder tests (exit0) and reviewed
all five patch files, guards and the scoped attribute rationale; it did not run
PHP or review the later composition helper. The later local suite has fifteen
passing tests. Its initial three synthetic path-setup errors are preserved in
composition-local-tests-initial-fail.txt; `exist_ok=True` corrected the fixture
parent-directory handling. The corrected composition report is byte-identical
to the initial real preparation. Independent composition/harness review and
native83 execution remain pending. The earlier manifest's open prerequisite
records the initial family-only phase, not the new composed cohort's selection.

## Native-only observation runner (pending independent review)

The prepared `observe.py` phase has nine processes (three cohorts × hierarchy,
configuration, exception). It mounts the complete existing exp12 tree read-only
and exact seven-file overlays. No database connections or generated application
execution occur. Hierarchy rows reflect all concrete PDO descendants together;
configuration rows exercise real ArrayAccess; exception rows explicitly bypass
APIErrors construction via reflection and exercise only real sleep/wakeup/legacy
serialization. Constructor/API dispatch acceptance is not inferred from this.

The observer persists each result incrementally, records raw safe fixture stderr,
checks full source/stage identities before/after and collects native binary,
module, linked-library and INI identities. Even a complete matrix returns exit2
with OBSERVED_NOT_ACCEPTED until a separate reviewed outcome contract exists.
No native call has yet been made for this preparation checkpoint.

Actual Claude native-prep review failed with session quota (exit1, no tests),
not an approval. The OpenCode fallback is separately recorded. Prior to fallback,
author review found two guard issues: verifier banners would contaminate probe
JSON stdout; and a freshly rehashed arbitrary source map could self-authorize.
The r2 runner silences only verifier success banners (not PHP diagnostics), and
observer checks a pinned composition report for every source map before staging.
Twenty-six local tests pass. Historical v1 scripts and failed CLI evidence remain.

## Historical native83 primary observations and initial blocked repeat

The nine processes completed; collector exit2 is intentional observational status.
[Primary](evidence/return-contracts/native-primary.json),
[bounded summary](evidence/return-contracts/native-primary-summary.json).
Full source/stage/runtime before/after identities are equal. No baseline74 use.

- Untouched exp12 hierarchy: exit255 at pre-existing DebugPDO::query signature.
- v3-only and v3+family full seven-class hierarchy: exit0, 29 reflection rows each.
- Native hierarchy diagnostics: 16 → 4. Retained controls are DebugPDO exec/query
  and both MSSQL lastInsertId methods; their messages remain visible on stderr.
- Exact native path/line/source-hash joins corroborate the twelve proposed API
  groups / 274 historical events. This is [new secret-free attribution evidence](evidence/return-contracts/native-attribution.json),
  not recovery of previously discarded raw API stderr or a new API execution.
- Configuration: eight typed output rows identical across all three cohorts;
  diagnostics16→12 retain dynamic singular parameter and missing-key warnings.
- Exception: six wakeup/serialized-byte rows identical across all three cohorts;
  declaration diagnostic1→0. Constructor/APIErrors bypass remains explicit.
- No SQL behavior, API HTTP result, full oracle, application acceptance or artifact
  selection follows from these observations.

Actual OpenCode independently reviewed the native-prep runner, ran26 local tests
and shell syntax (all0). Its later runtime-repeat attempt exited CLI0 but **did
not execute the runtime collector**: a combined tool call was explicitly denied.
The command requested sha256sum and cat of
`/tmp/php83-return-contracts-native-prep-r2/identities.json`, an optional local
`diff_match_patch` import and a local observer diff. Exact command/error retained
in [public failure report](evidence/return-contracts/opencode-native-repeat-public.json).
No retry, alternate-agent bypass or relocation of the denied object occurred.
Operator authorization for that specific access is needed before resuming it.
CLI0 is not independent PASS. Future preparations will originate repo-locally;
this does not authorize moving the denied existing stage to evade its restriction.

Native83 was released after primary/CLI termination. A separately requested,
read-only command-availability check found mariadbd, mariadb-install-db,
mariadb-admin and mariadb all absent. Nothing was installed and runtime39 was
unchanged. See native-sql-tool-availability.* evidence. Real SQL therefore needs
the existing baseline74 private MariaDB tooling and copied83 runtime after the
rehearsal owner releases it, or a separately authorized provisioned test server.

## Next real SQL/API contract — preparation only, no VM

Reuse the existing `pdo-return-audit` corpus/lifecycle design, not its old source
pins or blanket error-handler suppression. Build a versioned full-exp12 overlay
cohort and retain the original74 historical helper control where compatible;
never run the union/mixed candidate under74. Both v3-only and v3+family run under
copied83 on independently owned fresh socket-only datadirs. Check native PDO
`@@datadir` equals the exact newly registered owned path before schema writes;
stop the exact transient unit in finally and retain post-failure identities.
Never use an existing application database or infer ownership from a path prefix.

Expand real full-class coverage to PropelPDO, KalturaPDO and DebugPDO. Cases:

- successful/zero-row/failed exec and query, missing/null/named query arguments,
  ERRMODE_SILENT versus ERRMODE_EXCEPTION, exact exception class/SQLSTATE and
  strict typed values (no Python bool==int shortcut, no cast-to-int assertions);
- prepare cache on/off, repeated SQL object identity, prepare false/error path,
  bound values and result data, real statement class; logging/query counting
  must retain v3 semantics;
- nested commit/rollback/force rollback and no-active wrapper behavior, counter
  and physical transaction state, persisted versus rolled-back rows;
- custom attribute mixed inputs (false, zero, string-zero, null) and native
  getAttribute results; preserve types, do not coerce cache values;
- actual selected KalturaStatement interactions and dry-run behavior from prior
  selected repair, without dropping previous patches;
- MSSQL branches require separate backend or explicitly labelled synthetic exec
  seam tests. MySQL success is not MSSQL backend validation; retained untyped
  transaction contract remains a documented exception rather than claimed bool.

Fixtures may isolate logging/monitor boundaries only when named and hash-pinned;
PDO/KalturaPDO/DebugPDO classes and methods themselves must not be replaced.
Finally repeat the unchanged full API/CLI/addition corpora, compiler checks and
independent execution; expect only declared diagnostics to change after exact
source-line remapping. API security outcomes, serialization layout and typed
values remain gates. No new package/build/release selection is requested here.

## Authorized independent native83 repeat — current checkpoint

Following explicit operator confirmation of the requested temporary/SSH/lab
accesses, actual Claude CLI executed26 local tests, shell syntax and the same
nine native83 observations. No new operation was denied. Collector exit2 remains
`OBSERVED_NOT_ACCEPTED`, not automatic success: the coordinator verified all nine
records and ten identity/status fields by canonical JSON, preserving scalar types,
array order, raw stdout/stderr and diagnostic contents. Expected original exp12
hierarchy failure255 remains; the other eight processes exit0. Source and runtime
snapshots match primary and each other before/after. No SQL/API/constructor ran.

[Independent report](evidence/return-contracts/authorized-r1/native-repeat.json),
[coordinator comparison](evidence/return-contracts/authorized-r1/coordinator-comparison.json)
and [public CLI execution](evidence/return-contracts/authorized-r1/claude-public.json).
Only the reviewed reuse-option collector identity/flag and snapshot output paths
differ in metadata; no process record was normalized. The native83 reservation was
released after terminal completion, not during execution. Baseline74 was not used.

Provenance correction to the retained Claude conclusion: the primary collector
is preserved byte-exact as `evidence/return-contracts/primary-observe.py`, committed
in `c4f3ea84`. Its hash equals the primary report's recorded collector hash. It is
not untraceable merely because it was not committed at the live `observe.py` path.
Claude is the independent repeat executor relative to Codex's primary; its own
comparison was additionally checked by the coordinator, not falsely called a
second independent runtime executor.

The historical denial remains above as an earlier failed attempt. This closes
that execution gap only. Real SQL/typed effects, API integration, constructor
coverage, full artifact regression and release acceptance remain open. No held
source patch or ZIP was promoted by this repeat.
