# Native XML entity-loader policy experiment — preparation

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

14 local Python tests cover trusted preparation and synthetic validator controls
(including missing rows, duplicate rows, bool/int substitutions, missing canaries,
disclosure under block, missing callbacks, warning suppression, and source drift).
They are **not 14 PHP executions**. Bash syntax check passes. Host PHP lint is not
claimed. Actual independent local preparation review remains pending.

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
