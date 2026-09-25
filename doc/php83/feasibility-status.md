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
were presented to the operator; the operator approved them with “pode seguir”.
The planning artifacts have now been reconciled and pass strict validation.

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

Complete the source inventory,
isolated PHP 7.4 baseline, PHP 8.3 syntax/static/runtime investigations and the
three-distro provider matrix. Submit a bounded go/no-go report before changing
application source/package dependencies or the release workflow.

No existing task checkbox is marked complete: preparing a single runtime VM
and checking a source archive does not satisfy the broad phase-1 tasks.

## External references

- [Ubuntu native php8.3-cli package](https://packages.ubuntu.com/noble/php8.3-cli).
- [PHP support policy](https://www.php.net/supported-versions.php): PHP 8.3
  security support currently ends 2027-12-31; re-check before release.

## First source audit (2026-09-25)

The checksum-verified upstream archive contains 11,784 PHP-like files. PHP 8.3.6
syntax/compile checks rejected **58 files** (51 under vendor, six under alpha,
one under infra). A total of 126 files produced diagnostics, including those
58 failures. This is compiler evidence, not proof that all files are reachable
in supported runtime flows or that every failure is new relative to PHP 7.4.

Examples include removed curly-brace offset syntax and unparenthesized nested
ternaries. The bundled source identifies Zend Framework 1.9.6, Propel 1.4.2 and
PHPMailer 5.2.1; these are file-declared versions, not a completed dependency or
security audit. Do not replace entire frameworks automatically.

Pinned PHPCompatibility 10.0.0-alpha2 / PHPCS 4.0.4 produced **1,256 errors and
645 warnings** with `testVersion=7.4-8.3`. Those are untriaged static candidates,
including optional legacy drivers and baseline issues, not 1,901 proven
production failures. The analyzer is prerelease and cannot prove compatibility.

Evidence: [source audit files](evidence/source-audit/), reproducible
[tool instructions](../../tools/php83/README.md). The released Noble DEB payload
was audited separately so generated clients and packaging overlays are not
silently treated as identical to the upstream archive.

The candidate lab's PHP 8.3 packages are now pinned to native Ubuntu origins;
provider evidence was refreshed for the full selected package set. No main
package dependencies, release workflow, PHP application code or `.20` state
have been changed by this investigation.

## Published payload comparison

The verified Noble repository archive contains 13,454 PHP-like files after
extraction with `dpkg-deb -x` (no package hooks executed in the candidate lab).
The same 13,454 path/content hashes were checked with both PHP 7.4.33 and 8.3.6:

- PHP 7.4 rejected seven files.
- PHP 8.3 rejected 79 files: **72 new compiler rejections**, plus those seven
  existing baseline rejections. Runtime reachability still needs investigation.
- The packaged static scan reports 2,025 errors and 785 warnings; these remain
  candidates, including duplicate legacy player versions, not incident counts.
- 11,782 upstream PHP files are byte-identical in the package; two differ through
  packaging overlays. The 1,670 additional PHP files include 1,524 in legacy
  HTML5 player trees plus clients-generator/CLI files. See
  `evidence/source-audit/source-to-package-map.json` for paths and hashes.

A fresh synthetic `.74` AIO baseline was provisioned from the published
7.4 artifacts. It has no production data or host shared folders, matches the
candidate VM's box/CPU/RAM settings, and blocks outbound `.20` access during
bootstrap. No timings have been collected before protocol/fixture freeze.

The independent Claude follow-up review allows phase 1 to continue, while
explicitly retaining all feasibility, runtime and later release gates. Stale
context and scenario placement noted in that review were corrected; the Noble
candidate spec now excludes the PPA entirely. Findings are not waived or marked
complete merely because they are numerous. New test-client target guards have
four passing offline tests (literal lab identities, protected destination,
malformed/credential-bearing URLs and redirects).

### Noble baseline HTTP smoke acceptance

The isolated `.74` baseline completed provisioning and the checksum-pinned
legacy sanity script reported **zero failures**: nine services, searchd, API
ping, Admin Console/KMC HTTP responses, admin session, synthetic partner creation,
upload-to-READY, HLS manifest and segment retrieval. These HTTP checks are not
browser interaction tests or the final benchmark/TLS/rollback acceptance.

The smoke wrapper allowed new outbound connections only to guest loopback and
its own `.74` address while retaining established SSH connections; the temporary
chain was removed afterward. The independent `.20` rejection rule remains.
No fixture or secret was copied from `.20`. Evidence is under
[evidence/noble-baseline](evidence/noble-baseline/).

The first broad phase-1 task group remains incomplete. Next: map compiler/static
findings to exercised entrypoints, finish license/dependency/overlay attribution,
freeze and run the benchmark fixtures, execute controlled PHP 8.3 runtime probes,
and resolve the Ubuntu 26.04/EL9 provider matrices before the go/no-go decision.

## Independent Claude/Grok review and first runtime differential

Both CLIs reviewed supplied public-source snippets and phase-1 evidence with
all tools disabled; neither inspected or modified the VMs. Both advised keeping
compiler, static, library-runtime and full application acceptance evidence
separate, prioritizing first-party/bootstrap dependencies, and not silently
excluding optional code or duplicate player versions. Claude recommended tighter
OS-level isolation before expanding beyond the fixed no-I/O probes. Neither
review is a migration approval.

Five identical fixed library probes ran against extracted, unpatched public
payloads on `.74` and `.83`. All five exit successfully on PHP 7.4. On PHP 8.3:

- `Zend_Registry::set/get` fails with `TypeError`: its `offsetExists` passes an
  object to `array_key_exists` at `Zend/Registry.php:206`.
- Legacy `Services_JSON` fails on removed curly-brace offset syntax.
- Empty-options `Zend_Application`, a simple `Zend_Config` lookup and load-only
  Propel/PDO subclass discovery succeed, with legacy deprecation diagnostics.
  These successes do not establish full bootstrap, database or API compatibility.

An initial Propel harness include-path omission failed on both versions; it was
corrected before the recorded comparison and is not an application regression.
The runner is not an OS sandbox; only the reviewed fixed no-I/O probes were run.
Reports and harness hash: [runtime evidence](evidence/runtime-probes/).

Temporary Apache include tracing on synthetic `.74` observed API ping (325 files),
Admin login (361) and KMC shell (281), all HTTP 200. Zend Registry was included in
the Admin login flow; that does not establish which Registry methods executed.
The KMC shell included three PHP 8.3 compiler-rejected Symfony files:
`controller/sfRouting.class.php`, `helper/UrlHelper.php` and `util/sfCore.class.php`.
API ping and Admin login had no intersection with the 79 rejected paths; absence
in these limited requests does not prove a path unreachable in other flows. Instrumentation was
disabled, its Apache configuration removed, and Apache reloaded afterward.
No production application or data was involved.

The compiler differential is 51 new server-tree rejections plus 21 legacy-player
paths (seven distinct player-file contents). All remain tracked: deduplication
is for triage, not permission to drop a supported feature. Phase 1 remains open.

## Disposable Ubuntu 26.04 / EL9 provider probes

[Provider commands, image digests and logs](evidence/providers/) now establish
successful installation of the requested PHP 8.3 packages on Ubuntu 26.04 using
Sury's signed **matching `resolute` suite**, and on Rocky Linux 9 using Remi's
`php:remi-8.3` stream with EPEL/CRB. Both report CLI PHP 8.3.35. This is stronger
than repository URL availability, but is not application or complete ABI/SAPI
acceptance. The Ubuntu Apache module was installed, not HTTP-tested; EL9 FPM
module discovery was tested, not an application FastCGI request.

Native Ubuntu 26.04 did not resolve the requested PHP 8.3 packages. EL9 native
AppStream exposes PHP 8.3, but the partial listing did not include memcache/ssh2;
its exit-zero result is not a full dependency-resolution success. Full mandatory
extension coverage, provider selection and unattended application acceptance
remain pending. Existing packaging and workflows remain unchanged.

## Expanded sandboxed library probes

The [runtime triage ledger](runtime-triage.md) records 15 same-harness probes in
both Noble labs. PHP 7.4 completed all 15; PHP 8.3 failed five. In addition to
previous Registry/Services_JSON findings, forced Zend JSON fallback encoding and
decoding fail, and Propel `DebugPDO::query()` has an incompatible declaration.
Default Zend JSON encode/decode succeeds, demonstrating why fallback compiler
failures cannot be generalized to every JSON call.

Both runs verified non-root execution, a read-only payload, hidden protected
paths and denied internet socket creation before executing PHP. No DB connection
or configured application tree was used. Expanded reports preserve diagnostics,
module lists, included public-file hashes and harness identities. No application
patch, package change, `.20` action or task completion is implied.

## Shared full-source graph

The operator requested a shared Rigel source graph for Codex, Claude and Grok.
[Source graph guide](source-graph.md) records project
`kaltura-rigel-18.20.0-full`, byte-verified source provenance, the full 15,175-file
inventory and all recorded coverage gaps. Vendor/previously ignored directories
and `.phtml` templates are included through an analysis-only copy; original
application source is unchanged. Claude and Grok independently confirmed MCP
search/coverage access. This improves discovery, not runtime compatibility proof.

Minimal source-patch work is still experimental. Expanded Registry property
fixtures exposed a PHP 8.3 difference after an earlier narrower differential
passed; the scratch ZIP is therefore held, not approved or published. JSON offset
repairs passed the current standard/minimal-INI differential corpus. No task is
closed or application deployed based on these partial results.

## First experimental source artifact: exp2

The [JSON-only experimental ZIP](experimental-zip.md) is now assembled with three
minimal source patches (54 offset syntax replacements). Two builds using the
recorded Python/zlib toolchain match byte-for-byte. All original ZIP entries
remain; only the three declared source files and added experimental metadata
differ. The verifier checks file, patch, manifest and builder identities.

Eight differential JSON comparisons pass against unpatched PHP 7.4 across both
candidate runtimes and standard/minimal INI modes; each codec tests 13 values.
Both without-mbstring/iconv configurations are recorded. Compiler checks pass
for the patched files on both runtimes. Deprecation diagnostics are retained.
This is not full application acceptance or a performance claim.

The Registry cast patch remains held after the extended property fixture failed;
its unchanged source, DebugPDO and Symfony still block a complete PHP 8.3 switch.
No dependency upgrade was selected, no production package/CI reference changed,
and no GitHub migration release or `.20` deploy occurred. Tasks 1.3/1.5/1.6 and
later gates remain open despite this first bounded artifact.

### DebugPDO follow-up (2026-09-25)

The [held DebugPDO experiment](debug-pdo-experiment.md) removes the query
signature fatal in a synthetic SQLite test, without changing the active ZIP.
Original/patched 7.4 match, but patched 8.3 fails strict parity on numeric fetch
types; native PDO controls reproduce that difference. No waiver was applied.
Named-argument forwarding and MySQL/application behavior remain unverified.
The original DebugPDO files were restored in both disposable candidate trees
after evidence collection. All eight JSON comparisons and 27 offline tests
still pass; no broad migration task is complete.

The subsequent DebugPDO v2 held variant fixes reproduced named-argument loss
and removes the deprecated parent callable. Native-PDO return/error controls
pass in eight 7.4 and twelve 8.3 boundary cases. Explicit stringify-fetches
diagnostics match the baseline, but default numeric-type parity remains failed;
no application setting or acceptance gate changed. See the experiment document
and `evidence/debug-pdo/v2/`. Candidate trees were restored to exp2 after testing.

Extended v2 evidence adds deterministic in-memory logging with successful,
exception and silent-error accounting: both runtimes match original 7.4.
Native-PDO controls now cover 12 cases on 7.4 and 20 on 8.3, including object
identity and constructor order. All 33 offline tests and eight JSON comparisons
pass. The default numeric-type blocker remains; MySQL/application behavior is
not inferred from SQLite. See `evidence/debug-pdo/v2-extended/`.

The [isolated MySQL-driver experiment](mysql-type-experiment.md) now compares
both PHP binaries against one disposable MariaDB instance. Native prepares
match the synthetic 7.4 rows; emulated prepares with stringify disabled change
integer/float result types on 8.3. DebugPDO matches native PDO within each tested
configuration. No global attribute was changed; application connection settings
and JSON contracts remain unverified. The server was stopped after collection.

Grok's missing-SQL boundary finding was confirmed against v2 and corrected in a
smaller held v3 variadic-forwarding alternative. All 36 native-PDO controls,
named-SQL logging, 33 offline tests and eight JSON comparisons pass. Repeated
MariaDB tests preserve the same known numeric-type difference; no waiver or
global connection setting was added. V3 is not in the active ZIP. See the
DebugPDO experiment document and `evidence/debug-pdo/v3/`.

The [Propel initialization/hydration probe](propel-init-hydration.md) exercises
the actual connection factory, MySQL adapter and generated Baseentry hydration
with synthetic parameters. Unspecified connection options reproduce the raw
numeric-type difference. Constructor/post-construction native options and
stringify options are honored; selected hydrated integer fields match in all
four cases. This is not effective live-configuration or full API validation.
PDO7.4's unsupported stringify-attribute readback is explicitly recorded.

The real Kaltura JSON serializer now confirms a raw-object numeric JSON type
difference in the unspecified synthetic connection case; selected hydrated
fields retain identical JSON. A direct analytics row-to-JSON path was identified
for further synthetic endpoint testing, not executed. The characterization
collector retains the known mismatch explicitly. All 38 offline tests pass;
full API acceptance and promotion remain blocked.

The [analytics partner unit probe](analytics-partner-probe.md) now executes
hash-pinned function-only source with explicit query doubles and synthetic
string/integer/null rows. It confirms pp/se preserve incoming types identically
on both PHP versions. This is consumer-sensitivity evidence, not an endpoint
regression or permission to normalize all responses. No new source patch was
selected; downstream type expectations and real isolated query integration
remain open. All 38 offline tests continue to pass.

Analytics integration now feeds real MariaDB/PDO statements through the pinned
partner-update function using synthetic SELECTs and explicit peer/criteria
adapters. Nine combinations confirm JSON type changes for positive/zero values
under unspecified attributes; NULL/native/stringify cases match. This closes
the fixture's driver-to-function gap, not full query/schema/authentication or
endpoint acceptance. No global attribute or source repair was selected; the
probe service was stopped and original candidate source restored.

[Claude-assisted Registry investigation](registry-investigation.md) isolated
literal versus variable-name ArrayObject write behavior. A __set workaround was
rejected by real tests. The cast-only candidate passes inherited Zend bootstrap
container read/write operations in both runtimes and INI modes, but the broader
literal-property parity failure remains. Neither Registry candidate entered the
active ZIP; all 38 offline tests pass and lab originals were restored.

Real Zend ActionStack consumer tests now pass for singleton/custom registries,
LIFO/empty-action handling, request inheritance, forwarding and parameter
merge/clear behavior. Together with bootstrap-container tests, eight differential
comparisons pass across both runtimes and INI modes. The literal-property
Registry mismatch remains held; these tests do not waive it or replace full
HTTP/Admin Console acceptance. Originals were restored after collection.

[Symfony bootstrap investigation](symfony-bootstrap.md) adds seven held minimal
repairs and advances real public bootstrap into generated core-cache loading.
Six focused differential comparisons and eight JSON comparisons pass; 38 offline
tests pass. PHP 7.4 bootstrap completes, while PHP 8.3 still fails on duplicate
sfOutputEscaperObjectDecorator declaration. A private ephemeral cache avoids
modifying source/live cache. No patch was promoted; lab originals restored.

The Symfony duplicate-class blocker is now resolved experimentally by ordering
ObjectDecorator before its IteratorDecorator child in core_compile.yml (two-line
reordering only). Both bootstrap comparisons and post-bootstrap escaping tests
pass. Reverting only that order reproduces the fatal on 8.3. All eight held
source files were restored afterward; HTTP/API/worker acceptance and diagnostics
triage remain pending, and no patch entered the active ZIP.
