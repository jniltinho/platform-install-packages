# Cumulative Criteria experiment

This preparation compares the exact exp11 Criteria source against that source
plus one `#[\AllowDynamicProperties]` class attribute. It does **not** select a
manifest, build a ZIP, or claim cache/application acceptance. The older strict
cross-engine serialization comparison remains **FAIL**; no report is replaced.

`prepare.py` emits one cumulative original-to-candidate patch. A future manifest
must replace its existing Criteria entry, never append a duplicate. Parent's
exp12 draft owns that uniqueness/provenance gate. `composition-preparation-r2.json`
records the current preparer hash and exact strict local replay; original r1
records remain untouched. Removing the attribute restores exp11 bytes exactly.

## Focused native design

`fixture.py` binds both actual ZIP identities and four real dependency files,
then derives two probes without modifying their original files:

- Full actual Criteria + criteriaFilter + myCriteria + KalturaCriteria: 19 cases,
  repeated filters, clone/clear, exception marker, public/property_exists/null,
  serialized bytes, subclass hint and unrelated-class diagnostic control.
- Prior return corpus: 16 rows, real Iterator contracts, object identity,
  independent cursors, mutation snapshots, serialization, five alias cases;
  two intentionally invalid iterator accesses retain native warnings.

Only the Propel DB lookup/DBAdapter boundary is stubbed; no SQL or full bootstrap.
Four native **PHP8.3** processes compare exp11/candidate in both corpora. PHP7.4
is deliberately not run on exp11's PHP8-only `mixed` signatures. Earlier original
74/83 and imported typed-state evidence is separate, not reinterpreted here.
The filter corpus deliberately imports no legacy payloads; the previous seven
payload experiment remains the evidence for that separate question.

Run local tests before coordinator authorizes `collect.py`:

```sh
python3 -m unittest discover -s tools/php83/criteria-composition -p 'test_*.py' -v
bash -n tools/php83/criteria-composition/run.sh
```

Collector execution requires exclusive native83 lab ownership. It creates a new
immutable root-owned stage, parent-pins all fixture hashes, compares runtime,
module and linked-library identities with the recorded attribute experiment,
checks them before/after, and runs unprivileged read-only systemd sandboxes with
network sockets denied. It retains stdout/stderr/exit before validation. Validator
requires ordered four modes, same-runtime exact rows/serialized representation,
reflected return contracts, exact reconstructed native stderr and normalized
unchanged unrelated diagnostics. No full-cache, performance, API or release gate
is waived by a pass.
