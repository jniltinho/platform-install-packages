# exp7 isolated artifact regression

Fourteen-patch PHP8.3-only experiment. Stage with `stage.sh 74` and `83` into
fresh owned directories; run `collect.py NEW_REPORT.json` with exclusive ownership
of the baseline74 SQL fixture. Matrix: original/exp6 on74; original/exp6/exp7 on83.
The native-mixed candidate is explicitly unsupported and guarded on PHP7.4.
CLI retains original/exp6 baseline74 and original/exp6/exp7 on83 (60 rows).
No package, production, release or whole-application acceptance is implied.
