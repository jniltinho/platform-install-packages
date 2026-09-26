# OpenCode guard review — baseline-protocol preparation (read-only, local)

Status: PREPARATION review only. NOT acceptance. No release approval.
No network request, VM run, SSH, secret access, or source edit performed.

## Scope and identities

- Reviewed (read-only):
  - `tools/php83/baseline-protocol/guarded_http.py` sha256 `6e825b1eb87446f50908cc590e03eb51238eeedb9c75879bc8268f28cddee8f6`
  - `tools/php83/baseline-protocol/test_guarded_http.py` sha256 `71f839721cae2d39e47ceae55271f0477ff31522bd8fbbacbbbae7368e4c32ca`
  - `tools/php83/baseline-protocol/README.md` sha256 `1555b80f0b2c0047b47b0f6c9356e4259891d3e7a3c8767aedb125c5fbc3cc86`
  - `doc/php83/baseline-protocol-plan.md` sha256 `4482958d129cbd859c2321756c0af7608426adbd2df776d374f9455540f66dc9`
  - Decision 7 in `openspec/changes/migrate-kaltura-php83/design.md` (lines 38, 91)
- Executor: OpenCode (Muse Spark `opencode/muse-spark-1.3-contributor-free`), local worktree only.
- Environment: Python 3.12.3, Linux, worktree HEAD `a294207e`.
- Transport used in this review: mocked (`unittest.mock.patch` on `build_opener`) and pure-guard calls only. GET-only interface; no POST/auth/media/TLS handshake executed.

## Commands and exits

1. `python3 -m unittest discover -s tools/php83/baseline-protocol -p 'test_*.py' -v` → exit 0, **13/13 PASS** (literal, bad_targets, invalid_origin, nested_good, nested_bad, all_redirects_refused, bounded_body, bad_lengths, limit_types, ca_pinned, rejected_before_connection, proxy_disabled, transport_error_redacted).
2. Boundary probe batch (39 checks, mocked transport): 38 PASS, 1 FAIL caused by a typo in the probe itself (`Horn` NameError in the ad-hoc 301 line), not in source. Re-ran redirect codes cleanly:
3. `redirect_request` for 301/302/303/307/308 → all PASS `BoundaryError: Redirect refused`, exit 0.
4. Error-normalization probes (mocked): confirmed 2 concrete bugs below, exit 0.

## Guard boundary findings (verified)

- Literal identity: exact `scheme/host/port` match enforced; evil-suffix, prefix-IP, userinfo, fragment, IPv6, trailing-dot forms all refused. Explicit `:80` allowed on port-80 origin (correct).
- Exact scheme/port: cross-scheme and off-list-port refused, including `:bad` (via `p.port` ValueError → BoundaryError).
- Controls before urlsplit: leading space, `\n`, `\t`, NUL, DEL-127, backslash all rejected pre-parse. Correct order (check precedes `urlsplit`).
- Relative HLS references: `seg.ts`, absolute-path, and contained `../` resolve inside origin and pass; protocol-relative (`//host`), cross-scheme, and `file:` escapes refused via re-validation of the joined URL. Parent traversal cannot escape origin because any absolute result is re-validated.
- Redirects/proxy: all five redirect codes refused; `ProxyHandler({})` confirmed (`proxies == {}`), so ambient env proxies are bypassed.
- Pinned CA: HTTPS without CA refused; HTTP with CA refused; hash mismatch refused; non-bytes CA refused.
- Bounded body: exact-length match enforced both directions (declared-too-big, declared-too-short, overflow, unicode-digit CL all refused); `bool` limit rejected via `type() is not int`.
- Sanitized error: `open()` OSError redacted (`Transport request failed`); pre-validation rejects before `open` is called (`assert_not_called` PASS); GET method pinned; `response.geturl()` re-validated; timeout upper-bounded at 30.

## Concrete bugs (report before any baseline extension)

1. `trusted_context`: malformed CA input escapes the BoundaryError contract. Non-ASCII bytes with matching hash raise raw `UnicodeDecodeError` (`.decode('ascii')` outside try); ASCII garbage with matching hash raises raw `ssl.SSLError` (`load_verify_locations`). Caller-supplied path, low severity, but violates the module's own sanitized-error boundary. Fix (not applied here): wrap decode+load in try/except `(UnicodeError, ssl.SSLError, ValueError)` → BoundaryError.
2. `Client.get` body-read path not normalized: `response.read()` raising `http.client.IncompleteRead` (an `HTTPException`, **not** `OSError`/`URLError`) propagates raw instead of BoundaryError. Only `open()`-time errors are caught. Existing test covers `open` side-effect only. Fix (not applied here): extend the except clause or wrap `read_bounded` call to map `http.client.HTTPException` (and `Exception` from read) → BoundaryError without leaking bytes.
3. Not code bugs but binding limitations (already declared in README; must not be waived): socket `timeout=30` is per-operation, **not** a total/hard deadline — a slow stream can exceed wall time; no Range/206 contract (206 → `Unexpected HTTP status`); no POST/auth/HLS parser/retries; TLS success/wrong-CA and redirect transport proven only by mocks, never a real handshake. These block any claim of network/TLS/API/media acceptance.

## Bounded verdict

- The 13 local guard tests pass and the eight inspected boundaries behave as documented for pure-guard, mocked-transport, GET-only preparation.
- Two concrete low-severity error-normalization bugs (§1–2) must be fixed and re-tested before this client carries any real baseline workload.
- This review is PREPARATION, not acceptance: no network/TLS/API/media evidence produced; hard whole-request deadline and actual-TLS tests remain missing and are explicitly NOT waived. No release approved.
