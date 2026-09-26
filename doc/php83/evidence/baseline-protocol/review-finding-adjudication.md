# OpenCode r2 finding adjudication

Guard fixes independently reproduced: both error-normalization defects closed.

Media B1 is **not reproduced and contradicted by control flow**: the existing-path
check and `mkdir` are BEFORE the try/finally, so raising there never enters the
manifest-writing finally. Original r2 review is retained unchanged. New test
`test_existing_directory_does_not_write_manifest_or_execute` creates a sentinel
manifest, calls generate, verifies unchanged bytes/inventory and zero subprocess
calls. An existing regular-file test likewise proves no modification. All24 local
tests pass; no ffmpeg generation was executed. The media script has not changed
since the reviewed SHA e1ab367c...38f69.

B2 accurately describes raw schema exceptions but fails closed; this remains a
triage limitation, not a successful validation or swallowed failure. A missing-key
test asserts the actual KeyError. Independent focused adjudication is requested
before encoding; do not rewrite source merely to satisfy a false finding.
