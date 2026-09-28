# Task1.2: smallest next native observation package

Design proposal only. No VM/HTTP/SQL/credential access or implementation in this review. Root is the exclusive VM operator. Do not execute historical media-overlay-v3/run.py: its stage/output are already consumed and it uploads new media. Do not relabel V4 as published-intact.

## Existing contracts to reuse, unchanged

- Target guard: tools/php83/baseline-rehearsal/guest_inventory.py (SHA5ddb8bbbb1b6fdc4e77c93bd7833c31b046196dc44c42f6874de279aed70b0a6), hostname kaltura-php74-baseline, actual address192.168.56.74, rejects .20/.21/.30/.83. Management alias baseline74 in /tmp/kaltura-php74-ssh.conf currently routes127.0.0.1:2201. Refresh actual identity, do not infer it from SSH routing.
- API wire schema and unchanged34/33/33 sequence: tools/php83/baseline-api/protocol.py SHA4587eab6222c2cacc381b6ef100dc557f1afb814250dcc5ba92b3b2ee7eeca34. Existing run.py consumes an externally pinned fixture; it does not discover a correct fixture or attest privacy/environment.
- Preserve transport/deadline and both finite privacy scanners using media-overlay-v3/freeze.json SHAe51d356f651411626d928d9e314cacce0ed392ac61044f40b10209f2dc6ac35a. Its guest.py SHA716786236935d53bbe513275b4cac71b4f9b42b67cf1615d50031d76789b6810 shows reusable network_policy, overlay source/runtime/config comparisons, pre-auth invalid canary, USER-only flow, private_json and finite-window audit. Extract a separately reviewed derivative, not import/call its main.
- Actual V4 stage manifest expected by that guest: cf16bc5c49acbe5863934ba737c72e2b65878c84048389354e79163afeca0cb8. The installed five-source composition must still match it. Public media evidence primary.json SHA c80968c4fb88b677a5fa7466c7fc931a269cdb6accd15456869292dcb8faefdf is prior observation, not present attestation.

## Minimal delta: one untimed observation collector + host environment sidecar

No new upload is needed to freeze the API short-fixture fields. Use only the exact synthetic entry/asset/FileSync join already in primary.json after rechecking ownership/source bytes. Keep unchanged privacy-before-credential sequencing and post-request finite scans. Issue bounded USER media.list/get on that exact entry; export only protocol.FIELDS projection, totalCount with native JSON type, page_size1/page_index1/order_by+createdAt, and source-media hash. Observe media.get version -1,0 and the concrete version separately. Freeze a positive entry_version only after the response and source join; do not substitute asset version2 for entry version merely because the prior report recorded asset_version='2'. Preserve rejected-version outcomes.

Important current omissions: media-overlay-v3 validated totalCount via str but did not export it, exported media_projection but not the final protocol fixture, and never recorded selected conversion profile. Add a fixed allowlisted read of entry conversionProfileId and its tenant/global profile relationship using the native API or a prepared read-only DB query, bounded rows. Export only numeric profile/partner IDs, status and configured flavor IDs needed for reproducibility; no profile customdata, names, arbitrary URLs, secret configuration or raw error body. Record configured profile versus actual generated assets distinctly. Do not choose a new profile just to fill the field. Unknown/missing mapping stays unresolved.

A root host-side read-only VM sidecar must record the actual VM UUID/snapshot reference, box name/version/checksum,4vCPU/8192MiB and disk/controller settings, with guest CPU/RAM corroboration. Existing guest_inventory reports CPUs only; deb/noble/Vagrantfile is intended topology, not current .74 proof. Use exact known VM identity from coordinator records, never select by a broad name substring; no snapshot creation/configuration change in this collector. Package/archive/source/runtime identities join existing receipts; private config equality remains guest-memory-only and returns booleans, not secret digests.

Store observation separately from approved freeze. A tiny pure assembler can validate/merge environment sidecar, typed API fixture, source/runtime/overlay identities and profile observation into a new public contract, with baseline_label=PUBLISHED_PHP74_WITH_APPROVED_PRIVACY_OVERLAY and full_acceptance=false. Freeze its bytes only after independent receipt review. Do not expand protocol.validate_fixture's exact field set: keep its eight top-level fields unchanged, attach environment/profile in a separate envelope.

## Fixtures and boundaries

Existing source media in sibling artifacts/baseline-media-r1:
- short360.mp4:1511134 bytes, SHA612d179c75f8f2374b7ac59c2dd7edba65e38eb357b870e8ad8c2e83d63b5473.
- fullhd60.mp4:117210794 bytes, SHA611e3644fb56fc1f12ddccd1d889258d249e36a4eca445451c16d13f5c5f5b07.
- Independent technical validation receipt SHA77dbb15428b29ca23af63752c85c36a3e8217fec718f4db2b661bfac221d6151.

The existing short-only guest has2MiB source-delivery bound and30s transfer deadline; do not run117MiB fullhd through it unchanged or silently relax bounds. Long-media upload/worker/playback remains the next separately bounded execution, not part of this read-only freeze delta. HTTPS/HLS/decode and two warmups/five measured rounds remain required by Decision7; this proposal neither adds gates nor completes them. Baseline-api/run.py alone is not the orchestration/privacy wrapper for those rounds.

## Required local validation before root execution

Pure tests: preserve typed string/int distinctions; reject fixture/source/runtime/overlay drift, wrong target, wrong partner/profile join, zero/multiple source matches, secret-bearing public fields and incomplete privacy windows; explicitly test entry-version versus asset-version confusion. Reuse baseline-api test_protocol.py and test_transport.py; run new derivative tests independently. CLI failures stay NOT_EXECUTED/INCOMPLETE. Root later stages only frozen reviewed files into new exclusive paths and captures bounded sanitized exit/results. No existing receipt overwritten, no package/source/log-policy change, no credential export, no performance claim from this untimed observation.

Implementation correction: the pinned protocol has eight top-level fixture keys, not seven. This fixes the plan’s counting error without changing the protocol. Read-only observation may retain unknown snapshot/box hashes as null; such an observation is not an approved freeze or recovery proof.
