# Lab conversion profile for Decision 7 (1080p60 + 360p25) — design and read-only inventory

Operator decision (2026-09-29): option 1 — create a lab conversion profile that explicitly delivers
1080p60 and 360p25, identical in the 7.4 and 8.3 labs; mutation reviewed first. Lab only.

## Read-only inventory (`flavor-params-probe-r1.json`, sha256 0c2a764a7182b63c9db40ec5630a76688d1ea5081d7a886b26c26298802657da)
`flavor_params_probe.py` (pinned profile_socket transport, READ ONLY transaction): 21 video/thumb
params, all system (partner 0), every `frame_rate=0` (source) and none with `maxFrameRate` in
custom_data. Partner 102 profiles: 14 Default (params 0,2,3,4,5,6,7,19) and 13 Passthrough_Live.
Short fixture on profile 14: params 2,3,4 READY at 640x360@25 (source raster), 5–7 NOT_APPLICABLE.
So 360p25 is already delivered by the default profile; 1080p60 is not.

## Source basis
`infra/cdl/kdl/KDLFlavor.php:1363-1400` evaluateTargetVideoFramerate: frameRate 0 → source fps capped
by `_maxFrameRate` if >0 else `KDLConstants::MaxFramerate`; 60 is truncated to 30. `KalturaFlavorParams`
exposes writable `maxFrameRate` (api_v3/lib/types/conversionProfile/KalturaFlavorParams.php:197,276).

## Proposed mutation (to be reviewed before execution)
1. Clone system params 7 (HD/1080, h264h 4000, web,mbr,dash) into a partner-102 params
   `lab_decision7_1080p60` with `maxFrameRate=60` (all other writable fields copied).
2. Create partner-102 profile `lab_decision7` = profile 14's params with 7 replaced by the clone.
   Profile 14 and the partner default remain untouched; uploads pass conversionProfileId explicitly.
3. Re-upload both fixtures on `lab_decision7` and verify delivered 1080p60 / 360p25.
Admin KS is required; admin secret/KS are added to every privacy audit pattern set.

## Execution (operator-authorized admin KS) — `lab-profile-native-r1.json`, sha256 44eeac963c7021f2ad6aba1f5fdc2390aa2933ecdf0130393dd904b7529ea7be
`lab_profile.py` (5256e80d…), guest `guest_lab_profile_r1.py` (47080066…) from the reviewed phase-B guest,
runner `run_lab_profile_r1.py` (21bc95ed…) with the VM-clock guard. The partner-102 admin secret is read
in-guest only, tracked (full + 15-char prefix) before first use, and in every audit; never exported.
Reviews: Codex `gpt-6-luna` round 1 CHANGES_REQUIRED (partial-mutation visibility → progress ids exported;
set-based membership kept and documented), round 2 PASS; Opus 5.5 VALIDATED (99 tests; writable fields,
partner-from-KS, isDefault semantics, no other 60 fps cap in KDL); non-blocking suggestions applied
(profile 14 `isPartnerDefault` observed unchanged); Codex round 3 PASS.

Native unit `baseline-freeze-2e9f8e2c`: guest exit 0, `OBSERVATION_CAPTURED_NOT_APPROVED`.
- Created partner-102 flavor params **118** `lab_decision7_1080p60` (clone of 7, maxFrameRate=60, 35 writable
  fields copied) and conversion profile **15** `lab_decision7` = profile 14 params with 7 → 118.
- Profile 14 membership and partner-default flag observed unchanged; isDefault=0.
- Privacy: 5 audits zero (incl. admin secret/KS), Sphinx scans zero, common-end STABLE on attempt 2.
- Consumed once: a rerun aborts LAB_PROFILE_EXISTS. The 8.3 lab must receive the identical definition.
Next: re-upload FullHD60 (and short360) with conversionProfileId=15 and verify delivered 1080p60/360p25.

## FullHD60 phase A r2 on profile 15 — `long-upload-native-r2.json`, sha256 4a0f9059c745e7ff6e17165e30cd3dbeebd47ede1b41787fbca2686809065ca9
`long_upload_r2.py` (f4e0e663…: long_upload + conversionProfileId=15 echoed), guest/runner from the
new-log-aware base with clock guard (`guest_long_upload_r2.py` 8ee9ede7…, `run_long_upload_r2.py` 6aba9742…).
Codex `gpt-6-luna` PASS; Opus 5.5 VALIDATED (103 tests). Started in minutes 00–09 for margin.
Native unit `baseline-freeze-ec2a43b0`: guest exit 0, `OBSERVATION_CAPTURED_NOT_APPROVED`; 112 parts acknowledged
(117,210,794 bytes, 8.344 s), entry **`0_3h92ab2l`** on profile 15, addContent accepted (status 1). All four
finite audits zero **including the batch audit** (new worker logs handled), Sphinx scans zero, common-end STABLE.

## FullHD60 phase B r3 on profile 15 — `long-ready-native-r3.json`, sha256 668bfea1bc804363ac3ab04fd367ffe58d912697fb94a694a4b6864ec56e3b05
`long_ready_r2.py` (0eef7aa4…: entry 0_3h92ab2l, profile 15, params {0,2,3,4,5,6,118}), guest
`guest_long_ready_r3.py` (5c2e41a6…), runner `run_long_ready_r3.py` (ca41fe1d…). Codex `gpt-6-luna` PASS;
Opus 5.5 VALIDATED (106 tests). Native unit `baseline-freeze-b9e18cb6`: guest exit 0,
`OBSERVATION_CAPTURED_NOT_APPROVED`; 5 audits zero, Sphinx scans zero, common-end STABLE (attempt 2).
- Entry READY on profile 15, msDuration 60010; stored original bytes equal the fixture SHA256.
- **Params 118 flavor READY at 1920x1080, 60.0 fps**, avc1/isom, 4191 kbps → `delivered_1080p60_flavor_present=true`.
- Params 2–6 unchanged from profile 14 (360p–720p at 30 fps for a 60 fps source).
- Metadata only (API); delivered streams not yet decoded; the 360p25 requirement is met by the short fixture
  (profile 14 params 2–4 at 640x360@25) and must be re-observed on profile 15 for the timed protocol.

## Stored 1080p60 flavor full decode (step 1 of delivered-stream verification)
`flavor_decode.py` (70a4d15f…): pinned ffprobe/ffmpeg via sealed memfds (file protocol, -xerror, zero exit and
empty stderr), own bounded runner (CPU 150 s, wall 180 s, 2 GiB AS). Codex `gpt-6-luna` 4 rounds (stable read
with dev/ctime; validate bounds/codecs; single meets() rule; projection bounds) → PASS; Opus 5.5 VALIDATED
(111 tests) incl. a host-ffmpeg functional check (synthetic 1080p60 clip accepted, truncated copies rejected).
- r1 (`flavor-decode-native-r1.json`, 5dc3498cdd00…): failed closed at the first audit, FILES_UNDRAINED_TAIL (API/batch log
  bursts; a */15 clear_cache cron exists). No workload ran.
- r2 (`flavor-decode-native-r2.json`, 00ff55ad2722…): privacy zero, then FLAVOR_ASSET_BINDING at flavorasset.get under the
  user KS (no closed diagnostic; entitlement filtering on assetPeer::retrieveById is the unproven leading hypothesis).
- r3 (`flavor-decode-native-r3.json`, sha256 f9811a8b204d4fd242842d34cfdb9279c4145b8de2c02f3a30e29f7e502bb710): guest r2 binds via flavorasset.getByEntryId (proven path) and
  selects exactly 0_j6rfow09; runner r3, VM minutes 16–19. Unit `baseline-freeze-c603dc7e`, guest exit 0,
  `OBSERVATION_CAPTURED_NOT_APPROVED`; 4 audits zero, Sphinx zero, common-end STABLE.
  **Stored flavor 0_j6rfow09 (params 118, v2): 31,441,393 bytes, SHA256 c14cbe84aa6f401c813200a12b427518cd3f0c7dd68fb5b7f4d4bd7f8c9ccf7a;
  full decode h264 1920x1080, 60/1 fps, 3600 frames, 60.010 s, AAC 44.1 kHz stereo; meets_1080p60=true.**
  Note: audio resampled 48→44.1 kHz by the transcode. Not yet delivery: step 2 must fetch the delivered progressive
  bytes and match this SHA256 (plus Range 206); HLS is step 3.

## Step 2 pre-declaration (before consuming stage flavor-progressive-r1)
`flavor_progressive.py` (e17f1f67…) fetches the delivered progressive bytes of 0_j6rfow09 via getUrl → serveFlavor on
pinned HTTPS443 in 30 exact 1 MiB ranges and requires SHA256 = c14cbe84… (the natively decoded stored file). Reviews:
Codex `gpt-6-luna` round 1 CHANGES_REQUIRED (required Content-Length, removed unused PROG_TYPE, final budget check,
credential-encoding explained), round 2 PASS; Opus 5.5 VALIDATED (123 tests; grammar matches the pinned
getServeFlavorUrl/fileName derivation; no KS in serveFlavor path; 1 MiB fits media_get443 IPC).
**Expected-result declaration:** URL tokens, including the fileName segment (≥16 chars, not a credential), are enrolled
for privacy scanning. The lab 443 vhost logs only "%>s %B %D", so the request line is not written there; if the Kaltura
serveFlavor application logs record the path, BATCH_PRIVACY fails closed with PRIVATE_MARKER_LOGGED. That outcome would
be a recorded finding (non-secret route token logged), not a privacy pass and not a byte-equality failure; the public
TRANSFER diagnostic is only written after the hash matched.

## Step 2 native r1 — `flavor-progressive-native-r1.json`, sha256 753d6174063a33d161c6b8127b2956b2b77cc0bf7d5d62bd0a46a947e91400e6
Unit `baseline-freeze-bc2263f7` (VM minutes 16–19): guest exit 2, **PROG_ROUTE** at API_ROUND, before any GET.
URL diagnostic: HTTPS, owned host 192.168.56.74, port 443, no query/fragment/userinfo, **grammar=false**. Privacy:
3 audits zero, Sphinx zero, common-end STABLE. The returned serveFlavor path differs from the grammar observed for
the short fixture; which segment differs is unknown (no closed route-key diagnostic in this module). Next: add a
closed ROUTE_CHECKS (key names only, as thumbnail r3) before the rejection, review, rerun once.
