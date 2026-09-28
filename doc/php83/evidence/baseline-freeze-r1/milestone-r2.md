# Native observation capture corrected — task 1.2 remains open

R1's incomplete capture is preserved, including its unknown guest exit. Independent
local reproduction identified a parser mismatch: the guest may correctly report
an unresolved entry version, while the R1 host parser required a concrete fixture.
R2 uses the unchanged pinned guest/observation files and checks the consumed stage
before reuse; no source replacement, upload or profile mutation occurs.

Root ran `python3 -B tools/php83/baseline-freeze-r1/run_r2.py --check` (exit0),
then `--output ../platform-install-packages-php83-artifacts/baseline-freeze-native-r2`
(exit0). `actual-r2.json` and the separate independent native receipt retain the
sanitized result. Guest exit0, unit inactive, approved_freeze=false. All three
finite file/journal privacy windows completed with zero marker matches; this is
not universal privacy proof. Twenty-eight local tests passed independently.

The existing source asset/FileSync/hash and five privacy-overlay sources matched.
Native media.get(-1) and media.get(0) returned matching typed projections. A
positive concrete entry version remains unresolved, and selected profile14 was
not classified by the observer. Therefore the exported fixture is null and the
full baseline is not accepted. Source review found two observer assumptions to
correct in a separate version: positive-version selection is not required by
native default-current semantics, and the public profile type is
KalturaConversionProfile, not its physical model name KalturaConversionProfile2.
Neither finding permits inventing an entry version from asset version2, changing
profile permissions, or pretending the original failed attempt passed.

Git history, task count5/51 and production/release gates remain separate from this
partial successful observation. Next: versioned default-current fixture contract
and correct profile projection, independently reviewed before native execution.
