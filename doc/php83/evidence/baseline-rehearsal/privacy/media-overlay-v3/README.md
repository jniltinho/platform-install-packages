# Untimed baseline media rehearsal — bounded real success

Actual executor: Codex, `.74` only, PHP 7.4.33/apache2handler with approved
**lab privacy overlay V4**, not intact published application sources.
Guest exit **0**, status `SYNTHETIC_MEDIA_READY_AND_SOURCE_DELIVERY_OBSERVED`;
wrapper stderr zero, cleanup inactive (state query exit 4). Provider probe removed.

Real sequence: rejected invalid-secret nonce → synthetic tenant-102 USER
session → rejected admin escalation → upload one pinned technical ten-second
fixture → READY after 25 polls → owned media.list → original-asset HTTP bytes.

- Entry `0_wzmt2sfy`; original asset `0_ewuu0o46`; version `2`; FileSync `315`.
- Source, stored original, and delivered HTTP bytes all SHA256
  `612d179c75f8f2374b7ac59c2dd7edba65e38eb357b870e8ad8c2e83d63b5473`.
- Strict entry/partner and asset→entry/partner bindings passed.
- All five installed source hashes/UID/GID/mode stayed unchanged before/after.

## Finite privacy windows actually observed

| Phase | Files | File bytes | Pattern counts | Journal new records |
|---|---:|---:|---|---:|
| Invalid nonce | 416 | 14,004 | `[0,0]` | 0 |
| USER/admin-negative | 416 | 27,720 | `[0,0,0,0]` | 0 |
| Upload/READY/list/source HTTP | 416 | 7,145,043 | `[0,0,0,0]` | 0 |

Media/USER patterns are full secret, secret prefix, full KS and KS prefix;
values stayed private in guest memory. Each journal scan read 4,173 bytes
including anchors, **not 4,173 bytes of new events**; all pattern counts zero.
Files and journal reported complete finite windows, post-journal file rescan
covered the same offsets, uncovered tails zero. No sink was removed or log level
lowered. This is bounded absence in these windows, never universal privacy or
coverage of future writes/historical logs.

## Provenance and limits

This phase changes only fresh stage paths and the exact installed V4 manifest
pin from frozen media V2. Independent Codex/exp9 review executed 24 tests and
confirmed eleven hashes before the native run. Actual Claude independently
repeated the prerequisite SQL display and caller matrices; **it did not repeat
this full media upload**. Final receipt review is recorded separately.

V2's full KS/prefix counts `3+3` remain a real failure; V1's Incomplete remains
indeterminate. Neither is overwritten or relabeled as success. V4 repairs
prepared SQL log display plus caller attribution, while preserving SQL effects.
The new and older synthetic uploaded entries/assets remain retained; no deletion
or metadata rewrite was performed.

This is NOT a benchmark, baseline-100 measurement, HTTPS/HLS/decoded playback,
full worker acceptance, or functional PHP 8.3 AIO acceptance. Direct PDO raw SQL
and inline SQL literal negative controls remain explicitly outside the tested
prepared-bound-value privacy fix. No package/ZIP/main/tag/release was modified.
