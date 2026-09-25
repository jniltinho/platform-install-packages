# Held PDO boolean-result repairs

## Intentional public return correction

The preceding [real SQL audit](pdo-return-audit.md) demonstrated two existing
null/native-bool divergences. Two held patches now repair those return paths:

- `PropelPDO-bool-setAttribute.patch`: `setAttribute(): bool` returns the real
  parent result for native attributes, including false for unsupported attributes.
  The custom prepare-cache setter stores the same value and returns true to mean
  that its custom assignment was handled; it does not cast the assigned value.
- `KalturaStatement-bool-results.patch`: `execute(): bool` returns the saved
  parent execution result **after** existing log/monitor calls. Successful skipped
  dry-run writes return true without executing SQL. Actual dry-run SELECTs execute
  normally and propagate their result. PDO exceptions and the existing
  PropelException catch/rethrow remain unchanged. `bindValue(): bool` merely
  declares the boolean it already returned; its parameter defaults are unchanged.

This intentionally changes defective public **null returns to meaningful bools**;
it is not exact old return-value parity. It never converts an actual SQL failure
to unconditional success, casts null to false, weakens error reporting, or changes
transaction nesting. No experimental ZIP yet includes these held patches.

## Four real SQL variants

The fixture runs previous/candidate classes on PHP 7.4 and 8.3 using the approved
baseline74 private MariaDB and copied 8.3 runtime. The remaining exp8 application
is mounted read-only; candidate class overlays are private/read-only. Only these
classes support the measured 7.4 comparison, not the whole exp8 application.

Codex and Claude independently execute **29 cases × 4 variants**:

- Native and Propel attribute success/unsupported-attribute results.
- Custom prepare-cache storage and enabled/disabled statement identity.
- Nested commit, nested rollback/uncommittable commit and forceRollBack, including
  real row counts and transaction-depth/native transaction-state assertions.
- Native PDOStatement and real KalturaStatement success, failed SQL and input-array
  execution in silent, warning and exception modes; values 17/23 and SQLSTATE 42S02.
- Dry-run INSERT leaves zero rows, while dry-run SELECT returns 19.

The candidate has the native boolean result in all covered normal/failure paths.
The non-native custom setter and skipped-write cases explicitly return true.
Exception class/state, data, cache identity and transaction effects are unchanged.
The comparator permits differences only in the documented return-value positions,
while fixture assertions separately check their exact old and new values. Full
independent runtime-result objects match. Values agree across 7.4/8.3 for each
variant. Get_class assertions check actual connection/statement identity; each
process reports loaded-file SHA256 and reflected return contracts, which the
collector checks against patch metadata. The full base ZIP is verified before
and after the owned SQL run.

[Primary](evidence/pdo-bool/codex.json),
[independent](evidence/pdo-bool/claude.json),
[comparison](evidence/pdo-bool/comparison.json).

On 8.3, load-time deprecation groups fall from 8 to 5 in this fixture. The remaining
five belong to other PropelPDO methods, not resolved by these patches. Exactly two
intentional runtime E_WARNING controls remain (one native and one wrapper failed
SQL in warning mode); they are required rather than hidden. There is no claim
that the whole artifact API diagnostic count has changed before integration.

## Two retained harness/build corrections

1. The initial KalturaStatement diff produced by Python difflib did not encode
   the upstream missing-final-newline correctly. Strict isolated patch application
   failed even though the generated candidate PHP source passed SQL tests. The
   failed patch/metadata/audit remain in `attempts/eof-patch/`. Regenerating the
   unified patch with GNU diff preserves the proper no-newline marker. Original
   and candidate source bytes/hashes did not change. Final inventory verifies
   all 30 patches (3 active, 27 held) exactly; Cursor independently repeats it.
2. The first candidate 7.4 fixture used ReflectionType::__toString and generated
   three harness-only deprecations. Its probe, collector and both reports remain
   in `attempts/reflection-string/`. Switching to ReflectionNamedType::getName
   fixes the fixture without altering application bytes or suppressing warnings.
   The final collector explicitly requires only the two intended warning-mode
   runtime diagnostics. Codex and Claude repeat all four SQL variants afterward.

[Retained attempts](evidence/pdo-bool/attempts/),
[final patch inventory](evidence/pdo-bool/patch-inventory.json).
No failed check is reclassified as application success.

## Inheritance, callers and limitations

The preceding inheritance audit and refreshed exact-file coverage show no
setAttribute redeclaration in inspected KalturaPDO/DebugPDO/MSSQL descendants;
KalturaStatement has no descendant in the bounded graph trace. This is not proof
about external/dynamic subclasses. [Coverage](evidence/pdo-bool/coverage.json).
The other parent return declarations are deliberately not changed without their
corresponding subclass checks. This cycle does not execute MSSQL.

Logging, cache-side-effect and monitoring dependencies remain stubs. Their call
positions are preserved in source, but real side effects/exceptions are not yet
validated. No KalturaPDO constructor/bootstrap, PartnerActivity caller workflow,
API, shared cache or AIO/FPM acceptance is proved. A review found a direct execute
result assignment in PartnerActivity that is not subsequently used, but regex
search is not exhaustive caller analysis. Integration remains required before
promoting the patch or claiming behavior preserved for application consumers.

Other gaps: default/null binding, unsupported attributes in exception mode,
non-emulated prepare paths, dry-run SQL with comments/leading whitespace,
nonstandard custom-cache values, explicit return when disabling cache, and the
PropelException catch body. The original catch handles PropelException while
native SQL failures throw PDOException; this fixture preserves the latter and
must not be reported as testing both. Existing boolean bindValue returns did not
change, contrary to one fallback reviewer sentence grouping it with null returns.

## Reproduction, agent roles and gates

```sh
# After explicit first staging under /home/vagrant/php-pdo-bool:
python3 tools/php83/pdo-bool/collect.py /path/to/new-report.json
python3 doc/php83/evidence/pdo-bool/compare.py
```

Use exclusive baseline74 SQL ownership. The runner validates hostname/socket and
private datadir, and the fixture checks exact @@datadir before schema writes. A
new random unit/datadir is known before startup and stopped in finally; retained
datadirs are recorded, not deleted. Outputs contain synthetic values and reduced
errors, never raw SQL exception text, real configuration or tokens. Existing SSH
host keys/runtime binaries remain outside this cycle's revalidation; source-byte
verification does not verify filesystem permissions.

Claude independently executes/reviews real SQL, including the corrected fixture.
Cursor executes 136 local tests, reviews patches/overrides and independently reruns
the strict patch inventory after the EOF fix. Grok times out at 120 seconds, exit 124;
after termination, OpenCode Zen Muse Spark 1.3 Free executes 136 local tests and
reviews the first SQL evidence and patches. Its review predates the final fixture
getName correction, which changes no candidate application bytes. The local suite
does not supply new unit coverage of this collector. [Outcomes](evidence/pdo-bool/result.json).

No full acceptance task closes. Next is caller/real-bootstrap and combined
artifact API/SQL/HTTPS integration with explicit native-result expectations,
followed by remaining compatibility/distro/media/performance/recovery gates.
Package/CI integration, release and `.20` cutover remain separately gated.
