# PHP 8.3 provider runtime probes

Date: 2026-09-25. Progress on T4-01 / original 1.4, **not completion** of the
provider decision, Kaltura acceptance or production packaging integration.
[Scripts and reproduction](../../tools/php83/provider-probes/README.md).

## What was exercised

Separate pinned Docker images, no host mounts/published ports/host networking,
1 CPU / 1 GiB / 256 PIDs per probe. Only public scripts and package repositories
were supplied. No VM or existing Docker service was modified. Each provider
installs its PHP stack in a fresh disposable filesystem and answers real GET
and POST requests on **127.0.0.1:18083**, not merely `php -m`/`php-fpm -m`.

| Target | Candidate provider | Runtime observed | Web SAPI | Scoped result |
|---|---|---|---|---|
| Ubuntu 24.04 | Native Ubuntu | PHP 8.3.6 (Ubuntu security package revision in log) | apache2handler | CLI, GET, POST and invalid-POST rejection passed |
| Ubuntu 26.04 | Sury exact `resolute` suite | PHP 8.3.35 | apache2handler | Same provider fixture passed |
| Rocky 9 | Remi `php:remi-8.3` with EPEL/CRB | PHP 8.3.35 | fpm-fcgi through Apache/Unix socket | Same provider fixture passed |
| Rocky 9 native AppStream alone | `php:8.3` | Full requested transaction not resolved | Not started | Required probe packages `php-pecl-memcache` and `php-pecl-ssh2` not found; exit 1 |

The image identity and resulting OS/package versions are distinct: the pinned
Rocky base reports 9.3 before repository package transactions. This is a provider
container, not proof of full Rocky VM installation/reboot/security-policy behavior.
The previous native Ubuntu 26.04 probe remains a separate historical observation;
it was not reexecuted in this batch.

The fixture enforces the intended minor version and SAPI, loaded extension set,
PDO mysql driver, and bounded local operations for JSON, multibyte strings, math,
XML, image capability and normalization. SSH2/LDAP/memcache/APCu checks do not
connect to backends. INI paths, modules and synthetic per-run nonce are retained.
Invalid POST must return 500 with the expected failure category. No full API,
TLS, worker, media or performance acceptance is claimed.

## Findings that change the next action

1. **Legacy RPM dependency mismatch confirmed.** The installed Remi set supplies
   APCu, but `rpm -q --whatprovides php-pecl-apc` found no provider. Current
   front/batch RPM specs still require that capability. The source cache API and
   configuration need an explicit compatibility investigation; do not simply
   equate APCu with APC or change production dependencies before go/no-go.
2. **Native Rocky-only transaction is insufficient for this probe set.** Missing
   memcache/ssh2 is now an actual failed installation transaction, not inference
   from a partial package listing. This does not prove no combination of other
   reviewed repositories could satisfy it.
3. **Probe setup fixes, not application fixes.** Initial Ubuntu attempts stopped
   when packaged Apache envvars read optional unset variables under `set -u`.
   Nounset is now disabled only while sourcing that packaged env file; normal
   strict shell handling resumes immediately. No PHP diagnostics were suppressed.
4. **Signing-key failure retained.** The initially pinned Remi 2019 key rejected
   the release RPM. `rpmkeys -Kv` reported key ID `478f8947`; the official 2021
   key fingerprint `B1ABF71E14C9D74897E198A8B19527F1478F8947` was verified and pinned
   before retry. Signature checks stayed enabled. RPM header signature reporting
   uses `RSAHEADER`, not the legacy `SIGPGP` field that printed `(none)`.
5. **Strict collector caught log interleaving.** FPM startup notices initially
   landed between CLI response markers. The collector rejected the evidence
   rather than ignoring arbitrary lines. Service output now goes to dedicated
   temporary logs, emitted after response frames; messages are retained, not
   suppressed. Final primary and independent matrices were rerun on this fix.
6. **Sury bootstrap pin strengthened.** The official HTTPS keyring DEB is pinned
   to SHA256 `7511384559c9ddf1d5ce5f60be429ae9d4e7d01d9480d6f1b7a30c0810cf8b60`
   before executing its installation. This pins the observed artifact; it is not
   independent authentication of provider ownership or a support commitment.

The [official Sury bootstrap instructions](https://packages.sury.org/php/README.txt)
use the provider keyring package and suite-specific signed APT configuration.
The [official Remi configuration](https://blog.remirepo.net/pages/Config-en)
documents the EL9 release RPM, CRB/EPEL prerequisites and signing fingerprints.
Both references were checked in this batch. They are configuration references,
not proof that all Kaltura workflows support these providers.

## Evidence and remaining gate

Raw install/request logs, failure attempts, script/input hashes and structured
results live under [evidence/provider-runtime](evidence/provider-runtime/).
The CLI review of packaging metadata identifies declared dependencies, not an
exhaustive use inventory. Grok's review attempt timed out and was replaced by
OpenCode Muse Spark; these executions must remain separately attributed.

T4-01 / 5.16 and original 1.4 stay unchecked: final mandatory-extension/use and
ABI reconciliation, provider/support/update policy review and operator decision
remain. Follow with APC/cache compatibility analysis and real application runtime
acceptance. Nothing here approves package/CI integration, a release or `.20`
cutover. Existing release and rollback gates are unchanged.

## Agent execution and accounting

- Claude audited the declared packaging dependencies, then independently ran
  Noble and Rocky/Remi in separate disposable containers.
- Cursor reviewed scripts, independently ran Resolute and reviewed/executed the
  local evidence-collector suite.
- Grok's bounded script review hit its 120-second deadline (exit 124). OpenCode
  Muse Spark performed the fallback code review and shell syntax checks. Its
  later attempted Remi rerun was auto-rejected by the CLI's external-directory
  permission policy: process exit 0 did **not** mean the test ran. No safeguard
  was bypassed; Claude performed that independent runtime rerun instead.
- The collector independently requires the exact 35 web extensions (+ pcntl
  for CLI), all 15 named smoke checks, matching SAPI/method/minor version, fresh
  per-run nonce consistency, ordered unique response markers, the invalid-POST
  marker and zero script exit. Twenty-nine new offline tests include reduced
  module/check declarations and malformed evidence rejection. The full local
  suite contains **109 passing tests**, independently rerun by Cursor.
- Readiness polls are not counted as additional test cases. The three providers
  each have CLI, GET, POST and invalid-POST cases; independent reruns do not
  inflate that coverage denominator. No application task checkbox is closed.
