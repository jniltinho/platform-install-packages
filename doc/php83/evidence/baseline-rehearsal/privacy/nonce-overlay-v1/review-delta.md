# Actual OpenCode review and bounded local follow-up

Actual Muse CLI exited 0 and reported execution of eleven local tests. It did
not execute the VM or approve journal semantics. Original public report retained.

Two concrete driver issues corrected afterward, now thirteen local tests:
- Verify the pinned installed overlay manifest and every member before importing
  its guest module; no overlay code runs before this check.
- Parse systemd properties by exact key and compare exact deny/allow sets, rather
  than searching unrelated text for address substrings.

Other observations are bounded limitations, not universal guarantees: the host
IP check excludes named production peers rather than asserting a one-interface
host; the actual HTTP client permits only its literal74 destination. Stage bytes
are root-owned readonly and verified before/after, not independent per-import
host compromise protection. Public field checks supplement source-reviewed
scanner output schemas, not arbitrary secret-value detection. Public immutable
stages are deliberately retained for reproduction; only the transient execution
unit/provider probe is removed. The existing SSH config is an operator-managed
transport dependency, not newly authorized arbitrary targeting.

Journal review is a separate prerequisite; no VM execution before its final pin.
