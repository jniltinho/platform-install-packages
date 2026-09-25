# Paired exp9 / exp10 PHP 8.3 syntax scan

**Compiler-only experimental harness, not application acceptance.** The input
contract is now pinned to the independently verified exp10 build SHA256
`de177e6cbaedf3a3207661c2325f466cce37febb73190f3a49d31f24b740c053`.
The original null-pin contract is retained in preparation evidence. Both staging
and scanning reject a missing pin; never substitute an expected/guessed hash.
The exp9 baseline is pinned to
`cb61e4cd11009bbf9e6e362dfafa5ef2f4af22da817c75fedbd7741a08e44cbc`.

This adapts `../candidate-syntax/` without modifying that historical scanner.
The new owner-only stage is `/home/vagrant/php-candidate-syntax-exp10`; original
exp9 stages and all installed applications remain unchanged. No application
entrypoints/includes are executed: each PHP-like file is compiled with `-n -l`,
short tags enabled and unsuppressed E_ALL diagnostics. Extension set selection
is `.php`, `.phtml`, `.inc`, `.php5` (case insensitive), exactly 11,784 per ZIP.
Generated code, other extensions and semantic/runtime defects are outside this
compiler-only result; full migration and release gates remain open.

## Contract and expected comparison

The contract lists the 43 new curly-offset target paths with exp9/exp10 byte
hashes from `doc/php83/evidence/exp10-candidate/manifest.json` entries 16 onward.
Its selection-manifest hash is provenance, not a substitute for the ZIP hash.
The coordinator authorized the final pin after actual build/repeat/delta
verification and CLI review. Retain this frozen contract and updated harness
identity with every run; any subsequent change requires a new reviewed run.

The scanner hashes the ZIPs and checks every extracted file before and after
each scan. All PHP-like records are collected, including unsuccessful compiler
results. Runtime binary, linked libraries, version, modules, INI state and all
top-level harness files are identified and rechecked after the paired scan.
Read-only binds, unprivileged UID 1000, isolated networking, denied socket
syscalls, private temporary storage and inaccessible live Kaltura/DB paths
match the previous scanner. `php8.3` subprocesses have 20-second limits, four
parallel workers, with 1 GiB/2,400-second service bounds.

Observed counts must be reported rather than assumed. The anticipated 54 → 11
compiler rejections are explicit checked hypotheses. The bounded regression
passes only if all 43 targets were rejected in exp9 and are accepted in exp10,
all 11 remaining rejected paths and **every unchanged file's exit/diagnostics**
match, the changed PHP pathset is exactly the 43 pinned targets, both scans
contain 11,784 unique files and no subprocess is incomplete. Hash/pathset drift
aborts collection. A comparison mismatch retains a JSON report but exits 2.

`candidate_all_files_compile` remains false if even one compiler rejection
remains, including the expected 11. `application_acceptance` is always false.
An exit 0 means only complete, matching bounded compiler improvement; it is not
syntax acceptance of the whole candidate or acceptance of remaining warnings.

## Reproduction (coordinator's exclusive VM ownership only)

1. Obtain and independently verify the actual exp10 build identity; freeze the
   updated contract. Run the local tests and actual independent CLI reviews.
2. Ensure no overlapping `.83` writer/runtime workload. Check the intended
   guest hostname is `kaltura-php83-lab`, vagrant UID is 1000, and the exact new
   stage does not exist. Create only this fresh stage. Copy the two public ZIPs
   as `exp9.zip` and `exp10.zip`; copy this directory's regular files to `tools/`.
   Do not copy configured application trees or existing cached VM state.
3. As vagrant, invoke
   `python3 -B /home/vagrant/php-candidate-syntax-exp10/tools/stage.py`.
   It refuses existing extraction directories and verifies both archive pins
   and safe member paths. Runtime scanning independently revalidates all bytes.
4. Invoke `bash /home/vagrant/php-candidate-syntax-exp10/tools/run.sh` and
   collect stdout JSON, stderr and the real exit status independently (no
   pipeline that hides the runner's exit). The guest wrapper rejects another
   host/UID and exposes only read-only inputs to the transient service.
5. Independently check report schema, actual counts, target results, remaining
   failures, unchanged-file comparison, source/runtime/harness identities and
   cleanup. Record executor/reviewer separately; reviews are not VM execution.
   Preserve failures and logs. Remove only the experiment-owned stage after
   exporting evidence if cleanup is desired; never touch other experiment or
   installation paths.

Local unit tests (no VM, PHP execution or application acceptance):

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover \
  -s tools/php83/exp10-syntax -p 'test_*.py'
bash -n tools/php83/exp10-syntax/run.sh
```

No SQL, `.20`, production package/CI integration, publication, main merge or
release operation is authorized by this harness.
