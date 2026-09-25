# PHP 8.3 feasibility — initial preparation

Date: 2026-09-25. Branch: `proposal/migrate-kaltura-php83`.
This is partial evidence, **not a compatibility or migration approval**.

## Operator request and isolation

The operator requested starting the existing `.20`, independent review using
the Claude CLI, and a new initial Ubuntu 24.04 PHP 8.3 environment.

- `.20` was started with `vagrant up aio --no-provision`. Read-only inspection
  reported PHP 7.4.33 and active console/Apache/MariaDB. No manual package,
  configuration, database or media changes were made there. Normal service
  startup can write operational state; no pre-boot snapshot was taken.
- New VM `.83`: `kaltura-php83-noble-lab`, Ubuntu 24.04, 4 CPUs, 8 GiB RAM,
  separate guest disk, no host shared folders or production data. Host-only
  networking plus NAT means this is not an air gap: application test scripts
  must still enforce destination guards before sending requests.
- CLI and Apache both report PHP 8.3.6. Installed Ubuntu package version:
  `8.3.6-0ubuntu0.24.04.11`. The candidate mandatory extension sets passed for
  both SAPIs. CLI also verifies `pcntl` and `posix`.
- No Kaltura application/packages, MariaDB, partner secrets or media have been
  installed in `.83`. The temporary Apache probe was removed after verification.
- Runtime, module and package/provider reports are in
  [evidence/noble-runtime](evidence/noble-runtime/).
- `Rigel-18.20.0.zip` was downloaded locally and verified against
  `58d534d09b3b75c9a8333957268c884f79032638b2d44a278b1992fda1b0ab28`.
  The complete dependency inventory and compatibility audit are still pending.

## Independent Claude CLI review

Claude was invoked in print/plan mode, with tools and MCP disabled, and supplied
all seven planning Markdown artifacts. It reviewed their consistency, not the
actual repository or VM. No tools, edits or server actions were delegated.

Decision: **phase 1 conditionally approved; phase 2 and release not approved**.
This is advisory review, not operator authorization. Proposed artifact changes
were presented to the operator for confirmation before edits.

### Requested corrections

1. Distinguish expressly authorized `.20` boot/read-only inspection and normal
   service writes from forbidden manual package/configuration/data changes.
   Claude recommended a pre-boot snapshot; the requested boot had already
   happened before the asynchronous review returned. Do not claim otherwise.
2. Define distinct lab identities, no shared production storage/secrets, and
   test target guards against `.20`, including hostname resolution.
3. Fix a comparable baseline/candidate workload, resource allocation, synthetic
   fixture hashes and repetition count before collecting timing baselines.
4. Prefer native Noble PHP 8.3 and make package origins unambiguous; record
   every extension's origin/ABI. No PPA was added to the initial `.83` lab.
5. Keep main specs/CI and published 7.4 releases unchanged until release gates;
   archive and publish no migration tag prematurely.
6. Use verified published 7.4 artifacts for an isolated application baseline.
7. Turn extension ABI checks into concrete dependency and loaded-SAPI checks.
8. Explicitly cover unattended Noble application acceptance, not just packaging.
9. Verify EL9 AppStream versus Remi availability before selecting a provider;
   do not change the existing proposal's provider commitment without approval.
10. Verify Ubuntu 26.04 provider/suite compatibility rather than assume it.
11. Use synthetic upgrade data; copying `.20` data/secrets needs separate consent.
12. Pin compatible analyzer versions and distinguish lint/static/runtime results.
13. Record the new phase-1 authorization without implying live cutover approval.

## Next gate

Confirm and reconcile planning corrections, then complete the source inventory,
isolated PHP 7.4 baseline, PHP 8.3 syntax/static/runtime investigations and the
three-distro provider matrix. Submit a bounded go/no-go report before changing
application source/package dependencies or the release workflow.

No existing task checkbox is marked complete: preparing a single runtime VM
and checking a source archive does not satisfy the broad phase-1 tasks.

## External references

- [Ubuntu native php8.3-cli package](https://packages.ubuntu.com/noble/php8.3-cli).
- [PHP support policy](https://www.php.net/supported-versions.php): PHP 8.3
  security support currently ends 2027-12-31; re-check before release.
