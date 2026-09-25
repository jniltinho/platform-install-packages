# Whole-candidate paired PHP 8.3 compiler scan

## Result: collection complete, candidate still rejected

The [primary summary](evidence/candidate-syntax/primary-summary.json) records a
fresh paired scan of the original Rigel archive and exp9 on the same isolated
PHP 8.3.6 runtime. **Exp9 still has 54 compiler-rejected files.** This is not a
successful whole-application migration, an acceptance waiver or release approval.

| Artifact | PHP-like files scanned | Compiler rejected | Accepted with diagnostics | All diagnostic files | Incomplete |
| --- | ---: | ---: | ---: | ---: | ---: |
| Original | 11,784 | 58 | 64 | 122 | 0 |
| Exp9 | 11,784 | 54 | 64 | 118 | 0 |

Exit 255 means the individual compiler invocation rejected a file. A diagnostic
on an exit-zero file is **not** a compiler rejection. The collector's zero exit
means collection finished, not that all files compile. Its explicit
`candidate_all_files_compile` field is false and `application_acceptance` is false.

Four prior rejections now compile: Services_JSON, dateUtils and Zend JSON
Decoder/Encoder. There are no new compiler rejections in this paired case.
The 16 changed PHP source files exactly match the exp9 manifest's selected
source targets. Remaining failures comprise 49 vendor, four alpha and one infra
file; their exact paths, hashes and diagnostics are listed in the summary.
They must be adjudicated and repaired with behavioral tests, not silently
excluded because their entrypoint reachability is currently unknown.

## Immutable inputs and constrained execution

- Original ZIP SHA-256:
  `58d534d09b3b75c9a8333957268c884f79032638b2d44a278b1992fda1b0ab28`.
- Exp9 ZIP SHA-256:
  `cb61e4cd11009bbf9e6e362dfafa5ef2f4af22da817c75fedbd7741a08e44cbc`.
- Fresh stage: `/home/vagrant/php-candidate-syntax-exp9`, on
  `kaltura-php83-lab` only. No baseline74, SQL or `.20` work occurs here.

Both ZIPs and all extracted file bytes are verified before and after scanning.
The inventories contain 15,175 original files and 15,193 candidate files. The
selection is `.php`, `.phtml`, `.inc`, `.php5`, case-insensitive: 11,619 `.php`
and 165 `.phtml`; no `.inc` or `.php5` files occur. The other 3,391 original and
3,409 candidate files are individually listed with hashes and exclusion reasons;
the candidate's extra 18 are experimental metadata. This extension policy does
not prove coverage of extensionless scripts, embedded/generated PHP or runtime
code generation. No packaging overlay is applied by this case.

The trusted PHP interpreter is invoked only as:

```text
/usr/bin/php8.3 -n -d short_open_tag=1 -d error_reporting=32767 \
  -d display_errors=stderr -d log_errors=0 -l /audit/VARIANT/PATH
```

No application include, bootstrap, script body or package hook executes. `-n`
avoids ambient INI and extension loading. Binary hash, version, linked-library
hashes, built-in module list, no-INI output, fixed environment, harness hashes,
per-file commands, hashes, statuses and diagnostics are recorded in
[the full report](evidence/candidate-syntax/primary-r2.json). Four bounded workers
scan each variant sequentially; each file has a 20-second timeout. A timeout or
nonzero status other than 255 is incomplete evidence, never a compiler regression.

The unprivileged systemd runner has private network/tmp/devices, denied
`socket`/`socketpair` syscalls, no new privileges, resource limits, protected
home/system and explicit read-only audit binds. It verifies the read-only mount
flags. The block action is EPERM, not permission to open a socket. SSH host-key
policy remains inherited from the existing lab configuration; the hostname
check is a guard, not cryptographic machine identity.

### Retained unsuccessful first attempt

The original wrapper's default syscall-filter failure action terminated its
main process with **31/SYS**, before a report was produced. The original
`primary.exit` is 1, its output files are empty, and the original wrapper and
[authoritative unit journal](evidence/candidate-syntax/primary-attempt1-journal.txt)
are retained. This is a harness failure, not a compiler finding or a pass.

The correction sets `SystemCallErrorNumber=EPERM` while retaining the same denied
syscalls and private networking. The successful fresh run is explicitly named
`primary-r2`; no initial report was overwritten. The journal does not identify
the exact triggering socket call, and this report makes no such claim.

## Independent repeat commands

Obtain exclusive php83lab ownership before repeating. Do not recreate or modify
the frozen stage. All output paths must be new:

```sh
set -euo pipefail
out=$(mktemp -d /tmp/php83-syntax-repeat.XXXXXX)
rc=0
ssh -T -F /tmp/kaltura-php83-ssh.conf php83 \
  'bash /home/vagrant/php-candidate-syntax-exp9/tools/run.sh' \
  > "$out/result.json" 2> "$out/stderr" || rc=$?
printf '%s\n' "$rc" > "$out/exit"
python3 tools/php83/candidate-syntax/test_scan.py
```

Compare every path/hash/status/diagnostic and runtime/harness identity; only
per-file durations are nondeterministic. The primary 11 local tests include
valid inventory, wrong ZIP hash, drift, extra files, traversal, wrong root,
symlink, duplicate entry, diagnostic/status classification, flags and extension
selection. They do not execute application PHP or establish service acceptance.
Independent CLI results are recorded separately; this document does not infer
an independent pass merely from the primary collector succeeding.

## Historical report accounting and analyzer readiness

[The read-only identity audit](evidence/candidate-syntax/identity-historical.json)
was generated with `python3 tools/php83/candidate-syntax/historical-identity.py`.
All 11,784 historical raw-lint paths and hashes match the original ZIP's selected
files. Historical raw-static paths match that same set. Historical packaged
static and lint reports have identical 13,454-path sets, but matching report
paths alone does not authenticate package payload bytes.

The historical raw compiler scan had 58 rejections and 126 diagnostic files;
packaged PHP 8.3 had 79 and 149 respectively. The controlled `-n` scan above is
not INI-equivalent to those historical runs: it has 122 original diagnostic files.
It is a fresh paired comparator, not a replacement or retroactive correction of
historical runtime conditions.

A historical summary field is mislabeled: `static-summary.json` says
`files_with_findings: 11784`, but this is its scanned-file count. The complete
raw JSON actually contains **562 files with messages**, and packaged JSON has
**919**. The original summary was preserved. The 1,901 raw plus 2,810 packaged
static rows remain **4,711 unverified report rows**, not distinct defects.

The analyzer is available at `/home/vagrant/php83-tools` on php83lab; no install,
network download or analyzer execution occurred in this case.
[Read-only file identities](evidence/candidate-syntax/identity-installed-analyzer.json)
confirm its Composer manifest/lock match this repository. Lock SHA-256:
`1349200f714f39615153d319d88046b1f34b91a782954b76a7fe538c9b8b5e33`.
The lock pins PHPCompatibility 10.0.0-alpha2, PHPCS 4.0.4, PHPCSUtils 1.2.3 and
the disabled Composer installer plugin 1.2.1. Installed analyzer source bytes,
ruleset exclusions, effective configuration and analyzer runtime/modules still
need a full verified inventory before the next paired static rerun.

The documented static command selects
`--standard=PHPCompatibility --runtime-set testVersion 7.4-8.3
--extensions=php,phtml,inc,php5 --parallel=4 --report=json`. That range includes
baseline incompatibilities and intentionally PHP-8.3-only candidate signatures;
it must not be interpreted as a pure PHP 8.3 regression count. Prerelease-analyzer
blind spots and manual entrypoint/generated-code review remain open. No task,
package, CI, main merge, release or production gate is closed by this scan.

## Independent completed evidence

Claude independently repeats the real lab compiler matrix and executes all
11 local tests. [Its report](evidence/candidate-syntax/claude.json) exactly equals
the corrected primary after removing only per-file `duration_ns`. The
[comparison verifier](evidence/candidate-syntax/compare.py) additionally checks
current harness hashes, exact selected path sets and equal outcomes for all
unchanged source bytes. [The result](evidence/candidate-syntax/comparison.json)
records 23,568 independently equal logical rows, four repaired rejections and
no new rejections; 54 candidate rejections remain.

Cursor independently runs the 11 syntax tests plus the expanded 25 package
identity tests and reviews sandbox/identity/status accounting. The
[CLI reviews](evidence/candidate-syntax/agents/) are advisory alongside actual
execution evidence, not broad acceptance. Its observation that no positive
EPERM socket probe is recorded is retained: the configured filter and first
SIGSYS failure do not independently identify or test every denied call. No
syscall restriction was relaxed. Initial extraction occurs outside the scanner
sandbox, after pinned archive identity/path/link checks into a fresh stage; it
is not claimed to support arbitrary hostile archives. The historical-identity
and unit-test helpers are not part of the VM scanner's executed harness map.

Next runnable cases: inventory the installed analyzer/ruleset/configuration
before a paired static rerun, then source-supported classification and behavioral
regression of remaining compiler findings (including whether inputs are actual
entrypoints or generation templates). The byte-verified published package
identity join is now available in [package identities](package-identities.md);
its coverage remains separate from this raw-source ZIP compiler matrix.

OpenCode's authorized free fallback independently runs the 11 syntax tests and
25 package tests and reviews the scanner/summary after Grok's final follow-up
times out; see [fallback report](evidence/package-identities/agents/opencode-final.jsonl).
Its final sentence overstates missing real execution: Claude's lab repeat above
and package rebuild exist. The timeout affects Grok's final contribution, not
those independently recorded executions. No agent review closes full acceptance.
