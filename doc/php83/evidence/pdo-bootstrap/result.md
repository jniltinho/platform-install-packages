# Real bootstrap PDO boolean probe — Codex execution

The corrected `codex-r2.json` has two exit-zero variants, each asserting 23 cases.
The real API bootstrap creates `KalturaPDO`, whose constructor selects
`KalturaStatement`; no dependency stubs or manual statement-class substitution
are present. Seven runtime-loaded application/dependency source hashes match the
verified respective ZIP. Full extracted source verification passed before and
after; the owned SQL unit was stopped (inactive).

Exp8: 16 diagnostic groups / 18 events. Exp9: 13 groups / 15 events. These
remaining diagnostics are measured warnings/deprecations, not accepted exceptions.
Null-to-bool changes are explicitly expected only in the selected setter/execute
results. Data writes, cache identity, dry-run skip/select and native/wrapped error
outcomes match the exact other expected values. External cache and monitoring
services are disabled/unconfigured; real class loading is not service acceptance.

The initial execution failed due to a named-placeholder fixture error, retained
under `attempts/positional-array` and the initial `codex.*` report. The corrected
run did not change application bytes or relax result expectations. The 11 local tests cover positive acceptance, negative validation controls and
the static named-input regression guard. PHP 8.3 VM
syntax lint passes. Independent repeat/review results are recorded separately;
this note makes no claim about them. This probe does not close application,
package, CI, performance, release or production gates.
