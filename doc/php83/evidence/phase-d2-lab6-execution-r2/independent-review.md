# Independent successful incremental D2 evidence review

**Scoped milestone accepted:** exported evidence supports normal-APT lab6 installation and bounded Elasticsearch/native-configuration checks with privacy checks passed and workers held. It does not close full seed persistence, effective authorization, actual worker/media flows, full application/release acceptance or recovery requirements.

## Verified joins and chronology

Read all four JSON exports here, prior lab5 blocked/preflight/snapshot/recovery receipts, lab6 first execution/socket diagnostic, and both corresponding coherent-restore/checkpoint receipts. Local hash/serialization checks exited 0:

- Current executor equals contract pin `c5804a9ff6c16ab70e702375113bd851e08985f046d617fafaba22b6b027e99b`.
- Contract guest serialization matches actual-runtime contract hash; terminal guest serialization matches `f5446a3b5f167f379d95ee8d8b6218525567e48f513faf19a11d33b855c9efde`. execution.json has exactly the same terminal values.
- Recovery proof bytes match the contract pin. Snapshot proof matches the preserved phase-d2-lab5-execution-r1/snapshot.json bytes; build proof matches elasticsearch-r7-private-logs/verification-r1.json.
- Exact lab6 package identity is SHA256 `7959f637addad883be0d51ce54a43aa72ad0f155abdd37ddb68aeb57d582ab53`, previously independently checked against both artifact builds and unchanged data archive.

Lab5 was blocked before RUN/APT by the unchanged parent-trust gate. Lab6 first attempt failed the raw endpoint comparison; its exact mapped-loopback Java diagnostic was bounded and separately stopped with privacy/holds reported intact. Failed checkpoint104c911b-91bc-4aff-9931-e5dec08b98a3 remains recorded. Recovery joins restored checkpoint96acf6b1-5bdd-42db-8c4f-940253e7c397, with restore/start command exits0 and resume_failed_run false. Shutdown transport255 is retained, paired with clean-poweroff confirmation rather than misreported as command success. These are coordinator receipts, not independently repeated recovery tests.

## Successful scope

actual-runtime reports exit0, configured lab6 ii status, active Apache/Monit/MariaDB/ES, eight indices, eleven aliases, mapping pins, green cluster, ICU,1073741824-byte heap, disabled GeoIP downloader and effective native ES/local-cache configuration. All five terminal checks are true: package observation, metadata, input canaries, private ES-log capture and generated secrets. Held workers, no resume, both full-acceptance flags false and all three pending obligations are explicit. failure_contained:false is appropriate on this successful path. Earlier failed/blocked outcomes are not superseded or rewritten.

The exported after-dpkg digest and runtime summaries are coordinator observations; complete guest package listing, raw runtime proof and private audit/log contents are not included, so they were not independently re-derived here. Prior independent source/test reviews establish what the pinned executor checks; this review does not pretend to be another live execution.

## Confidentiality and Git scope

No credential values, private configuration bodies, arbitrary SQL data, raw ES/APT logs or secret-token hashes were found in inspected exports. Public source/config artifact pins, bounded statuses/counts, lab addresses/paths and recovery identifiers are acceptable for the requested scoped milestone. Include only reviewed helpers/builders/tests/public fixtures and sanitized evidence. Exclude private guest originals/logs, snapshot disk/memory payloads, credentials and unrelated worktree files; final staged-set review remains coordinator responsibility. No implementation edits, VM/SSH/DB/service/recovery action or Git operation was performed by this reviewer.
