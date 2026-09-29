# Thumbnail native r2/r3 — THUMB_ROW root cause and THUMB_ROUTE diagnosis

Date: 2026-09-28. Lab only (Baseline74 VM `9e954729-16f3-4eda-9db5-b94e5ada9e44`,
192.168.56.74). No `.20`, no production, no package/CI change. Partial evidence for
task 1.2 / 5.5; closes no checkbox. Coordinator/author: Claude Code (Opus 5.5).

## r1 failure (preserved)

`thumbnail-native-r1.json`, unit `baseline-freeze-5df47596`: `THUMB_ROW`, exit 2.
r1 files and receipt are unchanged; r2/r3 are derived, never overwrite r1.

## Root cause of THUMB_ROW (source + native)

r1 bounded `KalturaThumbAsset.size` to 1024 assuming the API doc's "KBytes". The
pinned source (server-Rigel-18.20.0) stores thumbnail size in bytes via `filesize()`:
`alpha/apps/kaltura/lib/myEntryUtils.class.php:68`,
`alpha/apps/kaltura/lib/batch2/bcdl/kBusinessPreConvertDL.php:220`,
`alpha/apps/kaltura/lib/batch2/kFlowHelper.php:1233`.
Native r2 confirmed: one READY asset `0_zobmj2vn`, 640x360 jpg, version 12,
thumbParamsId 19, `size_API_bytes` 45227.

## r2 — `thumbnail-native-r2.json`

Byte bound (<=1 MiB) and closed `ROW_CHECKS` (booleans + fileExt enum) before any
row rejection. Unit `baseline-freeze-e16b8e67`, stage
`/var/lib/kaltura-baseline-thumbnail-r2`: passed rows/selection, failed
`THUMB_ROUTE` (URL HTTPS, owned host, port 443, no query/fragment/userinfo). No GET.
Finite privacy scans complete and zero; common-end STABLE; unit inactive.

## r3 — `thumbnail-native-r3.json`

Adds closed `ROUTE_CHECKS` (booleans + allowlisted path key names, never values).
Unit `baseline-freeze-ec290fc3`, stage `/var/lib/kaltura-baseline-thumbnail-r3`:
`THUMB_ROUTE` with `ROUTE_CHECKS` = base/prefix true, pairs even, keys
`thumbAssetId`, `v`, `ks`. getUrl embeds a server-generated download KS
(`asset.php` getDownloadUrlWithExpiry: `isKsNeededForDownload()` true -> `/ks/<KS>`).
The guard correctly refused a credentialed GET. No GET, no decode. Privacy scans
complete and zero; unit inactive.

## Identities (sha256)

| File | sha256 |
|---|---|
| thumbnail_r2.py | 0de92151590477760453241da84f46fce75dcbe38fb849c9763edd9d39153e16 |
| prepare_thumbnail_r2.py | cb0590734aba87570316f5fe5610e2c4a35ffa69333f01d0bd119a708986eaae |
| guest_thumbnail_r2.py | b7ba358be2855a27307765ab5b1e9866ddbcd1e50a0390bcc8907a48258c17df |
| run_thumbnail_r2.py | e81fad649275370e94b8e0c3d524f5866bc59eab17e1c156e1a8a8f610c2837a |
| thumbnail_r3.py | 842f989ff27e58007a84208ec74892f9f6c1b5a6e282501a0fb56822443c952c |
| prepare_thumbnail_r3.py | e330f6118ce4d7d809f985566c9822666b8091b12b92da4397f27de0f7c013cb |
| guest_thumbnail_r3.py | 07c761a2358cf77c8a32e5c56ba0468ee32a135412e9391f6c8476ad78871236 |
| run_thumbnail_r3.py | 2ae4c33c183163f79861d33affc1301ee5aa98e6d5be1101d6fad19f33780f3e |
| test_thumbnail_r3.py | 5a8852eadb6489b112bf746cb01f3f5f8df6e81cf1b2c0b7637f598e087d07ae |
| thumbnail-native-r2.json | 7b55cae73700982643a632d2e6125b2dddcc90e1a0f00e5d21f39a07da416384 |
| thumbnail-native-r3.json | fc4b4ad5d2fd83e022d6d85c77409084d6da8ff906882f1202a81c07b3ebea61 |

Split proof pin reused: f6a09da7879e10e8fbc288dc56927a1c514169cf3f5fc545c9dd414d7ab9fd13.
Commands: `run_thumbnail_rN.py --check ...` (READ_ONLY_PREFLIGHT_PASSED) then one
`--output <new dir>` execution each; no retry, no stage reuse, HLS not repeated.

## Local tests (harness only, mocks excluded from runtime acceptance)

`python3 -B -m unittest test_thumbnail test_thumbnail_r2 test_thumbnail_r3`: 32 tests OK
(author and Opus validator both ran it).

## Independent reviews (source-only; not execution evidence)

| Case | Executor | Result |
|---|---|---|
| r2 | Claude CLI `sonnet` | PASS (non-blocking test gaps; two added) |
| r2 | OpenCode `opencode/muse-spark-1.3-contributor-free` | NOT_EXECUTED: timeout 600s twice, no output |
| r2 | Cursor `agent` | BLOCKED: authentication required; removed by operator |
| r2 | Codex `gpt-6-terra` | BLOCKED: model unsupported with ChatGPT account (HTTP 400) |
| r3 | Codex `gpt-6-luna` | PASS |
| r3 | Claude subagent Opus 5.5 (validating Codex) | VALIDATED; hashes/tests confirmed |
| r3 | Claude CLI `sonnet` | PASS |
| r3 | OpenCode Muse | NOT_EXECUTED: stopped at operator request |

## Remaining limitations / open decision

- No thumbnail GET, JPEG decode or dimension match has executed natively.
- Whether to GET a URL carrying a Kaltura-generated, entry/asset-scoped download KS
  (or serve via API POST, or first explain why the KS is required) is an operator
  decision; the "no credentials in GET" rule is not relaxed here.
- UI/Admin/KMC, FullHD60 upload, timing protocol and remaining 1.2 cases stay open.

## Why getUrl embeds a download KS — read-only probe (`thumb-ks-reason-r1.json`)

`tools/php83/baseline-freeze-r1/thumb_ks_reason.py` reuses the pinned `profile_socket.py`
transport (sha256 9735aad6…; guest-side password, DB identity check, READ ONLY
transaction, 4 aggregate SELECTs) and exports counts/booleans only. Guest guard
re-verifies installed `entry.php`, `asset.php`, `PermissionPeer.php`,
`accessControl.php`, `thumbAsset.php` against the pinned archive. Exit 0, stderr 0.

Observed: partner 102 has `FEATURE_ENTITLEMENT` active (status 1), which alone
makes `asset::isKsNeededForDownload()` true. The entry is not secured: moderation
normal, no future start / near end date, own live access control without rules.
So every getUrl for this partner's assets embeds a server-generated download KS by
design. How partner 102 acquired entitlement (installer default vs lab overlay) is
not yet established. Local tests: `test_thumb_ks_reason` 5 OK. Limitations:
compressed ACL rules are not decoded (rules column empty/`a:0:{}` check only);
timestamps compared with DB `NOW()`.

## Apache logging consequence (read-only config check, Baseline74)

Packaged Kaltura vhost logs `CustomLog /opt/kaltura/log/kaltura_apache_access_ssl.log
vhost_kalt`, and `vhost_kalt` includes `%r` (full request line). A GET of the
getUrl path therefore writes the generated download KS into the access log; the
API-log privacy overlay does not cover this. The config comes from the packaged
template (`@LOG_DIR@`), so the same behavior is expected on stock 7.4 installs;
production `.20` was not inspected (out of lab scope). Any thumbnail GET via getUrl
must treat this as a recorded privacy finding; operator decision pending.

## r4 — operator-approved GET with generated download KS (`thumbnail-native-r4.json`)

Operator decision (2026-09-28): GET via the real getUrl route and record the
access-log exposure as a finding. r4 accepts exactly one trailing `/ks/<token>`
(charset `[A-Za-z0-9_=-]`, 16–2048) after optional pv/ev; own session secret/KS,
`%`, query and foreign origin still rejected; DECODE exported as diagnostic.

Native unit `baseline-freeze-128d02f3`, stage `/var/lib/kaltura-baseline-thumbnail-r4`:
- GET HTTP 200, one `image/jpeg`, 45227 bytes (= API size, confirming bytes).
- Pinned ffmpeg strict full MJPEG decode: 640x360, 1 frame, API dimensions match.
- Privacy: FAILED at MEDIA_PRIVACY with `FILES_REWRITTEN` (scanner `REWRITTEN` in
  files_initial of audits 3 and 4): a scanned log file was rewritten/rotated during the
  finite window, so the scan is INCOMPLETE. Audits 1–2 had zero matches. The expected
  access-log KS finding is therefore neither confirmed nor excluded. Not a privacy pass.
- guest exit 2, stderr 0, unit inactive. No retry.

Identities: thumbnail_r4.py f389bb35737957fefc3518a7b081ee81c0ca81924f91cb7caf928ac8aae8a686,
prepare_thumbnail_r4.py 5a6eb7db34274e3b128cbde2532674a8913b623a0e4a1768008c75109d69d3e5,
guest_thumbnail_r4.py 4482e7fac847264b5b238fb9a44c7ed14619715feb81445e12fb685019a09f97,
run_thumbnail_r4.py 43bf607dca58d0c22b8fb68fc3e67ff1ad8bd504ce218c3714084173007710f0,
test_thumbnail_r4.py be4283bf3b6a64a79fc3230243cc122d548628b75499592316fa35c459e11ae3,
thumbnail-native-r4.json bc4c723a17b7aad76c55cb35df5faa036b22f1261a9004d7f5541133ec32d882.
Local tests: 53 OK (thumbnail r1–r4 + ks reason). Reviews: Codex `gpt-6-luna` PASS,
validated by Claude subagent Opus 5.5 (hashes, byte-identical guest rebuild, no
redirects, no false-PASS path). Neither is execution evidence.

Open: identify which log was rewritten (rotation vs application) and rerun privacy
audit in a quiet window; decide handling of the vhost_kalt `%r` KS exposure.

## r4 FILES_REWRITTEN root cause (read-only, Baseline74)

The append-window scanner (`baseline-rehearsal/privacy/append-window-v1/scan.py:72`)
raises `REWRITTEN` when a file keeps its size but changes mtime. VM clock is +3m55s vs
host; r4 ran 02:01:28–02:01:45 VM time. `/opt/kaltura/log/sphinx/data/binlog.meta`
(11 bytes) and `binlog.001` (0 bytes) were both rewritten at 02:01:30.92 inside that
window (sphinx `binlog_path` is under the log tree, `binlog_flush = 1`). This is a
Sphinx RT binlog data write with constant size, not a log leak. Earlier passing
rounds did not coincide with a Sphinx binlog write, so the risk applies to every
round. Handling these binary index files (separate full-content scan vs exclusion)
is a privacy-protocol decision; nothing was changed.
