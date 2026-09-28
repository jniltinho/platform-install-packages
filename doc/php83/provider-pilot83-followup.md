# Provider decision for the first installed PHP 8.3 pilot

2026-09-27. **Local evidence audit and proposed pilot decision only.** No VM,
package install, INI edit, cache activation or source patch was executed here.
The candidate agent owns the native83/AIO environment. This is not a release,
all-feature acceptance, or a substitute for the missing provider checks.

## Smallest coherent choice

Use **Ubuntu 24.04 and the already measured native 8.3 provider**, keeping CLI,
Apache PHP module or FPM, every worker interpreter and extensions in the same
provider/ABI/revision set. Add/enable the exact matching SOAP capability in that
isolated pilot only after coordinator approval. Keep APCu distinct from legacy
APC; do not install a global `apc_*` alias or pretend a dependency rename repairs
all cache consumers. Do not introduce a new PHP minor/third-party suite merely
to avoid these two gaps. This selects a repeatable laboratory starting point,
not a recommendation to freeze security updates forever.

### SOAP: require the capability, do not waive it

The historical 18 provider observations lacked SOAP. A passing JSON API or upload
can therefore coexist with an untested SOAP path. The original full
`infra/general/kSoapClient.php:2` extends native `SoapClient`; loading that class
requires ext/soap, regardless of whether the current test request invokes it.
Its constructor and call methods actually invoke the parent and change loader
state. No whole-application reachability/absence conclusion follows from a graph
class trace with zero edges. Do not call the SOAP requirement passed because a
particular media request did not load it.

There is already a concrete compatible provider, not a hypothetical install:
[evidence/xml-lifecycle/provider83-extraction.json](evidence/xml-lifecycle/provider83-extraction.json)
records signed Noble-updates metadata, exact package dependency and extracted
module:

- `php8.3-soap`, `8.3.6-0ubuntu0.24.04.11`, amd64; its exact dependency is
  `php8.3-common (= 8.3.6-0ubuntu0.24.04.11)`.
- DEB SHA256 `eeb541e17950d330e01f5d0c47620ad45de92b64517320980691646777e4ad29`.
- `soap.so` SHA256 `f26e8721dbdd2c2867351c26d99a9048a0f99fe6058162522a9d7e6a8119b467`,
  ABI directory `20230831`, with linked-library identities retained.
- Signed Release → Packages → DEB chain and extraction commands are recorded;
  original PHP83 execution used the r1 provider verifier, not the later74
  authentication implementation. See the provenance report/correction alongside it.

The later real-class XML lifecycle and [actual ZIP XML corpus](exp13-xml.md)
already exercised private SOAP loading, including success/fault/nesting and the
loader repair. That proves a usable module for those frozen processes, **not**
installed Apache/FPM/worker activation or real remote SOAP transport.

**Pilot gate:** recheck package/module/interpreter identities on the owned AIO
lab; enable only the matched83 module in the owned runtime configuration; record
`extension_loaded('soap')`, native `SoapClient` and `SoapFault` availability in
CLI, actual web SAPI and actual worker command environment. Execute the existing
synthetic local-WSDL lifecycle control under that selected configuration before
calling the extension requirement closed. Do not use PHP74 modules, silently
upgrade only one shared object, or retrofit old provider reports. Package or
identity drift means a new reviewed cohort, not reuse of these pins by name.
PHP documents SOAP as a separately enabled extension.
[Official SOAP installation](https://www.php.net/manual/en/soap.installation.php).

### APC: an explicit inactive legacy backend, not an alias

The bounded original sources make a configuration-dependent distinction:

| Source | Actual consequence without legacy functions |
|---|---|
| `alpha/config/cache/kApcConf.php:11–78` | Checks `apc_fetch`; inactive layer returns null/false. Store is also disabled in CLI. |
| `alpha/config/kConfCacheManager.php:6–30,123–161` | Iterates session/APC/local/filesystem/remote map layers, so another layer can satisfy a map. This is not proof each installed backend works. |
| `infra/KAutoloader.php:50–82,329–337` | APC operations are guarded; class-map loading remains a separate path. |
| `alpha/apps/kaltura/lib/cache/kLoggerCache.php:20–44` | Guarded APC fetch/store; logger construction from effective configuration remains available. |
| `infra/cache/kApcCacheWrapper.php:14–18` | Initialisation returns false; the backend is unavailable, not magically APCu. |
| `alpha/apps/kaltura/lib/cache/kCacheManager.php:71–118` | Failed initialization becomes null; single-layer selection uses the first section only. A list containing another backend is not automatic failover. |
| `infra/general/kLockBase.php:106–116` | Missing `apc_add` returns null; lock-sensitive callers cannot be called equivalent without their own observed contract. |

The [63-assertion direct-alias experiment](apcu-cache.md) failed four counter
assertions on both runtimes and was independently reproduced. The narrower
[web cache fixture](apcu-web.md) covers only configuration-map fetch/store/delete
with fixture aliases and a stub environment, not application cache acceptance.
APCu's counter API can create missing counters; that does not preserve the
legacy missing-counter expectation. PHP's manual explicitly states that
`apcu-bc` is unsupported as of PHP8. Do not propose it as the83 provider fix.
[APCu installation](https://www.php.net/manual/en/apcu.installation.php),
[APCu counter API](https://www.php.net/manual/en/function.apcu-inc.php).

**Pilot decision proposed:** keep the already observed absence of legacy APC
functions, with no shim and no new activation. Treat APCu as its own extension,
OPcache as opcode cache, and existing memcache as memcache (not memcached).
Before first full application request, audit effective cache mappings and
backend classes without exporting credentials/configuration values. Every
pilot-required cache mapping must resolve to a working intended backend; a
required first-layer `Apc` mapping or failed required lock is a blocker, not a
warning waiver. Reuse the application's existing filesystem/memcache layers
only where its effective configuration and real tests establish them; do not
silently rewrite all mappings or assert fallback from source alone.

Minimum installed tests are two web requests proving configuration/reflection
read + invalidation/reload and observed backend selection, then the real
nonce → USER → upload/READY/source-delivery gate with the selected83 workers.
Include the relevant actual cache/lock path if that operation requires it. Keep
opcode-statistics/admin APC view, legacy upload-progress and inactive vendor APC
paths explicitly **unaccepted**, not rebranded as APCu support. If any is required
for the claimed pilot scope, repair/test it before widening that scope. Full
feature parity/release remains blocked until the broader cache disposition is
resolved; the limited pilot is not a hidden waiver.

## Decision delivered to the AIO owner

1. SOAP has a concrete already authenticated matching83 module; plan its owned
   SAPI activation and runtime proof instead of a new provider search.
2. Legacy APC remains absent, explicitly, unless a separately reviewed migration
   is implemented. First audit effective mappings; do not add the rejected alias.
3. Hold the first **full83 acceptance claim** until the two gates above and the
   installed privacy/media flow actually execute. This task itself clears none
   of those runtime gates and does not alter package dependencies.

## Source evidence and limits

Graph project `kaltura-rigel-18.20.0-full` was ready; generation
`2026-09-25T12:19:00Z`, coverage recorded `12:19:04Z`, generation match true.
Exact-name search for the five cache/SOAP classes returned five rows, no more;
`kCacheManager`/`kConfCacheManager` snippets were read. The class-level SOAP trace
returned zero edges and was not used to infer inactive/unreachable code. Direct
reads of all eight paths below confirm the positive guard/control-flow claims.
Each exact path received `no_recorded_issue` / `metadata_match` coverage; this is
best effort, not exhaustive callgraph proof. The earlier 31-file APC literal
inventory remains in the historical APC report; no new exhaustive sweep or
claim that all direct consumers are handled is made here.

The following original-source SHA256 identities are joined to the immutable
original ZIP. Candidate/pilot sources still require their own actual-artifact
joins; an old source audit is not a deployment identity.

- `infra/general/kSoapClient.php`: `6fe1abef06f3f365fc1862de0e25ffeaef9da156e731fd7cc17b386623561b7e`.

- `alpha/config/cache/kApcConf.php`: `b866a78b84862006c5f4fa3a2b4fdeb7b30f5627dedb25d177465c728c7882a0`.

- `alpha/config/kConfCacheManager.php`: `19d4ffb4866339cae93eb8949fd06275978799804454e81d68dd7692fe050333`.

- `infra/KAutoloader.php`: `900cf01ffbab75b501358501f43bc84b086a45a1fbb8efdc3aee09837852fbf1`.

- `alpha/apps/kaltura/lib/cache/kLoggerCache.php`: `8300f56aacf491425f33935b8de749a553f36d3b21637bea5ddfd0a34da1c208`.

- `infra/cache/kApcCacheWrapper.php`: `f6e7df97e236ed6d2ac1f7d05bed17cba697a9d25d5ca485176076b8d845484f`.

- `alpha/apps/kaltura/lib/cache/kCacheManager.php`: `8aafeda151da7e9a14135abd7a0e094396a71ca9fe721d5ba24a9ba19697798b`.

- `infra/general/kLockBase.php`: `0ec22197d23184a7ab467235c760e14abf7c1e7eae925bb91ce478e3d5614348`.
