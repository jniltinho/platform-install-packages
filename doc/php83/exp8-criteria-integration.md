# exp8 cumulative Criteria return integration

## Separate artifact and source delta

This fourteen-patch PHP 8.3-only ZIP **replaces**, rather than stacks, the old
Criteria-null-alias entry with the cumulative Criteria-native-returns patch.
The alias guard remains byte-identical and the only exp7-to-exp8 application
change is six return declarations in `vendor/propel/util/Criteria.php`.
Previous artifacts, original archive and active exp2 manifest are unchanged.

- ZIP/repeat SHA-256: `67acaa1ad78332273901fceac9d75824b8f21437eb93607cb20a78db9cd77adc`.
- Two builds are identical; Cursor independently executes the verifier.
- Relative to original: fourteen source files change, sixteen metadata files are
  added, all other original entry bytes/comments remain identical.
- Each lab verifies all 15,191 regular files against the pinned ZIP.
- [Manifest](evidence/exp8-candidate/manifest.json),
  [verification](evidence/exp8-candidate/verification.json),
  [independent verification](evidence/exp8-candidate/cursor-verification.json),
  [exact previous-source delta](evidence/exp8-candidate/previous-delta.json).

The previous-delta verifier removes only the six new declarations from the
candidate bytes and requires exact equality to exp7. The exact old guard line is
read from the original alias patch, including whitespace. An initial ad-hoc
substring check incorrectly omitted that whitespace and failed; the source was
not altered to satisfy it. All fourteen manifest targets are unique and the old
Criteria patch name is absent from the candidate selection.

## Runtime policy and API evidence

Both exp7 and exp8 target PHP 8.3, not 7.4. The matrix therefore retains the
unchanged original74 baseline, original83 failure control and both artifacts on 8.3.
Unlike the prior cycle, no exp6-on 7.4 counterfactual is needed: its evidence remains
historical; neither current artifact is falsely presented as supporting 7.4.
Both runners reject artifact execution on 7.4 and list unsupported combinations.

| Runtime / source | Exit | Diagnostic groups / events |
| --- | ---: | ---: |
| original7.4 | 0 | 1 / 6 |
| original8.3 | 1, expected PDO signature fatal | 15 / 15 |
| exp7 on8.3 | 0 | 27 / 703 |
| exp8 on8.3 | 0 | **21 / 571** |

The real extracted `api_v3/web/index.php`, session/auth/permission pipeline and
synthetic SQL run under Apache HTTP and trusted HTTPS. Both artifacts match the
original74 normalized contract: eleven assertions per transport and the negative
untrusted-CA control. Exactly six Criteria return-contract groups / **132 events**
disappear, with every other diagnostic group/count unchanged. There is no
regression of the earlier alias repair. Remaining diagnostics are not accepted
exceptions. Codex and Claude independently repeat all four rows, serially, each
with a fresh uniquely owned DB unit/datadir and exact datadir guard before writes.

[Primary](evidence/exp8-api/codex.json),
[independent](evidence/exp8-api/claude.json),
[exact comparison](evidence/exp8-api/comparison.json).

## CLI regression and stronger local collector tests

Six cases × standard/minimal INI run original74 (12 rows) plus original83,
exp7 and exp8 (36 rows): **48 rows**, 44 zero exits and four expected original83
JSON syntax-fatals. All twelve exp8 and twelve exp7 rows exit zero. Twenty
artifact-output comparisons match original74; export compares serialized entries,
not producer/runtime identity. Independent rows match except duration, and local
fixture hashes match both reports. Prior-artifact bytes are verified before CLI
execution. [CLI parity](evidence/exp8-runtime/parity.json).

The suite now passes **136 local tests**. Ten new exp8-specific tests cover:
malformed/untrusted/timed-out DB startup cleanup, exact supported matrix,
complete mocked success, original baseline failure, candidate failure, unrelated
original83 failure instead of the expected signature control, unexpected stdout
rejection/redaction and cleanup remaining active. Mocked collector output in the
local test log contains synthetic unit IDs; it is not evidence of real DB units.
No test connects over SSH or starts SQL. This adds fault-path coverage but does
not claim all collector/security failures are covered.

## Reproduction and limits

```sh
# First staging only; existing stage directories are refused.
bash tools/php83/exp8-api/stage.sh 74
bash tools/php83/exp8-api/stage.sh 83
python3 tools/php83/exp8-api/collect.py /path/to/new-api-report.json
ssh -T -F /tmp/kaltura-php74-ssh.conf baseline74 \
  'python3 /home/vagrant/php-exp8-regression/exp8-regression/batch.py'
ssh -T -F /tmp/kaltura-php83-ssh.conf php83 \
  'python3 /home/vagrant/php-exp8-regression/exp8-regression/batch.py'
python3 doc/php83/evidence/exp8-candidate/compare.py
python3 doc/php83/evidence/exp8-candidate/verify-previous-delta.py
```

Serialize VM/SQL writers; do not run Python -O. Reports refuse overwriting old
runtime evidence. API stdout is whitelisted, stderr hashed/location-sanitized,
and no token-bearing raw logs are retained. Units stop in finally; synthetic
datadirs are retained. Exceptions may leave no structured partial report. Existing
SSH aliases do not pin host keys; baseline trees/runtime binaries are not rehashed
by this cycle and source-byte verification does not verify filesystem modes.

The copied PHP 8.3 runtime on baseline74 is not full AIO/FPM. The earlier sixteen
Criteria state/alias rows and two invalid controls were focused held-source tests;
this artifact cycle exercises actual API/SQL and six CLI cases, not that entire
state corpus again. Full Sphinx/cache/worker, persistent-session/revocation,
media/browser, clean-distro, benchmark and recovery requirements remain open.
No aggregate acceptance task, package/CI integration, release or `.20` gate closes.

## Independent CLI execution and review

Claude repeats both runtime matrices and executes all ten local exp8 collector
tests. Cursor independently executes the ZIP verifier (byte-identical report) and
reviews cumulative selection/runtime policy. Grok times out after the configured
120-second bound with exit124; after confirmed termination, OpenCode Zen
`opencode/muse-spark-1.3-contributor-free` runs136 local tests and reviews the
Codex/Claude runtime evidence and delta reports. [Roles/exits](evidence/exp8-candidate/result.json).

Corrections to advisory prose: the manifest status describes the exp7 base plus
its replacement, while `revision=exp8` identifies the new artifact. Keeping the
old patch under `held/` preserves history, not a selection to stack it. Claude's
“only Criteria and manifest changed” applies to the application delta only after
excluding experimental metadata; metadata also changes, including replacement of
the embedded patch. No claim that all other complete ZIP entries stayed identical
between experimental revisions is made. Claude's agent-availability caveat
predates the coordinator's consolidated results above.

Additional harness gaps remain: no new mocked overwrite/drift/verifier-failure or
mid-Apache-timeout coverage; unit state `unknown` is accepted after collected-unit
cleanup. Runtime observations are trusted from the hash-pinned synthetic fixture
and recorded as JSON without an independent field allowlist; reviewed records
contain version/module metadata, but the collector must not be reused for
untrusted/live log capture without tightening that boundary. These limitations do
not convert residual diagnostics into accepted exceptions or release approval.
