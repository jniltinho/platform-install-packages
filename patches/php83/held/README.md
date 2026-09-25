# Held experiments — not part of any active archive

`Registry-properties.patch` is a rejected __set experiment, retained with
failure evidence in `doc/php83/evidence/registry-investigation/`. It changes
the 7.4 baseline and does not fix 8.3 parity. Never add it to the active manifest.

The DebugPDO query-signature experiment is also held. It removes the PHP8.3
class-loading fatal in an isolated SQLite fixture, but strict cross-runtime
output parity fails on numeric types; named-argument forwarding needs testing.
See `../../../doc/php83/debug-pdo-experiment.md`. Do not add it to exp2.

`DebugPDO-query-v2.patch` is an alternative against the same original source,
not a patch to stack after `DebugPDO-query.patch`. It fixes the reproduced
named-argument loss and removes the deprecated parent callable; default
cross-runtime numeric-type parity still fails, so v2 is also held.

V2 additionally fails the reproduced named-fetchMode-without-SQL boundary.
`DebugPDO-query-v3.patch` forwards the original variadic arguments directly and
passes that control. It is another standalone alternative against the original,
not an incremental patch. V3 remains held: numeric/API behavior and runtime
diagnostics are not accepted merely because forwarding tests pass.

The Registry cast experiment is retained solely for review and reproduction.
The active `../manifest.json` does not list it. Do not add it through wildcard
patch discovery.

The latest extended fixture compares dynamic property assignment plus
`offsetExists` on ArrayObject flags 0–3. On flag 2, PHP 7.4 original returns false
for the property-written key while the PHP 8.3 cast candidate returns true;
on flag 3, the corresponding result flips from true to false. This needs a
semantic/API-impact decision and wider tests, not a silent exclusion of the
failing fixture. No claim is made that these low-level legacy semantics are ideal.

The original `array_key_exists($index, $this)` still fails on PHP 8.3; excluding
this patch therefore leaves a known compatibility blocker. No application-wide
acceptance is asserted for the JSON-only ZIP.

`Criteria-null-alias.patch` is a one-line explicit-null guard in Criterion::init.
Eight focused alias contracts pass on PHP 7.4/8.3; the actual SQL/API integration
is still pending. It is not part of exp2 or exp3. See
`../../../doc/php83/criteria-null-alias.md` for identities and limitations.
