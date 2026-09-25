# exp6 parameter-reflection integration

## Artifact and scope

This is a separate thirteen-patch experimental ZIP, not a release candidate or
full application acceptance. It adds only the previously focused-tested
`KalturaActionReflector-parameter-class.patch` to exp5. Original and previous
experimental archives and the active exp2 manifest remain untouched.

- ZIP SHA-256: `da11cbb9cc58e4e67d4eb8c875d651f272941c7d37d1209c63a02a48e4ba30be`.
- Two independent builds have identical bytes.
- Exactly 13 original source files change; 15 experimental metadata files are
  added. All other original entry bytes and archive/entry comments are preserved.
- Each lab verifies all 15,190 extracted regular files against the pinned ZIP.
- [Manifest](evidence/exp6-candidate/manifest.json) and
  [byte-level verification](evidence/exp6-candidate/verification.json).
- Native and real metadata edge-case contracts, including uppercase SELF/PARENT,
  unions, missing classes and exact errors, are recorded in
  [the focused reflection repair](reflection-parameter-repair.md).

## Actual API/SQL/HTTP/HTTPS execution

`tools/php83/exp6-api/` is the revision-pinned exp5 harness, comparing original,
exp5 and exp6 under PHP 7.4 and 8.3. Codex executes first; Claude independently
repeats the six-row matrix serially, each with a new uniquely owned synthetic DB.
The real `api_v3/web/index.php`, bootstrap, permission/session and KalturaPDO paths
run on extracted ZIP bytes, without overlaying the new reflection class.

The five successful rows preserve the original-7.4 normalized contract: eleven
assertions per transport plus an untrusted-CA negative control. Original 8.3
retains its expected PDO signature-fatal control. Candidate 7.4 emits no recorded
diagnostics. On 8.3, exp5 has 35 groups / 931 events; exp6 has **33 groups / 847
events**. Exactly the two deprecated parameter-getClass locations (84 events)
disappear; every other recorded diagnostic group/count is unchanged. No remaining
diagnostic is accepted as an exception.

[Primary report](evidence/exp6-api/codex.json),
[independent report](evidence/exp6-api/claude.json), and
[exact diagnostic comparison](evidence/exp6-api/comparison.json).

## Focused CLI artifact regression

The standard/minimal-INI matrix runs six cases on original/exp6 × PHP 7.4/8.3:
environment, legacy JSON, Zend JSON, doc-comment, export and real consumer.
There are 48 rows: 44 zero exits and four expected original-8.3 JSON syntax-fatal
controls. All 24 candidate rows exit zero. Twenty typed-output comparisons agree
with original 7.4 (export compares serialized entries, not producer identity).
Claude repeats both labs independently. Local fixture hashes and normalized
independent rows are checked, not merely the batch process exit.

[CLI parity](evidence/exp6-runtime/parity.json). The existing local Python suite
passes 122 tests; it does not constitute mocked coverage of every new collector.

## Reproduction and limits

```sh
# Fresh, owned lab directories only; existing stages are refused.
bash tools/php83/exp6-api/stage.sh 74
bash tools/php83/exp6-api/stage.sh 83
python3 tools/php83/exp6-api/collect.py /path/to/new-api-report.json
ssh -T -F /tmp/kaltura-php74-ssh.conf baseline74 \
  'python3 /home/vagrant/php-exp6-regression/exp6-regression/batch.py'
ssh -T -F /tmp/kaltura-php83-ssh.conf php83 \
  'python3 /home/vagrant/php-exp6-regression/exp6-regression/batch.py'
```

Serialize VM/SQL writers. Do not run Python with `-O`: inherited stage/batch
assertions require normal mode. API verification explicitly rejects optimized
mode. API/SQL stderr is hashed/sanitized, never retained as token-bearing logs.
Each DB unit is stopped in `finally`; its synthetic data directory is retained.
Exceptions may leave no structured partial report. Source verification does not
verify filesystem permissions. Existing SSH configuration does not pin host keys.

SQL/API PHP 8.3 uses the previously copied runtime bundle on baseline74; runtime
binaries and original baseline trees are not rehashed by this collector. This
is not full AIO/FPM, persistent-session/revocation, shared APC/cache, media,
distro-installation, performance, recovery or release acceptance. Metadata parity
and native reflection tests previously used a held overlay; this cycle proves
integration only for the API/CLI paths actually executed. No explicit autoloader
side-effect or shared-cache reflection test is added here. No acceptance checkbox,
production package/CI integration, main merge, release or `.20` change is implied.

## Independent agents and advisory corrections

Claude independently repeats API and both CLI runtimes and reviews Codex evidence.
Cursor executes the ZIP verifier and reviews the patch/harness and both evidence
comparisons. Its first Ask-mode run reports stdout verification but cannot write
our requested JSON; the subsequent execution-mode run writes a byte-identical
independent report. Grok times out at 120 seconds (124), without a completed
validation result. Only after termination, OpenCode Zen
`opencode/muse-spark-1.3-contributor-free` executes the 122 local tests and reviews
Codex/Claude reports and harness isolation. These are actual CLI executions, not
renamed internal agents. [Outcomes](evidence/exp6-candidate/result.json).

Raw reviewer prose is advisory: stopping the owned DB service is not deletion of
its retained directory; environment output differs in PHP identity as well as
modules. OpenCode's phrase “not integrated API/CLI” means full application
acceptance is absent, not that this bounded artifact integration was unexecuted.
The CLI matrix compares original and exp6, not exp5; the API matrix explicitly
includes exp5 as the diagnostic counterfactual. Historical focused-repair wording
has been updated to link this later integration. All acceptance gates remain open.
