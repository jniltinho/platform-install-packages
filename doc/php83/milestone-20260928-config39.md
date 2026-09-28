# PHP 8.3 lab milestone — 2026-09-28

Branch: proposal/migrate-kaltura-php83. Scope: reviewed isolated lab diagnostics,
not release acceptance. OpenSpec progress remains 4/51 (1.6,5.1,5.2,5.3).

## Verified progress

- Permission reuse fixture: author and independent reviewer each passed35methods
  and25invariants tests; offline PHP8.3.32 executed successfully. Peer/database
  doubles mean this is not SQL or full effective-permission acceptance.
- Config39 source mapping contract: independent19test pass and identical regenerated
  contract SHA2566fb193c1648a663069fceb44b529b78629d7f9659f9ebcca912d13b77f0168e7.
- Config39 collector: independently reviewed12tests before coordinator execution.
  Actual lab read-only transaction completed39preparedSELECTs,39unique rows,
  326declared-column comparisons matching,0mismatches and9matching hostnames.
  All114runtime file identities and private inputs remained unchanged. Private
  data was compared in memory, not exported.
- Collector SHA256f67a38a3bd380a0203ab4b49bc55282a2effdbfbea18bc16b041fb585be0512e.

## Open scope and next step

Sixteen field dispositions and complete defaults/save/related-permission behavior
remain outside this observation. No full persistence or application acceptance is
claimed. The operator approved incremental real installation and functional tests
in the isolated lab, with detailed final acceptance retained. Batch/Elasticsearch
incremental executors are implemented but require independent review and concrete
snapshot/target/package/privacy/hold preconditions before execution. Workers stay
held until a separately reviewed functional step. Production/publication remain
separately gated.

This first checkpoint records verified progress only. Bulk local evidence and code
are intentionally not swept into this commit: review and package them into coherent,
reproducible, secret-free follow-up milestones. No raw transcripts or private
configuration belong in Git. Existing unrelated edits remain untouched.
