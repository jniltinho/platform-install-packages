# Criteria null alias: held compatibility repair

The exp3 API matrix reported 694 events at `Criteria.php:1375`. Direct source
inspection confirms that `Criteria::getTableForAlias()` returns implicit null
when no mapping exists; `Criterion::init()` passes that null to `strlen()`.
The proposed one-line repair explicitly handles null before evaluating strlen,
retaining the existing fallback to the parsed table name. It does not change
non-null conversion, replace the condition with a truthiness test, or suppress
PHP diagnostics. In particular, the non-empty alias string `"0"` remains valid.

## Actual focused results

Codex runs the real Criteria/Criterion classes from pinned source and the patched
copy under native PHP 7.4.33 and PHP 8.3.6 in the existing isolated labs. Only the
DB lookup/adapter boundary is a fixture. Eight cases per source/runtime cover
missing, explicit null, empty string, named table, zero string, unqualified
column, false and integer zero aliases. All 32 observed rows pass strict expected
value assertions and match the original 7.4 rows. On original 8.3 the three
null-alias diagnostics occur; with the patch those three disappear. Other
interface return-type diagnostics remain visible in the reports.

This is **not SQL or full application acceptance**. The next integration check
must exercise a separate derived candidate through the actual SQL/HTTP/TLS
matrix and preserve the exp3 ZIP unchanged. The 694-event reduction in that
matrix is a hypothesis until measured, not an accomplished result.

## Identity and reproduction

- Patch/metadata: `patches/php83/held/Criteria-null-alias.{patch,json}`.
- The original file matches the pinned original ZIP member and unchanged exp3
  member. Applying the patch with `--fuzz=0` yields exactly the recorded after SHA.
- Graph project `kaltura-rigel-18.20.0-full`, generation
  `2026-09-25T12:19:00Z`: exact Criteria.php coverage has no recorded issue and
  matching metadata. Graph result/snippet for `getTableForAlias` was confirmed
  against the source. This is a bounded analysis, not exhaustive impact proof.
- Collector verifies both source files and fixture/runner hashes remotely before
  running the pre-staged `/home/vagrant/php-criteria-null-probe` fixture.
- Each process runs network-denied with a read-only source bind, no production
  application access, private temporary directory and time/memory limits.

```sh
python3 tools/php83/criteria-probe/collect.py /path/to/new-report.json
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tools/php83 -p 'test_*.py'
```

Evidence: [`evidence/criteria-null/`](evidence/criteria-null/).
The patch is held, not added to exp2/exp3, production packages or CI. No acceptance
checkbox is closed. Inventory identity/disposition evidence must be refreshed
when selecting this additional patch into a later candidate.

## Independent review and remaining harness limits

Claude independently reran all four real-runtime rows and the 122-test local
suite; Cursor independently ran the same local suite and reviewed the evidence.
Local unit tests do not exercise this new SSH collector. Execution/review is
attributed separately in `evidence/criteria-null/result.json`.

The collector currently uses Python assertions for its guards: run only the
recorded `python3` command, never `python3 -O` or with `PYTHONOPTIMIZE`. Before
reusing it as an automated gate, replace those with unconditional checks and add
fault-injection tests. Failures raise without saving a structured partial
report. SSH config paths and hostname guards are in the fixture commands, not
full environment attestations; existing SSH configs do not pin host keys.
The preserved diagnostic handler records warnings rather than discarding them;
it is a fixture only, not an application error-policy change. Array/object
invalid alias behavior, actual SQL generation and full-call-path integration
are not established by these eight cases.

Grok's bounded attempt timed out (exit 124). OpenCode Muse Spark Free then ran
all 122 local tests and reviewed the patch/harness. Its prompt abbreviated the
evidence path; it looked under `evidence/` rather than `doc/php83/evidence/` and
therefore did **not** review the runtime JSON. This gap is retained explicitly;
Claude and Cursor did review the correctly located runtime evidence. No model
self-identification in CLI prose is treated as verified runtime provenance.
