# Autoload held-patch behavior plan — preparation only

No application PHP executed yet. Local preparation and seven static/negative tests are not runtime acceptance. Baseline74 is reserved by coordinator until explicitly released.

Inputs: exp10 ZIP `de177e6cbaedf3a3207661c2325f466cce37febb73190f3a49d31f24b740c053`; three independently frozen held patches identified by `prepare.py` metadata. Local `/tmp/php-autoload83-r1/identity.json` pins all staged bytes. 1,616 files per variant: complete HTMLPurifier, Symfony and Symfony-data vendor directories; not full application. Original means **exp10 before these three patches**, not the original release ZIP.

## Matrix

* Before74/candidate74/candidate83: HP actual registration, prepended callback, EntityLookup class-file hit, prefixed/unrelated misses, existing callback ordering.
* Before74/candidate74 only: pre-existing legacy global loader preservation through actual HP registration. Never parse this fixture on PHP8.
* Three variants: sfCore actual Finder-derived class map; simple-only and full+simple SPL callbacks, existing callback hit, mapped class hit, missing class, actual unserialize-created class. Synthetic classes are targets, never substitutes for framework loaders. Full-loader setup uses actual `initSimpleAutoload` to populate its shared class map; no cache/config/SQL path is exercised.
* Three variants: full Symfony `-V` and `-T`. Version queue probes run in a labeled shutdown phase after actual early version exit; they do **not** establish task execution. Empty versus pre-existing SPL queue measures intentional global-wrapper to appended-SPL-closure composition delta. Existing first-loader hits must remain prior to fallback; before74 with existing SPL queue must miss fallback, candidate must reach it.
* Before83: require each of the three entire target files, preserving native removed-`__autoload` compile fatal and exit status. No extraction of function bodies.

All processes isolated, read-only source/project fixtures, synthetic class data, no SQL or application server. Native warnings remain stderr; normalized report records phase/severity/file/line/message hash. Report loaded source files/hashes and before/after staged inventory/runtime identity in collector. FullCLI old Pake incompatibilities must remain failure evidence; no stubs, suppression or extra repairs authorized. Missing-SPL branch unexecuted on these SPL-enabled runtimes. No universal PHP7.4 parity or full migration acceptance implied.

## Commands (staging/execution NOT AUTHORIZED YET)

Local preparation already executed:

```sh
python3 tools/php83/autoload83/prepare.py ../platform-install-packages-php83-artifacts/exp10/Rigel-18.20.0-php83-experimental.exp10.zip /tmp/php-autoload83-r1
python3 -m unittest discover -s tools/php83/autoload83 -p 'test_*.py' -v
bash -n tools/php83/autoload83/run.sh
```

After collector validation and coordinator lab grant, copy to a **new** `/home/vagrant/php-autoload83-r1` stage with refuse-existing mkdir and verify `identity.json` hashes. Execute `bash /home/vagrant/php-autoload83-r1/run.sh 74 original hp`, corresponding matrix cases, and preserve every stdout/stderr/exit. Any changed harness requires a fresh stage and explicit attempt identity; do not overwrite old results.

Collector preparation update: 23 process matrix; 15 local positive/negative/static tests passed (`test-local-r2.*`), preserving initial seven-test run separately. Collector validates expected functional values, exact callback order, real loaded-file hashes, fatal-control signatures/exits, and before/candidate74 HP/core functional equality. Diagnostic differences remain explicitly reported and require review (not blanket parity). It preserves public-source stdout/stderr and structured failures; no live configuration is mounted. Runtime snapshots use unchanged `tools/php83/exp10-api/runtime-identity.py` before and after; compare its `identity` object, not output filename.

```sh
# After explicit coordinator release ONLY:
python3 tools/php83/exp10-api/runtime-identity.py doc/php83/evidence/autoload83/runtime-before.json
python3 tools/php83/autoload83/collect.py /tmp/php-autoload83-r1/identity.json doc/php83/evidence/autoload83/primary-r1.json
python3 tools/php83/exp10-api/runtime-identity.py doc/php83/evidence/autoload83/runtime-after.json
```
