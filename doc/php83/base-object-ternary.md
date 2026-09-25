# Held baseObjectUtils nested ternary repair

## Scope and decision

**HELD, experimental PHP 8.3 only. No ZIP/package/release promotion.**
The remaining compiler rejection is `alpha/apps/kaltura/lib/baseObjectUtils.class.php:474`.
The patch inserts exactly two parentheses around the first ternary, preserving PHP
7.4's **left association**, not guessing intended XML formatting:

```php
$res .= ($xml_element_name == NULL ? "" :
    $close_xml_element) ? "/>\n" : ">\n" ;
```

A null-equivalent element name therefore still appends `>\n`, rather than the empty
string a right-associated rewrite would return. The [PHP ternary associativity
RFC](https://wiki.php.net/rfc/ternary_associativity) and [PHP 8 migration
notes](https://www.php.net/manual/en/migration80.incompatible.php) explain the
language transition; actual PHP 7.4 execution below establishes this source's behavior.

## Identity and byte proof

[Held manifest](../../patches/php83/held/base-object-ternary/manifest.json),
[patch](../../patches/php83/held/base-object-ternary/base-object-ternary.patch),
[source proof](evidence/base-object-ternary/source-proof.json).
Original ZIP, exp10 ZIP, and immutable source agree on all eight loaded source
files. Exact target before SHA-256:
`1834b0ce9ab903af000e95c6a1c065a8dfaa64a91cd454a57de3b44824ee9e03`.
No other source byte changes; line count unchanged. Strict GNU patch replay uses
`--fuzz=0`, rejects offsets, and checks candidate hash. The builder refuses upstream
hash drift and ambiguous matching. Source and metadata are separate from runtime proof.

## Executed behavior

[Primary r2 report](evidence/base-object-ternary/primary-r2.json):
147 cases in each of original74, candidate74, candidate83 (**441 positive rows**),
with identical output and model-call traces. Original83 is an explicit exit255
compiler fatal control, not a functional run.

- 130 fixed truth-table cases: ten element names (null, false, integer/float zero,
  empty string, string zero, named string, true, positive/negative integer) ×
  thirteen close values (null/false/zero/empty/string-zero plus truthy strings,
  integers, arrays and object). Independent fixed expected prefix/suffix table.
- Five field paths: flat names, associative alias, escaped extra map, actual
  `myBaseObject::envokeMethod` direct and nested invocation; field/getter trace parity.
- Twelve **actual `kAssetUtils::createAssets` caller** executions: duration zero,
  negative and positive × null/nonempty credit × ready/not-ready. Real escaping,
  output capture and synthetic model data; no database or media access.

Eight full original classes/interfaces are loaded, not copied method excerpts:
baseObjectUtils, myBaseObject, kAssetUtils, kString, Propel BaseObject/BasePeer,
entryStatus and BaseEnum. Only `TernaryModel extends BaseObject` is a synthetic
nonpersistent data/trace fixture. This does not validate generated ORM models,
real entry retrieval, HTTP templates, database integration or all callers.
Graph inbound evidence found the asset caller and three editor templates; templates
were not executed. Coverage was checked for each of the eight loaded files, with
no recorded gap/metadata match; that best-effort result is not completeness proof.

## Diagnostics and isolation

Original74 emits one load-phase ternary E_DEPRECATED at line474; both candidates
remove it. Candidate83 retains **five** real myBaseObject Iterator return-type
E_DEPRECATED diagnostics at lines473,487,480,494,465. These remain unresolved;
there is no claim of warning-free compatibility. Collector checks exact structured
messages, source, line, severity and phase. r2 records full stderr and SHA-256;
the handler returns false, retaining the native error channel.

Initial probe captured diagnostics but returned true, suppressing native stderr.
Its files and initial failed collector report are retained, explicitly superseded
by r2; initial collector correctly failed on the five not-yet-enumerated notices.
No old evidence was overwritten. Original74 initial raw command exit0 was observed
but not written as a standalone exit file; r2 embeds all four actual process exits.

Fresh [r2 before](evidence/base-object-ternary/r2-runtime-before.json) and
[after](evidence/base-object-ternary/r2-runtime-after.json) identities are exactly equal:
55 interpreter/module/Apache objects, linked libraries, three runtime modes and INI
hashes from the existing pinned runtime collector. Every run verifies remote source
and harness bytes before/after. Dedicated fresh read-only stage, private network,
socket syscall denial, protected home/system, private temp/devices, no privilege
escalation, resource bounds and inaccessible Kaltura/MySQL data; no SQL.

## Reproduce (coordinator-exclusive baseline74 ownership required)

```bash
python3 -m unittest discover -s tools/php83/base-object-ternary -p 'test_*.py' -v
python3 tools/php83/exp10-api/runtime-identity.py NEW-before.json
python3 tools/php83/base-object-ternary/collect.py NEW-report.json
python3 tools/php83/exp10-api/runtime-identity.py NEW-after.json
```

Collector refuses existing output. It uses the frozen disposable r2 guest stage;
do not restage or run concurrently with another lab owner. Ten local tests cover
two-byte proof, source drift, recorded positive execution, timeout/boolean exits,
wrong association, extra diagnostics, source hash, missing case and side-effect drift.
Actual independent CLI review/repeat is coordinator-owned and separate from these
primary results. T0-04/T0-05/T0-06 and release gates remain open.

## Post-review validator hardening (local replay, not new VM execution)

The initial reviewed collector checked four records but not unique mode identity:
a duplicated candidate74 row could replace candidate83 and still claim 441 rows.
The parent discovered this gap; OpenCode and Cursor's original advisory reviews
missed it. Actual primary and Claude reports contain all four distinct modes.
Original reviewed collector/tests are preserved as `reviewed-r2-collect.py` and
`reviewed-r2-test_ternary.py` under this evidence directory.

After both independent review processes terminated, the collector was hardened to
require the exact ordered mode sequence: original74, candidate74, candidate83,
original83. It now also checks exact native stderr against the already-constrained
JSON diagnostic records, retained stderr SHA-256, and the exact original83 fatal
channel (five dependency notices plus compiler fatal, empty stdout). Extra native
output is not silently accepted. Harness identity uses five explicit filenames,
including the test file, rather than globbing directory contents.

[Hardening replay](evidence/base-object-ternary/hardening-replay.json) validates both
retained actual primary and Claude records with the new validator; both pass.
This is **local revalidation of recorded runtime executions**, not a new VM run.
The PHP probe, guest runner, source and held patch are unchanged. Expanded local
suite: **21 tests PASS**, including duplicate/missing/unknown/extra/reordered modes,
extra/missing stderr, altered fatal stdout/stderr and stderr-hash drift. The old
10-test evidence is retained. Actual Cursor follow-up executed all 21 tests and revalidated both retained
reports successfully, with unchanged frozen identities. Its adversarial review
confirmed that the remaining 17 rows use native74 parity, not independent golden
expectations: identical tampering in all three retained outputs can pass those
comparisons. Only the first 130 truth-table rows have independent fixed expected
values. This oracle limitation does not establish full application acceptance.
See [Cursor follow-up](evidence/autoload83/cursor-hardening-review.txt).
