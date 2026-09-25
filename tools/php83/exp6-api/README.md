# exp6 isolated artifact regression

Revision-pinned exp5 follow-up, adding the parameter-reflection repair.
Stage once with `bash tools/php83/exp6-api/stage.sh 74` and `83`.
Existing stage directories are refused. Run `collect.py NEW_REPORT.json` only
with exclusive ownership of the baseline74 SQL/API fixture. It compares original,
exp5 and exp6 using private synthetic SQL and HTTP/trusted HTTPS.
No production, package, release or whole-application acceptance is implied.
