# Exp10 review phases

Selection is independently checked by actual Claude and OpenCode; Claude also
strictly replays all59 patches on private copies, preserving previous16 entries
and verifying all43 additional byte-only repairs. Claude's first manual audit
pointed at a different same-named ZIP outside the approved source cache and failed;
it then uses the pinned `/tmp/kaltura-php83-audit/Rigel-18.20.0.zip`. The erroneous
attempt is retained in its report, not counted as a successful check. The staging
helper correctly rejects that other archive as a negative control.

Grok timed out at120seconds with exit124 and no response, separately recorded.
OpenCode `opencode/muse-spark-1.3-contributor-free` is the exact resolved authorized
fallback, not a Grok success. It runs13 builder and10 newstaging guard tests and
checks the actual cumulative selection without building the artifact.

Cursor's first phase runs53 local tests (10selection/28syntax/15API) and shell
parsing and reviews prep-only contracts. Its report says pins missing and VM not
executed **at that phase**, correctly. Later pinning/staging/build/VM phases have
their own actual evidence and do not retroactively change that report. Cursor's
Portuguese advisory text is retained verbatim; project documentation is English.

Concurrent untracked prep files were assigned to separate workers; no runtime
ran before the reviewed actual artifact pin. Production/.20, package/CI and
release gates are unchanged. Source/patch transformation evidence is not all-file
runtime coverage. No aggregate acceptance task closes from this artifact alone.

Claude's baseline report says other executors still need arranging because its
scope forbids spawning them. Coordinator evidence already records their actual
separate runs; that advisory sentence is not an absence of independent review.
The final native83 snapshot command was corrected before execution from an
incorrect remote-pipe prompt to the actual local wrapper interface; all actual
snapshot reports/exits and unchanged identities are retained.

Final staged whitespace check reports one extra blank EOF line in the frozen
`tools/php83/exp10-syntax/test_scan.py` copy. It is intentionally not reformatted
after both VM executions: all six frozen/staged file hashes must remain the
executed identities. The whitespace check excluding that one exact file passes;
this cosmetic warning is not an application/runtime acceptance waiver.
