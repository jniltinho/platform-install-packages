# DebugPDO signature experiment — held

Date: 2026-09-25. Scope: OpenSpec `migrate-kaltura-php83`, task 1.6
(partial). This is not application acceptance or a deployment artifact.

## Change and result

`patches/php83/held/DebugPDO-query.patch` changes only the declaration from
`query()` to `query($query = null, ...$fetchModeArgs)`. The original body,
argument forwarding, logging and query accounting remain unchanged.
Hashes are recorded in the adjacent JSON. It is **not** in the active manifest.

| Runtime/tree | Execution | Strict stdout parity with original 7.4 |
| --- | --- | --- |
| PHP 7.4.33 original | passes | baseline |
| PHP 7.4.33 candidate | passes | passes |
| PHP 8.3.6 original | fatal incompatible query declaration | fails |
| PHP 8.3.6 candidate | passes fixture execution | **fails** |

In this SQLite fixture, 7.4 returns selected numeric values as strings and
8.3 as integers. An independent native PDO `SELECT 1` control reproduces the
difference; DebugPDO matches native PDO strictly within each runtime. This
isolates a driver/runtime difference in this test, **not** a finding about the
production MySQL configuration. No normalization or application setting was
added to make the gate pass.

Coverage: default/associative/column/class fetches (including constructor
argument forwarding), custom DebugPDOStatement, prepared binding/execution,
query count and last-query text, rollback, exception-mode error and silent-mode
error. Logging is disabled through synthetic Propel configuration. Return-type
and `parent`-callable deprecations remain visible in captured stderr.

## Safety and reproduction

Only disposable `.74`/`.83` copies were patched. `php7.4-sqlite3` and
`php8.3-sqlite3` were downloaded via each lab's existing apt sources and extracted
with `dpkg-deb -x`; **not installed**, no INI/service changes. Package versions,
package/module hashes and tested candidate hashes are in
`evidence/debug-pdo/php74-inputs.txt` and `php83-inputs.txt`.

Place the extracted module at
`/home/vagrant/php-patch-tests/sqlite/extracted/usr/lib/php/<ABI>/pdo_sqlite.so`
(ABI 20190902 for 7.4, 20230831 for 8.3), copy the harness files, and apply the
held patch only to the candidate tree. The wrapper loads that module per
invocation and runs as nobody with a read-only tree, no sockets/private network
and SQLite `:memory:`. It does not load application configuration or credentials.

```bash
python3 tools/php83/patch-tests/collect.py /tmp/debug-pdo.json \
  --case debug-pdo --mode standard
# Exit 1 is expected: the PHP8.3 strict parity gate currently fails.
```

`behavior.json` includes outputs, diagnostics and fixture hashes. Its environment
records describe the standard PHP process; the extra SQLite module is loaded
only for `debug-pdo`, with provenance recorded separately. After collection,
DebugPDO in both candidate trees was restored from the original packaged copy,
leaving the exp2 JSON-only candidate state. The exp2 ZIP was not rebuilt.

## Reviews and next gates

Claude and Grok were asked to review the patch and initial fixture using their
CLIs with tools disabled. Their opinions are advisory, not test evidence. The
native-PDO control was added after submitting the review input.

Claude identified a possible named-argument loss: `fetchMode:` lands in the
variadic parameter but the old body forwards `func_get_args()`. This requires
an explicit PHP8-only test before any promotion. Also pending: explicit null
fetch mode, missing arguments, FETCH_INTO/PROPS_LATE, enabled logging, subclass
overrides, and real isolated MySQL tests. A stringify-fetches variant may be
useful diagnostically but must not replace the failing default comparison.

All 27 offline Python tests pass; all eight JSON-only differential comparisons
still pass (see `json-regression.json`). Neither result closes the migration's
broader gates. `.20`, main, releases and the active patch manifest are unchanged.

## Follow-up: forwarding variant v2 (2026-09-25)

The completed Grok review is saved as `evidence/debug-pdo/grok-review.txt`.
Both reviewers requested native-PDO controls and boundary tests; their initial
review input predates the native control and the separately recorded module
identities. Those findings were addressed with evidence, not assumed approval.

The new `debug-pdo-edges.php` fixture confirmed that v1 silently discards named
`fetchMode:` and unknown named arguments on 8.3. The valid FETCH_NUM call returns
associative rows instead of numeric rows; the unknown-name call succeeds where
native PDO throws. Both failures reproduce under exception and silent modes.

`held/DebugPDO-query-v2.patch` is a **standalone alternative**, not an incremental
patch to apply after v1. It explicitly declares `$fetchMode`, retains positional
arity via `func_get_args()`, appends string-keyed variadic arguments so the parent
can reject unknown names, and dispatches with `parent::query(...$args)`. This
removes the deprecated parent callable from this method without suppressing
other diagnostics. It targets the tested PHP7.4/8.3 pair, not historical PHP5.

Evidence in `evidence/debug-pdo/v2/`:

- `edges.json`: eight native-PDO return/error comparisons on 7.4 and twelve on
  8.3 pass for v2; covers positional column index, null mode, zero arguments,
  null SQL, and (8.3 only) valid/unknown named arguments in both error modes.
  Query accounting is recorded, not asserted as equivalent to native PDO.
  Module version and available drivers are emitted in the actual test process.
- `behavior.json`: original/patched 7.4 default behavior matches. Patched 8.3
  default strict parity **still fails** on numeric types. A separate explicitly
  named `debug-pdo-stringify` diagnostic passes on both runtimes. It sets the
  attribute only on fixture connections; it is not a production setting or a
  replacement for the failing default gate.
- `source-checks.json`: tested source hashes and successful syntax checks for
  both runtimes. Patch/input/output hashes are in the v2 patch JSON.
- `json-regression.json`: all eight existing JSON differential comparisons pass.

The edge fixture is diagnostic rather than a cross-runtime acceptance case;
invoke `run-one.sh candidate debug-pdo-edges standard` inside either lab. Its
PHP8-only named-call syntax is in fixed eval strings, never user input. The
collector supports `--case debug-pdo-stringify --mode standard` separately from
`--case debug-pdo`. Existing 27 offline tests still pass.

V2 remains **held**. Missing return-type diagnostics, enabled logging, broader
fetch modes/subclasses and isolated MySQL/API behavior still need validation.
No migration gate was relaxed, no active manifest changed and no ZIP rebuilt.

After collecting v2 evidence, both lab candidate DebugPDO files were restored
to original hash `6178d39fd2c11c2bd2dcc220c4234f72dfb11364c11d381e7f7bfaf55089e021`.
The v2 patch was also applied from scratch locally with zero fuzz and its output
hash matched the tested source hash.

Claude's v2 review is retained as advisory text. Some suggestions concern
coverage already present: E_ALL stderr is captured and FETCH_CLASS constructor
arguments are exercised by `debug-pdo.php`, though not by the edge-only fixture.
Claims about PHP versions outside 7.4/8.3 were not validated or used for approval.
The graph-discovered `vendor/propel/adapter/MSSQL/MssqlDebugPDO.php` was coverage
checked (generation 2026-09-25T12:19:00Z, metadata match, no recorded gap) and read:
it inherits query without overriding it. This is a bounded source check, not
an exhaustive subclass audit or MSSQL runtime test.

## Extended v2 controls: logging and fetch semantics

Evidence: `evidence/debug-pdo/v2-extended/`. The source patch is unchanged.
The added logging fixture enables synthetic Propel logging to an in-memory
logger, with deterministic method/query-count prefixes and slow-only filtering
disabled. It asserts exact messages, count and last-SQL state after success,
exception-mode failure and silent-mode failure. Both patched runtimes match
unpatched 7.4 byte-for-byte (`logging.json`). This does not cover real log
destinations or timing/memory/slow-query prefixes.

The extended edge fixture adds FETCH_INTO identity, FETCH_PROPS_LATE constructor
order, mixed positional/named arguments and the variadic parameter name. All
12 native-return/error controls on patched 7.4 and all 20 on patched 8.3 pass.
The new collector also asserts expected successful values for positive cases:
two identical exceptions must not accidentally count as a successful fetch.
Original/patched 7.4 edge output matches byte-for-byte. Diagnostics remain in
stderr and are not waived; native warning parity is not asserted.

```bash
# Requires the held v2 patch applied to disposable candidate copies only.
python3 tools/php83/patch-tests/collect-pdo-edges.py /tmp/edges.json
python3 tools/php83/patch-tests/collect.py /tmp/logging.json \
  --case debug-pdo-logging --mode standard
python3 -m unittest discover -s tools/php83 -p 'test_*.py'
```

Six offline collector tests cover success, execution failure, wrong original
failure, equal-error false positives, missing cases and native mismatch. All 33
offline tests and all eight JSON regression comparisons pass. Source/module
identities remain those recorded for v2; the new reports pin the changed harness.
After collecting evidence, both lab candidate DebugPDO files were restored to
the original hash listed above. Active manifest, exp2 ZIP, main and `.20` remain
unchanged. No migration task is marked complete.

The v2 Grok CLI review still had no response at collection time; it is not counted
as approval. Next: isolated MySQL numeric/JSON behavior and remaining runtime
diagnostics, without applying stringify-fetches globally or waiving default
parity. These SQLite controls alone do not prove application compatibility.

## V3: preserve missing versus explicitly null SQL

The Grok v2 finding was reproduced: `query(fetchMode: PDO::FETCH_NUM)` raises
native `ArgumentCountError`, while v2 raised `ValueError` after injecting its
optional null SQL default. An explicitly supplied null query raises ValueError
on both. See `evidence/debug-pdo/v3/v2-counterexample.json`; both error modes
were exercised. V2 must not be promoted as-is.

Held v3 is a smaller standalone alternative: `query(...$args)` directly calls
`parent::query(...$args)` without reconstructing or adding arguments. After the
parent returns, logging selects the named `query` key if present, otherwise
the original positional key. PHP7.4's legacy zero-argument behavior, including
its diagnostic, remains unchanged; PHP8.3 delegates missing-argument rejection
to PDO. It is not stacked after v1/v2.

Recorded results under `evidence/debug-pdo/v3/`:

- 36 native return/error controls pass: 12 on 7.4, 24 on 8.3. The collector also
  checks successful expected values, not only equality of two failures.
- Logging now exercises named SQL on 8.3 versus positional SQL on 7.4; exact
  message/accounting parity passes, including subsequent query failures.
- SQLite default numeric-type parity still fails. The separate stringify
  diagnostic passes but remains diagnostic only.
- The disposable MariaDB matrix was repeated for v3. All native-PDO controls
  pass; the same cross-runtime difference persists only in the tested
  emulated-prepares/stringify-false configuration. No global attribute changed.
- Source hashes match both labs; syntax checks and zero-fuzz patch application
  pass. All 33 offline tests and eight JSON comparisons pass.

Claude reviewed the v3 forwarding diff without tools and reported no apparent
forwarding regression. The advisory review is saved; its request to repeat
MySQL was completed after submission. Return-type diagnostics, broader
inheritance/caller reachability and application hydration/API contracts remain
open. No release approval or broad task completion follows.

The disposable DB server was stopped and both candidate DebugPDO files restored
to their original hash after testing. V3 remains held outside the active
manifest; exp2, main and `.20` are unchanged.
