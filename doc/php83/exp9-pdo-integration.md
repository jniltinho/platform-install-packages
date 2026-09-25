# exp9 PDO boolean-result integration

## Artifact and intentional contract correction

The separate PHP 8.3-only exp9 ZIP retains all fourteen exp8 selections and adds
`PropelPDO-bool-setAttribute` and `KalturaStatement-bool-results`. Only those two
application files differ from exp8. The upstream archive, earlier experiments,
active exp2 manifest and published releases remain unchanged.

- ZIP/repeat SHA-256: `cb61e4cd11009bbf9e6e362dfafa5ef2f4af22da817c75fedbd7741a08e44cbc`.
- Sixteen unique source targets and eighteen added metadata files.
- [Manifest](evidence/exp9-candidate/manifest.json),
  [two-build verification](evidence/exp9-candidate/verification.json),
  [Cursor verification](evidence/exp9-candidate/cursor-verification.json),
  [exact prior-artifact delta](evidence/exp9-candidate/previous-delta.json).

This is an explicit public **null-to-bool correction**, not exact old-return
parity. The setter propagates native success/failure and returns true for a
handled custom prepare-cache assignment. Statement execution returns the native
result after existing logging/monitoring; dry-run skipped writes return true.
`bindValue` declares its already-returned boolean. Exceptions remain exceptions.
The [focused held-patch SQL evidence](pdo-boolean-repair.md) remains separately
scoped; it used stubbed logging/cache/monitor dependencies.

## Extracted-artifact API and CLI regression

Codex and Claude each run the complete matrix serially, using a fresh owned
synthetic MariaDB and the actual extracted Kaltura web entrypoint. HTTP and
trusted HTTPS retain eleven normalized assertions per transport plus an
untrusted-CA negative control. Current/prior artifact trees are verified against
their pinned ZIP bytes before execution. Candidate execution on 7.4 is rejected;
original7.4 remains the reference, not a promise of candidate7.4 support.

| Source / runtime | Exit | Diagnostic groups / events |
| --- | ---: | ---: |
| original7.4 | 0 | 1 / 6 |
| original8.3 | 1, expected PDO signature control | 15 / 15 |
| exp8 / 8.3 | 0 | 21 / 571 |
| exp9 / 8.3 | 0 | **18 / 503** |

Exactly three groups / 68 events disappear: two KalturaStatement return groups
(22 each) and PropelPDO's setter group (24). All other groups/counts remain
unchanged. No warning suppression is introduced. The remaining 503 events are
not accepted exceptions.

[Primary API](evidence/exp9-api/codex.json),
[independent API](evidence/exp9-api/claude.json),
[exact comparison](evidence/exp9-api/comparison.json).

Both executors also run 48 CLI rows: twelve original74, then twelve each of
original83, exp8 and exp9 under standard/minimal INI. Forty-four exit zero; four
original83 JSON syntax failures are expected controls. All twelve exp9 rows pass.
Twenty artifact-output comparisons retain typed equality to original74; export
compares entries, not runtime identity. Independent rows agree except durations.
[CLI parity](evidence/exp9-runtime/parity.json).

Ten new exp9 collector fault/matrix tests bring the root local suite to **146**.
These are mocks, not real SQL or runtime acceptance. They cover malformed,
untrusted/timed-out startup cleanup, supported cases, success, baseline/candidate
failure, unrelated original83 failure, unexpected stdout and active cleanup.

## Reproduce the bounded matrix

```sh
# Initial staging refuses an existing directory.
bash tools/php83/exp9-api/stage.sh 74
bash tools/php83/exp9-api/stage.sh 83
python3 tools/php83/exp9-api/collect.py /path/to/new-report.json
ssh -T -F /tmp/kaltura-php74-ssh.conf baseline74 \
  'python3 /home/vagrant/php-exp9-regression/exp9-regression/batch.py'
ssh -T -F /tmp/kaltura-php83-ssh.conf php83 \
  'python3 /home/vagrant/php-exp9-regression/exp9-regression/batch.py'
python3 doc/php83/evidence/exp9-candidate/compare.py
python3 doc/php83/evidence/exp9-candidate/verify-previous-delta.py
```

One writer per VM/DB; never run Python with `-O`. Source verification concerns
bytes, not filesystem modes. API stdout is whitelisted; stderr is hashed and
reduced to locations/counts, never stored as raw token-bearing logs. Owned DB
units stop in finally; synthetic datadirs are retained. Exceptions can leave no
structured partial report. Runtime binaries and original baseline trees are not
rehash-verified by these collectors, and existing SSH aliases do not pin host
keys. The copied 8.3 runtime is not a complete installed 8.3 AIO/FPM system.

## Independent reviewers and boundaries

Cursor executes the archive verifier and reviews both patches. Claude repeats
both runtime matrices and reviews the artifact evidence. Claude's advisory
inference that unchanged HTTP output proves callers do not consume the return
value is stronger than the evidence: only the exercised output is proven equal.
A dedicated real-bootstrap boolean probe is tracked separately, not inferred
from these golden API responses.

No aggregate acceptance checkbox closes. Full caller/default-binding,
non-emulated prepare, MSSQL, configured cache, worker, persistent-session,
browser/media, three-distro, benchmark and recovery scope remains open. No
package/CI integration, release, main merge or production change is authorized
by passing this experimental matrix.

## Real-bootstrap boolean probe

`tools/php83/pdo-bootstrap/` now exercises **23 strict rows per artifact** using
the real API bootstrap, DbManager connection and KalturaPDO-selected statement
class. Seven loaded dependencies are reflected and hash-checked against each
ZIP: KalturaPDO, PropelPDO, KalturaStatement, KalturaLog, KalturaMonitorClient,
kApiCache and kQueryCache. No dependency stubs are used. This establishes actual
class loading/call execution, not full configured external cache/monitor behavior.

Codex and Claude independently pass all 46 rows with identical typed outputs,
diagnostic locations/counts and source/harness identities. Nine documented slots
change from null to native bool; all other rows are identical. Cases cover native
success/failure/exception controls, supported/unsupported attribute, cache setter
and statement identity on/off, bound integer and named-array INSERT/data, silent
SQL failure, exception class/SQLSTATE, and dry-run INSERT-no-write/SELECT-data
with the actual KalturaPDO comment prefix.

The first run failed both variants due to the **fixture** passing a positional
array to named `:p1` SQL. The initial report, failed exits and probe are retained;
the sole fixture correction is explicit `array('p1' => 23)`. Application bytes
are unchanged. The corrected primary is `codex-r2.json`, not the failed
`codex.json`. Eleven separate local tests cover positive/negative collector
validation and a static guard against the fixture regression. They require
explicit discovery under the nested directory and are not included in the 146
root-suite count. An initial comparison-script invocation referenced the old
helper-hash field name; fixing it to the actual report schema yields exact
independent comparison, without changing either report.

- [Corrected primary](evidence/pdo-bootstrap/codex-r2.json)
- [Independent repeat](evidence/pdo-bootstrap/claude.json)
- [Typed comparison](evidence/pdo-bootstrap/comparison.json)
- [Retained failure](evidence/pdo-bootstrap/codex.json)
- [Attempt explanation](evidence/pdo-bootstrap/attempts/positional-array/README.md)
- [Graph/source coverage](evidence/pdo-bootstrap/coverage.json)
- [Claude review](evidence/pdo-bootstrap/claude-review.md)

The dedicated bootstrap probe reduces its own diagnostics from 16 groups / 18 events
to 13 groups / 15 events; this is distinct from the API matrix’s 18 groups / 503 events.
The dedicated collector verifies artifact bytes before and after the run, rejects
unexpected JSON fields/types, and hashes raw stderr without saving it. Sanitized
diagnostics agree independently; differing raw stderr hashes are not claimed to
be explained by an inspected raw-log comparison. Synthetic datadirs remain for
inspection (not silently removed). SQL-server/runtime binary provenance and SSH
host-key pinning are not strengthened here. No full caller/default-binding,
warning-mode-in-real-bootstrap, non-emulated prepare, concurrency or complete
application acceptance is inferred.

Grok terminated at the 120-second timeout with exit124. The authorized OpenCode
Zen `opencode/muse-spark-1.3-contributor-free` fallback actually ran 146 local tests
successfully, but its requested evidence-file write was denied and its initial
review did not finish; CLI exit0 does not make that missing review successful.
A bounded read-only follow-up then ran the 11 bootstrap local tests (exit0) and
completed independent evidence/guard/contract review. The denied write was not
retried or bypassed. Raw CLI outcomes and follow-up are retained in
[evidence/exp9-candidate/agents](evidence/exp9-candidate/agents/).
