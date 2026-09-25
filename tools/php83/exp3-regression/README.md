# exp3 artifact regression

`stage.sh 74|83` creates a **new**, dedicated directory in the corresponding
existing synthetic lab, copies the immutable public exp3 ZIP and fixtures, then
verifies SHA256 before extracting. It refuses an existing staging directory;
never delete another experiment to rerun it. Existing candidate and installed
application/service/configuration paths are not replaced.

Run the staged `batch.py` through the corresponding fixed lab SSH alias. It
rechecks every extracted regular file against the ZIP, then records all 24
original/exp3 × standard/minimal × environment/JSON/parser/consumer rows.
`run-one.sh` uses nobody, read-only source, private cache/config tmpfs, private
network and denied socket creation, with 512 MiB / 60-second process limits.
Minimal consumer explicitly loads POSIX/ctype/iconv to retain the real euid guard;
other minimal cases use `-n` (+ JSON on 7.4). No guard is bypassed.

The **batch command can exit zero with failing rows**: it is an evidence collector,
not an acceptance gate. Inspect each exit/stdout/stderr. Original 8.3 JSON syntax
fatals are controls; new candidate failures are not. Passing value assertions
with deprecations is partial compatibility, not clean runtime acceptance.
SSH uses existing loopback lab configuration/hostname checks without host-key
pinning; this is not production transport assurance. No benchmarks are claimed.

The 15183 extracted regular files include 15175 original files plus eight
experimental metadata files. Mountpoint directories may be created by systemd;
this verification covers file bytes, not identical directory metadata.

This fixture does not execute the patched PDO/date paths, live API/DB/Apache,
media/jobs/UI, cache backend acceptance, or a release. Continue those cases using
the same extracted artifact rather than substituting manually patched sources.
