# Independent R2 delta review

**Approved for the coordinator's narrowly authorized lab repair, conditional on all runtime guards. No remaining source blocker found.**

Verified helper SHA256 `de3aa641b31f4612d993b671d81aa21ae46002aee5b2cfb7e513433b201f4ad0` and tests `e7b0c3cfe3901b183f21023fafcbb35728251b14a525fd8dc548f220a09f6245`. Compared complete R1/R2 diffs: production changes are only grp/pwd imports and the exact known parent exception. Target/pre/post pins, mutation, private journal, authorization, snapshot, held-worker, confidentiality and no-resume behavior remain unchanged.

The exception is restricted to `/opt/kaltura/app/configurations`, uid/gid 0 and exactly 0775. Supplementary root-group members must be a subset of root, and every enumerated primary gid-0 account must be named root. Directory type/root ownership and absence of xattrs remain mandatory, including for that exception. Wrong path, gid, mode, world-write and symlink cases fail. Other ancestors retain their strict no-group/other-write requirement. This matches the coordinator-confirmed local root-only group and parent metadata without changing permissions.

Independently executed `PYTHONDONTWRITEBYTECODE=1 python3 tools/php83/pilot83/test_cache_write_config_repair_r2.py -v`: exit 0, **15 tests PASS**, including unauthorized supplementary/primary membership, ACL/xattr and parent negatives plus all original transformation/private-file/scope tests. No source edits, VM, SSH, DB or service operations. Whole guest apply/failure paths remain source-reviewed rather than integration-executed; R1 review limitations still apply.

Stage the revised helper and updated externally pinned contract, not R1. Existing repair RUN must remain absent: its unchanged exclusive path does not authorize reuse. Actual success still requires the terminal's privacy and held-worker checks and the unchanged D2 guard afterward. This is not full acceptance or a cache-service runtime claim.
