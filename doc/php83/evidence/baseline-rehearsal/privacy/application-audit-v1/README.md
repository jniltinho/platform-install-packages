# Installed baseline privacy audit — read only

All recorded commands are terminal; no source/config/service/application changes,
HTTP requests or private USER credential file reads. Six local tests passed;
independent Codex exp9 reviewed the local audit and its bounded interpretation.

- Sixteen installed source files match the pinned upstream ZIP, including all
  four overlay targets, logging factory and exact filesystem configuration parser.
  Files regular/single-link; UID/GID/mode retained. Runtime/source before/after
  stable. PHP7.4/json and cache audit's memcache module match established pins.
- Real kFileSystemConf ordered host resolution/merge selects logger.ini's api_v3
  map. Three Stream writers, three Simple formatters with message placeholder,
  Priority/Type filters, extras keys without message. API/analytics/tests sinks
  are local. The reported core-writer mapping is supported by pinned factory
  source, NOT a live writer-instance inspection. Existing APC object unobserved.
- Both local and remote config-cache endpoint configurations are nonempty.
  Bounded direct native Memcache GET performs **four GETs over two named keys**:
  local CONF-MAP-logger and remote CONF_CACHE_VERSION_KEY, each twice. Logger is
  missing on both local reads; configurations privately stable, no diagnostics.
  Cache values/hashes never exported. Disk equivalence is conditional on a fresh
  worker after startup cache invalidation, not proof of an existing APC object.
- Reused unchanged logging_preflight checks55 configuration files for known
  body/piped/forwarding patterns and running forwarding agents. Stable private
  hashes never exported. This is its existing bounded check, not universal proof.
- Apache maps the PHP7.4 module; two daemonized PHP processes resolve to
  KGenericBatchMgr.class.php and populateElasticFromLog.php. Initial environment
  audit misses relative script names; environment-r2 resolves cwd safely, keeping
  both observations. No process argv/environment content is exported.
- Both installed init scripts exactly match reviewed repository scripts. Monit
  configuration identifies batch/apache. Monit summary exit1 is retained and
  classified as HTTP interface disabled, not authorization/permission failure.
  Do not enable its management interface. A reviewed short supervisor maintenance
  window can use the existing systemd service rather than a disabled HTTP control.

Minimum remaining application boundary: reviewed rollback transaction with fresh
source/config/init/PID-file joins; coherent four-file overlay and restarted known
workers; effective post-restart provider/logger proof; bounded invalid nonce
privacy check before USER. Approved append-window r2 handles files; journal is
separate. No benchmark acceptance and no published-artifact modifications.

The eventual reference must be labelled published PHP7.4 with an **approved
privacy overlay**, never published-intact. Negative intrinsic/pre-rendered/extras
leaks from the synthetic corpus remain explicit outside the exercised gate.
