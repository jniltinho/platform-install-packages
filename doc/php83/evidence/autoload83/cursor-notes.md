# Cursor local execution/review accounting

The actual `agent -p --trust --auto-review --output-format json` CLI finished
with exit 0 under a 180-second bound. It executed the two recorded unittest
commands: **10 ternary tests and 15 autoload tests passed**; both shell runners
passed `bash -n`. Test outputs and real exits are retained as `cursor-*-tests.*`
and `cursor-bash-n.exit`. Tests read existing recorded runtime evidence and
exercise local guards; they do not constitute new PHP/VM execution.

All 24 input file hashes were identical before and after this review. See
`cursor-input-identities.json` and `cursor-final-input-identities.json`. The
public review is retained verbatim in `cursor-review.txt`; source authors did
not rewrite its conclusions. The CLI made no VM/SQL/package/release changes.

## Review limits and corrections

Cursor accurately described the minimal three autoload patches, explicit SPL
queue composition delta, native-diagnostic visibility, and the ternary's
left-associative repair. It also observed that `expected('cli-tasks') == {}`
does not assert positive task-list content. That gap must remain visible, even
though Cursor called it a nonblocking local observation.

Its overall **“no blockers” and complete missing-case guard assurance are too
broad**. Independent coordinator/runtime work identified counterexamples:

- The frozen ternary collector accepted a duplicate candidate-PHP-7.4 record in
  place of candidate-PHP-8.3; it did not prove the exact unique four-mode matrix.
  Genuine existing primary/repeat records are not invalidated by this guard
  defect, but a passing old unit suite cannot establish adequate rejection.
- The runtime worker's first autoload matrix exposed PHP's empty-array JSON
  representation (`loaded: []`) in a fatal control; the frozen collector called
  `.items()` as if it were always a mapping and crashed. The 15 local tests did
  not cover that actual shutdown output. Real `-T` dependency failures also
  remain failures, not permission to waive full-entrypoint results.

These are attributed findings from the coordinator and runtime worker, not
discoveries or executed PHP cases by Cursor. The source freeze was released
only after Cursor became terminal and hashes were checked; subsequent repairs
and adversarial tests belong to a separately pinned follow-up phase. Retain the
initial evidence and do not relabel this initial advisory review as approval of
files it did not inspect. No application, integrated candidate or release
acceptance follows from this local review.

## Hardened ternary follow-up: bounded parity passed

Actual Cursor completed a separately pinned, 180-second-bounded follow-up with
exit 0. All eight input hashes remained unchanged. It executed **21 local
tests**, exit 0, and locally imported the hardened collector to revalidate both
genuine retained `primary-r2.json` and `claude.json`, exit 0. This is recorded
evidence replay, not another PHP/VM run. See `cursor-hardening-review.txt`,
`cursor-hardening-review.json`, `cursor-hardening-tests.*`,
`cursor-hardening-replay.*` and the corresponding before/after identities.

The follow-up independently confirmed duplicate-mode rejection and explicitly
corrected the earlier overbroad assurance. The real collector order is
`original74, candidate74, candidate83, original83`; the prompt had mistakenly
listed the final two in reverse order. Cursor identified this discrepancy and
reviewed the actual frozen collector rather than changing it to match prose.

**Oracle boundary:** 130 of the 147 cases have fixed expected values. The final
17 flat/alias/map/invoke/nested/caller cases require parity against genuine
original-PHP-7.4 output; they do not have independent golden expectations.
Cursor demonstrated that changing one of those values identically in all three
positive-mode records still passes. This exposes the limits of a differential
oracle, not evidence that actual candidate output differed from the recorded
baseline. Therefore the supported conclusion is **bounded parity passed**, not
“all 147 values independently proven correct” or immunity to coordinated report
fabrication. Input-report identities and independent actual runtime execution
remain separate evidence. No new ternary tool changes were authorized for this
oracle limitation; stronger goldens can be future coverage work without
misrepresenting the current result.

The autoload `loaded=[]` collector repair/runtime results are outside this
follow-up. Application, broad migration and release acceptance remain open.

## Final autoload local review: preserved failures and exact denominator

The actual final Cursor invocation completed with exit 0 and all 17 pinned
inputs unchanged. It executed **19 local tests**, exit 0, and read-only replay
of `primary-r3.json`, exit 0. The latter means the expected mixed outcomes were
verified: **20 positive PASS, three original-PHP-8.3 EXPECTED_FATAL controls and
three empty-project CLI FAIL results**. The primary report remains `FAIL` with
three failed checks; neither replay exit 0 nor local test success means all 26
runtime processes passed.

The three configured `-T` outputs contain the real task-list header and required
`init-project`, `init-module` and `propel-build-model` tasks, with identical
whole listings across modes. Empty-project `-T` still exits 1 with missing
`kConf`; those failures are retained. Current loader-inventory guards and object
serialization address the earlier empty-array representation gap, within the
current tested contracts.

Cursor corrected a mistake in the review prompt: **1,630 selected source files
per tree** is the stage denominator. **37 loaded files** describes only each
configured CLI case; it is neither the selected tree size nor every case's
loaded count. The actual report/identities were not changed to match the prompt.

The tested append-to-existing-SPL-queue composition remains bounded. Later-added
or prepended callbacks, duplicate-class winners, callback exceptions, repeated
includes and no-SPL runtime behavior are **not tested**, rather than successful
cases inferred from the patch review. Actual independent VM repetition belongs
to Claude's separate evidence, not this local Cursor replay.

Final artifacts: `cursor-autoload-final-review.{txt,json}`,
`cursor-autoload-final-tests.*`, `cursor-autoload-final-replay.*`,
`cursor-autoload-final-cli.*`, prompt and before/after identities. The
`cursor-evidence-index.json` file hashes the complete owned evidence set. No
whole-application or release approval is asserted.
