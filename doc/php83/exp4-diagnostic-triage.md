# exp4 remaining diagnostics: repair batches, not accepted exceptions

This review accounts for **all 40 severity/path/line groups and 1,073 events in
one bounded API matrix**. It is not a complete static-source finding inventory,
40 unique bugs, or a full application acceptance assessment. The exp4 source ZIP
is pinned to `a1ce4c46792667b07a733e622a3ee71dd01c87a94f7841edfc72d58746ab9d08`.
No source patch, build, package or production change is made by this triage.

## Accounting

| Source-supported candidate cause | Groups | Events | Required next evidence |
| --- | ---: | ---: | --- |
| Native/interface return contracts | 27 | 618 | Inspect every return branch/subclass; compare native return types and actual call behavior |
| Dynamic properties | 2 | 156 | Identify owning class; visibility/default/isset/serialization/copy behavior |
| Null arguments to string/serialization functions | 5 | 142 | Confirm actual argument types; explicit-null controls, invalid-input controls, permission/API parity |
| Deprecated reflection getClass | 2 | 84 | Class/builtin/nullable/self/parent/union handling and API metadata parity |
| Legacy Serializable implementations | 2 | 48 | Preserve old serialized payload readability; define new write format/cache interoperability |
| Deprecated libxml entity-loader call | 1 | 24 | Preserve entity/DTD protections; explicit XML security corpus on both runtimes |
| Optional parameter before required parameter | 1 | 1 | Call/reflection/default metadata tests before signature edit |
| **Total** | **40** | **1,073** | **None accepted as resolved** |

[Exact locations and artifact source excerpts](evidence/exp4-triage/locations.json)
pin each source SHA256; [classification](evidence/exp4-triage/classification.json)
accounts for each observed group once. Raw diagnostic text was intentionally not
retained by the API collector because logs may contain KS/SQL/secrets. Accordingly,
classification from the source location is a **source-supported hypothesis**,
not fabricated recovery of the original warning message. Confirm individual
causes with minimal non-sensitive reproductions before patching.

## Native-runtime evidence

Codex executed the read-only `tools/php83/diagnostic-triage/native-contracts.php`
through the existing hostname-guarded SSH lab aliases, using `/usr/bin/php7.4`
and `/usr/bin/php8.3`. It only reflects built-in classes/interfaces: no app source,
DB connection, disk write or network operation inside PHP. Both executions exit
0 and record 22 method contracts. PHP 7.4.33 reports no tentative return types;
PHP 8.3.6 exposes bool/int/void/Traversable plus mixed/union contracts.
[Native 7.4](evidence/exp4-triage/native-74.json),
[native 8.3](evidence/exp4-triage/native-83.json).

This establishes the actual interpreter contracts, not safety of adding them to
legacy subclasses. A bool annotation must not turn an existing null/false/int
branch into a silent conversion; void can conflict with existing return values.
PHP-8-only mixed/union syntax cannot simply be inserted while claiming 7.4
parse compatibility. No mass `ReturnTypeWillChange` change is approved here.

## Proposed execution order

1. **Explicit null handling**, with separate permission and logging/custom-data
   controls. Preserve zero-string/false/empty behavior and invalid-type failures;
   do not broadly cast input. Permission defaults and dependency filtering need
   denied/escalation/explicit-dummy-name cases. Unserialization needs legacy
   payload/namespace handling tests, not an unrelated format/security rewrite.
2. **Declared-property candidates**, only after inspecting actual owning classes
   and observable property/serialization behavior. Correcting a misspelling to
   a private declaration can change an existing public dynamic property's API.
3. **Return contracts**, grouped by owning class and actual return branches,
   with subclass checks. Separate a demonstrated compatible declaration from a
   compatibility bridge; neither is automatic acceptance of semantic bugs.
4. **Reflection, serialization and XML**, with their own behavior/security
   fixtures before integration. These cannot be replaced by a warning counter.
5. Build a separately versioned combined candidate only after patch-specific
   evidence; rerun real API SQL/HTTP/TLS, CLI and required broader application
   cases. Source inventory, cache, media/browser, distro, performance and recovery
   obligations remain open beyond these 40 groups.

## Graph and upstream context

The original-source graph `kaltura-rigel-18.20.0-full` is ready at generation
`2026-09-25T12:19:00Z`; exact coverage checks for all 18 files report matching
metadata and no recorded issue. This is best-effort, not exhaustive coverage.
[Coverage evidence](evidence/exp4-triage/coverage.json). Actual excerpts come from
exp4 ZIP bytes, not assumptions that original and patched methods are identical.

PHP's migration guides document the relevant categories: null passed to
non-nullable built-ins and legacy Serializable usage in
[PHP 8.1](https://www.php.net/manual/en/migration81.deprecated.php),
reflection/optional-parameter/libxml deprecations in
[PHP 8.0](https://www.php.net/manual/en/migration80.deprecated.php), and dynamic
properties in [PHP 8.2](https://www.php.net/manual/en/migration82.deprecated.php).
These explain candidates; they do not establish application-specific correctness
or replace observed runtime tests.

## Coordination outcomes and correction of provisional suggestions

The first broad Claude, Cursor and Grok attempts each hit their time limits;
none is recorded as a completed approval. Cursor wrote a partial report before
timeout, preserved under `attempts/`. Its suggestions are untrusted proposals:
returning early for all non-string inputs, broadly normalizing scalar inputs,
or renaming an implicitly public dynamic dispatcher to a private property would
change behavior and **are not selected**. The next null-only experiment must
leave every non-null input on its existing path. Bounded follow-ups and the
authorized Grok fallback are tracked separately in the coordination result.

The intended next experimental batch is the five null-argument sites (142
observed events), using only null-to-empty-string compatibility handling.
This predicts a diagnostic reduction but does not establish one. Mandatory
controls include null/empty/false/zero/whitespace/non-string behavior, permission
denial/default/dummy/dependency semantics, serialized custom-data handling and
full exp4-vs-new-candidate API output/diagnostic comparison. Dynamic-property,
return-contract, reflection, serialization and XML changes are not smuggled
into that batch.

### Correction to native-type review prose

Claude's bounded follow-up correctly verified accounting and the 22 contracts,
but overstated that `mixed` breaks PHP 7.4 parsing. A separate native 7.4 control
**parses** `function php83ProbeMixed(): mixed { return 1; }`, then throws TypeError
because `mixed` is interpreted as a class name rather than the PHP 8 universal
type. See `php74-mixed-control.json`. Thus the compatibility concern stands,
but the failure mode differs from PHP-8-only union syntax. Reviewer prose does
not override executed evidence; no signature change is selected here.

### Limits of the fallback's broader proposals

OpenCode completed its assigned source review and 122 local tests. Its report is
retained as **advisory**, not an approved patch plan. In particular:

- Adding a default to required `$rank`, adding rank validation, or reordering
  arguments changes behavior and is not the minimal deprecation repair. First
  test removing only the ineffective preceding `$entryType` default, with
  arity/named/positional/reflection controls; do not silently reject numeric
  strings accepted by the baseline.
- `void` itself is supported by PHP 7.4; the exception wakeup proposal does not
  inherently require a separate branch for syntax reasons. Inspect actual
  serialization/code-field behavior rather than assuming Exception properties
  have enforced types from their documentation alone.
- Adding magic serialization hooks changes newly written wire representation;
  retaining old methods alone does not prove bidirectional old/new cache reads.
  No payload format change or credential-state simplification is selected.
- The fallback's description of `libxml_disable_entity_loader` as a no-op is
  not established by its source review. The official manual warns about parser
  options that enable external entity loading; modern libxml defaults are not
  a blanket proof of safety. `LIBXML_NONET` does not by itself block file entities.
  Do not add `LIBXML_NOERROR` to hide failures. XML tests must use disposable
  synthetic marker files, never read real host secrets or `/etc/passwd`.

See the [official libxml function manual](https://www.php.net/manual/en/function.libxml-disable-entity-loader.php).
These corrections prevent advisory agent output from silently expanding scope
or weakening behavior/security requirements. No fallback proposal is executed.
