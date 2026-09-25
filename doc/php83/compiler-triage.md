# Exact-source classification of exp9 compiler rejections

This audit classifies **all 54** files still rejected by the exp9 PHP 8.3 syntax
scan. It changes no application source, runs no PHP, removes no rejection and
waives no acceptance requirement. **The candidate still does not compile in
its entirety; T0-04 and application acceptance remain open.**

## Evidence and identity boundary

The [primary classification report](evidence/compiler-triage/primary.json) joins
these existing observations:

- [Paired original/exp9 syntax scan](evidence/candidate-syntax/primary-r2.json).
- [Historical 7.4/8.3 compiler comparison](evidence/source-audit/php74-vs-php83-compile.json).
- [Exact published DEB payload identities](evidence/package-identities/primary.json).
- [All-54-file graph coverage](evidence/compiler-triage/coverage.json), supplied
  by the coordinating parent at Tier 2.
- [Exp9 manifest](evidence/exp9-candidate/manifest.json) and
  [held Symfony repair metadata](../../patches/php83/held/symfony-bootstrap.json).

Both original and exp9 ZIP identities are pinned. For **every one of the 54
files**, original ZIP, exp9 ZIP and immutable local source bytes agree. The
compiler records' hashes also agree, and the published package and historical
7.4 comparison have the **same exact file hash**. No baseline result was
transferred merely because filenames match. Reports include raw compiler
messages, concrete source excerpts, placeholder lines, owners and all imported
evidence hashes.

A package/history contradiction fails. Different candidate bytes would not
inherit a historical result; the generic join marks them not comparable, and
this fixed exp9 cohort additionally rejects an unexpected changed source.
Missing historical evidence remains unresolved rather than defaulting to PASS.
Duplicate evidence paths, source drift, unknown compiler causes, unsupported
source/diagnostic combinations and denominator changes also fail.

## Complete denominator

| Compiler cause, verified against source | Files | Exact-source historical 7.4 result |
|---|---:|---|
| Removed curly-brace offset syntax | 43 | Accepted; new PHP 8.3 rejection |
| Unparenthesized nested ternary | 1 | Accepted; new PHP 8.3 rejection |
| Removed `__autoload` declaration | 3 | Accepted; new PHP 8.3 rejection |
| Reserved `Object` import alias in RiakCache | 1 | Rejected already |
| Unexpanded Symfony generator/skeleton placeholders | 6 | Rejected already |
| **Total** | **54** | **47 new + 7 retained baseline rejections** |

These are file-level first compiler rejections, not all defects or all unsupported
expressions within each file. Additional diagnostics are retained in each row.
The 47 language incompatibilities cannot be labelled inactive merely from their
vendor/build-directory location. The retained Riak failure is likewise not
waived because the baseline also rejects it.

## Six template sources, not six removed failures

Direct source evidence shows:

- `vendor/symfony-data/generator/sfPropelAdmin/default/skeleton/actions/actions.class.php`
  and its `sfPropelCrud` counterpart: line 11 contains
  `class ##MODULE_NAME##Actions extends auto##MODULE_NAME##Actions`.
- `vendor/symfony-data/skeleton/module/module/actions/actions.class.php`: line 11
  contains `class ##MODULE_NAME##Actions extends sfActions`.
- `vendor/symfony-data/skeleton/batch/default.php` and `rotate_log.php`: line 16
  contains `define('SF_DEBUG',       ##DEBUG##);`.
- `vendor/symfony-data/skeleton/controller/controller.php`: the same unresolved
  DEBUG token appears on line 6.

The source context explains why linting these **unexpanded** files rejects them
on both versions. It does not prove that template rendering or the generated
PHP works. The separate
[positive template-consumer investigation](evidence/compiler-triage/template-consumers.json)
records copy/token-replacement chains; that evidence is not a generator test,
an exhaustive caller proof or permission to drop these six files from the
54-file scan denominator. Generated-output compilation, correct substitutions
(including DEBUG handling) and relevant generator behavior remain open.

## Graph gaps and held repairs

Coverage reports **5 files without a recorded issue and 49 partial files** for
project `kaltura-rigel-18.20.0-full`, generation `2026-09-25T12:19:00Z`. The builder
reads and retains all reported missed ranges from hash-verified immutable source,
in addition to direct diagnostic-line excerpts. The graph is not used to claim
absence of callers, dead code, inactivity or complete runtime reachability.
The classification is grounded in compiler observations and exact source bytes.

Five files match existing held repair metadata and patch hashes:
`sfRouting.class.php`, `UrlHelper.php`, `sfCore.class.php`, `sfFinder.class.php`
and `Spyc.class.php`. None is selected in exp9. These are identity annotations
only: this audit neither applies the patches nor transfers old tests to a new
integrated candidate. Generator-related code outside the six literal skeletons
is still classified as actual language incompatibility when supported by its
compiler diagnostic; a directory name alone does not earn a template exception.

## Reproduction and tests

```sh
python3 tools/php83/compiler-triage/build.py \
  --source-root /home/nilton/Projetos/nilton/NOVOS/kaltura-rigel-18.20.0-source/server-Rigel-18.20.0 \
  --original /tmp/kaltura-php83-audit/Rigel-18.20.0.zip \
  --candidate /home/nilton/Projetos/nilton/NOVOS/platform-install-packages-php83-artifacts/exp9/Rigel-18.20.0-php83-experimental.exp9.zip \
  --output /tmp/php83-compiler-triage-new.json
python3 -m unittest discover -s tools/php83/compiler-triage -p 'test_*.py'
```

Outputs must be new. The tool is a trusted-local immutable-input audit, not a
hostile-archive filesystem/concurrency sandbox. It reads ZIP members without
extracting or executing them. No VM/network/package operation is performed.

**17 local tests pass**, including object-property offsets, source disagreement,
all five categories, template-path-only rejection, unknown diagnostics, path/line
mismatch, duplicate evidence, traversal, exact/new/retained baseline joins,
changed-candidate refusal to inherit results, missing history and archive drift.
They are nested tests requiring the command above, not automatically included
in the older top-level suite. Two primary builds are byte-identical.

[Tests](evidence/compiler-triage/primary-tests.stderr),
[exit status](evidence/compiler-triage/primary-tests.exit),
[repeat report](evidence/compiler-triage/primary-repeat.json), and
[primary phase record](evidence/compiler-triage/primary-result.json) are retained.
The initial classifier failed closed because its recognition pattern omitted
`$this->buffer{...}` syntax; the
[attempt record](evidence/compiler-triage/primary-attempt1.txt) and
[old builder](evidence/compiler-triage/primary-attempt1-build.py) are preserved.
Only the classifier pattern changed; the application/source/54-file denominator
remained untouched. The new object-property regression test covers that correction.
Independent CLI execution/review is coordinated separately.

## Next runnable work

Prioritize a reviewed batch of the 47 source-confirmed language incompatibilities
with focused before/after controls, then rerun the unchanged full syntax
selection and the actual impacted entrypoints. In parallel, render and compile
all six skeleton outputs with deterministic inputs. Baseline failures still need
a named disposition and tests; no finding is accepted simply because it predates
PHP 8.3. Static semantics, dependencies/licenses, broader entrypoint coverage and
runtime acceptance remain separate requirements.

## Follow-up: strict compiler status validation

After the initial independent CLI reviews completed, the coordinator identified
a fail-closed gap: arbitrary nonzero statuses could be treated as rejections.
The frozen reviewed sources are preserved as
[old builder](evidence/compiler-triage/primary-reviewed-build.py) and
[old tests](evidence/compiler-triage/primary-reviewed-tests.py), alongside all
17-test-phase reports. The real recorded statuses were already integer 0/255;
this gap did **not** change the observed 54-file / 47-new / 7-baseline result.

The hardened builder accepts only integer 0/255 for every original/candidate
scan record. The rejected cohort specifically requires integer 255. An exact
historical join requires integer 0/255 for 7.4 and integer 255 for its rejected
8.3 observation. Timeouts, signals, other statuses, booleans, floats, strings
and null values cannot become accepted compiler classifications. No classifier
regex or application source changed in this phase.

**19 local tests pass** with new negative-status families applied to both scan
variants and both historical fields. The
[hardened primary](evidence/compiler-triage/primary-r2.json) and
[repeat](evidence/compiler-triage/primary-r2-repeat.json) are byte-identical;
all 54 classified rows are unchanged from the prior report. Only the recorded
builder identity changes. See
[test output](evidence/compiler-triage/primary-r2-tests.stderr) and
[phase/identity record](evidence/compiler-triage/primary-r2-result.json).
Independent follow-up is coordinated against this new frozen version; earlier
reviews must not silently be attributed to the revised code.

## Independent verification and limitations

Claude independently rebuilt both reviewed phases: the initial 17-test phase
and the hardened 19-test phase. Final `claude-r2.json`, `primary-r2.json` and
`primary-r2-repeat.json` are byte-identical. The
[comparison verifier](evidence/compiler-triage/compare.py) checks current input
and builder hashes, all 54 exact-source baseline joins, integer status values,
and unchanged rows across the hardening. See the
[comparison result](evidence/compiler-triage/comparison.json). Only the builder
identity changes between phases; no application file or classification changes.

The classifier is a **fixed-cohort lexical heuristic, not a general PHP parser**.
It matches a compiler diagnostic to its path/line and inspects regex patterns in
that line or a small source window. It does not validate diagnostic columns or
parse all possible expressions/comments. Independent source review supports the
causes in these particular 54 files; this must not be generalized into sound
classification of arbitrary PHP. An unknown pattern fails the build instead of
being silently waived.

Cursor executes the 11 existing scanner tests and independently verifies all
13 template/consumer file identities against both ZIPs, including recorded
consumer-body excerpts. Those excerpts omit some function headers/argument checks;
they support positive copy/token-replacement chains, not every precondition or
complete workflow behavior. Source fallback records retain six requested graph
ranges extending beyond physical EOF using `available_end`; no nonexistent line
is invented, and this best-effort graph metadata is not completeness proof.

Grok's bounded attempt terminates after 120 seconds with exit 124. The authorized
OpenCode Zen `opencode/muse-spark-1.3-contributor-free` fallback runs the initial
17 tests and independently joins all 54 scan/package/historical rows with zero
missing paths or hash conflicts. It confirms the 47/7 split and unresolved
runtime reachability. Its execution belongs to the initial phase; the final
19-test/status-hardening phase is independently executed and reviewed by Claude.
All CLI outcomes are retained in
[evidence/compiler-triage/agents](evidence/compiler-triage/agents/).

No template placeholder is mechanically removed to make raw lint green. Actual
rendering and generated-output checks remain required. The reserved Riak Object
import remains an identified baseline defect, not an accepted migration exception.
All 54 rows remain open for their appropriate repair, generation or disposition
work, and the 4,711 static-report rows remain a separate broader obligation.
