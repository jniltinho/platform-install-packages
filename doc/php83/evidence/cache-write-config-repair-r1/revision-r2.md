# R2 exact existing directory trust

R1 preserved unmodified and not executed. Independent reviewer identified existing configurations directory root:root0775, so its strict parent check would block before any repair. Root read-only metadata confirmed all other parents root:root0755/no xattrs; group0 explicit members empty, nonroot primary gid0 count0.

New helper `cache-write-config-repair-r2.py` accepts only the exact `/opt/kaltura/app/configurations` directory root:root0775 after live supplementary and primary group0 exclusivity checks. All parents must remain actual directories/root-owned/no xattrs. Every other directory remains non-group/other-writable. No chmod, ACL change, source/package rewrite, broad group permission exception or symlink acceptance.

RUN remains original exclusive repair-r1 journal since no repair attempt occurred; either derivative cannot resume another. Root stages distinct helper filename, updates executor hash and contract hash, preserves staged R1. Command names change to R2 only; other protocol unchanged. 15 Python tests PASS, including wrongpath/mode/gid/worldwrite/ACL/symlink and unauthorized root-group membership negatives. Review pending; no VM operation by author.
