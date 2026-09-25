# Original parser caches and real annotation consumer

Date: 2026-09-25. Follow-up to the held [property declaration](doc-comment-property.md),
not artifact promotion or release approval.

## Full original-object cache transfer

`doc-comment-export` ran under the unchanged PHP 7.4 original tree in the
socket-denied, unprivileged fixture runner. It exported six **complete parser
objects** as base64 PHP serialization, with the producer PHP version, verified
original parser SHA256 and per-payload SHA256. Inputs are the six synthetic
comments from the earlier fixture; there is no production cache/data export.
The checked-in fixture is `tools/php83/patch-tests/doc-comment-legacy-cache.json`.

The new consumer verifies each payload hash, restricts unserialize to
KalturaDocCommentParser, compares all public fields and ordering against a fresh
parse, and requires both restored and freshly parsed serialization to equal
the exact original 7.4 bytes. [Four comparisons](evidence/doc-comment-consumer/cache.json)
pass on candidate PHP 7.4/8.3 in standard/minimal modes. The original empty
comment already contains this property as an empty array; declaring it did not
invent a field absent from constructor-produced caches.

This tests complete individual parser objects, not an entire historical
KalturaServicesMap cache or an artificial object built without its constructor.

## Real consumer and conversion

[The consumer report](evidence/doc-comment-consumer/report.json) uses actual
API bootstrap, KalturaActionReflector, KalturaParamInfo and request deserializer,
without DB access or invoking a service action. It reflects the **real** mixed
PlaylistService::updateAction docblock: `playlist` disables relative-time
conversion, while `id` and `updateStats` do not. The full parsed docblock's
serialized hash also matches original 7.4.

A small synthetic action signature with two synthetic KalturaObject containers
then exercises the real reflection/deserialization path. Both objects contain
a `@var time` property with `-3600`. The marked argument preserves the literal;
the unmarked argument converts to an integer in the current-time-minus-one-hour
window. Only the private fixture config sets max_relative_time=86400. No clock,
parser, reflection or conversion implementation is mocked.

The first fixture used top-level scalar time parameters and expected conversion.
Original 7.4 rejected that assertion: KalturaPropertyInfo normalizes the scalar
type to int. The test was corrected to nested time properties, the actual
conversion path; no application change was made for that harness mistake.
Both final candidate comparisons pass. Other existing deprecations remain
visible and are not accepted as a clean-runtime result.

Graph discovery/coverage checked KalturaActionReflector, KalturaDocCommentParser,
PlaylistService, KalturaParamInfo, KalturaPropertyInfo, KalturaRequestDeserializer
and kTime (ready generation 2026-09-25T12:19:00Z, no recorded gaps for these paths).
The exact source was read; no exhaustive graph claim is made.

## Parallel CLI tasks and honest execution accounting

The operator asked for Claude/Grok in parallel again:

- [Claude executed nine HTTP-client unit tests](evidence/doc-comment-consumer/claude-http-tests.txt),
  all passing. These are mocked client tests, not new VM/TLS execution.
- [Grok read the integrity verifier but its CLI blocked execution](evidence/doc-comment-consumer/grok-integrity-attempt.txt).
  A retry supplied the complete read-only source, but execution was still denied.
  **No hash test execution is attributed to Grok**, and no protection was bypassed.
- The primary agent separately ran the read-only verifier and recorded
  [the result](evidence/doc-comment-consumer/integrity.json): original-source and
  held-patch hashes match for parser/PDO/date; exp2 retains its published
  experimental identity. This does not qualify exp2 as a release.

The final primary-agent local suite has **68 passing tests**, including three
new original-cache provenance/payload checks. PHP consumer/cache fixtures ran
serially in the labs; no concurrent destructive DB work was delegated.

## Reproduce and cleanup

Use the held parser patch only in each candidate tree. Copy the new consumer,
cache JSON and exporter changes beside the existing fixture harness, then run:

```sh
python3 tools/php83/patch-tests/collect.py /tmp/cache.json --case doc-comment-cache
python3 tools/php83/patch-tests/collect.py /tmp/consumer.json \
  --case doc-comment-consumer --mode standard
python3 -m unittest discover -s tools/php83 -p 'test_*.py'
```

To reproduce the original cache export, run `run-one.sh original
 doc-comment-export minimal` on the isolated .74 host. Verify the output's
source_sha256 against held metadata before replacing the committed fixture.

Both candidate parser files were restored and compared to originals. No DB
server was needed or started in this follow-up. `.20`, main, package workflows,
releases and exp2 are unchanged; the parser patch stays held while broader
migration diagnostics and acceptance gates are still open.
