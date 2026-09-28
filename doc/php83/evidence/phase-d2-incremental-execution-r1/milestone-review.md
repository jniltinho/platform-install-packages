# Independent scoped milestone review

## Verdict

The inspected public repair code/tests/template and sanitized execution receipts are suitable for a focused milestone recording **successful exact cache-placeholder repair followed by a contained failed D2 installation**. They do not support successful Elasticsearch installation, full application acceptance, recovery rehearsal or task closure. Preserve rejected repair R1, the original D2 guard rejection and failed transaction evidence; do not replace their outcomes with later success claims.

## Evidence consistency

Read all JSON files in cache-write-config-repair-r1/execution and this directory, plus pilot83/pre-d2-incremental-snapshot-r1.json, pre-d2-incremental-snapshot-r2.json and failed-d2-incremental-snapshot-r1.json. Local hash/serialization checks exited 0:

- Repair R2 contract pins the reviewed current helper `de3aa641b31f4612d993b671d81aa21ae46002aee5b2cfb7e513433b201f4ad0`; historical R1 remains `fda04e325fa32e4f3e69cf1069892dfacf7e86b92b9d65e3d9ef15a204dc77d4`.
- Both D2 contracts pin the unchanged executor `88aca9759756e37b15d190ac84dadf0b065608bbe257c753ec746b2c15751efb`.
- Exact repair snapshot and both D2 snapshot-proof bytes match their respective contract hashes. Snapshot IDs agree with external pre-D2 checkpoint receipts: initial c721bf36-3bb4-4003-9f88-f9e6c2fc844d and cache-repaired d0cdbfcb-84dc-4436-afae-b2228bac7345.
- Failed terminal serialization reproduces its recorded hash `9f65070e9a2075ae9734ae898bcbc14bc43c31ac4a16a1c9e2bc85f14b6b92ae`.

Repair result reports exact config replacement, privacy and held-worker checks, exit 0 and externally restored services. The helper itself does not restore services: services_restored and executor_exit are coordinator observations added to the export, not helper-generated fields.

The initial D2 endpoint rejection explicitly preceded RUN/APT. After repair, a read-only guard passed and a new checkpoint was recorded. Actual D2 then failed at source line 226, the bounded normal APT invocation. Package iF status, failed Elasticsearch and inactive Apache/Monit are consistent with an unsuccessful transaction. Final checks include privacy and private ES-log capture; failure_contained and worker_hold_preserved are true. These containment checks do not turn the failed install into acceptance. The source-pinned prestart receipt proves configuration preparation, explicitly not service start.

Recorded diagnosis is AccessDeniedException for the ES log subtree beneath private root:www-data01770. Listed metadata supports the permission explanation, but this local review did not independently read the private ES log or inspect process supplementary groups. Do not weaken parent confidentiality to fix it. A separately reviewed relocation remains future work.

Failed-state checkpoint 899a5799-b35a-45e8-b069-6075ecc9b1fb records snapshot/resume exit 0. All checkpoints keep restore_automatically and full recovery acceptance false. No receipt reviewed here records a subsequent restore, and this review does not authorize one.

## Confidentiality and limits

Inspected exports contain bounded outcomes, artifact/state identities, public template token, fixed lab paths, modes and checkpoint IDs. No credentials, private config bodies, arbitrary SQL rows, raw daemon/APT logs or secret-token hashes were found. Repair pre/post hashes are demonstrably hashes of public-template-derived cache configuration, not authentication secrets. Keep raw guest backups/logs and memory/disk snapshot payloads out of the milestone. A coordinator must still review the actual staged-file set; this review is scoped to the named files, not every unrelated worktree change.

Independent repair R2 validation previously executed all 15 tests successfully. This follow-up performed local evidence/source/hash checks only: no VM, SSH, database, services, package action, Git operation or restore. Full seed persistence, effective authorization, worker/media flows and final acceptance remain pending.
