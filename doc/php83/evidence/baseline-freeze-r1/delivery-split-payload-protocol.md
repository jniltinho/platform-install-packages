# Native profile split payload protocol (not standalone deployment approval)

Payload frozen: delivery_profile_split.php
SHA256682ec53750b050bf8d7ee9836f91776433442c1da0eb3ad78283ba33dc2e5f3b.
Source and local test identities: delivery-split-payload-freeze.json.

Root's actual read-only preflight observed exact global/default profile1001,
parent0/priority0; tokenizer/recognizer/custom_data SQL NULL and zero length.
This removes those opaque-configuration ambiguities, not partner override or
runtime selection requirements. The payload rechecks all predicates immediately.

Outer executor exclusively creates /var/lib/kaltura-baseline-delivery-split-r1
root:root0700 with intent and reviewed recovery/source/TLS proofs. It invokes
pinned PHP7.4/payload `prepare`, capturing stdout/stderr privately and finitely.
prepare locks1001, checks sole type61 global default and partner102's native
getDeliveryProfileIds empty, and writes all19 original columns to before.json
root0600 exclusively. **Outer validates and fsyncs the file before apply.**
PHP7.4 fflush is not a durability attestation. Whole-row content and any hashes
of potentially private strings must not enter public receipts.

`apply` rereads exact before.json, locks1001 and compares every column; creates
exclusive apply-intent.json and performs native model copyInto/setters/save:
- Existing1001 changes only media_protocols NULL→http plus native updated_at.
- New native allocated ID preserves the copied default=true,parent0 and all
  other fields, except URL=192.168.56.74:8444/hls, media_protocols=https and native
  created_at/updated_at. This is a separate default, not cloneToNew's immediately
  persisted default=false child. No guessed ID and no direct SQL mutation.
- Recheck all19 columns; unexpected deltas fail. Private
  after-before-commit.json is explicitly not proof of committed persistence.
- Original native save/query-cache/object-event/instance-pool lifecycle remains.
  PropelPDO nested transactions keep the two saves inside one outer transaction.
  Native events/cache effects occur before outer commit: SQL rollback does not
  roll back every external effect. No general transactional-cache claim.

After a failed or ambiguous exit, do not re-invoke prepare/apply or delete markers.
Retain private outputs/rows and contain traffic. Root performs bounded read-only
state diagnosis and deliberate coherent-checkpoint recovery as appropriate.
A COMMITTED return still requires outer post-row/source/privacy checks and fresh
HTTP/HTTPS context selection proof. No HLS delivery or full acceptance is claimed.

## Executed local tests

Command: python3 -B tools/php83/baseline-freeze-r1/run_delivery_split_fixture.py
Author and independent Codex reviewer each executed both already-installed,
immutable PHP7.4.3-4ubuntu2.29/PHP8.3.32 images, network none/read-only/cap-drop ALL,
256MiB/64PIDs/60s. Eight cases each, exit0/stderr0. Actual pinned copyInto/setUrl
methods were composed; database/model save and event behavior were explicit
doubles, not live ORM execution. Cases cover preservation/split, retry refusal,
backup drift, unexpected opaque field, competing default, partner override and
unexpected post-save delta with SQL-state rollback. Sources remain frozen.

No VM call by author or reviewer. Independent review is conditional on the
separately owned outer envelope; this document grants no native execution.
