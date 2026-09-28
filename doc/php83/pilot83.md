# First installed PHP 8.3 application pilot

## Current state and authorization boundary

**PRIVATE_LAB_PACKAGE_DERIVATION_AUTHORIZED; NOT_INSTALLED.**

The user explicitly authorized the private `.83` DEBs on 2026-09-27
("pode fazer por favor"); implementation resumed on 2026-09-28. Historical
read-only observations below remain unchanged. No CI/publication/main/`.20` scope
is granted. Hooks and composed payloads require independent review before install.
No package was generated, installed or changed in this phase. The coordinator received specific authorization to derive and install private
laboratory DEBs. This plan does not change production packaging, CI, published artifacts,
main, releases or `.20`. The selected laboratory is only `192.168.56.83`, actual
hostname `kaltura-php83-lab`. The `.74` baseline is not owned by this phase.

The objective is a real installed native83 flow: API → synthetic USER → upload
→ actual worker → READY → source delivery. Earlier source probes, compiler and
API fixtures are prerequisites/evidence, not a substitute for this flow. No
benchmark or universal application/privacy acceptance is claimed.

## What was actually inspected

[Read-only guest report](evidence/pilot83/preflight-readonly.json) records Ubuntu
24.04.3, native PHP 8.3.6 / Ubuntu package revision
`8.3.6-0ubuntu0.24.04.11`, and enabled Apache PHP83 module. There is no
`/opt/kaltura/app`, `/opt/kaltura/bin`, `/opt/kaltura/web` or `/var/lib/mysql`.
The application, MariaDB, memcached, Elasticsearch and Monit are not configured
and running there. SOAP is absent. APCu exists; legacy APC does not.

The first hostname guard used the historical VirtualBox name and stopped before
inspection; a separate literal hostname/IP read established the actual guest
name above. The corrected guarded read then exited zero. No guest mutation was
needed. The package subquery itself returned exit1 with 290 stderr bytes for
missing package matches; the wrapper zero is not a package-closure pass. Virtual
package names may be uninstalled while their implementation modules are loaded;
the later dependency simulation must resolve that distinction. CLI configuration is not evidence that the web or worker SAPI has the
same effective configuration.

[Published control inventory](evidence/pilot83/published-control-inputs.json)
records the 17 original DEB hashes/control fields read from the published bundle.
The original bundle is immutable:
`kaltura-server-noble-repo.tar.gz`, SHA256
`91629580441f6a896ebf9e51f0256532221715bee57a3e5a64c66ff0c4e3127b`.
The candidate is the already verified exp14 ZIP, SHA256
`459feaf9caf2abe55963dce0cac51b8b593e4ff1b46d2eaf9cb7d5c3f13f62a1`.
Upstream ZIP SHA256 is
`58d534d09b3b75c9a8333957268c884f79032638b2d44a278b1992fda1b0ab28`.

## Smallest proposed installation delta

Use normal Debian package transactions, not fake installed-package records,
manual invocation of extracted maintainer hooks, or the RPM configurator.
Create separately identified **private `+php83lab` derivatives under the
recorded private-lab authorization**. Preserve each published input and record control,
payload and maintainer-script before/after hashes and exact reasons.

1. Keep the published non-PHP application/package layout and its existing
   packaging overlays. Apply the 76 selected exp14 source changes by strict
   original-source joins, then the tested five-target privacy policy on the
   exp14 side (trace/parameter copies, exact caller-frame skip, prepared SQL
   display metadata). Do not replace the whole packaged tree blindly: the
   package identity audit found generated clients/extras and deliberate source
   differences. A collision requires an explicit reviewed composition, not
   overwriting whichever version is encountered last.
2. Replace PHP74 dependency edges in base, front, batch, html5lib and html5lib3
   with the selected native83 equivalents; include matching SOAP. Other
   packages may need a private version only if their actual payload/hook is
   changed. Record the complete package closure and simulate dependency
   resolution before installation; any PHP74 or foreign PHP-runtime/extension provider selection
   fails this pilot. Do not silently update just one native extension.
3. Pin explicit `/usr/bin/php8.3` in generated application/worker settings and
   actual hook invocation. Apache remains the existing Ubuntu Apache module
   topology, not an unreviewed switch to FPM. Inspect real worker command lines
   and effective INI/modules after activation.
4. Adapt only necessary private maintainer-hook behavior: remove password and
   partner-secret values from child-process arguments and diagnostic output;
   use private files/FD/stdin with restricted permissions and cleanup. MySQL
   `--defaults-extra-file` may carry credentials, but the filename, not values,
   is the only argument. Secret-bearing `sed -e` substitutions and PHP script
   secret arguments also require replacement at their actual call sites.
   Preserve database statements and config output semantics. Do not claim
   privacy from merely disabling shell tracing or hiding the terminal.
5. Preserve installation logs and failures. Explicit fresh-cache initialization
   is not permission for blanket log deletion. The upstream db hook contains
   log cleanup and several hooks contain secret arguments, so the unmodified
   legacy installer is not the approved recipe. Retain useful diagnostics and
   never lower logging levels to make privacy checks pass.

The checkout's `deb/noble/install-aio.sh` also adds the PHP74 PPA and defaults to
`.20`; it must not be executed unchanged. `RPM/scripts/postinst/kaltura-config-all.sh`
assumes RPM/httpd and carries secret-argument/log-cleanup behavior; it is not an
Ubuntu installation shortcut. Actual DEB hook bytes must be joined to source
before transforming them; checkout inspection alone is not deployed provenance.

## Ordered executable milestones after authorization

### A. Freeze installation inputs and recovery

- Record guest identity, provider/package sources, free space, service/process
  inventory and immutable pre-install VM recovery point before mutation.
- Freeze the selected exp14 manifest and every cumulative privacy transformation
  and source identity, not just the ZIP filename/hash. Assign a distinct executor
  and independent reviewer for preparation and the first functional slice.
- Inventory and authenticate permitted non-PHP dependency origins (including the
  actual Elasticsearch prerequisite) with signed metadata and exact package
  identities; the PHP-provider restriction is not a claim that all application
  dependencies originate in Ubuntu. Unknown dependency origin blocks install.
- Build the private derivatives outside published output directories; verify
  payload manifest, strict source composition and dependency closure locally.
- Review the narrow hook/privacy transformations and run syntax/adversarial
  tests, then inspect the package transaction simulation. Do not execute
  unreviewed hooks just to discover their side effects.
- Retain private command output and public exit/category/identity receipts.
  On installation failure stop the exact owned services and recover the
  pre-install laboratory state; retain failed evidence before snapshot restore.
  This is a fresh installation rollback, not the five-file baseline overlay
  rollback recipe.

### B. Install and configure the isolated application

Use the existing package order as a starting point: postinst/base; UI payloads;
front; sphinx; db; batch; nginx; Elasticsearch; server. Confirm actual dependency
ordering rather than forcing broken packages. Before invoking those hooks,
freeze the installation output/log inventory and private credential canaries.
After installation, scan the bounded installation window and private command
outputs for those values without exporting them. Audit debconf/private config
permissions separately: intended restricted credential storage is not an
allowed public log emission. A leak blocks progression to application auth.
Supply independently generated
lab-only DB/service/tenant credentials through private inputs; no `.74` or
production credential copy. Establish MariaDB schema/config before database
hooks, preserving required casing/SQL settings. Keep all exposed origins and
service bindings confined to the pilot host. Retain hook exit failures instead
of treating a launcher zero as success.

### C. Provider, configuration and privacy gates before USER

Follow [the provider decision](provider-pilot83-followup.md), selecting Apache mod_php
(not its generic FPM alternative) for this pilot: install/activate the
exact matched native SOAP capability, verify CLI/web/worker identities and run
the existing local-WSDL control in the selected configuration. No PHP74 `.so`,
legacy APC alias or `apcu-bc`. Audit effective cache mappings; required first-layer
APC without a working intended backend is a concrete blocker. Two web requests
must establish the chosen cache read/invalidation behavior; inspect relevant
locks, not just `extension_loaded()`.

Audit effective writers, filters, extras, module/config identities and installed
privacy targets before nonce/USER secrets. Installation secrets are covered
separately by the stage-B gate above. Use the approved append-window and journal
scanners, fresh private nonce and full/prefix controls, fixed literal origin,
body-only requests, total deadline and no redirects/proxies. Preserve intrinsic
message/preformatted-string/inline SQL negative controls as limits; the policy
is scoped to the exercised flow, not universal redaction. An observed new leak
stops progression and identifies the narrow emitter before another upload.

### D. First functional vertical slice

Adapt the frozen `media-overlay-v3` driver into this pilot's new paths, changing
only reviewed host/provider/source/fixture identity assumptions. Never modify
that historical driver. Prove actual native83 web SAPI, reject invalid secret,
accept synthetic USER type0 and reject admin escalation. Then create one owned
entry and upload the existing 10-second technical fixture, verifying tenant,
entry, asset and original source SHA bindings throughout. Observe actual83
workers/process identities until READY, list/get the same owned media, and
verify delivered original bytes over the fixed-origin HTTP path. Retain all
phase failures, source/config pre/post checks, finite log-window results and
cleanup. A PHP83 runtime incompatibility is a new measured repair task, not an
excuse to route that operation through PHP74.

Initial HTTP source delivery is deliberately not TLS/HLS/playback acceptance.
After this slice works, schedule independent actual execution and the remaining
TLS/206/HLS, UI/search, conversion/failure/recovery/reboot and broader cache
checks already required by the proposal. Do not add all those as artificial
prerequisites to attempting the first slice, and do not mark them done from it.

## Comparability and open boundaries

Both installed laboratory sides will carry the explicitly approved privacy
policy, but `.74` is a **modified laboratory baseline**, not unchanged published
packages. Native83 package/hook/runtime changes must also be documented before
any later performance comparison. No timing claim is made here.

Current next step is exact DEB hook/payload composition and review under the
received private-package authorization. SOAP activation, cache selection,
installation, USER, worker READY and delivery on native83 are **NOT_EXECUTED**.
The 51-task proposal is not closed by this plan. Published package/CI/release
integration remains a separate gate.

## Source-discovery limits

The packaging graph is ready at generation `2026-09-25T19:28:02Z`, but points to
the main sibling rather than this migration worktree. Checked installer/base/
front/batch paths had metadata matches and no recorded coverage issue; the
mistyped provision path was absent and the actual bootstrap was read directly.
Exact local source reads and actual DEB control bytes support this plan, not a
claim that the graph indexes every migration tool. Full source/provider graph
coverage and its limits are recorded separately in the provider follow-up.

## Independent plan review and exact hook join

Actual Claude CLI completed local read-only review with exit0 and no VM/tests.
Its public final and terminal are retained in `evidence/pilot83/claude-plan-review.*`;
the reviewed original plan is `reviewed-plan-r1.md`. The current revision closes
the concrete wording gaps concerning PHP-only origin restrictions, installation
credential windows, package-subquery exit, explicit mod_php and future input
freezes. These are preparation changes, not runtime passes. The review's date
objection is not adopted as a factual error: live UTC was 2026-09-27 while São
Paulo was still 2026-09-26; the provider document uses the UTC date.

`published-hook-inputs.json` records 26 actual maintainer-hook hashes: 14 exactly
match checkout files. Base/front/batch/db postinst are exact matches. The bounded
static candidate scan confirms password-bearing commands there and in html5lib,
and database postinst line263 log deletion. It does not claim an exhaustive
secret-flow audit or execute any hook. Actual DEB controls, payload scripts and
all reached sensitive call sites remain inputs to the authorized derivation.

## Authorized implementation checkpoint (2026-09-28)

Local composition now joined all 17 pinned published DEBs (43,765 payload
members) to 78 unique replacement/addition targets: 76 selected exp14 paths,
five privacy targets with three overlaps. The single new XML helper is absent
from upstream/published payload; every replaced source exactly matched upstream
before composition. The two known packaging source overlays and generated
clients are outside the changed set. R4 pins imported privacy helpers before
execution and checks all five resulting hashes against prior native evidence.
Fourteen local payload tests and independent Codex review passed; actual Claude
executed the earlier ten payload/eight control tests and inspected the joins.
No inference of installed application acceptance follows.

All 17 control files have private revision suffix `+php83lab1`; five runtime
packages substitute PHP74 dependency tokens with PHP83, and base explicitly
requires the selected matching common/SOAP revision. `control-preparation-r1`
is not an APT-resolution result. Read-only native83 APT metadata confirmed the
matching SOAP candidate and Ubuntu MariaDB/Sphinx/FFmpeg/memcache dependencies;
Elasticsearch requires its separately authenticated origin and pinned ICU plugin.

Actual Claude found two concrete R1 hook defects despite 16 passing local tests:
MySQL command substitution also changed one database-name argument, and two
legacy destructive reinstall branches still passed the root secret in argv.
R2 preserves the database argument and deliberately rejects both destructive
branches with exit94. This pilot supports **fresh installation only**. Source
failures now abort92. Seven postinst files and the reached functions.rc change;
all old optional redirects remain explicitly historical, not proof of successful
hook execution. Claude R2 executed19 tests and confirmed the exact27 transformed
records. The two transport helpers remain byte-identical to reviewed R1.

The real native83 PHP bridge ran eight synthetic cases plus lint successfully,
with argv/argc/server fields, empty/newline/Unicode arguments, exec-argv privacy,
permission/symlink/target failures and cleanup checked. `bridge-native-primary-r1`
records exact helper/probe/PHP binary/CLI-INI before/after identities. This is not
full linked-library attestation or an installed application request. An initial
reviewer suspicion about a literal backslash-n was incorrect: AST/native execution
confirmed the actual newline, and the proposed edit's assertion failed without
changing the probe hash. No fixture credential was exported.

The first two complete private builds both exited0, but the independent actual
verifier rejected their lone blank md5sums line in three payload-empty packages
(front/db/server). That failure is retained. The builder now emits an empty
file, not a newline, for an empty checksum inventory; an eighth local test covers
it. Two fresh R2 builds and the unchanged strict verifier are the next checkpoint.
No failed artifact is eligible for installation. Published input archives remain
intact and no maintainer hook has run. The verifier additionally checks all
outside-allowlist bytes, types, links, modes and numeric ownership, including
36 originally uid/gid500 members, and full repeated DEB byte identity.

Installation still needs the actual verified R2 artifacts, immutable recovery
point, APT simulation, fresh database/credential preparation and bounded
installation-log privacy checks. No synthetic USER/upload on native83 has run.

### Verified packages and handoff state

Both fresh R2 builds completed; the unchanged independent verifier then passed
all 17 packages (177,120,680 total bytes per build). Actual Claude independently
ran that same verifier and produced an identical complete result object. Evidence:
`verifier-actual-r2.json` and `claude-private-debs-r2.json`. Numeric ownership,
all unchanged members and regenerated md5sums were checked, not merely the
builder's report. These artifacts remain private and **NOT_INSTALLED**.

VirtualBox recovery snapshot `5fbc9e28-ae82-4410-aa24-978eb408f019`, named
`php83-pre-private-pilot-20260928`, completed successfully for the exact `.83` VM.
The post-snapshot check confirmed application/database absence. The local combined
pilot test suite ran 88 tests successfully; this count is not application tests.

A subsequent artifact-stage promotion stopped before any destination write:
`/var/lib/kaltura-php83-pilot` already existed with a `simulation-r1` receipt.
This agent did not create or execute that stage. Its read-only, allowlisted
metadata says APT simulation exit0, native revision `.11`, no mutation and no
origin acceptance; application and database remain absent. The coordinator must
attribute/reconcile that existing stage before continuing, rather than overwrite
it or count this agent as its executor. My separate transfer remains in
`/home/vagrant/pilot83-transfer-r1`; all of its artifacts are non-secret. The
failed stage assertion and the compound transfer command's missing shell
fail-fast behavior are recorded explicitly in `stage-transfer-r1.failure.json`.
No credentials were generated and no package install was attempted by this agent.
