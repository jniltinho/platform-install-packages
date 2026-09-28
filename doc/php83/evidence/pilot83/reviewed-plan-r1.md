# First installed PHP 8.3 application pilot

## Current state and authorization boundary

**READONLY_PREFLIGHT_COMPLETE; PRIVATE_PACKAGE_BUILD_NOT_AUTHORIZED_YET.**
No package was generated, installed or changed in this phase. The coordinator
has asked for specific authorization to derive and install private laboratory
DEBs. This plan does not change production packaging, CI, published artifacts,
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
needed. CLI configuration is not evidence that the web or worker SAPI has the
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
Create separately identified **private `+php83lab` derivatives only after the
pending authorization**. Preserve each published input and record control,
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
   resolution before installation; any PHP74 or foreign-provider selection
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
ordering rather than forcing broken packages. Supply independently generated
lab-only DB/service/tenant credentials through private inputs; no `.74` or
production credential copy. Establish MariaDB schema/config before database
hooks, preserving required casing/SQL settings. Keep all exposed origins and
service bindings confined to the pilot host. Retain hook exit failures instead
of treating a launcher zero as success.

### C. Provider, configuration and privacy gates before USER

Follow [the provider decision](provider-pilot83-followup.md): install/activate the
exact matched native SOAP capability, verify CLI/web/worker identities and run
the existing local-WSDL control in the selected configuration. No PHP74 `.so`,
legacy APC alias or `apcu-bc`. Audit effective cache mappings; required first-layer
APC without a working intended backend is a concrete blocker. Two web requests
must establish the chosen cache read/invalidation behavior; inspect relevant
locks, not just `extension_loaded()`.

Audit effective writers, filters, extras, module/config identities and installed
privacy targets before new secrets. Use the approved append-window and journal
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

Current next blocker is the private-package scope authorization, followed by
exact DEB hook/payload composition and review. SOAP activation, cache selection,
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
