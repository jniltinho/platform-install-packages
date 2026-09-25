# Zend_Config native return contracts (held PHP 8.3 patch)

## Selected change and runtime boundary

`patches/php83/held/Zend-Config-return-types.patch` changes six signatures only:
`count(): int`, `current(): mixed`, `key(): mixed`, `next(): void`,
`rewind(): void`, `valid(): bool`. Bodies, visibility, parameters, state fields,
mutation policy and serialized representation remain unchanged. No blanket
compatibility attributes or diagnostic suppression are added to the application.

This is deliberately a **PHP 8.3-targeted source experiment**. Previously tested
candidates incidentally ran on 7.4 too; dual-runtime support is not the migration
contract. `mixed` is the universal type on 8.x but a class name on 7.4: parsing
alone is not compatibility. The runner refuses candidate execution on the 7.4
host; the unchanged original class on 7.4 remains the behavioral baseline.
A later combined ZIP must use original7.4 versus candidate8.3 regression, not
mislabel an expected candidate7.4 failure as a successful control. Original
archives and the exp6 artifact remain immutable. This page records focused
held-patch evidence; the subsequent [exp7 integration](exp7-config-integration.md)
adds it to a separately built ZIP and tests real API/CLI paths. Package/runtime
provider and release gates remain unchanged.

## Source and subclass checks

Actual native contracts were previously recorded in
[the native return triage](exp4-diagnostic-triage.md). The source shows count
written by constructor/set/unset using native `count`, current/key delegated to
native array operations, valid as a comparison, next with a bare-return skip
branch or no return, and rewind with no return. The int annotation relies on
normally constructed/application-produced configuration invariants; this does not
promise unchanged behavior for forged serialized protected `_count` values or
external subclasses overriding typed methods without compatible declarations.

Graph discovery/INHERITS and a literal source scan identify direct Ini/Xml and
transitive scheduler/task/worker-status subclasses. The six selected methods are
not redeclared in those inspected source files. This is bounded source evidence,
not proof no dynamically generated or externally installed subclasses exist.
[Coverage](evidence/config-return/coverage.json) is metadata-matching, best-effort
at generation `2026-09-25T12:19:00Z`.
[Exact file hashes/declarations](evidence/config-return/source-inspection.json).

## Executed fixture

`tools/php83/config-return/` mounts the byte-verified exp6 application read-only.
Only the candidate class gets a private read-only bind overlay. The unprivileged
PHP process has a private network, socket syscalls denied, private temp directory,
read-only system/home protection and inaccessible production application path.
Synthetic INI files stay in private temp; XML is a literal synthetic string.
No real bootstrap, database, scheduler constructor, or worker script runs.

Sixteen result rows agree exactly across original7.4, original8.3 and candidate8.3:

- Empty, scalar/null/nested values and mixed numeric/string keys; strict counts,
  iterator exhaustion and null return of void operations.
- Unset-current skip branch, insertion/update counts, merge result/identity,
  clone isolation and byte-preserving serialized roundtrip.
- Read-only set/unset/nested-set exceptions after merge and setReadOnly.
- Real Ini/Xml constructors with section inheritance.
- Real scheduler/task classes loaded, with constructor bypass and base storage
  initialized explicitly; inherited methods and count tested, not orchestration.
- Foreach unset-current traversal with absolute expected sequence.
- Mid-iteration clone and serialize observations compared to baseline, preserving
  existing pointer/index quirks rather than silently redesigning iteration.
- Mixed object return identity.

The fixture captures E_ALL diagnostics and the collector enforces them: original
8.3 emits exactly six return-contract deprecations; original7.4 and candidate8.3
emit none. Six reflected candidate signatures are checked independently of row
parity. The initial 12-row probe and output are retained with its original source;
four additional controls were added before the independent rerun.

[Final primary](evidence/config-return/codex-expanded.json),
[independent Claude](evidence/config-return/claude.json),
[comparison](evidence/config-return/result.json).

```sh
# After explicit first-time staging of probe.php, run.sh, candidate.php into
# /home/vagrant/php-config-return on the two approved isolated labs:
python3 tools/php83/config-return/collect.py /path/to/new-report.json
```

The collector refuses overwriting evidence, verifies probe/candidate hashes and
the entire base ZIP before/after each lab, checks every row/contract/warning and
fails on unexpected process exit. Its small report is synthetic only; it must not
be repurposed to capture real configuration/secrets. Original baseline runtime
binaries are not rehashed, SSH host keys are not pinned by existing aliases, and
base verification does not verify filesystem permission bits.

## Independent roles and remaining gaps

Claude repeats the runtime collector and reviews Codex outputs/patch. Cursor
executes 122 local tests and independently reviews source/signature/subclass risks.
Grok times out at its 120-second bound; after termination, OpenCode Zen
`opencode/muse-spark-1.3-contributor-free` executes the 122 tests and independently
reviews patch/fixture/collector. Local tests do not exercise the new live-runtime
fixture. Cursor also executes the unsupported-runtime guard on baseline74: exit64 with
empty stdout/stderr, before any mount or PHP invocation per the runner. It checks
full equality of the independent runtime reports. Exact CLI outcomes and report
identities are retained separately. The patch inventory now passes strict hash
and isolated application checks for 27 patches (3 active / 24 held).

Cursor's suggested “7.4 parse error” is incorrect: mixed-as-class behavior, not
parse failure, is the reason candidate7.4 is unsupported. Its direct-subclass
statement does not cover all transitive subclasses; the source inventory and two
loaded scheduler classes above supplement it. OpenCode correctly flags omitted
malformed/missing-section INI/XML paths and scheduler constructor coverage; the
fixture does test nested read-only behavior after merge, contrary to that review
item. Claude incorrectly described the initial report as replaced: it is retained
alongside its original probe; the expanded report is the current evidence.
Mid-iteration copy state is observed before rewind, but continuation without
rewind and direct protected-index assertions remain untested. Advisory prose is
not authoritative test evidence.

The later exp7 cycle supplies bounded combined ZIP/API SQL/HTTP/trusted-TLS and
CLI integration. Remaining work includes broader service/cache use, malformed
config/error paths, scheduler constructors,
external subclass inventory, and full AIO/media/distro/performance/recovery tests.
These 16 rows do not establish full application acceptance or resolve all return
contracts elsewhere. No acceptance checkbox or release gate closes.
