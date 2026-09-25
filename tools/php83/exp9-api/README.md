# exp9 isolated artifact regression

Sixteen-patch PHP8.3-only experiment. Adds native boolean-return repairs to
PropelPDO::setAttribute and KalturaStatement::bindValue/execute over exp8.
The null-to-bool result change is intentional, not exact legacy return parity.
Stage once with `stage.sh 74` / `83`.
API: original74 baseline plus original83/exp8/exp9 (four rows). CLI: original74
(12 rows), original83/exp8/exp9 (36 rows). Both artifacts reject PHP7.4 execution.
Use exclusive baseline74 SQL ownership; reports refuse overwrite. No package,
production, release or whole-application acceptance is implied.
