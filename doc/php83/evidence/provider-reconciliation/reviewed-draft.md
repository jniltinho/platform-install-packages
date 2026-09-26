# PHP 8.3 provider decision record — draft, not integration approval

2026-09-26. Supports original1.4/1.5/1.7 and detailed5.6/5.16.
This consolidates existing evidence rather than selecting a production stack.
No package/CI configuration, source ZIP or installed VM runtime is changed.

## Observed candidates and unresolved decisions

| Target | Observed candidate | Recorded evidence | Disposition before full application use |
|---|---|---|---|
| Ubuntu24.04 | Native Ubuntu PHP8.3.6 | Independently repeated CLI/Apache GET/POST provider probe; separate native lab/runtime identities | Preferred by approved design; final package-origin/ABI and application-extension reconciliation remains open |
| Ubuntu26.04 | Sury exact resolute suite PHP8.3.35 | Independently repeated CLI/Apache GET/POST provider probe | Candidate only; suite/signature evidence does not promise future maintenance or approve every application extension |
| Rocky9 | Remi php:remi-8.3, PHP8.3.35, EPEL/CRB | Independently repeated CLI/FPM GET/POST provider probe | Candidate only; legacy php-pecl-apc dependency cannot be silently relabeled APCu |
| Rocky9 native-only transaction | AppStream php:8.3 | Requested memcache/ssh2 package transaction failed | Rejected for the exact recorded transaction, not proof no reviewed repository combination could work |

[Provider runtime report](provider-runtime.md) retains exact container/image,
package, signature and CLI evidence, including failed attempts. Numeric upstream
PHP versions above are observed runtime strings, not complete package revisions.
Do not compare them alone to infer security patch levels or substitute a later
minor version. Frozen exact package revisions remain in those original logs.

## Extension findings to carry into the final manifest

The [reproducible join](evidence/provider-reconciliation/primary.json) hashes its
inputs and records18 observed rows, including independent repeats, representing
nine target/method combinations. All satisfy their historical35 web/36 CLI
probe requirements. **None of the18 loaded-module lists contains SOAP or legacy
APC; all contain APCu and memcache.** This is a snapshot observation, not a claim
about every package available from those repositories.

1. **SOAP is a real coverage gap, not a passed requirement.** The original
   kSoapClient lifecycle could not execute without ext/soap. Later
   [lifecycle experiments](xml-lifecycle.md) privately loaded exact signed Noble
   SOAP modules for7.4/8.3; those fixtures did not enable installed web/worker
   services, add a final package dependency or test Resolute/Remi SOAP. Decide
   and record the supported SOAP feature requirements, then verify the chosen
   module origin/ABI and both SAPIs. Do not retrofit success into the old probe.
2. **APCu is not an accepted replacement for the complete legacy APC surface.**
   [Application-cache investigation](apcu-cache.md) retains the rejected direct
   alias/counter experiment. [Web-cache observations](apcu-web.md) cover only
   narrowly selected configuration-cache behavior. Opcode statistics, upload
   progress, lock semantics, direct consumers and backend use are not supplied
   by renaming a dependency. A cache policy or adapter requires an explicit
   bounded decision and actual integration tests.
3. **memcache and memcached remain distinct.** The observed extension is memcache;
   a daemon package or different extension name is not a capability substitute.
4. **Optional vendor drivers remain explicit unresolved features.** For example,
   [Riak provider evidence](riak-provider.md) does not demonstrate a working
   native provider or permit an unsupported driver to be marked accepted. Any
   scoped exclusion needs named rationale/tests and the approved gate decision.

The35/36 historical probe set is not an exhaustive application-use inventory.
Private module extraction and library-level tests do not close T4-01, T1-03,
real application acceptance or the packaging-integration gate.

## Update/support review, checked2026-09-26

PHP8.3's upstream active-support period ended2025-12-31; security support ends
2027-12-31. This leaves a finite maintenance window and does not transfer a
security guarantee to every packaged extension. The requested target remains
8.3; changing it needs an explicit proposal decision.
[PHP support calendar](https://www.php.net/supported-versions.php).

The [Sury bootstrap instructions](https://packages.sury.org/php/README.txt)
document a Signed-By keyring and suite-derived repository configuration. They
are not a per-extension support SLA. The [Remi configuration page](https://blog.remirepo.net/pages/Config-en)
documents EL9 release packages, CRB/EPEL prerequisites and signing keys, but does
not make the existing Kaltura dependency names correct. Do not infer an
unconditional future-support promise from either configuration guide.

Final selection must retain signed, suite-compatible origins, exact package and
loaded-module identities, and the reviewed update policy. Pin acceptance inputs,
then separately validate security updates within8.3; never silently mix suites,
load7.4 extension binaries into8.3 or bypass signature checking. The distribution
support window is not itself proof that each extension has the same coverage.

## Decision fields still required

- Final supported application features and mandatory-extension/SAPI matrix,
  including explicit disposition of SOAP/APC-dependent paths.
- Per-package origin, signing chain, module/ABI and web/CLI/worker interpreter
  identity reconciled against that matrix on each target.
- Per-component upgrade records with old/new pins, scoped license/upstream
  references, benefit, regression/revert evidence, or an explicit deferral.
  Compatibility patches do not implicitly select dependency upgrades.
- Consolidated feasibility go/no-go and operator approval before production
  package/CI integration. No release or `.20` cutover approval is implied.

Rebuild the report with `python3 doc/php83/evidence/provider-reconciliation/build.py
--output <new-path>`. It performs repository-local JSON/Markdown reads only and
refuses an existing output. Independent review/execution is recorded separately.
