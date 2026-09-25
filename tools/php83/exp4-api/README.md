# exp4 isolated artifact regression

This fixture is deliberately revision-pinned. Do not point it at production or
reuse it for another ZIP without new identity/review evidence.

1. Build exp4 from the retained manifest twice using `build-experimental-zip.py`;
   verify both artifacts with `verify-experimental-zip.py`.
2. Run `bash tools/php83/exp4-api/stage.sh 74` and `... 83` once only. Each refuses
   an existing stage. Required approved SSH configs and the existing baseline
   application/copy of runtime83 are described in `doc/php83/exp4-candidate.md`.
3. With sole writer ownership of baseline74, run `python3 tools/php83/exp4-api/collect.py NEW_REPORT`.
4. For focused CLI regression, on each approved VM run
   `python3 /home/vagrant/php-exp4-regression/exp4-regression/batch.py` and capture
   stdout locally. The batch exit alone does not prove all rows passed: inspect
   each row; four original-8.3 JSON fatal controls are expected. Candidate failures
   must never be reclassified as expected failures.

The current stage script also transfers the CLI runners. In the first recorded
cycle those two files were copied separately after the stage was created; runtime
reports record their hashes. The initial baseline stage printed the stale label
`EXTRACTED_VERIFIED_EXP3`; archive/byte/hash checks were for exp4, and the message
was corrected before the 8.3 stage. Neither difference changes tested inputs.

API diagnostics are sanitized; never commit raw KS-bearing application logs.
CLI cases contain only synthetic parser data. Preserve diagnostic stderr there.
New API fixtures reuse existing SQL/auth/HTTP/TLS cases without removing any.
Both API and CLI results are bounded evidence, never release approval.
