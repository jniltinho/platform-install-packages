# Independent local D1 execution-evidence review

## Verdict

The exported evidence supports the scoped incremental lab milestone: normal APT batch installation reported successful, with workers held and the four final checks true. It does not establish full seed persistence, effective authorization, worker execution, upload/playback or full application acceptance. Suitable for a narrowly scoped Git milestone, subject to the coordinator's final staged-file confidentiality review; not task closure or production publication approval.

## Checks performed

Read all four JSON files in this directory, the pre-D1 checkpoint receipt, current D1 executor validation/execution/finalization logic, and the authenticated C10 source overlay constants. A local Python hash/AST comparison (exit 0) confirmed:

- Current D1 executor SHA256 equals contract pin `98e813f23dbdedf3c1774340d5feddfd685d544cc84719a0e931e976b10a0b8f`.
- Exact exported scope and snapshot bytes match their contract hashes.
- C10 source SHA256 equals D1's pinned `606fd1e82d2a561dc612e0f1a1d9ff0ea5fda3bb297d7b82d14e75b9b513fea1`; all five scope overlay hashes match its source constants.
- Exported C10 terminal bytes match the D1 contract's C-terminal hash.
- Package identity is the executor's exact kaltura-batch 18.20.0-1+php83lab3/all row, artifact SHA256 `c2e36051a86ba4136709f8646db42ab1dbad863d2d830e4896fc75b6ed9e72fa`.
- Snapshot ID agrees with `pilot83/pre-d1-incremental-snapshot-r1.json`; that receipt reports snapshot/resume exit 0, paused full-memory/disk checkpoint, no automatic restore and no full recovery acceptance. This is recorded checkpoint evidence, not an independently repeated restore test.

Execution-result SHA256 is `3956c912ab9bb58f567bbee1100526b6bdaf8cf5c8587c1ce1bbc7475f111ed1`. Its status matches the executor's success constant. Package observation, metadata, input-canary and generated-secret checks are all true; normal APT was attempted; worker hold is true. `failure_contained: false` is consistent with successful execution, not a failed containment claim. Both full-acceptance flags remain false, all three pending obligations remain explicit, and resume is unsupported.

## Confidentiality and evidence limits

The inspected exports contain only bounded statuses, package/source/target identities, public lab paths, checkpoint identifiers and hashes of artifacts/state identities. No credential values, private config bodies, SQL rows, APT logs or secret-derived token hashes are present. Raw private guest evidence should remain excluded from a public/scoped milestone. This review did not independently scan unpublished guest logs or re-observe the machine; privacy success is the pinned executor's exported assertion.

The initial four-file export lacked a separate process-exit envelope. The subsequent process-result.json now records the coordinator SSH pipeline exit 0 with pipefail. Raw runtime/generated-audit/after-dpkg files remain unexported; execution was not independently repeated here. D2 must still validate its own required D1 guest proofs and every original safety prerequisite. No VM, SSH, DB, service operation, install, contract change or Git write was performed for this review.

## Addendum: process envelope and milestone

Reviewed process-result.json and milestone.md. Local recomputation confirms the command's explicit contract hash equals the staged pretty-printed contract bytes, and both recorded guest contract and terminal hashes equal the executor's `json.dumps` serialization of the exported objects. The different staged/guest hashes are therefore explained without weakening any pin. The recorded after-dpkg hash is an external observation, not independently recomputed from an exported package listing. No credentials, private log bodies or secret-token hashes appear in these additions.

The milestone accurately limits the commit to sanitized execution evidence rather than a complete reproducible release and retains full-acceptance/worker/recovery gaps. Its D2 blocker and typo diagnosis are coordinator-reported subsequent findings, not independently established by this D1 review. No objection to these additions for the scoped milestone.
