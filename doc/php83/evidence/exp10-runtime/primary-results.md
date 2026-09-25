# Primary exp10 runtime integration results

The earlier `plan.md` and `preparation.json` record the initial unexecuted,
unpinned preparation phase. This result supersedes that pending execution status;
the original planning evidence is preserved.

Verified exp10 ZIP SHA-256:
`de177e6cbaedf3a3207661c2325f466cce37febb73190f3a49d31f24b740c053`.
Fresh stages were created on the explicitly owned baseline74 and php83lab in
separate serialized ownership windows. No existing stages or system PHP selection
were changed. Baseline74 and php83lab were released promptly after their runs.

## Completed bounded cases

- **48 CLI rows:** 44 individual exit-zero cases and four expected original
  PHP8.3 JSON syntax-fatal controls (exit 255). Exp9 and exp10 each have 12 positive
  rows. Twenty JSON-type-preserving result comparisons against original PHP7.4
  pass; environment rows are not claimed cross-version identical. For parser
  export, the established comparison contract covers the `entries` field.
- **Four API rows:** original74 passes; original83 reproduces its required
  KalturaPDO signature fatal; exp9 and exp10 both pass the unchanged HTTP,
  trusted-HTTPS, negative authentication and untrusted-CA rejection contract.
  Both candidates retain **18 diagnostic groups / 503 events**. Those diagnostics
  remain open, not suppressed or waived. The owned synthetic SQL unit was
  confirmed inactive after cleanup.
- **Actual exp10 class corpus:** three real artifact-loaded class processes,
  **68 cases**, pass exact comparison to the prior PHP8.3 held-candidate corpus.
  This covers the two Google_Utils versions and HTMLPurifier_Encoder only, not
  every changed application file.

Full exp10 and exp9 source identities were reverified after the relevant API/CLI
runs; the actual-exp10 class collector also verifies the full artifact before and
after. `primary-summary.json` records the 48-row validation and twenty comparison
results. Each command's stdout/stderr/exit and detailed reports are retained.

## Fresh runtime identity closes the preparation gap

Baseline74 before/after identity JSON is exactly equal: **55 PHP/Apache binaries
and modules**, linked libraries, three runtime modes and PHP7.4 standard CLI INI
hashes. The copied PHP8.3 binary/modules are included. Native php83lab before/after
identity JSON is also exactly equal: **39 binaries/modules**, their linked
libraries, standard/minimal PHP8.3 module lists and CLI INI hashes. No INI values
or credentials are persisted. The snapshot helpers execute only runtime
version/module/INI inspection, not application entrypoints.

The source/runtime identity gap noted in the initial plan is therefore closed
for this bounded primary cycle, not retroactively for previous reports. Existing
SSH host-key policy remains inherited and is not newly authenticated by the
hostname guards. Application `PROBE_RUNTIME` observations remain in API evidence.

## Not acceptance or release

These positive rows do not close remaining compiler failures, untriaged static
findings, generated-code workflows, full AIO/FPM/cache/service coverage,
performance, package, CI, merge, release or production gates. PHP8.3 diagnostic
severity changes in the separate class corpus remain explicitly characterized.
No source repair, package integration, production write or release was performed.

Independent Claude/Grok/Cursor evidence and cross-executor comparisons are
coordinator-owned and must be evaluated separately. This document describes
primary execution only and does not infer an independent pass.
