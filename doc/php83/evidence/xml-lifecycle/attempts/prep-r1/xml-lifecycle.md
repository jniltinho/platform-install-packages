# Real kConf / kSoapClient XML lifecycle — unchanged-source preparation

**Preparation only. No PHP/VM execution, application patch or artifact selection.**
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
not downloaded URLs. WSDL caching is disabled and all files are readonly.
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

Normal successful operations should end blocked, with wrappers removed;
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

The initial local suite has **21 Python tests**, including exact preparation,
bad archive/source pins, old flaw controls, class/source identity, missing canary,
bad scope/runtime/types, warning retention and retained SSH failure observations.
These synthetic tests are not actual PHP coverage. bash -n is also local only.
Actual independent CLI preparation review is pending.

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
