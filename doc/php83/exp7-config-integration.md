# exp7 native configuration return integration

## Artifact and explicit runtime support

The separate **PHP 8.3-only** fourteen-patch ZIP adds the focused-tested
Zend_Config return declarations to exp6. Original and exp2–exp6 archives are
unchanged; the active exp2 manifest is not promoted or replaced.

- ZIP SHA-256: `a0934bbd4f742aa2b30e34590aa8a12b761aa47f54da78be1fa913b783d4482a`.
- Two builds are byte-identical, independently verified by Cursor.
- Exactly 14 original source files change; 16 metadata files are added; all other
  original entry bytes and archive/entry comments remain identical.
- Each lab verifies all 15,191 extracted regular files against the pinned ZIP.
- [Manifest](evidence/exp7-candidate/manifest.json),
  [verification](evidence/exp7-candidate/verification.json),
  [independent verification](evidence/exp7-candidate/cursor-verification.json).

Native `mixed` return declarations are intentionally unsupported on PHP 7.4.
API/CLI runners reject exp7 on74 and reports explicitly record this unsupported
combination. The original PHP7.4 class/application remains the functional baseline;
exp6 is retained as a compatible counterfactual on both runtimes. This changes
which candidate/runtime combination is supported, not the requested 8.3 target
or the required behavioral comparison. No failed candidate7.4 row is counted as
successful acceptance. See [focused contract evidence](config-return-contracts.md)
for the 16 actual-class controls before integration.

## API/SQL/HTTP/trusted-HTTPS matrix

Five rows run the real extracted application web entry point, private synthetic
SQL, session/auth/permission pipeline, HTTP and verified HTTPS:

| Runtime / source | Exit | Diagnostic groups / events |
| --- | ---: | ---: |
| original7.4 | 0 | 1 / 6 |
| exp6 on7.4 | 0 | 0 / 0 |
| original8.3 | 1, expected PDO signature fatal | 15 / 15 |
| exp6 on8.3 | 0 | 33 / 847 |
| exp7 on8.3 | 0 | **27 / 703** |

All three successful artifact rows preserve the original7.4 normalized API
contract (eleven assertions per transport plus the untrusted-CA negative). Exactly
six Zend_Config diagnostic groups / **144 events** disappear; every other group
and count remains unchanged. This demonstrates the real integrated class, not a
fixture-only overlay. No remaining diagnostic is accepted as an exception.
Codex and Claude run independently and serially, each owning a new random SQL
unit/datadir with exact datadir checks before schema writes and cleanup in finally.

[Primary](evidence/exp7-api/codex.json),
[independent](evidence/exp7-api/claude.json),
[diagnostic/row comparison](evidence/exp7-api/comparison.json).

## CLI matrix and local fault injection

The six focused cases run with standard/minimal INI: original/exp6 on74 (24 rows)
and original/exp6/exp7 on83 (36 rows), **60 rows total**. Fifty-six rows exit zero;
four original8.3 JSON syntax-fatals remain expected negative controls. All twelve
exp7 rows and twenty-four exp6 rows exit zero. Thirty typed-output comparisons
match original7.4, with export comparing serialized entries rather than producer
identity. The environment case is observed, not claimed cross-runtime identical.
Claude repeats both batches. Every independent row agrees except duration and
all recorded local fixture hashes match. Prior-artifact bytes are verified before
CLI execution; batch explicitly rejects optimized Python.

[CLI parity](evidence/exp7-runtime/parity.json).
The local suite now has **126 passing tests**: four added exp7 collector tests
cover malformed startup, untrusted startup identity, timeout cleanup ownership
and exact five-row runtime matrix. These are mocked local controls, not a claim
of full failure-path coverage or an alternative to runtime execution.

## Reproduction and operational limits

```sh
# First staging only; existing owned stage directories are refused.
bash tools/php83/exp7-api/stage.sh 74
bash tools/php83/exp7-api/stage.sh 83
python3 tools/php83/exp7-api/collect.py /path/to/new-api-report.json
ssh -T -F /tmp/kaltura-php74-ssh.conf baseline74 \
  'python3 /home/vagrant/php-exp7-regression/exp7-regression/batch.py'
ssh -T -F /tmp/kaltura-php83-ssh.conf php83 \
  'python3 /home/vagrant/php-exp7-regression/exp7-regression/batch.py'
python3 doc/php83/evidence/exp7-candidate/compare.py
```

Serialize VM/DB writers; never run Python -O. API/SQL output is whitelisted and
stderr reduced to hashes/sanitized locations. No token-bearing raw logs are saved.
Owned DB services stop, but synthetic data directories remain for diagnosis.
Unexpected exceptions may leave no structured partial report. Baseline runtime
binaries and original baseline application trees are not rehashed by this cycle;
SSH host keys are not pinned by the existing configuration, and source-byte
verification does not verify filesystem permission bits.

The SQL/API 8.3 runtime is the copied bundle on baseline74, not full AIO/FPM.
This is not persistent-session/revocation, shared cache, media/browser, clean
distro install, benchmark or recovery acceptance. The sixteen detailed class
controls were run earlier using a held overlay, not rerun wholesale on this ZIP;
this cycle exercises only its actual API and six CLI paths. External subclass,
malformed configuration, scheduler constructor and mid-iteration continuation
coverage remain open. No full acceptance task closes; package/CI integration,
release approval and `.20` cutover gates remain unchanged.

## Independent review outcomes

Claude repeats both runtime matrices and executes the four new local collector
checks. Cursor independently executes the ZIP verifier (identical report) and
reviews source selection/runtime policy. Grok times out at the 120-second bound,
exit124; after confirmed termination, OpenCode Zen Muse Spark1.3 Free executes
126 local tests and reviews both Codex/Claude evidence and collector safety.
[Recorded roles/exits](evidence/exp7-candidate/result.json).

Advisory correction: OpenCode's “after124s” confuses exit124 with the configured
120-second timeout; no duration measurement of124seconds is asserted. Service
cleanup means stopped, not deleted. Claude correctly notes that new unit tests
cover startup cleanup and case selection, not all stdout/signature/acceptance
branches. The live fixture retains those positive and negative controls, but
unexercised failure branches remain a test-coverage gap, not an approved exception.
