# Finite journal window v1 — local preparation only

Small companion to append-window-v1, not a second authentication framework.
No VM/native journal read or authentication was executed by this implementation.

Interface:

```python
start = snapshot()  # Cursor object remains guest-private, before invalid nonce
result = scan_window(start, private_patterns, limits=Limits())
```

`Cursor` has opaque token/boot fields omitted from repr; never serialize it into
public receipts. `snapshot()` reads only the newest journal record with
`journalctl --no-pager --output=json --all --lines=1`. The operation is bounded and
fails closed for empty/unreadable journals; no historical wall-clock fallback.
Start can be reused when scanning the later USER secret/KS, including the whole
phase since before the invalid nonce.

Each scan round obtains an end cursor, reads **inclusively** from the anchor
using `--cursor=...`, requires the first record to equal that anchor and requires
the fixed end to occur. The initial historical anchor entry is not scanned;
new entries through end are. Duplicate cursors, changed boot, missing anchor/end,
malformed JSON, unrecognized/truncated null fields, process/stderr/byte/record/
time failures are INCOMPLETE. Cursors are opaque: no lexicographic ordering or
invented consecutive sequence number. If a newer tail exists, the next round
anchors at the previously scanned end; that anchor is excluded to avoid double
counting. A changing tail after three rounds fails, not zero leaks.

All journal values in the covered records are scanned guest-side, not only
MESSAGE. JSON strings, binary byte arrays and repeated-field arrays are decoded
before matching. Counts are nonoverlapping occurrences per private pattern per
field; they are not compared numerically to file scanner occurrence counts.
The decision is zero/nonzero. No reconstruction across separate journal entries
or transformed/encoded application messages is claimed. Full canary and the
previously observed15-byte trace prefix remain explicit caller patterns.

Default combined limits:8MiB output,15seconds,10000records,three rounds,
32patterns of8..8192bytes. Output and stderr are directed to private unnamed0600
TemporaryFiles, with child RLIMIT_FSIZE and subprocess timeout before reading.
No raw values, cursors, hashes of values or command stderr leave this module.
Errors are fixed codes. Bytes include private snapshot/inclusive-anchor/drain
reads, not just messages searched. One bounded JSON parse/native search and
kernel I/O are not hard-preemptible; the orchestrator still owns its outer timeout.
The preexec RLIMIT helper is intended for the existing single-threaded Linux lab
runner, not a general multithreaded process manager.

Normal journald retention/rotation is permitted only while the anchor and end
remain available; an expired/vacuumed boundary fails closed. This does **not**
cryptographically prove that a malicious operator deleted an interior record
while retaining both boundaries, or prove hostile journal integrity. No vacuum,
manual rotation, clock/boot transition or configuration mutation is allowed in
the owned request phase. Any observed gap/unknown encoding stops. No permission
change, journal flush/rotate/vacuum command, journal write or credential API exists
in this module.

Success reports only counts, bytes, records, rounds, `cutoff_covered=true`,
`future_writes_covered=false`, `files_covered=false`, `privacy_acceptance=false`.
It covers the final observed cursor, not future asynchronous writes. Before USER,
the caller must combine zero counts with the effective sink audit, bounded file
window/drain, expected invalid-auth response, unchanged source/provider identity
and a complete journal result; an exception never authorizes USER. New writes
while switching between file and journal checks need the existing finite combined
phase drain policy, not a claim of an atomic snapshot of all sinks.

Local reference inspected: installed journalctl help/man documents inclusive
--cursor, exclusive --after-cursor, JSON null truncation above4096bytes unless
--all, and binary/repeated value arrays. Native lab version remains checked by
the executor; unsupported switches fail through process status, never fallback.

Local command (15 mocked/synthetic tests; no journalctl process invoked):

```bash
python3 -m unittest discover -s tools/php83/baseline-rehearsal/privacy/journal-window-v1 -p 'test_*.py' -v
```

Cases cover private snapshot, inclusive-anchor exclusion, decoded values, missing
anchors/ends, duplicate cursors, boot change, bounded tails, no double counting,
malformed/truncated encoding, byte/record/deadline limits, private errors and
mocked process exit/stderr/timeout. Independent review is pending at preparation.

## R2 observed-tail correction

Independent Codex review ran15 tests but also reproduced a concrete r1 defect:
the read already contained a post-cutoff cursor with a canary; a subsequent tail
snapshot regressed to the cutoff. R1 ignored the observed suffix and returned a
false complete result. The same omission could hide a previously observed suffix
when a later drain skipped that cursor. Both failures and r1 source are retained.

R2 validates boot/uniqueness for the whole returned cursor sequence and retains
the observed post-cutoff suffix. The next inclusive read must reproduce that
suffix as its exact initial sequence. Latest==cutoff with an observed suffix now
fails `TAIL_REGRESSED`; a skipped observed suffix fails `OBSERVED_TAIL_MISSING`.
This is not an assertion about deleted entries never observed.18 local tests pass,
including those counterexamples and invalid boot/duplicates in the suffix.

R2's focal review found the same high-water issue for a cursor observed only by
the separate latest snapshot, not in the fetched suffix. That counterexample is
also retained against r2. R3 tracks **every observed cursor**, including snapshot
results, and requires all unscanned observations to reappear before completion;
missing ones fail `OBSERVED_CURSOR_MISSING`. All observed cursors must be in the
covered set at success.20 tests now pass, including both disappearance controls
and a normal snapshot-only-tail drain; no cursor value is published. An initial
r3 guard-order assertion failure was retained separately before preserving the
existing `END_CURSOR_MISSING` precedence. Native execution remains unperformed.
