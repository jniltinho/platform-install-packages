# Held batch: 43 curly-offset compatibility repairs

This experiment changes only removed curly-brace array/string offset delimiters
in the **43 exact files** identified by the
[compiler triage](compiler-triage.md). It creates a **held**, separately reviewed
patch series, not exp10, production packaging or application acceptance.
The original tree, original ZIP, exp9 and all existing held alternatives remain
unchanged. No `.20`, baseline74, SQL, dependency install or network workload was
used by this patch-generation phase.

## Transformation and evidence

The existing lab analyzer was invoked on fresh private writable copies with:

```text
PHPCompatibility.Syntax.RemovedCurlyBraceArrayAccess
--standard=PHPCompatibility
--sniffs=PHPCompatibility.Syntax.RemovedCurlyBraceArrayAccess
--runtime-set testVersion 7.4-8.3
--extensions=php,phtml,inc,php5
```

Tool versions are PHPCompatibility 10.0.0-alpha2 / PHP_CodeSniffer 4.0.4; the
Composer lock is pinned to
`1349200f714f39615153d319d88046b1f34b91a782954b76a7fe538c9b8b5e33`.
All **767 regular analyzer/configuration files** are hashed before and after
and match. Analyzer symlinks are rejected by this runner's identity policy.
The analyzer is read-only in the sandbox; no downloads or Composer installation
are involved. The primary report retains the exact version, sniff, INI/runtime
selection, tool identities and source bytes.

[Primary PHPCBF/native evidence](evidence/curly-offsets/primary-lab.json):

- **43 files**, **153 distinct offset pairs**, **306 individual byte changes**.
- PHPCS reports 155 fixable messages: `pakeGetopt.class.php` reports two opening
  positions twice (12 messages for 10 distinct pairs). The report preserves all
  messages; byte/token proof deduplicates identical opening positions, not source
  changes. No message or changed pair is silently discarded.
- PHPCBF 4.0.4 exits **0** after successful correction; a fresh targeted PHPCS
  scan exits 0 with zero errors, warnings or fixable findings.
- All **43 original PHP 8.3 compile controls exit 255**; all **43 candidate
  compile checks exit 0**. Other candidate deprecations remain recorded; these
  results do not mean the rest of Kaltura compiles or works.
- All 43 generated patches apply to private original-file copies using
  `patch --batch --fuzz=0 -p1`, without offsets, reversal or fuzz, and reproduce
  the exact candidate hashes.

[Held manifest](../../patches/php83/held/curly-offsets/manifest.json) pins every
original, result and patch hash. GNU diff preserves original newline boundaries.
A second strict patch replay with hardened metadata validation produces identical
patch/source hashes; only temporary artifact locations differ.
The old mixed Spyc repair is **not reused**: its unrelated `each()` repair is not
part of this curly-only batch. Future integration must explicitly reconcile any
overlapping held alternatives, not apply both blindly.

## Independent layers of change-purity checks

1. Native `token_get_all` runs **without `TOKEN_PARSE`**, so the original removed
   syntax can be tokenized under 8.3. Token count, type, content and byte/line/column
   positions remain identical except individual punctuation `{`→`[` and `}`→`]`.
   Comments, quoted literals, interpolation and all other array tokens must be
   unchanged. This is before/after token identity, not an assertion that every
   runtime use was tested.
2. Every changed opening token must correspond to the **targeted sniff's fixable
   finding** at its original line/column. Its changed closing token must pair
   with it on the original token brace stack. Control-block delimiters cannot be
   changed merely because they are punctuation.
3. An offline byte verifier reconstructs the entire candidate from only those
   approved paired offsets, preserving length, whitespace, line endings and
   every other byte. Extra changes, bad positions, hash drift and missing native
   proof are rejected.
4. Original/candidate compilation controls run separately for every file. No
   source includes or application entrypoints are executed by these checks.

[Native synthetic controls](evidence/curly-offsets/primary-token-controls.json)
pass **11 cases**: valid and duplicate-message cases are accepted; changed
comments, strings, control blocks, interpolation, other code, closing-only,
no-change, wrong-sniff and wrong-location cases are rejected. These controls run
inside the same type of isolated lab service, not on production.

The local suite has **23 tests** at this phase: 15 byte/report-policy tests plus
8 separately owned behavior-harness tests. Run the nested discovery command
below; the older top-level discovery does not automatically include it.
[Initial local results](evidence/curly-offsets/primary-tests.stderr) had 18 tests;
[strict-policy results](evidence/curly-offsets/primary-r2-tests.stderr) add five
case families that reject boolean/float/string/timeout statuses, false unchanged
claims, empty/drifting identity maps, wrong versions/sniff policy and nonzero or
invalid targeted totals. Integer exits, literal `true`, pinned analyzer identities
and exact policy are required. Initial builder/verifier copies are preserved.

## Isolation and runtime identity limitation

`build-run.sh` accepts only UID 1000 on `kaltura-php83-lab`. The service uses a
private network, `socket/socketpair` denial with EPERM, read-only system/home
views, private temporary directories/devices, inaccessible application/DB paths,
no new privileges and bounded memory/runtime. Original stage and analyzer mounts
are read-only; only private candidate copies are writable. No system interpreter
selection, PHP configuration, database or service configuration changes occur.

The primary run records PHP binary hash/version but did not capture all shared
module/library hashes **before that initial run**. A subsequent
[runtime snapshot](evidence/curly-offsets/primary-runtime-before-independent.json)
records the interpreter plus five explicitly loaded modules (6 objects) and
16 linked libraries. This snapshot is after the primary run and before the
planned independent rerun; it must not be misrepresented as initial pre-run
proof. Independent reruns should collect `verify-runtime.py` immediately before
and after and compare identities. Earlier PHPCBF/native proofs retain this
explicit provenance limitation.

## Retained setup failures

- Attempt 1 inherited read-only file modes through `copytree`; PHPCBF correctly
  failed to write a disposable copy. The runner now sets owner-writable mode
  **only on newly created private copies**. Original/analyzer mounts remain
  read-only. [Attempt 1](evidence/curly-offsets/primary-attempt1-lab.stderr).
- Attempt 2 used an obsolete expectation that successful PHPCBF fixes exit 1.
  The pinned 4.0.4 `ExitCode.php` instead defines success with no remaining issues
  as 0. The corrected policy still demands zero remaining targeted diagnostics,
  complete token/byte proof and exact compile controls.
  [Attempt 2](evidence/curly-offsets/primary-attempt2-lab.stderr).

No setup failure is counted as a successful application test, and no source was
changed to make a verifier pass. The final run uses fresh stage
`/home/vagrant/php-curly-offsets-r3`; every execution creates fresh private copies.

## Reproduction

Local validation and strict held-patch replay:

```sh
python3 -m unittest discover -s tools/php83/curly-offsets -p 'test_*.py'
mkdir /tmp/php83-curly-new-patches
python3 tools/php83/curly-offsets/build-patches.py \
  --source-root /home/nilton/Projetos/nilton/NOVOS/kaltura-rigel-18.20.0-source/server-Rigel-18.20.0 \
  --candidate-output /tmp/php83-curly-new-candidate \
  --patch-dir /tmp/php83-curly-new-patches \
  --report doc/php83/evidence/curly-offsets/primary-lab.json
```

Patch directory must be empty and candidate output must not exist. Only run the
following with exclusive php83lab ownership:

```sh
ssh -T -F /tmp/kaltura-php83-ssh.conf php83 'python3 -' \
  < tools/php83/curly-offsets/verify-runtime.py > NEW_RUNTIME_BEFORE.json
ssh -T -F /tmp/kaltura-php83-ssh.conf php83 \
  'bash /home/vagrant/php-curly-offsets-r3/tools/build-run.sh' > NEW_LAB_REPORT.json
ssh -T -F /tmp/kaltura-php83-ssh.conf php83 'python3 -' \
  < tools/php83/curly-offsets/verify-runtime.py > NEW_RUNTIME_AFTER.json
```

[Owned frozen tool hashes](evidence/curly-offsets/primary-frozen-tools-r2.sha256),
[primary result](evidence/curly-offsets/primary-result.json) and
[strict replay output](evidence/curly-offsets/primary-r2-patch-replay.stdout)
identify this phase. Actual independent CLI runs and representative function
regressions are coordinated separately and must be attributed to their own
execution reports, not inferred from these primary checks.

## Remaining acceptance

This batch proves a bounded lexical transformation and 43 focused compile
controls, not behavior of all methods/callers. Representative original74 versus
candidate74/83 runtime controls and independent verification are now recorded
below; the remaining 40 files and broader impacted entrypoints still need
behavior/integration coverage. Other compiler failures, diagnostic groups,
providers, licensing/inventory, full-service/media/performance, upgrade/recovery
and release gates are unchanged. No integrated ZIP or acceptance checkbox is
created by this held batch.

## Independent execution and representative behavior

Actual Claude CLI independently repeated the entire fresh PHPCBF/token/compiler
run. All 43 source rows and 767 analyzer identities match exactly. Its true
pre/post runtime snapshots cover six objects and 16 linked libraries. Differences
are restricted to PHPCBF truncated temporary-directory prefixes and elapsed time,
and `ldd` ASLR addresses; exact comparison is enforced by
[`compare.py`](../../tools/php83/curly-offsets/compare.py), with
[comparison evidence](evidence/curly-offsets/comparison.json).
Eleven native token controls are byte-identical between executors.

A separate baseline74 stage runs the actual two bundled Google utility classes
and HTMLPurifier Encoder, each in its own process, under original74, candidate74
and candidate83: **9 processes and 204 case rows**, independently repeated by
Claude with **byte-identical reports**. Values and runtime diagnostic rows agree
on 7.4; candidate83 preserves values with an explicit NOTICE-to-WARNING mapping.
Original74 curly load deprecations disappear as intended. Diagnostics remain
enabled and the recording error handler returns false, not suppression.
See [behavior result](evidence/curly-offsets/behavior-result.md) and
[primary report](evidence/curly-offsets/behavior-primary.json).

The Google multibyte length overread and incorrect lengths remain baseline
**defects**, not accepted production exceptions. Native overread controls verify
the severity difference separately. Runtime coverage is **three source files,
selected methods**, not all 43 classes or complete application behavior.
The full application error-handler consequences remain untested.

| Actual executor/reviewer | Executed scope | Outcome |
|---|---|---|
| Claude CLI | Fresh PHPCBF43, native controls11, behavior204, local tests23; independent review | PASS for these bounded cases |
| Cursor Agent CLI | Behavior validator tests8, shell syntax; later all43 PHP7.4 compiler/token controls and six guard tests; independent reviews | PASS for bounded local and VM cases |
| Grok CLI | Bounded read-only audit attempt | Timeout124; no successful result |
| OpenCode Muse Spark1.3 Contributor Free | Independent43-file source/patch/candidate byte audit, local tests23; purity review | PASS as authorized fallback, not Grok |

Raw reports and prompts are retained under `evidence/curly-offsets/`. The
[review interpretation](evidence/curly-offsets/cycle-notes.md) reconciles findings,
limited assertions, and the deliberate r1-to-r2 purity-tool hardening while
behavior tools stayed unchanged. No package, exp10 or release was produced.

## Additional all-file PHP 7.4 controls

The fresh read-only `php-curly-compiler74-r2` stage compiles **all 43 originals
and 43 candidates** with PHP7.4 and runs the same native token verifier for each
pair. All **86 compiler processes and 43 token processes** pass. These are
compile/tokenizer checks, not execution of application source bodies. Source,
harness, runtime, explicit JSON/tokenizer modules and linked libraries are
verified before and after. The candidate's old-style `pakeYAMLNode` constructor
deprecation remains visible in `pakeYaml.class.php:54`, not waived.

The first attempt failed before scanning because the harness assumed the remote
mount had repository-depth parents; its error and source are retained. The
corrected fresh stage resolves repository paths only for local preparation,
and a shallow-import regression check is retained alongside six local controls.
See [compiler74 summary](evidence/curly-offsets/compiler74-summary.md).

Cursor subsequently executed the exact pinned read-only PHP7.4 command and
independently reproduced the entire report **byte-for-byte**. The
[compiler74 comparison](evidence/curly-offsets/compiler74-comparison.json)
records all86 compiler exits and43 native proofs, with no excluded fields.
The held manifest's original “candidate74 pending” note records its creation
phase; these later linked reports supply the completed scoped evidence, without
rewriting earlier patch/provenance identities or implying full acceptance.
