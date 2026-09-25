# Held explicit doc-comment property repair

Date: 2026-09-25. Phase-1 evidence; no ZIP promotion or release approval.

## Root cause and bounded change

`KalturaDocCommentParser::__construct()` always assigns the array returned by
getDisableRelativeTimeParams to a previously undeclared public property.
PHP 8.3 deprecates its dynamic creation both during construction and while
restoring serialized service-map objects. The second report location,
KalturaServicesMap.php:45, is the unserialize call, not another independent bug.

The held `doc-comment-property.patch` explicitly declares that same public,
untyped property last among the declared members, immediately after
utf8truncate. It adds no global AllowDynamicProperties attribute, changes no
regex/parser logic and does not lower diagnostic reporting. The constructor
still always initializes the value, including [] for absent annotations.
An object instantiated without its constructor, or an artificial serialized
object missing that property, is outside this bounded equivalence claim.

Source and patch identities are recorded in the adjacent JSON metadata. Both
lab originals matched its before hash. Graph coverage for the parser and
service map recorded no gaps; exact constructor/helper source was read.

## Evidence

[Focused report](evidence/doc-comment/focused.json): six annotation inputs
(empty, one/multiple/duplicate names, empty name, case-sensitive tag) preserve
values and serialized-byte SHA256 against **original PHP 7.4**. Four candidate
comparisons pass across native .74/.83 and standard/minimal INI modes.
Same-runtime get_object_vars after serialize/unserialize also matches exactly.
A synthetic legacy serialized public-property entry loads successfully; it is
not represented as an exported complete production cache.

[Apache after](evidence/doc-comment/apache-after.json) runs the existing real
entrypoint HTTP/trusted-HTTPS suite with unchanged harness hashes. Adding only
this declaration to the existing held PDO/date candidate preserves successful
stdout and all exact session/error/JSON assertions. Selected construction and
unserialize diagnostic locations decrease from **4,408 to zero**, as checked by
[the comparator](evidence/doc-comment/comparison.json). This is an occurrence
count for the fixed workload, not a unique-bug count or performance benchmark.
Other diagnostics remain open and are not waived.

Recheck the specific reduction independently:

```sh
python3 tools/php83/compare_doc_comment.py \
  doc/php83/evidence/api-web/apache.json \
  doc/php83/evidence/doc-comment/apache-after.json /tmp/parser-comparison.json
```

The comparator fails on missing before evidence, remaining selected diagnostics,
harness drift, runtime failure or changed output. Five new offline tests cover
these decisions; the final local suite has **65 passing tests**.

## Parallel verification

At the operator's request, Claude and Grok were launched concurrently with
separate responsibilities. Claude owned read-only offline execution/patch
review; Grok owned read-only test-evidence audit without tools. Neither was
allowed to edit files or operate the shared disposable DB; the primary agent
ran the serial destructive fixture matrix.

Claude's first execution was denied by a too-narrow command allowlist and is
not counted as a run. The retry executed the 60 then-existing unit tests with
exit 0, without permission denials. Its source concerns were checked against
the unconditional constructor assignment and four original-7.4 comparisons.
The five comparator tests were added afterward and run by the primary agent.
Advisory reviews are not release approval.

## Cleanup and remaining gates

The parser was restored and compared to original in both VMs. PDO/date were
also restored on .74 and the disposable DB was stopped. The patch remains held;
exp2 still contains only JSON repairs. `.20`, main and package/release paths
are unchanged.

Before a release: continue diagnostic remediation; finish inventory/provider
and feasibility gates; build/install the PHP8.3 package/source combination on
Ubuntu 24.04, Ubuntu 26.04 and Rocky9; exercise full media/worker/UI behavior,
performance and upgrade/rollback; obtain final release approval. No reliable
calendar date follows from this bounded test alone.

## Grok review reconciliation

[Grok completed its parallel audit](evidence/doc-comment/grok-evidence-review.txt).
Its input was a compact focused-output summary and the *pre-patch* Apache report;
it correctly could not establish diagnostic removal from that input alone.
The compact input omitted mode/stderr fields that are present in the full
focused report, and the Apache-after report was generated while Grok ran.
Do not interpret the audit as approval of evidence it had not seen.

A [message-specific check](evidence/doc-comment/focused-diagnostics.json) against
the full retained stderr now confirms 13 original-8.3 dynamic-property notices
and **empty candidate stderr** in each of standard/minimal modes. The later
same-harness Apache comparison independently covers the workload reduction.
Grok's additional suggestions—full historical cache transfer and a real
relative-time consumer case—remain explicitly outside the current bounded
claim. The patch remains held pending broader coverage; no global acceptance
was inferred from either reviewer.
