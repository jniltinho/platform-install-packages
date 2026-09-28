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
