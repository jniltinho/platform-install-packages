# exp8 isolated artifact regression

Fourteen-patch PHP8.3-only experiment; cumulative Criteria patch replaces the
prior null-alias entry, retaining its fix. Stage once with `stage.sh 74` / `83`.
API: original74 baseline plus original83/exp7/exp8 (four rows). CLI: original74
(12 rows), original83/exp7/exp8 (36 rows). Both artifacts reject PHP7.4 execution.
Use exclusive baseline74 SQL ownership; reports refuse overwrite. No package,
production, release or whole-application acceptance is implied.
