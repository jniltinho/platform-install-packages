# Independent source-fixture validation — baseline-media-r1

**Status: PASS.** Source-fixture checks only. NOT application acceptance. NOT cross-build reproducibility. No regeneration, upload, VM, or network.

## Case / executor / reviewer

- **Case:** `baseline-media-r1-source-fixture-independent-validation`
- **Executor:** Cursor Agent (Composer)
- **Reviewer:** Cursor Agent (Composer) — independent of freeze_media generation author run
- **Started (UTC):** 2026-09-26T16:28:40Z
- **Ended (UTC):** 2026-09-26T16:30:00Z

## File / runtime identities

- Worktree: `/home/nilton/Projetos/nilton/NOVOS/platform-install-packages-php83`
- `git HEAD`: `85ce77ba71049c4f79f975aa69137c97790e89ec`
- Host: `linux-desktop` / user `nilton`
- `freeze_media.py` sha256 `e1ab367ca3cdf6dea452a99bbb19a85725b33d3900889b57d1057a4baaf38f69`
- Recorded manifest `media-generation-r1-manifest.json` sha256 `1a356b492f82299f3f5881a86469302b3a01342c78af168baafb7b457820e0fe` (status `SOURCE_FIXTURES_VALIDATED_PENDING_INDEPENDENT_REVIEW`; not overwritten)
- Artifact dir: `/home/nilton/Projetos/nilton/NOVOS/platform-install-packages-php83-artifacts/baseline-media-r1`
- Artifact `manifest.json` sha256 `1a356b492f82299f3f5881a86469302b3a01342c78af168baafb7b457820e0fe` (read-only; not overwritten)

## Tool identities (exact executable hashes)

| Tool | Path | Observed sha256 | Recorded sha256 | Match | Version line | Exit |
|---|---|---|---|---|---|---|
| ffmpeg | `/usr/bin/ffmpeg` | `ed16af623947494a72e284b6eb8ff225f2da22b38b5d5069c2fd4b4ba3384e41` | `ed16af623947494a72e284b6eb8ff225f2da22b38b5d5069c2fd4b4ba3384e41` | YES | `ffmpeg version 6.1.1-3ubuntu5 Copyright (c) 2000-2023 the FFmpeg developers` | 0 |
| ffprobe | `/usr/bin/ffprobe` | `272f6ebc634a63d9c8b4ca68e964119d980f25154e5aa2c35e5487da48e9a58f` | `272f6ebc634a63d9c8b4ca68e964119d980f25154e5aa2c35e5487da48e9a58f` | YES | `ffprobe version 6.1.1-3ubuntu5 Copyright (c) 2007-2023 the FFmpeg developers` | 0 |

Full ffmpeg/ffprobe configuration dumps omitted; identity is path + sha256 + first version line.

## Decision 7 expectations checked

- `short360`: 10s, 640×360, 25 fps, H.264, AAC 48 kHz stereo, **250** decoded video frames
- `fullhd60`: 60s, 1920×1080, 60 fps, H.264, AAC 48 kHz stereo, **3600** decoded video frames
- Duration tolerance: at most one video frame + one AAC frame → `Fraction(1,fps)+Fraction(1024,48000)` on video, audio, and container durations

## Commands, exits, results

### short360

- Path: `/home/nilton/Projetos/nilton/NOVOS/platform-install-packages-php83-artifacts/baseline-media-r1/short360.mp4` (access: readable)
- Hash command: `sha256sum /home/nilton/Projetos/nilton/NOVOS/platform-install-packages-php83-artifacts/baseline-media-r1/short360.mp4` → exit implied 0; observed `612d179c75f8f2374b7ac59c2dd7edba65e38eb357b870e8ad8c2e83d63b5473` / 1511134 bytes
- Recorded: `612d179c75f8f2374b7ac59c2dd7edba65e38eb357b870e8ad8c2e83d63b5473` / 1511134 bytes — **sha match: YES; bytes match: YES**
- Probe wrapper (180s bound): `timeout 180 /usr/bin/ffprobe -v error -count_frames -show_streams -show_format -of json /home/nilton/Projetos/nilton/NOVOS/platform-install-packages-php83-artifacts/baseline-media-r1/short360.mp4`
- Probe exit: **0**; elapsed 0s; window 2026-09-26T16:28:53Z → 2026-09-26T16:28:53Z
- Probe stderr: empty
- Probe summary: video `h264` 640x360 avg=25/1 r=25/1 nb_read_frames=250 dur=10.000000; audio `aac` 48000Hz ch=2 (stereo) dur=10.000000; format dur=10.000000 size=1511134
- Predeclared tolerance: `23/375` s; expected decoded frames: 250
- Checks: **PASS** (9/9)
- Fixture row: **PASS**

### fullhd60

- Path: `/home/nilton/Projetos/nilton/NOVOS/platform-install-packages-php83-artifacts/baseline-media-r1/fullhd60.mp4` (access: readable)
- Hash command: `sha256sum /home/nilton/Projetos/nilton/NOVOS/platform-install-packages-php83-artifacts/baseline-media-r1/fullhd60.mp4` → exit implied 0; observed `611e3644fb56fc1f12ddccd1d889258d249e36a4eca445451c16d13f5c5f5b07` / 117210794 bytes
- Recorded: `611e3644fb56fc1f12ddccd1d889258d249e36a4eca445451c16d13f5c5f5b07` / 117210794 bytes — **sha match: YES; bytes match: YES**
- Probe wrapper (180s bound): `timeout 180 /usr/bin/ffprobe -v error -count_frames -show_streams -show_format -of json /home/nilton/Projetos/nilton/NOVOS/platform-install-packages-php83-artifacts/baseline-media-r1/fullhd60.mp4`
- Probe exit: **0**; elapsed 10s; window 2026-09-26T16:28:53Z → 2026-09-26T16:29:03Z
- Probe stderr: empty
- Probe summary: video `h264` 1920x1080 avg=60/1 r=60/1 nb_read_frames=3600 dur=60.000000; audio `aac` 48000Hz ch=2 (stereo) dur=60.000000; format dur=60.000000 size=117210794
- Predeclared tolerance: `19/500` s; expected decoded frames: 3600
- Checks: **PASS** (9/9)
- Fixture row: **PASS**

## Verdict

**PASS** for source-fixture independent validation only.

- Application acceptance: **false / NOT claimed**
- Cross-build reproducibility: **false / NOT claimed**
- Baseline workload / upload / READY / delivery: **NOT_EXECUTED**

## Limitations

- Source-fixture validation only; does not prove upload, READY, flavor delivery, HLS, or installed-AIO baseline acceptance.
- Does not claim cross-build byte reproducibility of fixtures.
- Did not regenerate media, touch VMs, or use network.
- Prior media-generation-r1-manifest.json and artifact sources were not overwritten.
- Full ffmpeg/ffprobe configuration lines omitted from public summary by design; executable sha256 + first version line recorded.
- Concurrent localtest/newdeadline work was not edited or executed in this case.

Machine report: `doc/php83/evidence/baseline-protocol/media-independent.json`
