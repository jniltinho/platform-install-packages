# Real kConf / kSoapClient XML lifecycle — unchanged-source experiment

## Current status: bounded behavior observed; strict diagnostic failures retained

Actual native PHP7.4 and PHP8.3 now each completed all22 processes with exit0
using privately extracted exact-version SOAP. Each collector retains **18 accepted
contracts +4 FAIL** (missing-WSDL and nested-constructor cases ×2 provenance
variants): native error-handler diagnostics are captured but some are not emitted
in native stderr by SOAP. No warning was suppressed, fabricated or removed to
make the strict assertion pass. See [native observations](evidence/xml-lifecycle/native-observations-r1.json).
Both runtime snapshot pairs are unchanged. Actual Claude independently repeated both native matrices, serially by lab: CLI exit0, command exits0/1/0, exact matrix bytes and runtime snapshots matching the primary. [Comparison](evidence/xml-lifecycle/repeat-comparison.json) retains all8 strict failures per author. Actual tool calls/results and individual command exits establish execution; byte equality alone is not the proof.

Measured on these unchanged actual classes in both runtimes:
- Without a preexisting callback, kConf blocks the local marker.
- A permissive preexisting fixture callback still resolves the marker after
  kConf disables the old loader flag: the global flag alone does not override it.
- Malformed/missing WSDL and invalid SOAP method exceptions leave entities and
  HTTP wrappers enabled because the original cleanup is not in finally.
- An inner successful call disables shared policy while the outer call is still
  active; an inner fault leaves it enabled until outer successful cleanup.
These are bounded observations, not a repaired security policy or full backend
acceptance. Fixed synthetic transport remains the only transport seam.

### Preserved unsuccessful prerequisite attempts

The first baseline74 attempt reached the native interpreter but all 22 processes
exited 65 at the extension prerequisite: `soap.so` is absent. Native startup
warnings and collector exit 1 remain preserved in
[primary74.json](evidence/xml-lifecycle/primary74.json). This is
**NOT_EXECUTED application/SOAP behavior**, not 22 failed application contracts.
The [classification](evidence/xml-lifecycle/primary74-classification.json) is
additive; the original collector failure has not been rewritten. Both runtime
snapshots (55 objects) are identical. Read-only native83 preflight likewise found
SOAP absent, so its matrix was not launched. No module was installed, no system
INI changed, and no application patch or artifact was selected.

A fixture-private exact-version SOAP provider is under investigation; installation
and global runtime changes are not authorized. That initial attempt remains separate from the later private-provider outcomes. The preparation/review sections below describe
the earlier frozen phase, not executed application acceptance.

## Historical preparation

**Preparation phase: no PHP/VM execution or application patch selection.**
This follows the [native policy experiment](xml-loader.md): removing the security
call exposed local markers under NOENT/DTD options; a deny callback alone is not
proven compatible with SOAP or application lifecycle.

## Scope and exact inputs

[source-pins.json](../../tools/php83/xml-lifecycle/source-pins.json) pins:
- Original ZIP: `58d534d09b3b75c9a8333957268c884f79032638b2d44a278b1992fda1b0ab28`.
- exp11 ZIP: `f2474f5b951bfd2d121291025c8dd4554697fb5bb4024e132987643dab6144a7`.

Five **full actual classes** are byte-identical across these two archives:
kConf, kEnvironment, kConfCacheManager, kCacheConfFactory and kSoapClient.
The real kConf top-level code loads its actual dependencies, changes the loader
and http/https wrapper state; actual getEnvMap() is called. There is no dummy
config/cache class. No getMap()/DB/cache backend is invoked: empty synthetic
configurations and Zend include directories exist only for relative path setup.
This is not the full API/configuration bootstrap or exp11-on-PHP7.4 support.

[Graph evidence](evidence/xml-lifecycle/coverage.json) records ready fullsource
generation 2026-09-25T12:19:00Z, five clean metadata-match paths, targeted class
lookup/snippet and a class trace. That trace omits method/require edges visible
in source; exact ZIP bodies, not graph absence, establish this bounded include
chain. No exhaustive caller or active-path claim.

## Planned matrix

**11 cases × 2 source subsets = 22 processes per runtime** (7.4 and 8.3):
bootstrap; good/malformed/missing WSDL constructor; explicit successful call;
magic successful call; nonexistent-operation SoapFault; existing external
callback; nested constructor in a resolver callback; nested successful call;
nested faulting call.

Original and exp11 subsets are separate provenance controls, not two independently
different implementations. Every process is fresh to prevent an original global
state leak from contaminating another case.

The WSDL and imported XSD are synthetic local files. The SOAP address is a
non-network `urn:xml-lifecycle:transport`; schema namespace URLs are identifiers,
not downloaded URLs. WSDL caching is disabled and files are readonly inside the runtime bind (the local preparation itself uses normal writable modes).
The expressly authorized fixture subclass overrides **only __doRequest** to
return a fixed SOAP envelope. Real kSoapClient/native SoapClient construction,
dispatch and response decoding still execute. **No real HTTP/network transport
or backend coverage** is claimed. Invalid operation faults happen before that
transport seam.

A fixed local file canary observes loader behavior before real kConf, after it,
within the synthetic transport and after the operation. Exact wrapper sets,
callback identity availability (runtime-dependent), native diagnostics, actual
loaded source hashes, functions, exceptions and result values are recorded.
The existing callback accepts only four exact fixture identifiers; it does not
forward arbitrary entities. In the nested-constructor case it creates another
real kSoapClient, recording the resulting state/exception rather than assuming
nested state is safe.

## Original flaws are controls, not repaired

kSoapClient's unchanged beforeCall/afterCall lack finally and ownership depth.
The malformed/missing constructor and invalid-operation cases are expected to
leave entities enabled and wrappers restored when afterCall is bypassed. The
collector requires those baseline observations rather than calling them secure.
A discrepancy is preserved as FAIL_RETAINED_OBSERVATIONS, not silently waived.

Normal successful operations without a pre-existing callback should end blocked,
with wrappers removed; callback-composition marker outcomes are separately observed;
nested outcomes are explicitly **not security approval**. No source replacement,
global deny callback, no-op deletion or lifecycle repair is under test yet.
Future finally/callback-stack changes require separate reviewed held patches,
precise prior-callback/wrapper restoration, nested/overlapping caller rules and
fresh unchanged-baseline comparisons.

## Guarded preparation / execution gate

The stage has 18 files (10 actual source members, probe, runner, six synthetic
fixtures), plus manifest and empty path-setup directories. Archives and each
source member are pinned; existing stage/output destinations are refused.
The runner restricts host, UID, subset and case, then verifies all source/harness
hashes before and on exit. Network/socket denial, readonly bind, private temp,
open_basedir and no production/DB paths apply. Missing modules or native fatals
remain failures. E_ALL/native stderr are retained; no @ or warning filtering.

The revised local suite has **30 Python tests**, including exact preparation,
bad archive/source pins, old flaw controls, class/source identity, missing canary,
bad scope/runtime/types, warning retention and retained SSH failure observations.
These synthetic tests are not actual PHP coverage. bash -n is also local only.
The initial actual Claude preparation CLI reached its outer timeout (**124**) after
21 tests, bash check, exact ZIP/source identities and fresh preparation all
completed with exit 0; it wrote a review before timeout. This is not CLI exit 0
or native approval. Its blocking contract findings were fixed before any VM:
- Preserve permissive pre-existing callback behavior as an explicit observation,
  not a universal "kConf blocks callback" expectation. The hypothesized bypass
  is still unexecuted; neither exposure nor blocking is invented.
- Tag resolver events by phase and require a WSDL/XSD URI during a non-observer
  operation. A marker canary callback alone cannot prove SOAP loader reach.
- Restore the diagnostic phase after each canary and nested resolver operation.
- Cover all 11 case families across both variants and runtimes in synthetic
  validator fixtures; these are not 44 actual runtime processes.
Initial sources/reports are retained under attempts/prep-r1; fresh local stage
r2 has its own manifest. Actual Claude correction review is terminal **exit 0**: 30 Python tests and bash
syntax commands also exit 0; frozen inputs unchanged. Its
[review](evidence/xml-lifecycle/claude-r2-review.md) finds no remaining blocking
defect for the bounded unchanged-source observation, not repair acceptance.
Native PHP/SOAP execution and lab ownership are still pending coordinator grant.

The canary is an active DOM parse, not a passive getter: it invokes any installed
external callback and changes diagnostic/last-error state. Its marker entity
identifier and observer phase are distinct from SOAP/WSDL events. Marker remains
allowed by the synthetic pre-existing callback, deliberately avoiding a fake
blocked result from deleting the canary permission. Exact full file URI and
canonical fixture path forms are accepted; arbitrary paths are not.
The current observational collector retains all native diagnostics but does not
yet pin a complete expected diagnostic set. Unexpected diagnostics must be
reviewed before any repair acceptance. Custom http/https wrapper replacement,
forwarded SOAP headers/options and overlapping independent execution are not
covered by this first lifecycle matrix.

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tools/php83/xml-lifecycle -p 'test_*.py' -v
bash -n tools/php83/xml-lifecycle/run.sh
python3 tools/php83/xml-lifecycle/prepare.py /tmp/php-xml-lifecycle-prep-new
# Only after coordinator grants exclusive lab ownership, fresh stage then:
python3 tools/php83/xml-lifecycle/collect.py 83 /tmp/php-xml-lifecycle-prep-new /tmp/xml-lifecycle83-new.json
```

Runtime binary/module/linked-library snapshots must bracket actual runs.
Native matrix and independent repeat remain NOT_EXECUTED. Criteria/DEBUG lab
ownership must be respected; this document does not authorize VM access.

## Private SOAP provider preparation (after missing-module finding)

Both labs lacked SOAP. No `apt install`, maintainer script or PHP INI mutation
was performed. Exact matching providers were downloaded/extracted into new
fixture-private directories (subsequently loaded only by the isolated fixture):

- 7.4: `1:7.4.33-30+ubuntu24.04.1+deb.sury.org+1`, Ondřej noble;
  DEB SHA256 `f25c5a8342b852ed5f97154e270f22805f4dc221132b15084c6936f59016511b`.
- 8.3: `8.3.6-0ubuntu0.24.04.11`, Ubuntu noble-updates;
  DEB SHA256 `eeb541e17950d330e01f5d0c47620ad45de92b64517320980691646777e4ad29`.

[Provider provenance](evidence/xml-lifecycle/provider-provenance.json) maps the
actual executed inspector revision to each report. The first 7.4 attempt stopped
on `gpgv` exit 2: a valid authorized signature plus an additional unknown signing
key. That failure is retained, not waived. A separate 7.4 phase used isolated APT
source/list/cache directories and the byte-identical existing Signed-By source;
APT authentication succeeded with insecure/unauthenticated options disabled.
8.3 used existing Ubuntu keyring and `gpgv` exit 0. Both chains verify signed
InRelease → uncompressed Packages digest → exact DEB hash and version.

ELF headers/dependencies were inspected before `ldd`; all resolved dependencies
already exist and are hash-pinned. No new shared library was installed.
`run-private.sh` uses a distinct immutable fixture stage, readonly module bind
and explicit `-n -d extension=/audit/soap.so`, retaining network denial and native
warnings. Interpreter, native XML/DOM/JSON modules, private SOAP and resolved
libraries are checked before and after each process. **Resolved-library identity
is not proof of every actual mapped library**; that limitation is not hidden.
The global original runtime identity is separately bracketed, not relabeled as
including the new private provider.

The first private-phase local review retained two blockers: a legacy test fixture
without the new phase metadata, and missing explicit mapping to the earlier
inspector that produced the 8.3 report. Corrected fixture/provenance and exact
provider version/hash guards now pass 35 local tests. Independent correction
review completed before native execution; local tests are not SOAP
behavior evidence.

## Final bounded-cycle disposition

Both labs are released. Actual independent local reviews and native repeats are
terminal; 36 local tests and shell syntax checks pass. This cycle is **not all
application contracts OK**: each native runtime retains four strict diagnostic
channel failures; no repair was selected or integrated. The first missing-SOAP
and mistaken hash-schema preflight attempts remain separate NOT_EXECUTED
application evidence. The exact corrected 7.4 stage is recorded in
[native harness identities](evidence/xml-lifecycle/native-harness-identities.json).

Next bounded work: independently review a precise two-channel diagnostic
contract without deleting native warnings; then prototype an explicitly held
8.3 lifecycle improvement with saved/restored callback, try/finally cleanup and
nesting ownership. The real class must be reviewed again before implementation.
Custom preexisting callbacks and HTTP wrappers need additional positive/negative
cases; no blanket restoration may replace wrappers belonging to other callers.
No-op deletion and a global deny callback are not accepted replacements.
Original7.4 controls stay separate from intentional improvement semantics.
