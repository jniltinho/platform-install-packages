# Prepared SQL display policy — preparation, not installed

Only KalturaStatement's DEBUG representation changes: retain queryString
(placeholders/table/column structure) plus ordered bind type metadata; do not
interpolate bound values into the displayed SQL. Actual bindValue/execute,
return values, old interpolation for dry-run and monitorDatabaseAccess remain
unchanged. Types use gettype, not casting/serialization/magic methods.

Original and exp14 source are independently archive-pinned and patches strictly
replayed. Seven local transformation guards pass. Independent Codex/exp9 executed the seven tests and verified the concrete prepared CRUD path; actual Claude source/probe review and native execution remain pending.
No artifact or installed source changed. This is separate from caller-frame-v1.

Limits: raw literals already present in queryString are not sanitized. Three
other PDO entry points continue raw display. bindParam is inherited and is not
newly introspected; existing positional bookkeeping is deliberately not repaired
here. No universal SQL privacy claim. Monitor source inspection shows only
operation/table/time/length in its output record, not the SQL body; it remains
unchanged. New runtime tests must prove bound values/DB effects and fresh real
media window must determine whether another emitter remains.

## Prepared CRUD attribution
Independent source read follows BaseentryPeer doInsert/update into BasePeer
prepare/populateStmtValues/execute (lines 293,406/409/411 and 561/596/598),
with KalturaPDO constructor selecting KalturaStatement. Its line-61 DEBUG
interpolates bound data. Graph full generation 2026-09-25T12:19:00Z coverage
for relied source files reported metadata_match/no_recorded_issue; method lookup
misses were resolved by direct source read, not treated as absence proof.

Native probe planned: actual full Statement class over native PDO/MySQL with
private database only; ten INSERTs (bound/array × serialized KS, quotes, null,
integer, boolean), two repeated UPDATE/cache controls, dry-run, exception, and
explicit inline-literal negative control. Logging/cache/monitor are named seams,
not a full application bootstrap. Original74 and exp14 returns differ historically;
compare before/display on the same engine, never invent cross-engine parity.

## Executed phase and validator correction
Codex primary and actual Claude repeat each executed four native processes with
14 INSERT/UPDATE rows per process, plus dry-run/error/inline controls. All exits
zero, native stderr/diagnostics empty, eight private DB units stopped/inactive.
Stored bytes, native returns/cache and monitor arguments match within each PHP
engine; all four raw stdout channels repeat byte-for-byte. Four broad runtime
snapshots match. Stages/private datadirs remain intentionally retained.

Claude prep ran seven tests and warned about positional arrays with named
placeholders. The probe was corrected to named arrays before any native run;
independent Codex microreview ran 17 tests. The fixture now uses minimal
track_entry(id,ks), six values including a direct synthetic KS and serialized
fixture: twelve INSERTs and two UPDATEs. Actual caller is BaseTrackEntryPeer,
not the earlier over-specific entry/CUSTOM_DATA attribution.

Independent comparator review found Python bool/int equality and unvalidated
stderr channels. R1 files/results are preserved; R2 uses canonical typed JSON,
requires empty stderr/diagnostics, and strict cleanup exit integers. Thirty-six
local tests pass; both untouched native reports revalidate without VM reruns.
`repeat-exact.json` records exact native repeat channels, not just semantic parity.
No installed source has changed as part of this experiment.

Final tiny follow-up also uses typed JSON for explicit null74/bool83 expected returns, rejecting identical true→1 corruption in both83 cohorts. No native rerun was needed.
