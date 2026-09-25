# Exp11 native PHP8.3 independent CLI repeat

**PASS — bounded 36-case native83 repeat only.** Actual Claude CLI completed with
exit 0, executing snapshot → existing staged batch → snapshot on the exclusively
assigned `php83` lab. Each command returned 0 with empty runner stderr. This was
fresh execution, not a copy of the primary report; current tool calls/results
are retained in `claude-native83-agent-stream.jsonl`.

## Exact outcomes

* Ordered unique matrix: `original`, `exp10`, `exp11` × `standard`, `minimal` ×
  six existing CLI cases = 36 processes.
* 32 positive exit-0 cases.
* Four expected original-source compiler exit-255 controls: legacy JSON and Zend
  JSON under both INIs, empty stdout and the native removed-curly-offset fatal
  at `Services_JSON.class.php:176` or `Zend/Json/Encoder.php:557`.
* All per-case exit/stdout/stderr equal the primary exactly; only `duration_ns`
  differs. All other batch metadata equals primary except its fresh UTC timestamp.
* Verified exp11 archive pin is `f2474f5b951bfd2d121291025c8dd4554697fb5bb4024e132987643dab6144a7`,
  with 15,240 extracted files; the batch also rechecks the prior exp10 artifact.
* Primary and repeat before/after runtime identity objects all match: 39 binary/
  module objects with linked-library hashes, native standard/minimal modules and
  INI configuration identities. All 22 frozen local inputs remain unchanged.

Claude's `claude-native83-comparison.json` is corroborated by
`claude-native83-codex-validation.json`, including strict integer statuses, exact
ordered matrix, concrete negative-control messages/source lines and full runtime
identity comparison. A batch exit 0 alone is not interpreted as 36 positive cases.

## Actual commands

```sh
python3 doc/php83/evidence/exp10-runtime/snapshot-php83.py doc/php83/evidence/exp11-runtime/claude-native83-runtime-before.json
ssh -T -F /tmp/kaltura-php83-ssh.conf php83 'python3 /home/vagrant/php-exp11-regression/exp11-regression/batch.py'
python3 doc/php83/evidence/exp10-runtime/snapshot-php83.py doc/php83/evidence/exp11-runtime/claude-native83-runtime-after.json
```

The batch output is `claude-native83-cli.json`, with separate exit/stderr sidecars.
Existing staged source/harness and the snapshot wrapper were unchanged; no
restaging, baseline74 access or SQL was performed. Nativephp83 ownership was
released after authoritative completion and reconciliation.

## Evidence and limitations

The stream retains nine actual current tool calls and nine results plus the
public final report. Historical hook context and explicit reasoning blocks were
removed; original stream hash/count provenance is in
`claude-native83-stream-sanitization.json`, with no raw reasoning archive.
Identical deterministic JSON is not proof of execution independence; the actual
CLI command/tool-call record provides that evidence. The VM clock was observed
ahead of the local clock, so the batch timestamp is metadata, not an independence
or wall-clock-duration guarantee.

This same-VM native83 repeat does not validate original74 semantics, HTTP/API,
DB/backend behavior, whole-application acceptance, release or cutover. Those
remain separate coordinated work. No sources, patches, tools, package or release
were changed by this task.
