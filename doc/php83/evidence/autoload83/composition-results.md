# Real-loader composition: bounded primary results

Primary `composition-primary-r2.json`: **30 processes, 27 positive passes and 3
expected full-file redeclaration fatals**, collector exit 0. This is additional
bounded evidence, not a replacement for the first matrix's three retained
empty-project `-T` failures and not application acceptance. Independent repeat
and review remain pending at this update.

The new probe runs unchanged real loader implementations from immutable
`php-autoload83-r2`, with its own `php-autoload83-composition-r1` stage. Each case
runs separately under before74/candidate74/candidate83. Synthetic callback target
files intentionally compete with the real HTMLPurifier class path or Symfony
Finder-derived project model path; framework loaders are neither replaced nor
extracted. Reflection winner paths and all included source/fixture hashes are
required, together with exact callback queues, ordered event traces, caught
exception class/message and native diagnostics.

## Executed controls

* HTMLPurifier: later appended versus prepended callback and duplicate class
  winner; throwing miss callback with no subsequent handler; repeated real
  registration plus direct autoload-file include. Real loader hit takes
  precedence over an appended callback; a prepended competing callback wins.
* sfCore: repeated full and simple registration using its actual Finder-generated
  class map. Its internal callable list duplicates the full callback, whereas
  the SPL queue de-duplicates it. This is observed behavior, not blanket
  idempotence.
* Symfony: actual full `-V` followed by explicitly labeled shutdown composition
  phase, later appended/prepended competing callback, throwing callback before
  and after framework loader, and repeated full CLI direct inclusion.
* Before74's implicit global `__autoload` disappears from the active queue when
  the first later SPL callback is registered. Its appended duplicate target
  therefore wins, or its throwing callback prevents the hit. The candidate's
  existing SPL closure remains ahead of an appended callback, so its real target
  wins and only misses reach that callback. A prepended callback wins in both.
  These intentional native queue differences are explicit, not forced into
  false universal parity.
* Repeated whole CLI inclusion is not idempotent: original74 reports global
  `__autoload` redeclaration at line 107; candidate74 and candidate83 report
  `simpleAutoloader` class redeclaration at line 36. All exit 255. The probe
  flushes pre-include provenance before that intentional fatal, and the collector
  verifies the exact native stderr text/file/line and exit. It does not claim the
  pre-fatal JSON itself captured the later fatal.

Warnings are not suppressed: exact expected warning fields/message hashes and
complete native stderr/fatal text are checked. Removed global-autoload warnings
and retained old-style Pake constructor warnings are distinguished by variant
and runtime. The first collector revision is retained under
`composition-attempt-r1/`; r2 adds strict diagnostic reconciliation without
changing the executed probe or source stage.

All source/harness inventory checks remained unchanged. Runtime identity objects
in `composition-runtime-before-r1.json` and `composition-runtime-after-r2.json`
match. 13 local composition tests passed (`composition-tests-r2.*`). The base
collector additionally received exact diagnostic-message/fatal-line checks:
21 local tests pass and `behavior-revalidation-r4.json` replays both prior
primary and Claude 26-process reports without new guest execution, preserving
20 positives, three expected fatals and the three specific empty-project
failures. Old base collector r3 is preserved in `behavior-attempt-r3/`.

Not executed: missing-SPL environment, all possible third-party callback
compositions, task execution, configuration cache misses/backends, SQL or full
application acceptance. No patch integration, ZIP rebuild, package or release
occurs in this phase.

## Repeat commands

After coordinator's exclusive baseline74 grant, use fresh output names:

```sh
python3 tools/php83/exp10-api/runtime-identity.py doc/php83/evidence/autoload83/composition-claude-runtime-before.json
python3 tools/php83/autoload83-composition/collect.py /tmp/php-autoload83-r2/identity.json doc/php83/evidence/autoload83/composition-claude.json
python3 tools/php83/exp10-api/runtime-identity.py doc/php83/evidence/autoload83/composition-claude-runtime-after.json
python3 -m unittest discover -s tools/php83/autoload83-composition -p 'test_*.py' -v
python3 -m unittest discover -s tools/php83/autoload83 -p 'test_*.py' -v
```

## Collector-only typed-value correction

After the first actual Cursor review completed successfully, an additional
read-only author mutation showed that Python equality accepted `true` replaced
by integer `1` in a composition result. The exact mutation and initial accepted
result are preserved in `composition-author-adversarial-r1.json`; passing prior
reviews did not exclude this gap. Genuine retained runtime records were not
altered.

Both collectors now use canonical JSON comparisons for functional values (and
composition diagnostic structures), require integer—not boolean or float—exit
codes, and reject boolean/integer/float substitutions in new negative tests.
Base diagnostic severities/lines are also strictly integer. Current totals:
**23 base tests and 15 composition tests**, all passing. Prior collector/test
versions remain under `behavior-attempt-r4/` and `composition-attempt-r2/`.
`composition-typed-revalidation.json` records local replay of all three retained
runtime reports with unchanged exact outcomes. No new guest execution is
implied by this correction. `composition-harness-typed-final.json` is the new
freeze; independent validation of this final revision is tracked separately
from the preceding Cursor phase. These controls are bounded, not proof that all
possible falsified inputs have been exhausted.

## Actual Cursor final typed follow-up

The separate actual Cursor typed follow-up completed its local commands before
its **150-second CLI timeout (exit 124)**: 15 composition tests and 23 base tests
returned exit 0; retained three-report replay returned exit 0 with the same
explicit outcomes; 24 type-confusion/extra/missing-row mutations were rejected
and four genuine positive controls passed. Frozen inputs remained unchanged.
Its written `composition-cursor-typed-review.json` records the executed commands,
results and limitations. The CLI produced no final response JSON, so the overall
CLI attempt is TIMEOUT, not an exit-0 reviewer run. Use the review JSON rather
than text (the text has missing inline-code fragments). See
`composition-cursor-typed-status.json`; no retry or new scope is implied.

## Final independent execution and cycle boundary

The first Claude attempt is retained in `composition-claude-review.*`: quota
failure, exit 1, **NOT_EXECUTED**. Its post-reset retry completed with exit 0
(`composition-claude-retry-review.*`). Actual CLI session
`7d65fa9e-e973-463c-ae29-ca9dcccb52e4` executed the lab collector and runtime
snapshots; `composition-claude.json` records 27 positive passes and three
expected fatal controls. All 30 records equal the primary records; the final
typed collector hash differs legitimately. Before/after runtime snapshot bytes
match and 15 composition plus 23 base tests pass. Actual executed CLI tool calls
and commands establish the independent run; identical deterministic JSON alone
would not distinguish execution from copying.

The earlier Cursor review completed exit 0; the final typed follow-up's executed
commands/review artifacts and its overall timeout 124 remain separate, as above.
No further expansion is part of this checkpoint. The CLI composition phase is
shutdown-after-`-V`; the extra sfCore case covers repeat registration only.
Arbitrary third-party combinations, no-SPL, backends/SQL, task execution and
whole-application acceptance remain untested. Base empty-project failures stay
FAIL and patches remain held. This bounded cycle is ready for the coordinator's
checkpoint, not release approval.
