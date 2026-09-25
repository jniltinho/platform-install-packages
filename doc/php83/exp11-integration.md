# Exp11 artifact regression — preparation

Status: **bounded actual-artifact regression and independent repetition passed**.
This is not complete application or release acceptance. Codex and actual Claude
executed the matrix below; Cursor separately reconciled the reports. The selected
exp11 ZIP is experimental. The API still emits 18 diagnostic groups / 503 events,
and whole-source compilation still rejects seven files. Detailed limitations and
outer CLI failures remain recorded rather than normalized into success.

## Serialized lab matrix

Only the named disposable `baseline74` and `php83` labs are in scope. The `.20`
server, package integration and release workflows are out of scope. Acquire
exclusive lab ownership before staging or running synthetic services. Staging
creates `/home/vagrant/php-exp11-regression` and refuses an existing directory;
never overwrite prior evidence or repair a frozen stage in place.

| Surface | Planned actual execution | Limitation |
| --- | --- | --- |
| Apache API | original PHP7.4, original PHP8.3 negative control, exp10/8.3, exp11/8.3 | Synthetic SQL; HTTP, trusted HTTPS and rejected untrusted CA, not AIO/FPM |
| Focused CLI | 12 original74 and 36 original/exp10/exp11 native83 processes | Standard/minimal INI, selected helpers only |
| Curly-offset classes | Three actual-artifact processes, 68 cases | Previously reviewed bounded class corpus |
| Four new patches | 17 exp11/8.3 processes | 16 positive and one expected duplicate-include fatal |

The last row replays the reviewed ternary, autoload and autoload-composition
corpora against the full extracted ZIP rather than held replacement source.
It includes 147 ternary rows, six autoload cases and ten composition cases.
`evidence/exp11-runtime/addition-corpus.json` pins the previous independent
Claude reports and fixture bytes. Exact output equivalence is not a new golden
oracle or a claim of complete application compatibility.

## Evidence requirements

- Verify full ZIP, extracted source, harness and runtime identities before and
  after execution; retain original and previous-artifact controls.
- Record native diagnostics, expected original failures and duplicate-include
  failures. Existing API deprecation groups are not waived by functional parity.
- Use the synthetic database's unique owned systemd unit and verify shutdown.
- Preserve only whitelisted API stdout and sanitized diagnostics; never record
  raw session keys or authentication material.
- Run the actual Claude CLI for a separate full repeat after primary execution;
  reconcile outputs with explicit nondeterministic-field exclusions.
- Keep executor and reviewer results separate. OpenCode MiniMax and Cursor each
  actually executed 25 local tests and six individual shell syntax checks, but
  their first preparation reviews were incomplete (permission failure/no final
  result and timeout, respectively). The actual repository-only OpenCode Muse follow-up completed with no blocking
  defect found. These local results do not count as runtime execution.

All broad migration, package, release and cutover gates remain open.

## Primary execution completed

The staged actual ZIP now passes the bounded primary API comparison to original
PHP7.4 over HTTP/trusted HTTPS with untrusted-CA rejection. Both exp10 and exp11
retain exactly **18 diagnostic groups / 503 events**; no warning was waived.
The unique synthetic DB unit is inactive after collection. The baseline executes
12 successful CLI rows, while native83 executes 32 successful rows and four
expected original-source JSON compiler failures. The three-class corpus passes
68 cases, and the additional four-repair corpus passes its 17-process exact-byte
contract (including one expected duplicate-include fatal). All 55 baseline runtime
object identities match before/after. Independent baseline repetition remains
pending; these results are not whole-application acceptance.

## Independent reconciliation

Actual Claude completed separate native83 and baseline74 executions with CLI
exit 0. All 18 reports reconcile under the explicit policy in
`evidence/exp11-runtime/comparison-runtime.json`: 48 CLI rows, 20 typed
candidate-to-original74 comparisons, four API rows, 68 class cases and 17 new
repair processes. Each lab has four equal runtime snapshots; native and copied
PHP8.3 interpreter hashes agree. Exact additional-corpus reports agree as well.
The runtime object's byte identity does not attest kernel/systemd/MariaDB or all
host configuration, nor prove a separate independent environment.

API comparison excludes only per-row duration and opaque raw-stderr hashes;
synthetic database UUIDs are different and each known unit's cleanup is checked.
Raw KS-bearing logs were not retained. Equality is limited to exact whitelisted
responses, diagnostic groups/counts and runtime observations; no claim is made
that differing raw stderr hashes arise only from timestamps.

Cursor actually ran 18 local guard tests and the full reconciler successfully,
producing an identical comparison report and a written semantic review. Its
outer CLI timed out at 180 seconds (exit 124); it is not reported as CLI exit 0.
Duplicated fixtures in guard tests are not independent runtime execution. The
reconciler does not itself prove executor provenance: actual Claude tool calls,
step exits and sanitized execution records provide that separate evidence.
Full application, all-63-source behavior, FPM/AIO, service, media, upgrade,
performance, packaging and release gates remain open.
