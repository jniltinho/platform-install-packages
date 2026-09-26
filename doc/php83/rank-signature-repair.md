# Rank signature repair — bounded signature proof, still held

Actual Codex and independent Claude have each executed four full-class
signature/omission processes on baseline74 (native74 and copied83). No artifact
selection, successful rank-body execution or persistence follows from this proof.
The source-only preparation below remains frozen historical provenance. The exact original and exp13 ZIPs contain the same target
bytes. The proposed edit deletes only seven bytes (` = null`) at line1836 of
`api_v3/lib/KalturaEntryService.php`; all names, parameter order, visibility,
untyped/null acceptance, method body and all other file bytes are unchanged.
See [held manifest](evidence/rank-signature-repair/prepared-r1/manifest.json).

## Evidence and rationale

The actual exp13 API primary has one diagnostic group at this path/line, count1.
Its privacy-preserving ledger retains category/location/count and raw stderr hash,
not a free-text message. The optional-before-required attribution is supported by
the source and earlier full-class native83 rank metadata observation, not by
reconstructing missing raw stderr. This does not assert independent exp13 parity.

The [PHP8.0 migration manual](https://www.php.net/manual/en/migration80.deprecated.php)
recommends removing ineffective defaults before required parameters. This
parameter is untyped, so the implicit nullable-type exception does not apply.
The [PHP8.1 migration manual](https://www.php.net/manual/en/migration81.incompatible.php)
also describes required treatment for named arguments. PHP8.0 named-argument
behavior is not a compatibility target for this experiment.

Graph Tier2: ready full-source project, generation2026-09-25T12:19:00Z;
[coverage](evidence/rank-signature-repair/graph-coverage.json) is metadata-current
with no recorded gap for the service hierarchy and three callers. Direct source
reads confirm BaseEntry passes null, Media passes MEDIA_CLIP and Mixing passes
MIX, always as the middle of three positional arguments. Public actions retain
entryId/rank signatures. [Trace](evidence/rank-signature-repair/graph-trace.json)
finds these three callers without pagination. Its ambiguous outbound generic
model method matches are not trusted as resolved dependencies. No exhaustive
absence/dead-code claim is made.

## Historical evidence and the now-executed bounded contract

Earlier native83 original full-class metadata/omission observations, independently
repeated under dispatch-rank, show three required parameters, default unavailable,
and five missing-argument calls raising ArgumentCountError. They contain no
successful rank body. The prior74 run tested dispatcher only: **that historical phase did not execute rank74 reflection
and omissions**. Do not label74 behavior already proven.

The subsequent focused four-process matrix on the exclusively assigned baseline74 lab:
original74, candidate74, original copied83, candidate copied83. Load the complete
real KalturaBaseService and KalturaEntryService without constructors; collect
ReflectionParameter name/position/optional/default/type/by-reference/variadic
metadata and ReflectionMethod required count. Record positional omissions0/1/2
in both engines; named missing-middle/missing-leading controls only83 using
Reflection invokeArgs (no named-argument syntax in a74 file). Every call must fail
before the body with ArgumentCountError. Preserve raw diagnostics and stderr;
the one original83 load deprecation should disappear only in candidate83.
Compare original/candidate within each engine; any74 default-reflection difference
is an explicit metadata delta, not silently normalized or called parity.

These are signature/omission controls, **not positive rank functionality**.
Real database persistence, entry/user context, all three public action flows,
statistics and teardown remain in the [positive plan](rank-functional-plan.md).
Do not add fake peers or a new SQL schema to call this signature change accepted.

## Reproduction (local source preparation only)

```sh
python3 -m unittest discover -s tools/php83/rank-signature-repair -p 'test_*.py'
python3 tools/php83/rank-signature-repair/prepare.py \
  --original /tmp/kaltura-php83-audit/Rigel-18.20.0.zip \
  --exp13 ../platform-install-packages-php83-artifacts/exp13/Rigel-18.20.0-php83-experimental.exp13.zip \
  --output /tmp/rank-signature-new-preparation
```

Output must not exist. The first eight local tests check exact edit, body/prefix identity,
original/archive drift and altered/reordered candidate rejection. Upstream
snapshot whitespace is intentionally preserved; do not claim entire diff clean.

## Completed observations and independent repeat

The first [primary observation](evidence/rank-signature-repair/primary.json) is
preserved as a non-pass: both 74 processes exited 0, but both copied83 attempts
exited 1 before PHP because systemd could not resolve the namespace-mounted
interpreter. The old runner is `reviewed-run-r1.sh`. The only runner correction
prefixes `/usr/bin/env`, deferring interpreter resolution until inside the
unchanged restricted unit. A fresh source stage was used; no app or PHP source
repair was needed. Source/runtime identities remained unchanged even in failure.

[Primary r2](evidence/rank-signature-repair/primary-r2.json) and
[actual Claude repeat](evidence/rank-signature-repair/claude-repeat.json) each
contain four process exits 0 and 16 omission calls (3+3 on 74, 5+5 on copied83).
Every omission raises the exact expected ArgumentCountError; no autoload request
occurs, and no entryPeer or kvote class loads. Three parameters remain required.
The full real two-class sources load, but constructors and positive rank bodies
are deliberately never invoked.

**Observable PHP 7.4 reflection difference, not normalized:** for entryType,
`default_available` changes from true to false; `getDefaultValue()` changes from
null to ReflectionException. Both still report non-optional and required count 3.
The original/candidate positional omissions are identical. On PHP 8.3 the full
parameter metadata is identical; the original's one E_DEPRECATED disappears in
the candidate and no other diagnostic replaces it. This artifact proposal is
PHP 8.3-only; it does not promise PHP 7.4 reflection-default parity.

The collector intentionally exits 2 / OBSERVED_NOT_ACCEPTED. The separate
[explicit validator](../../tools/php83/rank-signature-repair/validate.py) asserts
all four exact bodies, native stdout/stderr, input identities and the known
metadata delta, returning 0 only for this bounded contract. Its 25 local tests
include missing/duplicate modes, bool exit, hidden 74 delta, wrong shared golden,
body access, diagnostic suppression and source/runtime drift. Actual Claude ran
all 25 tests, shell syntax, four fresh processes and the validator, then reviewed
the exact delta and compared all evidence. This is independent of author Codex,
not an independent second reviewer of Claude's own repeat.

[Codex cross-executor comparison](evidence/rank-signature-repair/codex-repeat-comparison.json)
reproduces the match: every record body/stdout/stderr/exit/mode is exact; only the
new owned stage token in the command differs. Source identities and all four
runtime snapshots match. The frozen runtime helper is f2985a7d…da463 and covers
native74, copied83 and module/linked-library identities. Its historical exp12
artifact field is provenance of that helper, not rank artifact authorization.
Claude's earlier scope-only NOT_VERIFIED on that helper was resolved by direct
Codex full-source reading and the final Claude repeat review, not a permission
bypass. The actual executor reports are retained as sanitized public JSON;
private reasoning/hook streams are not committed.

Baseline74 is released; native83 was never accessed in this phase. Three root-owned
read-only stages remain for evidence.
No SQL, whole generated app, package, ZIP rebuild or production operation ran.
Full positive rank persistence/public-action acceptance remains open, and the
held preparation manifest was not rewritten into a selection record.

Reproduce the stored comparison without VM access:

```sh
python3 doc/php83/evidence/rank-signature-repair/compare-repeat.py
```

A future **explicitly owned baseline74** observation uses
`python3 tools/php83/rank-signature-repair/observe.py NEW_REPORT.json` (expected
collector exit 2), then `validate.py NEW_REPORT.json NEW_VALIDATION.json`.
Existing outputs are refused. This command is not permission to acquire the lab.
