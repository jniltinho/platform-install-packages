# Append-window v1 — local file scanner, not an authentication gate alone

Prepared standalone small scanner at
`tools/php83/baseline-rehearsal/privacy/append-window-v1/scan.py`.
No VM, installed application, credential or historical helper changes.

Interface:

```python
start = snapshot(discover_reviewed_sinks())  # before invalid synthetic nonce
result = scan_window(start, private_patterns,
                     inventory=discover_reviewed_sinks, limits=Limits())
```

The discovery callable MUST rediscover the complete effective reviewed file sink
inventory on every call. A cached list misses new sinks and is not acceptable.
It must be local, finite and nonblocking; scanner deadlines cannot interrupt a
hung caller-supplied Python discovery function or kernel filesystem operation.
The immutable `Mark` values are device/inode/size/mtime; callers must preserve
this trusted start snapshot, not reconstruct it from post-request observations.
The same start can be rescanned for the later synthetic USER secret/KS: earlier
new phase bytes are then deliberately included. No implicit advancing checkpoint.

Default bounds: 512 regular single-link files,64MiB newly appended bytes,
10 seconds,64KiB chunks,three drain rounds,50ms quiet recheck,32 patterns of
8..8192 bytes. The minimum allows the previously observed15-byte trace prefix.
Counts are per input index, including overlapping occurrences, not matching
chunks. Both full canary and the reviewed trace prefix are caller inputs and
never published, hashed or placed in errors. Exception strings are fixed codes.
Only public sink paths/end offsets, counts and bounded metadata are returned.

Historical bytes below each start offset are not scanned. Per-file tails span
both chunks and drain rounds, so a split canary is not missed or double-counted.
New/removed sinks, symlinks (including parent paths), hardlinks, FIFO/nonregular
files, inode replacement, shrink or observed same-size modification fail closed.
Any newly observed append is drained within the limits; if the final finite
quiet check still observes bytes beyond the read cutoffs, `UNDRAINED_TAIL` stops
instead of returning a zero-hit report. Path identity is rechecked after reads.
No rotation reconciliation is guessed; a fresh explicitly owned retry is needed.

`COMPLETE_FINITE_FILE_WINDOW` means only the returned offsets were observed and
scanned at the final check. It never covers later asynchronous writes, journal,
network forwarding or a malicious writer that truncates/rewrites/regrows between
observations while hiding metadata changes. The deployment audit must establish
append-only sinks and effective routes; stable counters are not host tamper proof.
No raw compressed stream is silently treated as decoded logging: effective
active sinks must be ordinary append-only text/bytes; rotation/compression during
this phase fails through inventory/identity checks. Historical compressed bytes
below the captured offset are deliberately irrelevant to this new nonce window.

Before USER, the orchestrator must require all counts zero, finite scan complete,
the separate continuous journal scan complete, effective configuration unchanged,
provider/source identity and the expected invalid-auth outcome. Any exception,
nonzero count or missing result stops. This scanner does not request credentials,
send HTTP, write logs, lower logging levels, change permissions, clear caches or
claim privacy acceptance. Intrinsic/pre-rendered/extras negative controls remain.

Local command:

```bash
python3 -m unittest discover -s tools/php83/baseline-rehearsal/privacy/append-window-v1 -p 'test_*.py' -v
```

21 synthetic tests initially cover historical exclusion, split/full/prefix
matching, repeated snapshot use, growing drains, quiet-tail exhaustion, rotation,
truncation, same-size rewrite, swaps, new/missing files, links/FIFO, byte/deadline
bounds, invalid limits/input and private exception content. These are local file
fixture tests, not native installed-flow or independent execution evidence.

## Reviewed correction r2

Actual OpenCode Muse review exited0 and ran21 tests, reporting no blocker in r1.
Independent Codex review subsequently reproduced a concrete counterexample:
`fstat` observed growth beyond the read cutoff, followed by truncation still above
that cutoff; r1 discarded the high-water mark and could return a false complete
zero-hit result. The retained r1 scanner and failing synthetic regression are
preserved, and the earlier CLI approval does not override this finding.

R2 retains the latest opened/post-read `fstat` mark for every file and compares it
to the next inventory snapshot. The observed shrink now raises `TRUNCATED`.
23 local tests pass, including that new interleaving and dense-match deadline checks; no native execution or
second CLI approval is implied. Independent Codex focal recheck is requested.

The same review found dense overlapping matches could overrun the CPU deadline
before the next chunk check. R2 also checks time between patterns and every1024
matches. Kernel/caller blocking and one bounded native bytes.find still cannot
be preempted; this is a cooperative finite budget, not a hard OS timeout.

Independent Codex focal r2 review is terminal:23 tests passed; the reviewer
independently reran both counterexamples. Observed growth24→shrink2 now fails
`TRUNCATED`; the dense2MiB/32-pattern/.05-second test stops with `DEADLINE` at
about.050s instead of6.496s. All three frozen inputs were unchanged during review.
These local timings are regression observations, not application benchmarks.
No remaining local blocker was identified in this bounded scope. The retained
review receipt is `evidence/baseline-rehearsal/privacy/append-window-v1/codex-r2-review.json`.
No new external CLI or native execution is implied by that focal review.
