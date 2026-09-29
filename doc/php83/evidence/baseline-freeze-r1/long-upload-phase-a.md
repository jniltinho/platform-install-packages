# FullHD60 phase A — chunked upload (Baseline74 lab)

Date 2026-09-28/29. Lab only (VM 9e954729-…, 192.168.56.74); no `.20`. Partial evidence
for 1.2/5.5 (and T3 upload path); closes no checkbox.

## Staging
`stage_long_fixture.py`: fullhd60.mp4 (117,210,794 bytes, SHA256 611e3644…5b07) copied once to
`/var/lib/kaltura-baseline-long-media-r1/fullhd60.mp4` (root, 0444), hash verified on both sides,
temp removed (`temp_cleanup: NOT_NEEDED`).

## Workload (`long_upload.py`)
Pinned Rigel semantics (UploadTokenService.php:70-100, kUploadTokenMgr.php:118-215, 406-481):
part 1 resume=0/finalChunk=0 → PARTIAL(1); parts 2..112 resume=1, resumeAt=offset → uploadedFileSize
=offset+len; part 112 finalChunk=1 → FULL_UPLOAD(2). autoFinalize never requested; no retry; any
unexpected acknowledgement stops. POST multipart over pinned-CA HTTPS 8443 (spawned worker, no
redirects, request body ≤ 1 MiB+64 KiB, response ≤ 1 MiB); KS in POST body only. Then media.add +
media.addContent (KalturaUploadedFileTokenResource).

## Native run (`long-upload-native-r1.json`, sha256 8f0f93203de76771d3ddbed78eaa6a23acf6cf0aed03c31851a9aec7f8f9709d)
Unit `baseline-freeze-56fbc341`, stage `/var/lib/kaltura-baseline-long-upload-r1`; guest exit 2,
stderr 0, unit inactive.
- Upload: all 112 parts acknowledged, 117,210,794 bytes; entry `0_wzlsbwmy` created; addContent
  accepted (`long_upload_progress` full). This mutation must not be repeated.
- Privacy: audits 1–4 (invalid nonce, user, MEDIA_PRIVACY) zero, Sphinx full-content scans zero.
  BATCH_PRIVACY failed `FILES_INVENTORY_CHANGED` (audits 5–6): new daily worker logs
  `/opt/kaltura/log/batch/extractmedia-0-2026-09-29{,.err}.log` were created when processing began.
  The batch audit for this window is therefore INCOMPLETE; not a privacy pass. The round's KS is
  not recoverable for a retroactive batch scan.
- READY/flavors not observed (phase B).

## Reviews (source-only)
Codex `gpt-6-luna`: round 1 CHANGES_REQUIRED (request-body bound, staging temp cleanup, final-part
resumeAt disputed with pinned source), round 2 PASS. Claude subagent Opus 5.5: CHANGES_REQUIRED
(public `upload_attempted` label; fixed + entry_id in progress + cleanup reporting), then VALIDATED
(83 tests, byte-identical guest, 43 pins).

Identities: long_upload.py 38b4e98a…a5ee2, guest_long_upload_r1.py 241aaa5a…fc383,
run_long_upload_r1.py b24cdd07…05a02, prepare_long_upload_r1.py 7e3d34fa…18e26,
stage_long_fixture.py f9fb9574…2fe15, test_long_upload_r1.py 5e0ca558…a13d1.

## Next
Phase B must scan log files created during its window from offset 0 (append scanner rejects new
files), then observe READY, flavors and delivered 1080p60 properties for `0_wzlsbwmy`.

# FullHD60 phase B r1 — read-only READY observation (failed before any media call)

Reviewed additions: `privacy_new_logs.py` (logs created in-window scanned from offset 0; per-window
registry so a new log that vanishes/shrinks/changes identity fails closed — an Opus-reproduced false
PASS in an earlier draft was fixed), `long_ready.py` (READY poll ≤240 s checked before each poll,
profile 14, closed flavor projection with recomputed invariants, stored original bound via file_sync to
the fixture SHA256). Codex `gpt-6-luna` 6 rounds → PASS; Opus 5.5 VALIDATED (92 tests).

Native unit `baseline-freeze-068f5a98` (`long-ready-native-r1.json`, sha256 bdb4d32bb4a87285284b57fb2fb9da22ef7b5babad22517648f2883a5ce94030): FAILED at the first
audit (INVALID_NONCE_PRIVACY) with persistent `FILES_INVENTORY_CHANGED`. Private diff: six
pre-existing `batch/*-2026-09-27*.log` files were deleted at 02:50 VM time by Kaltura's hourly
DirectoryCleanupBatchLogs job (HH:50). The scanner correctly fails closed when a start file vanishes.
No media API call, no mutation. r2 adds a VM-clock start guard (minutes 00–29, not 23:xx / 00:00–00:14).

# FullHD60 phase B r2 — READY and flavors observed (`long-ready-native-r2.json`, sha256 58f1a71341c2eebad8d10abe1862b0f0e98deeb1b9d16c0d17772ed54c0810bf)

Runner r2 (`run_long_ready_r2.py`): same reviewed guest/pins, new stage, VM-clock start guard
(minutes 00–29 UTC; VM timezone confirmed Etc/UTC). Codex `gpt-6-luna` accepted as best-effort start
guard; Opus 5.5 VALIDATED (11 tests; guard runs in --check and staging).

Native unit `baseline-freeze-18154d61`: `EXISTING_MEDIA_FREEZE_OBSERVATION_COMPLETE` / runner
`OBSERVATION_CAPTURED_NOT_APPROVED`, guest exit 0, stderr 0, unit inactive. All 4 finite audits zero,
Sphinx full-content scans zero, common-end STABLE.

- Entry `0_wzlsbwmy`: READY (first poll), conversion profile 14, msDuration 60067.
- Stored original (`0_laweerrb`, 1920x1080, 60.0 fps, avc1/isom) bound via file_sync: bytes equal the
  fixture SHA256 611e3644…5b07 (end-to-end chunked upload integrity).
- Transcoded flavors, all READY, avc1/isom: params 2 640x360@30, 3 854x480@30, 4 960x540@30,
  5 1024x576@30, 6 1280x720@30, 7 1920x1080@30.
- **Finding:** the published 7.4 default profile does not deliver 60 fps; `delivered_1080p60_flavor_present
  = false`. Decision 7 / protocol plan require the accepted conversion profile to include delivered
  1080p60 (and 360p25) explicitly; a profile decision is needed before timed rounds.
- API metadata only; delivered streams were not decoded/inspected (`stream_inspected=false`).

Identities: run_long_ready_r2.py fde7bef2…48ec, test_long_ready_r2.py c15df243…fa02; guest 75a36006…,
long_ready.py 59874e7e…, privacy_new_logs.py d0978aba… (unchanged from r1).
