# Native XML entity-loader policy experiment — executed bounded result

**Primary and independent actual Claude repeat passed the frozen native-policy
contract. No application patch is selected and kConf/kSoapClient are untested.**
Both labs have been released. The historical preparation below is retained as
phase context, not the current execution status.

[Final summary](evidence/xml-loader/final-summary.json),
[Claude execution/review](evidence/xml-loader/claude-native-review.md) and
[exact fixture/harness pins](evidence/xml-loader/harness-frozen.json).

## Current results

- Primary: 24 native processes / **1,008 parser observations** across PHP 7.4.33
  and 8.3.6 (12 processes / 504 observations each).
- Independent actual Claude: a further 24 processes / 1,008 observations,
  six serialized snapshot/matrix commands exit 0; reports **byte-identical** to
  primary. Native execution is evidenced by actual retained CLI tool calls and
  command sidecars, not by equality alone.
- Loaded libxml is 20914 in both runtimes. Binary/module/library identities remain
  identical before/after and across executors, per lab (55 baseline snapshot
  objects; 39 native83 snapshot objects). Baseline helper also records its older
  exp11 artifact pin; that is helper metadata, not application execution here.
- Every native process exits 0 with warnings retained, including malformed and
  DTD validation warnings. The six PHP8 enabled/legacy processes additionally
  retain E_DEPRECATED from the old policy switch.
- Canary reads succeed before blocking conclusions: each parser reads the local
  file and custom wrapper with NOENT, and the DTD with NOENT|DTDLOAD.

| Policy | DOM marker rows | SimpleXML marker rows | XMLReader marker rows |
|---|---:|---:|---:|
| enabled | 12 | 12 | 8 |
| default (no call) | 12 | 12 | 8 |
| legacy block | 0 | 0 | 0 |
| denying callback | 0 | 0 | 0 |

These counts are **per runtime**, not unique defects. Marker reads for file and
wrapper occur with NOENT, NOENT|DTDLOAD and NOENT|DTDLOAD|NONET in all parsers;
DOM/SimpleXML also expose them under DTDVALID. DTD contents appear under
DTDLOAD, DTDVALID and the combined flags in DOM/SimpleXML; XMLReader exposes them
under the NOENT combinations. Thus the combined NONET case still reads **nine**
local markers per enabled/default policy. Zero/NONET-only outcomes must not be
generalized to other flags.

**Simply removing the security call is unsafe within this tested corpus.**
The denying callback prevented marker exposure here, but its registration
lifetime, existing callback restoration, nested call composition and SOAP/WSDL
compatibility have not been validated. No drop-in application repair is proven.

Cross-runtime diagnostics are not falsely normalized: 36 denying-callback rows
differ only in native warning wording (7.4 says external entity "NULL"; 8.3 says
the resolver returned null). Exact deltas are retained in final-summary.json.
Other per-case fields match. Callback and old-block warning counts themselves
also differ, deliberately retained; no warning suppression was used.

## Source-grounded next lifecycle recommendation (not implemented)

The [bounded graph/source record](evidence/xml-loader/lifecycle-coverage.json)
rechecks graph freshness and coverage for kConf/kSoapClient. The class trace
omits visible method calls, so the exact source body, not an absence claim,
supports these observations. Source hashes are separately pinned.

- `alpha/config/kConf.php:7-11` disables entities and unregisters http/https.
- `infra/general/kSoapClient.php:5-24` brackets constructor, __call and
  __soapCall with before/after, **without finally**.
- Its lines 25-36 restore wrappers/enable entities, then disable entities/remove
  wrappers. Exceptions can bypass afterCall; no nested-owner state exists.

Options, in order of what can safely be claimed today:

1. **Retain the existing blocking calls temporarily.** Keep their deprecations
   visible while real lifecycle tests are prepared. This is not a repair of the
   existing exception-cleanup weakness, but avoids the demonstrated no-call
   regression.
2. **Experiment with an explicitly owned, scoped resolver policy.** A default
   denying callback is the promising native primitive, not a proven drop-in.
   Before changing the application, model loader ownership and previous state,
   then acquire/release an operation scope through try/finally. Use per-scope
   tokens and a stack/reference depth so one nested operation cannot disable or
   broaden a still-active outer scope. Distinct nested allowlists need an
   explicit restrictive composition rule, not unconditional enable/disable.
   Never replace an unknown third-party callback silently: first establish how
   its exact callable can be captured/restored on each supported runtime.
   Loader registration return values are not previous callback identities.
3. **Isolate exceptional SOAP loading in a separate process if shared-state
   ownership cannot be made safe.** This costs more and needs performance/API
   design review, but avoids pretending a process-global loader toggle is
   request-local in a long-running worker. This option is not implemented.

For option 2, start with **local synthetic WSDL plus XSD import** on actual
kSoapClient. An explicit fixture-only resolver may allow exactly pinned
canonical fixture paths while denying other external entities. Do not broadly
delegate arbitrary URIs to an earlier loader. A production URL allowlist and
redirect/address policy require separate review, not an unrestricted enabled
window. Leaving a denying callback installed while only calling the old
disable(false) is not proven to restore SOAP loading.

Next concrete acceptance matrix (real classes, no replacement stubs):
- Real kConf bootstrap with synthetic configuration; verify default external
  reads stay blocked and a pre-existing third-party loader is not lost.
- Real kSoapClient constructor with good/malformed/missing local WSDL and XSD;
  successful operation and SoapFault/exception paths, including constructor
  failure before an instance exists.
- Two nested clients/calls: inner success and throw must restore the outer
  policy; outer completion must restore the precise initial loader/wrapper
  state. A simple global depth counter is insufficient if scopes differ.
- Snapshot http/https wrapper state before/during/after; do not blindly restore
  built-ins over custom wrappers. Restoration must not mask the original
  SoapFault when cleanup itself fails.
- Repeat blocked external-entity canaries after every success/failure, and
  exercise multiple sequential operations in one worker. Callback behavior
  during libxml re-entry or overlapping execution remains a separate gate.
- HTTP/FPM, production SOAP endpoints and performance remain outside this local
  follow-up. No package/release gate closes here.

# Historical preparation and method

**NOT_EXECUTED on PHP/VM; no application patch is selected.** This phase measures
native parser policies before any proposed change to the 24 observed API
deprecations at `alpha/config/kConf.php:7`. It does not load kConf, kSoapClient,
KDOMDocument or application bootstrap and cannot claim application coverage.

The [PHP manual](https://www.php.net/manual/en/function.libxml-disable-entity-loader.php)
deprecates the old loader switch as of PHP 8, but explicitly distinguishes the
default from entity/DTD-enabling options. It recommends a custom external loader;
PHP 8.4's newer NO_XXE flag is not a PHP 8.3 repair. The
[loader callback manual](https://www.php.net/manual/en/function.libxml-set-external-entity-loader.php)
describes callback control. These are policy hypotheses to test, not permission
to delete a security call. `NONET` alone does not establish protection against
local files; the matrix deliberately tests that distinction.

## Bounded matrix

Each runtime (exact 7.4 or 8.3 family) has **12 isolated processes**, four policies
× three native APIs: DOM, SimpleXML and XMLReader. Each process parses 42 inputs
(six documents × seven flags), so **504 native parser observations per runtime**.
Fresh native objects are used per input; policy processes are separate.

Policies:
- `enabled`: old switch false, positive external-read control.
- `legacy`: old switch true, current startup-like blocking policy.
- `default`: no loader mutation; observe, do not assume secure.
- `deny`: external loader callback returns null and logs attempted identifiers.

Documents: plain text, internal entity, malformed XML, external local file entity,
a registered in-memory-only wrapper entity, and a local DTD defining the marker.
Flags: zero, NOENT, DTDLOAD, DTDVALID, NONET, NOENT|DTDLOAD, and the latter plus
NONET. Marker/DTD are synthetic static fixture bytes; never real host secrets,
remote servers, DNS or Riak/SQL/other backends. No entity expansion bomb.

The enabled policy must expose the marker in the file+NOENT, wrapper+NOENT and
DTD+NOENT|DTDLOAD controls for every parser before a blocking result is accepted.
Missing canaries fail the bounded matrix, not pass as secure. Denying policies
must expose no marker; callback mode must record attempted loads on those same
controls. Plain/internal positive parser functionality must remain observed.
Default-mode marker observations are reported without a security PASS claim.

XMLReader's initial XML() return is **not** successful complete parsing:
read() false means EOF or error. Diagnostics and values remain separate; malformed
inputs must produce diagnostics or an exception. We do not infer validity from
that initial return value or erase DTDVALID warnings.

## Safety, identity, and diagnostics

`run.sh` allowlists the named labs, UID, policy/parser and a host-pinned SHA256.
Stage manifest/source/probe/runner bytes are checked before and in the exit trap.
The service is readonly, private-network, socket-denied (EPERM), private-TMP,
with inaccessible production/DB paths and `open_basedir=/audit/probe`.
Marker references are fixed to that readonly fixture. PHP runs with -n,
explicit required XML modules, E_ALL and native stderr diagnostics.

The error handler records diagnostics and returns **false**: warnings and PHP8
deprecations remain in native stderr; no @, NOERROR/NOWARNING, reduced
error_reporting, internal-error swallowing or diagnostic equality assumption.
Positive enabled controls deliberately exercise a deprecated call too.

Coordinator must snapshot binaries/modules/linked libraries/INI before and after
each matrix. Source fixture hashes and module/libxml versions are in every probe.
The collector is not an identity snapshot replacement. Preserve failed attempts;
do not alter source/harness while an executor owns a frozen stage.

## Source context and remaining application phase

[Source identities](evidence/xml-loader/source-identities.json) pin five original
ZIP files. Parent supplied a ready source graph and clean targeted coverage;
the new fixture makes no exhaustive graph or reachability claim. kConf disables
the loader and unregisters http/https; kSoapClient restores wrappers and enables
the loader before calls, then disables/unregisters them afterward, without a
finally block. Character validation is not automatically XXE protection.

Later **separate full-source tests** must load real kConf/config dependencies and
kSoapClient with isolated local WSDL/import fixtures, exercise success and
exception cleanup, callback restoration/composition, stream-wrapper changes,
DOM option forwarding, and representative application consumers. No constructor
or dummy class stub may substitute for those real application tests. SOAP/FPM,
HTTP lifetime/global callback interactions, XInclude/XSLT, other wrappers and
full consumer inventory are outside this native policy phase.

## Local preparation and planned commands

26 local Python tests cover trusted preparation and synthetic validator controls
(including missing rows, duplicate rows, bool/int substitutions, missing canaries,
disclosure under block, missing callbacks, warning suppression, and source drift).
They are **not 26 PHP executions**. Bash syntax check passes. Host PHP lint is not
claimed. Actual Claude initial preparation review finished exit 0 and found real validator
gaps. Initial 14-test evidence and source are preserved under attempts/prep-r1.
The revised 26-test collector rejects malformed record types, missing PHP8
policy deprecations, wrong policy returns, wrapper access and marker leakage in
diagnostics under blocking policies. OSError/timeout now produce retained failed
records (partial timeout stdout/stderr preserved). Native warnings must also occur
in stderr. Actual Claude correction review is now terminal **exit 0** with 26 local tests,
bash syntax and its own mutation checks passing; verdict
[READY_FOR_BOUNDED_NATIVE_EXPERIMENT](evidence/xml-loader/claude-r2-review.md).
No VM ran. Remaining validator limits are explicit: an empty exception class/
message can satisfy malformed evidence, and stderr matching uses substrings
(empty diagnostic messages are not independently rejected). These synthetic
malformed-input limits are not claims about any actual native output. OSError
records preserve failure; only TimeoutExpired records carry incomplete/partial
stdout/stderr. The review's shorthand grouping of those two cases is not an
assertion that both have timeout fields.
File entity reads remain observable through returned marker text only; this is
not a syscall/file-access audit. Callback identifiers and wrapper events provide
stronger direct observation for those specific controls.

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tools/php83/xml-loader -p 'test_*.py' -v
bash -n tools/php83/xml-loader/run.sh
python3 tools/php83/xml-loader/prepare.py /tmp/php-xml-loader-prep-new
# Only after explicit lab ownership, a fresh /home/vagrant/php-xml-loader-r1 stage:
# snapshot before; then (runtime83 example):
python3 tools/php83/xml-loader/collect.py 83 /tmp/php-xml-loader-prep-new /tmp/xml-loader83-new.json
# snapshot after; compare; retain all warnings/failures; release lab.
```

No VM staging/execution is authorized by this document itself. Parent controls
the next run; package/release/application acceptance remains open.
