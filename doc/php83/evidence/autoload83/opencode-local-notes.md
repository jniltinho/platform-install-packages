# OpenCode safe repository-only fallback

Actual `opencode/muse-spark-1.3-contributor-free`, resolved through `opencode models opencode`, ran under a 180-second timeout; process exit 0. JSONL records actual bash execution: **8 local unittest tests PASS**, plus matching patch/manifest SHA-256. This is OpenCode fallback evidence, not Grok evidence and not runtime execution.

The earlier attempt's denied read-tool operations were the immutable-source paths ending in `vendor/htmlpurifier/library/HTMLPurifier.autoload.php` and `vendor/symfony-data/bin/symfony.php`; exact paths and rejection messages are preserved in `opencode-local-summary.json`. They were not retried by another tool or copied around the permission denial. Earlier exit0 did not complete that source review.

The new task remained repository-only. Two tests (`test_two_bytes_only`, `test_source_drift`) themselves access external immutable source, so were explicitly NOT_EXECUTED here. Existing primary ten-test evidence is separate; this fallback claims eight only. No VM, build/collector main, source edits, promotion or whole-application acceptance.

Review limitation: OpenCode described existing guards but did not identify the parent's separately discovered duplicate-mode gap. A local coordinator-agent reproduction replacing the candidate83 record with candidate74 still passed `validate()` and incorrectly reported 441 rows. Actual retained primary records do have four distinct modes, so those recorded executions remain valid. The collector requires follow-up hardening with exact unique-mode coverage and a negative test; this test/review pass is not blanket approval. Frozen collector was not changed while Claude's independent runtime repeat was active.
