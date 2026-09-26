# Cursor media review — freeze_media B1 adjudication (read-only, local)

Status: PREPARATION review only. NOT application/upload/benchmark acceptance.
No release approval. No FFmpeg/ffprobe execution. No VM/SSH/network. No source edits.
Prior evidence preserved untouched (`opencode-r2-review.md`, `review-finding-adjudication.md`).

## Scope and identities

| Path | sha256 |
|---|---|
| `tools/php83/baseline-protocol/freeze_media.py` | `e1ab367ca3cdf6dea452a99bbb19a85725b33d3900889b57d1057a4baaf38f69` |
| `tools/php83/baseline-protocol/test_freeze_media.py` | `5e69530224896e19729403f24e24906f741496f27dc55517d79766fb6e71893d` |
| `doc/php83/evidence/baseline-protocol/opencode-r2-review.md` | read as-authored (B1 claim under test) |
| `doc/php83/evidence/baseline-protocol/review-finding-adjudication.md` | read as-authored |

- Reviewer/executor: Cursor Agent (this session), local worktree only.
- Worktree HEAD: `c7cf5fb4`. Sources under `tools/php83/baseline-protocol/` remain **untracked** (`??`).
- Environment: Python 3.12.3, Linux. Host has `/usr/bin/ffmpeg` and `/usr/bin/ffprobe` present; **neither was invoked** (no `-version`, no encode, no probe of media files).
- Transport: unittest mocks + AST/control-flow inspection only. `generate()` was exercised only on pre-existing paths under tempfile (refusal path); no new fixture directory was created for encoding.

## Muse B1 claim under test

OpenCode r2 (`opencode-r2-review.md`) alleged **B1 BLOCKING**: when `output` already exists, `ValueError('Refuse existing fixture directory')` is followed by `finally: report.write_text(...)`, overwriting `manifest.json` inside the refused directory; and that `mkdir` failures are similarly masked by `finally`.

Adjudication note already contradicted that claim; this review independently re-checks control flow and runs the sentinel + full local suite.

## Actual Python control flow (`generate`)

AST statement order inside `generate` (line numbers from current `freeze_media.py`):

| Order | Line | Statement | Relative to `try` |
|---|---|---|---|
| 0 | 51 | `if output.exists(): raise ValueError('Refuse existing…')` | **before** try |
| 1 | 53 | `programs = …` | before try |
| 2 | 54 | `if not all(programs.values()): raise …` | before try |
| 3 | 56 | `identities = …` (may call `subprocess.run` for `-version`) | before try |
| 4 | 59 | `output.mkdir(parents=True, exist_ok=False)` | **before** try |
| 5–6 | 60–62 | `manifest` / `report` locals | before try |
| 7 | 63–89 | `try` / `except` / `finally: report.write_text(...)` | try+finally |
| 8 | 90 | `return manifest` | after try |

Sole `write_text` in `generate` is at line 89 inside `finally`. Raising at the existing-path check (L51) or at `mkdir` (L59) **never enters** the `try`/`finally` block, so `manifest.json` is not written on those paths.

Therefore **B1 is a FALSE FINDING** for the alleged existing-output overwrite. The related mkdir-masking claim is likewise false: `mkdir` precedes `try`.

What `finally` *does* do (correct for a run that created the directory): after a successful `mkdir`, mid-run failures set `status=FAILED` in `except` and still persist the partial manifest into the **new** directory this invocation created. That is not “refuse then overwrite an existing directory.”

## Executed commands and exits

Working directory: repo root unless noted. All local; no ffmpeg argv executed by these harnesses (subprocess mocked in refusal tests; verification tests are pure `verify()`).

1. Sentinel regression (existing dir + preserved sentinel bytes):

```text
cd tools/php83/baseline-protocol
python3 -m unittest test_freeze_media.MediaPreparationTests.test_existing_directory_does_not_write_manifest_or_execute -v
```

- Result: `ok` — Ran 1 test — **OK**
- Exit: **0** (`EXIT_SENTINEL:0`)

2. Full local suite (24 tests: 9 media + 15 guarded_http):

```text
cd tools/php83/baseline-protocol
python3 -m unittest discover -s . -p 'test_*.py' -v
```

- Result: Ran **24** tests — **OK**
- Exit: **0** (`EXIT_FULL:0`)
- Includes: `test_existing_directory_does_not_write_manifest_or_execute`, `test_existing_file_unchanged`, frame/raster/duration/schema/command checks, and all guarded_http tests.

3. Ad-hoc control-flow + Decision7 static probe (heredoc; exit **0**):

- Confirmed PRE_TRY stmt list and `write_text` only at L89.
- Temp existing dir: sentinel `manifest.json` bytes unchanged; inventory unchanged; `subprocess.run` not called.
- `CASES` exact: `short360` 10s 640×360@25 → 250 frames; `fullhd60` 60s 1920×1080@60 → 3600 frames.
- `command()`: `-n` present, `-y` absent; `libx264` + `yuv420p`; `aac` + `48000` + stereo; CFR/GOP flags as coded.
- `verify()` accepts matching synthetic probes for expected frame counts; ffmpeg **not** executed (`ffmpeg_executed: false`).

## Decision 7 readiness — source fixtures only

Decision 7 (`openspec/changes/migrate-kaltura-php83/design.md`) requires synthetic **10s 640×360/25fps** and **60s 1920×1080/60fps** H.264/AAC fixtures, with encoder settings and SHA-256 recorded, for later identical-byte reuse in labs.

| Requirement (source-prep subset) | Finding |
|---|---|
| Fixture shapes | Exact `CASES` match Decision 7 durations/raster/fps. |
| Codecs / layout | Explicit argv: H.264 (`libx264`/`yuv420p`) + AAC stereo 48 kHz; list-form, no `shell=True`. |
| No overwrite of existing output dir | Existing path raises before try; sentinel test proves no manifest write / no subprocess. `-n` + `mkdir(…, exist_ok=False)`. |
| Exact decoded frames | Probe uses `-count_frames`; `nb_read_frames` must equal `duration*fps` (250 / 3600); rates asserted. |
| Duration tolerance | One video frame + one AAC frame: `Fraction(1,fps)+Fraction(1024,48000)`. |
| Timeouts / identity joins | `timeout` on version/generate/probe; tool path+sha256+version recorded; post-run drift re-hash; per-fixture sha256/bytes. |
| Non-acceptance flags | `application_acceptance: False`, `cross_build_reproducibility: False` — preserved; **no cross-build byte claim**. |

**Verdict on generation readiness:** exact proposed FFmpeg commands and source-frame validation are **ready for one bounded local synthetic generation** under approved Decision 7 *source-fixture preparation*, with B1 not blocking.

This readiness is **not**:

- application acceptance, upload-to-READY, stream/HLS verification, or benchmark/workload PASS;
- lab dual-copy / identical-byte reuse evidence (bytes do not exist until a generation run);
- cross-build byte reproducibility (explicitly flagged false in manifest/README);
- linked-library/host attestation (declared absent in README).

B2 from r2 (raw `KeyError`/schema exceptions in `verify`) remains a **triage limitation**: fail-closed via `except Exception` → `FAILED`; covered by `test_bad_schema_fails_closed`. Not a successful validation; not a demonstrated overwrite bug; no source rewrite performed for a false B1.

## Explicitly NOT executed / NOT claimed

- No `ffmpeg` / `ffprobe` process started in this review.
- No fixture `.mp4` bytes produced; no media SHA-256 from a real encode.
- No VM, SSH, network, TLS, API, upload, or baseline measurement round.
- Passing 24/24 local harness tests ≠ full application acceptance or release gate.

## Bounded verdict

1. **B1 = FALSE FINDING.** Existing-output refusal and `mkdir` both precede `try`/`finally`; sentinel + full suite exit 0 prove no manifest overwrite on the refused path.
2. **Commands + frame validation = ready** for one operator-authorized bounded local synthetic generation (Decision 7 source fixtures only).
3. **Limitations preserved:** not app/upload/benchmark acceptance; no cross-build byte claim; generation itself remains **NOT_EXECUTED** here.
4. No source changes. No prior evidence rewritten.
