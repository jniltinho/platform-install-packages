# OpenCode r2 review — baseline-protocol preparation (read-only, local, synthetic-only)

Status: PREPARATION review only. NOT acceptance. No release approval.
No FFmpeg run, no network request, no VM/SSH run, no secret access, no application/code edit performed.
Prior evidence preserved untouched (`opencode-guard-review.md`, `reviewed-r1/`, `guard-r2-tests.log/.exit`).

## Scope and identities

- Reviewed (read-only):
  - `tools/php83/baseline-protocol/guarded_http.py` sha256 `4cc44f15645ced42e1e156586a79a2795d38f929c6f812eb695e427ee7e47b59`
  - `tools/php83/baseline-protocol/test_guarded_http.py` sha256 `fd7cf96639553f5e516e8d89d095c080b2ec8646461dc3a03036902ef9961912`
  - `tools/php83/baseline-protocol/freeze_media.py` sha256 `e1ab367ca3cdf6dea452a99bbb19a85725b33d3900889b57d1057a4baaf38f69`
  - `tools/php83/baseline-protocol/README.md` sha256 `e321a3ddd87d67d19e8ef0406def0b98cb014fb8ee5c5e46794b81d8682f4acf`
  - `doc/php83/evidence/baseline-protocol/reviewed-r1/guarded_http.py` sha256 `6e825b1eb87446f50908cc590e03eb51238eeedb9c75879bc8268f28cddee8f6`
  - `doc/php83/evidence/baseline-protocol/reviewed-r1/test_guarded_http.py` sha256 `71f839721cae2d39e47ceae55271f0477ff31522bd8fbbacbbbae7368e4c32ca`
  - `doc/php83/baseline-protocol-plan.md` and Decision 7 in `openspec/changes/migrate-kaltura-php83/design.md` (lines 38, 91) per r1 citations (not re-hashed here).
- Executor: OpenCode (Muse Spark `opencode/muse-spark-1.3-contributor-free`), local worktree only.
- Environment: Python 3.12.3, Linux, worktree HEAD `a294207e`. NOTE: `tools/php83/baseline-protocol/` and `doc/php83/evidence/baseline-protocol/` are UNTRACKED (`git status` shows `??` for both); the new sources exist only in the worktree, not in any commit.
- Transport used in this review: mocked (`unittest.mock.patch` on `build_opener`) and pure-guard calls only, plus static AST/`py_compile` inspection of `freeze_media.py`. `generate()` was NEVER called; no `ffmpeg`/`ffprobe` binary was executed (not even `-version`). GET-only interface; no POST/auth/media/TLS handshake executed.

## Commands and exits (all local, synthetic-only)

1. `python3 -m unittest discover -s tools/php83/baseline-protocol -p 'test_*.py' -v` → exit 0, **15/15 PASS** (13 prior guard tests + 2 new `ErrorNormalizationTests`). Independently reproduces the preserved `guard-r2-tests.log` (15 ok, exit 0).
2. Regression probe batch (ad-hoc heredoc, mocked transport, exit 0): N1 non-ASCII matching-hash CA → BoundaryError; N2 ASCII-garbage matching-hash CA → BoundaryError; N3 `IncompleteRead` with synthetic secret in body-read path → BoundaryError with no leak and context-manager `__exit__` called; N4 `BadStatusLine` in read path → BoundaryError; N5 `RemoteDisconnected` at open → BoundaryError.
3. r1-confirm probes (read-only `importlib` load of `reviewed-r1/guarded_http.py`, exit 0): both malformed matching-hash CAs raise RAW `UnicodeDecodeError` / `ssl.SSLError`; r1 source contains no `HTTPException` catch. Confirms `reviewed-r1/` preserves the OLD (buggy) source — it is a frozen reference, not the fixed code.
4. `python3 -m py_compile` on `guarded_http.py`, `test_guarded_http.py`, `freeze_media.py` → OK (compile check only, no execution).
5. Static AST inspection of `freeze_media.py` (no subprocess executed): CASES exact, no `shell=True`, 3 `timeout=` sites, `-n` + `exist_ok=False` + refusal string present, `-count_frames` + `nb_read_frames` present, tolerance expression as specified, single-thread flags present, libx264/AAC/48k/stereo present, sha256/`-version`/drift re-check present, both non-acceptance flags False, `finally:` + `report.write_text` present (see defect B1).

## Exact new `guarded_http.py` fixes vs `reviewed-r1` (verified by `diff -u`)

- Hunk 1: `from http.client import HTTPException` added (new import).
- Hunk 2 (`trusted_context`, r1-bug §1): bare `ctx.load_verify_locations(cadata=ca_pem.decode('ascii'))` wrapped in `try/except (UnicodeError, ssl.SSLError, ValueError)` → `BoundaryError('Invalid private CA certificate')`. Matches the r1-proposed fix exactly, including the `ValueError` arm.
- Hunk 3 (`Client.get`, r1-bug §2): `except (URLError, OSError)` extended to `except (URLError, OSError, HTTPException)` → `BoundaryError('Transport request failed')`. Covers `IncompleteRead` and every other `http.client` read-path failure without leaking bytes.
- New tests (`ErrorNormalizationTests`): `test_malformed_matching_ca` (both r1 payloads: `b"invalid PEM"` and `bytes([255])`, hash-matched) and `test_incomplete_body_is_redacted` (`IncompleteRead(b'synthetic-sensitive-marker', 42)`, asserts BoundaryError, asserts marker absent from message, asserts `__exit__` called once). 13 → 15 tests; old 13 unchanged and still passing.

## Guard regression validation

- Probes N1/N2 close r1-bug §1: both payload classes that previously escaped as raw `UnicodeDecodeError`/`ssl.SSLError` (re-confirmed raw on the r1 copy) now normalize to BoundaryError with no CA bytes in the message.
- Probes N3/N4/N5 close r1-bug §2: body-read `IncompleteRead` (with secret payload — no leak), `BadStatusLine`, and open-time `RemoteDisconnected` all normalize to BoundaryError; context-manager cleanup verified.
- No regressions: literal/evil-target/controls/nested/redirect/proxy/CA/body-limit/pre-validation/GET-pin/`geturl`-revalidation/timeout-bound behavior unchanged (13/13 old tests pass unmodified).

## `freeze_media.py` pre-encoding review (Decision 7 mapping, static only — NOT_EXECUTED)

| Decision 7 / prompt requirement | Static finding |
|---|---|
| Fixtures 10s 640x360/25fps + 60s 1920x1080/60fps | `CASES = [('short360', 10, 640, 360, 25), ('fullhd60', 60, 1920, 1080, 60)]` — exact. |
| H.264 / AAC stereo 48k | `-c:v libx264 … -pix_fmt yuv420p -r <fps> -fps_mode cfr -g <2*fps> -keyint_min <2*fps> -sc_threshold 0`; `-c:a aac -b:a 128k -ar 48000 -ac 2`. Explicit. |
| Explicit commands | List-form argv, no `shell=True` anywhere; full command + probe command + exits + stderr recorded per fixture row. |
| At most one video + one AAC frame duration tolerance | `tolerance = Fraction(1, fps) + Fraction(1024, 48000)` applied to video, audio, and container durations — exactly one video frame + one AAC frame (1024 samples @ 48 kHz). |
| Exact 250 / 3600 decoded frames | `int(v['nb_read_frames']) != duration*fps` with `-count_frames` in probe; 10×25=250, 60×60=3600; `avg_frame_rate` and `r_frame_rate` both asserted == fps. |
| Timeout | `timeout=1200` generate, `timeout=180` probe, `timeout=10` tool `-version`. Present on every subprocess call. |
| Output refusal | `output.exists()` → `ValueError('Refuse existing fixture directory')`, `-n` flag, `mkdir(…, exist_ok=False)`. BUT see defect B1. |
| Hash/version joins | ffmpeg+ffprobe path+sha256+`-version` stdout recorded pre-run; binaries re-hashed post-run (`Encoder/prober drift`); per-fixture media sha256 + byte size; manifest always written. Linked-library/host attestation absent — already declared in README, not waived. |
| Preparation-only marking | `status` starts `RUNNING`, ends `SOURCE_FIXTURES_VALIDATED_PENDING_INDEPENDENT_REVIEW`; `application_acceptance: False`, `cross_build_reproducibility: False`. Correct. |
| Stream shape | `len(streams) != 2` refused; exactly one video + one audio enforced. Correct. |

## Blocking defects before ANY encoding (must fix first)

- **B1 (BLOCKING — output-refusal join broken): `generate()` writes into the directory it just refused.** When `output` pre-exists, the `ValueError('Refuse existing fixture directory')` raise is followed by the `finally:` block's `report.write_text(...)`, which creates/overwrites `manifest.json` INSIDE the pre-existing directory — the very directory generation refused to touch. Same root cause masks `mkdir` failures: if `mkdir` raises, `finally` raises `FileNotFoundError`/`NotADirectoryError` over the original error. Fix before generation (e.g. only write the manifest when this run created the directory; return before any write on the pre-exists path). No media bytes are overwritten (only `manifest.json`), but the stated "refuses an existing directory, never overwrites" guarantee does not hold as written.
- **B2 (non-blocking, recommend): `verify()` uses direct key indexing** (`probe['streams']`, `v['avg_frame_rate']`, `v['nb_read_frames']`, `a['duration']`, …). A probe JSON missing keys (e.g. `nb_read_frames` without `-count_frames`, `duration: "N/A"`, `avg_frame_rate: "0/0"` → `ZeroDivisionError`) raises raw `KeyError`/`TypeError`/`ZeroDivisionError` instead of a named `ValueError`. Fail-CLOSED (`generate` catches `Exception` → `FAILED`, no false PASS), so not verdict-blocking, but normalize to `ValueError('<field> mismatch/missing')` for triageable manifests.
- **Observations (non-blocking):** full-file `media.read_bytes()` hashing holds ~100s-of-MB 1080p60 in RAM (fine for lab, note for constrained hosts); audio frame counts not asserted (video frames + duration tolerance cover the prompt's exact-frame requirement); no profile/level/SAR/DAR/sample-fmt assertions (Decision 7 does not require them); `output` symlink/parent-race edges unhandled (covered by `exist_ok=False` fail-closed).

## Explicitly NOT waived / untested scope

- Real TLS handshake (success/wrong-CA), real redirect/no-forwarding transport, and hard whole-request deadline remain UNIMPLEMENTED: `timeout=30` is a per-operation socket timeout, documented in README, and must not be called a total bound.
- No network/TLS/API/media evidence produced by this review; `freeze_media.py` is NOT_EXECUTED (no bytes generated, no hashes exist yet); cross-build reproducibility and linked-library attestation absent by declaration.
- GET-only, no KS/auth, no uploads, no HLS parser, no Range/206 contract, no retries/benchmark statistics.
- Passing 15/15 harness tests does not prove full application acceptance and does not approve any release, baseline workload, or cutover.

## Bounded verdict

- The two r1 error-normalization bugs are FIXED in `tools/php83/baseline-protocol/guarded_http.py` exactly as prescribed, covered by 2 new regression tests (15/15 PASS, exit 0), and independently validated by probes N1–N5; `reviewed-r1/` confirmed frozen at the old buggy source (hashes match the r1 record).
- `freeze_media.py` matches Decision 7 on fixtures, codecs, explicit commands, stream shape, tolerance, exact frame counts, timeouts, and hash/version joins — BUT defect B1 blocks encoding: fix the refuse-then-write manifest path (and consider B2 normalization) before ANY generation run.
- This review is PREPARATION, not acceptance: real-TLS/hard-deadline work remains missing and is explicitly NOT waived. No release approved. No code or prior evidence modified.
