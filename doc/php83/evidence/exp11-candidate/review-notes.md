# Independent actual CLI preparation reviews

All review processes are terminal. **Status remains PREPARED_NOT_SELECTED**;
none of these reviews approves selection, construction or runtime acceptance.
The exact 72 input hashes were unchanged across the entire review window; see
`review-input-identities.json` and `review-final-identities.json`.

| Actual executor | Terminal CLI exit | Executed evidence | Boundary |
|---|---:|---|---|
| Grok | 124 (120-second timeout) | No test sidecar, no public result bytes | **NOT_EXECUTED**; no successful review attributed |
| OpenCode, `opencode/muse-spark-1.3-contributor-free` | 0 | 23 local tests, exit 0; repo-only metadata/patch inventory review | Authorized Grok fallback, not Grok; no original-ZIP preflight |
| Claude | 0 | 23 local tests and exact 63-patch original-ZIP/private-copy preflight, both exit 0 | No ZIP construction or PHP execution |
| Cursor | 0 | 23 local tests and independent repo-only selection inventory, both exit 0 | No original-ZIP preflight or PHP execution |

These are **23 test cases repeated independently**, not 69 distinct new
application tests. The OpenCode model was resolved from the installed model
listing before invocation; no paid substitute was selected. No permission
bypass or alternate access after a denied read occurred. Grok's terminal
timeout was confirmed before the fallback started.

After these attempts, the operator updated coordination to prioritize Claude,
Cursor and OpenCode without routine Grok retries. That current rule is reflected
in `AGENTS.md`; the failed Grok attempt above remains honest history, not a
requirement to try it again. This cycle used Muse Free, not the separately
authorized but untested MiniMax-M3 option.

Claude was launched only after a fresh clock check confirmed the specified
18:20 America/Sao_Paulo quota-reset boundary. Its actual timestamp is retained
in `claude-launch-time.txt`; there was no retry before that boundary in this
task. The earlier quota-limited attempt from another review remains separate
history, not overwritten or counted as a success here.

## Independently observed preparation evidence

- Claude's `claude-preflight.json` is byte-identical to the primary
  `preflight-final.json`: all 63 strict applications, resulting source hashes,
  manifest and tool identities match. `claude-preflight-comparison.json`
  records both report hashes and equality.
- Cursor and OpenCode separately verified all 59 prior entries field-for-field
  and in order, the four new disjoint targets, all 63 source-patch hashes,
  unique source paths/leaf names and all five anchored metadata documents.
- Existing sfCore is used once. Mixed Spyc/bootstrap alternatives are not new
  additions; previously selected curly-only repairs remain exactly as in exp10.
  The ternary manifest's seven unchanged helper files do not become patches.
- Actual unittest stdout/stderr/exit sidecars prove execution. A CLI exit 0
  alone was not treated as a passed test or accepted application result.

Public reviewer outputs are retained separately as `claude-public.txt`,
`cursor-public.txt` and `opencode-public.txt`. The unavailable Grok result is
recorded in `grok-outcome.json`. Raw provider traces remain temporary outside
the repository; hidden thought fields were not copied into evidence.

## Advisory findings and retained limits

The reviewers found no blocker to these **exact frozen preparation inputs**,
but identified limits that must not be generalized into safety or compatibility
guarantees:

1. The synthetic tests do not explicitly cover every rejection branch: malformed
   prior identity, multi-helper ternary fixtures, fuzz/reversed patches, extra
   output objects/cumulative drift, duplicate/nonregular ZIP members or existing
   CLI report/staging outputs. Offset rejection and other listed tests did run.
2. Header detection is conservative and may reject a patch whose removed source
   line resembles a diff header. General git/mode metadata is not categorically
   rejected, although none of these 63 pinned patches contains that metadata.
3. The final output inventory counts regular files; it is not an exhaustive
   filesystem-object audit for arbitrary untrusted patches. The actual inputs
   are reviewed, hash-pinned single-target patches replayed in private copies.
4. The tool records rather than fixes the entire manifest's hash. Unrelated
   descriptive fields are protected in this review by the separately verified
   freeze, not by a generic all-fields manifest schema.
5. Python/GNU patch version and test-script identity are not embedded in the
   preflight result itself. Reviewer execution details and the broader input
   freeze supply separate context. `preflight_sha256` means the preparer script
   hash; it is not the report's own hash.
6. Per-patch resulting hashes—not a separate hash after every hunk—are checked,
   followed by whole-series rechecks. The suite has 23 total cases, including
   its positive replay case; shorthand calling all 23 “negative tests” in the
   fallback review is imprecise.

No tools or patches were edited while reviews were live. These findings are
retained rather than silently fixed under the existing evidence identity.
Autoload composition qualification and any subsequent selection decision belong
to the coordinator's separate review. No VM, `.20`, package/CI, git, ZIP build,
release or application-acceptance operation was performed by this review task.
