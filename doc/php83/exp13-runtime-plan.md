# Exp13 actual-artifact runtime regression plan

**CURRENT: primary + actual Claude independent API4/CLI48 executed; bounded
comparison passed, no application/release acceptance.** See
[evidence/current result](evidence/exp13-runtime/README.md). The plan and
preparation sections below are chronological; pending statements are historical.
Reuse the
reviewed exp12 scopes in a separately versioned exp13 adapter after final artifact
verification and exclusive coordinator ownership. Never edit frozen exp12 tools
or relabel held-source observations as built-artifact results. Compiler coverage
is owned separately by the coordinator; this plan does not duplicate it.

## Artifact gates and identities

- Original ZIP: 58d534d09b3b75c9a8333957268c884f79032638b2d44a278b1992fda1b0ab28.
- Exp12 reference ZIP: de5e61a1b54f472e605ef2e87669302a3915616fd85378e0f05706fcb06a7e8b.
- Exp13 verified ZIP: **6d0bc4947207e6c5457b7843948d263aa8d5f251480e58cbf9086c0add79a944**,
  91,210,445 bytes; verification.json records two equal builds. Consume coordinator-selected manifest and
  independently verified two-identical-build receipt. Do not infer a pin from
  proposed source hashes. Proposed manifest SHA is
  b6ec7cc58a1828611d9c4558a8557eaa6fbf57ea72a40ef02e2095d9af177b17;
  future selected metadata must be recorded independently, not overwrite it.
- Expected inventory is75 unique targets, preserving62 exp12 entries, three
  cumulative replacements and ten new targets. Exact artifact delta is13 source
  paths (12 modifications/one addition), subject to actual verifier result.
- Bind every loaded file to actual ZIP bytes, selected path/hash and immutable
  extracted tree. Frozen held fixtures must join those exact bytes before reuse;
  source replay alone is not proof of actual ZIP execution.
- Preserve native version/SAPI/INI/module/shared-library identities, source and
  harness pre/post checks, fresh start/end/exit ledgers and cleanup receipts on
  every phase, including failed phases. Same hash is not evidence of fresh runs.

The new previous-artifact join MUST use `/home/vagrant/php-exp12-regression/api/verify-source.py`
and require de5e61a1b54f472e605ef2e87669302a3915616fd85378e0f05706fcb06a7e8b;
current uses only fresh php-exp13-regression and the final pin above. Any lingering
exp11 verifier/reference in the new API4/CLI48 adapter is a defect. Record original
upstream ZIP provenance separately from the prior/current artifact pair.

## Reusable matrices and adaptation seams

| Scope | Reuse | Required exp13 adaptation / retained boundary |
|---|---|---|
| API4 | exp12-api/{collect.py,run-apache.sh,start-db.sh,verify-source.py} | Original74 success, original83 signature fatal, exp12/83 and exp13/83. Fresh owned synthetic DB only, whitelisted output, no KS export; finally stop exact owned unit and verify source after failure. |
| CLI48 | exp12-regression/{batch.py,run-one.sh} | Keep original74 twelve and original83/exp12/exp13 twelve each; expected original83 fatal rows are not successes. |
| Curly68 | exp12-api/collect-curly.py and frozen probe | Actual exp13 class bytes; preserve all cases and typed outcomes. |
| Additions17 | exp12-api/{collect-additions.py,run-additions.sh,addition-corpus.json,validate-additions.py} | Preserve exact stdout/stderr/exit contract, complete case inventory, native fatal controls and loaded-source identities. Old validator hardpins exp11/exp12 and nine Pake/DEBUG loaded fields: cannot reuse unchanged or broaden to arbitrary hash replacement. Join exp12/13 first; any new exact field allowance needs case/path/source proof. |
| Generator72 | exp12-api/generator | Candidate loaded from full exp13 read-only mount; retained32-file prerequisite control. Existing stage.py rebuilds a held cohort then byte-joins exp12: new adapter must join actual exp13 dependencies, not silently use held originals. No generated app executes; no whole exp13-on74 claim. |
| Criteria4 | exp12-api/criteria | Same19 filter +16 return +2 invalid controls, exp12→13 native83. Old stage.py derives exp11→12 repair; replace that staging seam with actual ZIP pair joins, not another attribute insertion. Keep unrelated warning control and strict cross-engine cache-layout FAIL. |
| XML38 | xml-lifecycle-fix/{prepare-native.py,prepare-chain.py,collect-native.py,collect-chain.py,contract-r2.py,reconcile.py} | Join kConf/kSoapClient/new helper and complete fixture closure to exp13. Preserve original44-row lifecycle evidence separately. Actual38 held corpus has exact dual diagnostic-channel ledger, native SoapFault wrapping controls, loader ownership/LIFO/custom wrapper/finally contracts. Do not manufacture missing SOAP stderr or claim network/fiber acceptance. |
| AWS134 | serialization-contracts R3 tools/report_contract.py/reconcile-r3.py | Preserve38 original74 and96 native83 observations with actual imported74 wire bytes. Join all actual exp13 loaded family/cache files; retain cachefix-only control separately and original83 reversed-implode failures. Source/payload identity must come from final ZIP, not held stage. |
| Returns9 + SQL2×91 | return-contracts and return-contracts-sql | Reuse explicit typed/error/effect oracles and source-pinned seams, but join actual exp13 classes/statement/dependencies. SQL uses copied83 on baseline74, AF_UNIX fresh DB per cohort, hides real sockets; native83 has no server and must not gain packages. Preserve original/prerequisite fatal and remaining diagnostics. |

The above inventory is read from existing harness/docs, not a new graph-wide
structural or completeness claim. Directly inspected source seams include
exp12-api stage.sh/collect.py/validate-additions.py, criteria/stage.py and
generator/stage.py, full exp12-regression/batch.py and return-contracts/observe.py.
Coordinator graph check found packaging index points to the main sibling, with
exp12-regression/batch.py missing from that index; these migration-worktree claims
therefore use exact direct-source fallback, not graph completeness. Existing
source-family graph audits remain in their respective
docs; new structural assumptions require fresh graph coverage/direct source reads.

## Diagnostics: measure, do not fit the forecast

Exp12 API measured **17 groups/371 events**. That is the reference, **not an
expected exp13 pass count**. Classify actual exp13 groups by path, source line,
severity, exact message and multiplicity. Map each intended disappearance to its
selected family and loaded source; retain every unrelated/new diagnostic and raw
channel. Do not subtract held-fixture counts from371 or change an oracle merely
to accept fewer warnings. Logical HTTP/auth/trusted-HTTPS/rejected-CA results must
remain exact; signature fatal control remains explicit. Intrinsic API/privacy
limitations remain outside this bounded synthetic matrix and block real USER
work until the separate privacy gate is satisfied.

## Wire and state compatibility are explicit release gates

AWS exp13 writes native O where original74/original83 write/read C. Candidate
reads legacy C, but old readers reject new O: **known incompatibility**, not
universal serialization parity. Keep exact typed getter/state results separate
from wire equality. Replay actual74 payload bytes, invalid UTF8 write-time
failure, malformed payloads, cache hit/expiry/corrupt/refresh and rollback-reader
negatives. No authentic credentials or shared application cache.

Deployment still needs selected/rehearsed worker drain + isolated versioned cache
or snapshot/restore recovery. This plan does not select that operational policy.
Criteria's pre-existing cross-engine serialized-property ordering/cache-key risk
remains FAIL; logical preservation does not convert byte parity to PASS. Neither
family is fixed by custom blanket serialization or erasing cache evidence.

## Prioritized artifact composition slice (not a new release requirement)

The family counts above identify available reusable corpora, not a demand to
repeat every historical source probe before any progress. Start with the existing
API4/CLI48 artifact integration matrix, preserving its complete assertions. Reuse
curly/additions/Criteria/generator only where actual loaded dependencies or the
selected13-path delta intersect; establish exact unchanged source joins for
unchanged families without falsely calling those joins new execution. Mark each such family
**NOT_RERUN_SOURCE_JOIN_ONLY**, never a fresh runtime PASS.

For new families choose a bounded composition slice with explicit case IDs before
execution: XML loader ownership + custom callback + nested SOAP/finally + native
exception channels; AWS actual74 C import + candidate O write/read + old-reader
rejection + real FileCache hit/expiry + invalid-UTF8 failure; returns real typed
PDO/Propel/Kaltura/Debug operation and transaction/cache effects. Prefer an intact
existing small matrix when filtering would weaken its complete oracle. Preserve
all assertions for every reused matrix/case, including diagnostic/raw channels;
never remove a failing case after observing it. Reference previous full held
corpus evidence as historical, not new artifact evidence. Record excluded cases
and rationale explicitly; expand only when a composition difference warrants it
or a pre-existing release gate requires it. Coordinator chooses this slice during
adapter review; this plan adds no unapproved release scope.

## Ordered command contract for the future reviewed adapter

Commands below specify the newly prepared paths; independent review is pending. They are
not executable approval and must not be pointed at frozen exp12 tools with a
changed ZIP argument (many paths/pins/matrices are hardcoded).

1. Freeze tools/php83/exp13-api and exp13-regression adapters after local tests
   and actual independent CLI review. Every shell gets its own `bash -n` call.
   Test wrong/current/prior pins, duplicate/missing/reordered cases, source drift,
   unexpected diagnostics, raw-body/hash binding and cleanup failure controls.
2. Set E=doc/php83/evidence/exp13-runtime and T=tools/php83/exp13-api only after
   these directories exist and are reviewed. Outputs must be new filenames.
   Run `python3 "$T/runtime-identity.py" "$E/runtime-before.json"` and the
   corresponding runtime83-identity.py; stage.sh74/83 must use fresh immutable
   php-exp13-regression paths and the final verified artifact pin.
3. `python3 "$T/collect.py" "$E/api-primary.json"`; invoke each lab's new
   exp13-regression/batch.py, retaining actual command/exit/stdout/stderr. First feedback ends here: **API4+CLI48 only**. Curly/additions and other
   family adapters are later explicitly selected phases, not this initial batch.
4. Run reviewed artifact-join adapters for generator/Criteria/XML/AWS/returns,
   each with complete pinned input manifest and isolated stages. SQL and API
   serialize baseline74 ownership; no overlapping DB units/app fixture execution.
   Wire74 collection precedes83 reader cases and has immutable payload binding.
5. ALWAYS capture fresh post identities and source checks and reconcile cleanup.
   Independent actual Claude/Cursor/OpenCode execution repeats the same frozen
   matrix in new evidence/owned DBs, not just revalidating existing JSON. Report
   partial/timeout/fatal records honestly; do not overwrite or drop failures.
6. Compare exact bodies/stdout/stderr and typed contracts; exclude only explicitly
   documented nondeterministic envelope duration/UUID/stage fields. No generic
   source-path/diagnostic regex normalization. Consolidate per-scope actual
   counts, matched/failed/not-run gates and provenance, then release VM slots.

No production, package/build publishing, .20 access, full media baseline,
performance claim, TLS browser workload, cache deployment or release acceptance
follows automatically. Goal is one coherent actual-artifact regression pass,
not a growing substitute for the still-open full application baseline.

## Actual plan review and corrections

Actual Cursor CLI exited0 after read-only review (82.8s); public receipt is
`evidence/exp13-runtime/cursor-plan-public.json`. Its verdict was NOT_READY for
three documentation gaps: prior verifier remap, explicit NOT_RERUN status and
initial-batch boundary. All three are now explicit above. This is an author
correction after rejected initial review, not a fabricated reviewer approval.
Final ZIP identity arrived after that review and is recorded above. Adapter
review/tests must still validate these concrete implementation obligations.

## Minimal adapter preparation status

New exp13-api/exp13-regression preserve frozen12 parents (hash map tested), use
exact current/prior pins, reject duplicate/symlink ZIP entries and restrict stage
tar to API/CLI scopes. Author31 local tests and four individual shell parses pass.
Claude and Cursor adapter-review attempts both timed out180s with empty stdout;
no independent tests or approval are inferred from either. Public receipts are
retained under exp13-runtime. OpenCode free fallback also timed out120s after public progress text, without
a final verdict/test count; that is not an approved CLI review. No VM action
has occurred; proposed orchestration scripts are evidence/preparation only.

Root authorized a short independent Codex delta review instead of indefinite CLI
prep retries. Two bounded guards now add: exact eight-source original ZIP joins
pre/post (not full loaded closure or full baseline attestation), and incremental
API records with both current/prior post-source checks in finally even after
startup/case/cleanup errors. Author37 local tests pass; three CLI preparation
failures remain unchanged. Independent native repeat is still required.
