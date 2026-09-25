# Held reflection-parameter compatibility repair

Candidate patch: `patches/php83/held/KalturaActionReflector-parameter-class.patch`.
It replaces two deprecated `ReflectionParameter::getClass()` calls with one
scoped resolver using type reflection, then reuses that result. No error-policy,
property, parameter default, authorization or serialized-format change is selected.
The original exp5 ZIP remains unchanged. This page records the held-patch
validation before integration. The subsequent separate
[exp6 experiment](exp6-reflection-integration.md) integrates it and records actual
SQL/HTTP/TLS and CLI execution; its storage under `held/` does not imply release
approval or promotion into the active exp2 manifest.

## Native observations changed the implementation

A named-type-only replacement would be incorrect: actual PHP 8.3 native reflection
returns the class component for `ClassName|int`, but null for two-class unions,
intersections and the tested DNF combinations. The resolver preserves those
observed distinctions; this does not add general union-type support to the API.
It instantiates a ReflectionClass only after establishing a single class component,
resolves self/parent through the declaring class (including inherited methods),
and preserves missing-class errors instead of replacing them with doc fallback.

The first implementation failed the uppercase `SELF` control on both runtimes.
That failure is retained under `attempts/case-sensitive/`. The final resolver uses
case-insensitive keyword comparisons and also tests uppercase `PARENT`. No failing
case was deleted or turned into an accepted exception.

## Executed controls

| Layer | PHP 7.4.33 | PHP 8.3.6 | Comparison |
| --- | ---: | ---: | --- |
| Native ReflectionParameter vs resolver | 15 cases | 22 cases | Exact class/error, optional and nullable observations match |
| Real KalturaActionReflector metadata | 17 cases | 24 cases | Types/options/defaults/errors and serialized parameter hashes match within each runtime |

Native cases include untyped, builtin scalar/array/callable/object, named class,
nullable class with/without default, inherited self, self/parent (including upper
case), missing class, one-class/scalar union, two-class union, iterable union,
missing-class union, mixed, intersection and DNF where supported. The PHP 7.4-only
parent-without-parent control retains its pre-existing declaration warning/error;
that syntax is not loaded in the PHP 8 fixture.

The real-metadata fixture boots the application, adds doc-comment fallback,
reserved-name and missing-doc controls, and calls `getActionParams()` twice to
verify in-object cached metadata. It uses the actual exp5 classes. Candidate code
is a private read-only file bind over the class, not a mutation of the extracted
ZIP. Full ZIP byte verification runs before and after collection.

On PHP 8.3 the native control has 22 getClass diagnostics and the candidate has
none; real metadata has 42 before and none after. These are **focused counts**,
not the 84 historical exp5 API events. The latter reduction remains unmeasured
until real API integration. Bootstrap diagnostics remain visible separately.

[Primary complete report](evidence/reflection-repair/codex.json),
[native 7.4 rows](evidence/reflection-repair/74-native.json),
[native 8.3 rows](evidence/reflection-repair/83-native.json),
[real metadata 7.4](evidence/reflection-repair/metadata-74-candidate.json),
[real metadata 8.3](evidence/reflection-repair/metadata-83-candidate.json).

## Scope and reproducibility

```sh
# Requires the already approved, pre-staged private reflection-probe lab folder.
python3 tools/php83/reflection-probe/collect.py /path/to/new-report.json
# Independent executors can own one VM each:
python3 tools/php83/reflection-probe/collect.py --runtime 74 /path/to/new-74.json
python3 tools/php83/reflection-probe/collect.py --runtime 83 /path/to/new-83.json
```

The collector pins candidate/original/fixture/bootstrap hashes, checks actual exp5
source bytes, rejects missing cases and refuses existing evidence paths. Runs use
nobody, private config/cache/tmp, read-only binds, network/socket denial, time/memory
limits and inaccessible production paths. The low-level native fixture stubs only
the unused reflector base class so it can invoke the real private helper; the
real-metadata fixture uses the full bootstrap and real base class instead.

No real KS, DB connection, remote API or user data is used. Synthetic warnings and
bootstrap stderr are retained, not suitable for a live-data capture tool. Direct
reflection calls and private file overlays do not prove full dispatcher behavior,
shared APC/APCu persistence, autoloader side-effect parity, every possible type
combination, PHP versions other than the two recorded, or full application
acceptance. Cross-runtime serialized hashes are not asserted identical: comparison
is before/after **within each runtime**.

The graph generation remains `2026-09-25T12:19:00Z`; checked reflection files have
matching metadata and no recorded issue (best effort). Outbound graph resolution
contains heuristic edges for generic method names; actual ReflectionParameter
behavior here is established by source reads and executed native controls, not
by assuming those generic edges identify the correct target.

[Strict patch inventory](evidence/reflection-repair/patch-inventory.json) now has
26 patches (3 active exp2 / 23 held). No acceptance checkbox or release gate closes.

## Independent validation

Claude reran PHP 7.4 and Cursor reran PHP 8.3 on separate labs; their full records
match Codex's corresponding slices exactly, including warning arrays, errors,
serialized hashes, source and fixture identities. Grok timed out (124); OpenCode
Muse Spark Free then ran the 122 local tests and independently reviewed the
reports and held patch. Local suite remains 122 tests; it does not contain new
mocked tests for this collector. CLI outcomes and gaps are explicit in
[`result.json`](evidence/reflection-repair/result.json).

The subsequent exp6 cycle measures removal of the 84 historical API reflection
events in its bounded SQL/HTTP/trusted-TLS matrix. Actual shared service
reflection/cache coverage remains required. In-object cache reuse here is not
APC/APCu persistence or cross-process invalidation.
