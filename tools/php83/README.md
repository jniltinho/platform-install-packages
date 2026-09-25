# Phase-1 PHP audit tools

These tools collect evidence, not application fixes. Use only an isolated lab.
No package postinst hooks or Kaltura application entrypoints are executed by the
syntax collector. It records every PHP-like file hash, return code and diagnostic.

```sh
# Guest has Python 3 and PHP 8.3; root is an already verified/extracted archive
# or a root assembled with dpkg-deb -x (NOT dpkg -i).
python3 lint-tree.py /path/to/tree /path/to/lint.json --php php8.3 --workers 4
```

`short_open_tag=1` and `error_reporting=E_ALL` are explicit. Symlinks are excluded.
The collector exits successfully when collection finishes even if files fail
lint: inspect `failed_count`. A passing file does not prove runtime compatibility.

## Pinned static analyzer

Run as an unprivileged user in the isolated lab, never in the Kaltura application:

```sh
cd analyzer
composer install --no-interaction --no-plugins --no-scripts
vendor/bin/phpcs --config-set installed_paths ../../phpcompatibility/php-compatibility,../../phpcsstandards/phpcsutils
vendor/bin/phpcs -i
vendor/bin/phpcs /path/to/tree --standard=PHPCompatibility \
  --runtime-set testVersion 7.4-8.3 --extensions=php,phtml,inc,php5 \
  --parallel=4 --report=json --report-file=/path/to/findings.json
```

`composer.lock` pins all dependency references; scripts/plugins are disabled and
standards are registered explicitly. Initial toolchain: PHPCompatibility
10.0.0-alpha2 (`e0f0e5a3dc819a4a0f8d679a0f2453d941976e18`) and PHPCS 4.0.4.
Composer is a lab-only tool; no Composer update is run in application packaging.

The analyzer is prerelease software with incomplete coverage. Findings are
candidates requiring manual triage, including legacy code that may already be
incompatible with 7.4. `testVersion=7.4-8.3` reports incompatibility anywhere in
that range, not only regressions introduced after the baseline. PHPCS status 3
can mean findings, not analyzer failure; always verify the JSON/totals.

References: [tagged dependency constraints](https://github.com/PHPCompatibility/PHPCompatibility/blob/10.0.0-alpha2/composer.json),
[release including PHP 8.3 checks](https://github.com/PHPCompatibility/PHPCompatibility/releases/tag/10.0.0-alpha2),
[coverage limitations](https://github.com/PHPCompatibility/PHPCompatibility#php-version-support).

## Test destination boundary

`lab_target.py` permits only literal `.74` or `.83` URLs matching the selected
lab identity, rejects userinfo/other ports/control characters, disables ambient
proxies and refuses all automatic redirects. This is a guard for the new
synthetic workload client, not a retrofit of the legacy sanity script.

```sh
python3 -m unittest discover -s tools/php83 -p 'test_*.py'
```

## Fixed library runtime probes and temporary include tracing

Run only against the checksum-verified, extracted public package payload, never
against a configured production tree. Copy both probe files to the same lab
folder, then run (substitute the matching lab's root and interpreter):

```sh
python3 run-runtime-probes.py /path/to/extracted/opt/kaltura/app php8.3 result.json
```

Each probe gets a separate process and 30-second timeout. The runner disables
URL fopen/include, but this is **not an OS network sandbox**. The five fixed
probes do not open a DB/network connection or read application configuration;
do not extend this to arbitrary `require` scans without OS-level isolation.
The JSON contains interpreter version, harness hash and per-probe output/status.
Exit zero from the runner means collection completed, not that all probes passed.
A load-only Propel success does not imply DB functionality. Environment and
extension versions differ between the baseline and candidate.

`include-trace.php` is temporary Apache `auto_prepend_file` instrumentation for
the disposable synthetic `.74` only. It records allowlisted labels, included
Kaltura file paths and last error *type*, never request content, URLs or errors.
Use a non-web-accessible `/var/lib/kaltura-audit-traces` directory writable by
Apache. Enable only for controlled requests and remove the Apache directive
and reload afterward. The collected inclusion set is not method-call coverage;
absence does not prove a file is unreachable. Do not deploy this to `.20`.

### Expanded sandboxed probes (v2)

The wrapper `run-sandboxed-probes.sh` now runs 15 fixed probes using systemd in
the two named disposable VMs only. Copy it, `run-runtime-probes.py` and
`runtime-probes.php` into the same dedicated guest folder, then run:

```sh
bash /home/vagrant/php-probes-v2/run-sandboxed-probes.sh > result.json
```

The payload and tools are bind-mounted read-only at `/audit/app` and
`/audit/tools`. The transient service uses nobody/nogroup, private networking
and temporary storage, no new privileges, denied socket/socketpair creation, hidden home/root
and configured application paths, a 512 MiB memory limit and 600-second overall
limit. Before invoking PHP, the runner verifies its non-root UID, read-only
payload, inaccessible protected directories, and denial of AF_INET socket
creation for AF_INET, AF_INET6 and AF_UNIX. No live network request is used to test this restriction.

These constraints are useful isolation, not a general untrusted-code sandbox.
Only fixed reviewed probes are allowed, not arbitrary application code. The
preflight is a partial check, not an independent attestation of every systemd
property; the wrapper hash records the intended configuration.
The hostname allowlist prevents accidental use on another host but is not
cryptographic host authentication; SSH identity/host-key validation is separate.

Each PHP process explicitly disables CLI OPcache/URL fopen/include and uses UTC;
normal lab extension configuration remains loaded and is recorded. Shutdown
output includes the path/hash of successfully included public payload files.
A fatal failure can omit the failing file from that list; do not interpret it as
complete attempted-file coverage. Original five-probe reports are preserved;
expanded evidence resides in `runtime-probes/sandbox-v2`.

Recreate the exit comparison (this is classification, not an acceptance gate):

```sh
python3 tools/php83/compare-runtime-probes.py \
  doc/php83/evidence/runtime-probes/sandbox-v2/php74.json \
  doc/php83/evidence/runtime-probes/sandbox-v2/php83.json
```

Different runner/probe/wrapper identities, flags or probe sets are rejected.
Successful probes must also match their expected fixed output. Runner exit zero
means collection completed, not acceptance; inspect `summary` and every record.
Module/INI file lists are recorded without dumping potentially sensitive INI
values. Duplicate PHP log output is disabled, not error reporting. The public
payload include path excludes ambient system PHP libraries. Timeouts are
incomplete evidence, never automatically classified as PHP regressions.
