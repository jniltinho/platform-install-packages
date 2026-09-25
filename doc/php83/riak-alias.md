# Riak Object alias — held source experiment

Status: preparation only, not selected into exp11 and not backend acceptance.

A four-site lexical repair replaces the reserved local `Object` alias with
`RiakObject`: one import, two constructions and one argument type. It preserves
the resolved provider name `Riak\Object` and every method body, including the
existing `count($objectList)` sibling index. It does not upgrade Doctrine, remove
the driver, install a provider or copy unrelated upstream fixes. Doctrine's
[1.8.2 source](https://github.com/doctrine/cache/blob/1.8.2/lib/Doctrine/Common/Cache/RiakCache.php)
provides precedent for the alias, not proof of this bundled version's behavior.

The preparation verifies the pinned original ZIP, six actual source files,
patch bytes and exact after hash; it stages full real interfaces and parent,
not provider stubs. The intended four-process original/candidate74/83 matrix
retains original compiler failures and candidate load/reflection results.
Candidate checks inspect actual resolved Bucket/Object types, interfaces,
namespace accessors, the expiry constant and the real no-provider stats method.
No constructor, provider IO, cache fetch/save/delete or conflict resolution runs.
The object is explicitly created without a constructor for those local checks;
this is not a working backend instance or application bootstrap.

`run.sh` is restricted to the two named disposable labs and checks a host-supplied
manifest hash plus all frozen source/probe/runner bytes before and after a
read-only, network-denied isolated process. PHP7.4's JSON extension is explicit;
PHP8.3 uses its built-in JSON. Runtime identity must additionally be bracketed by
the coordinator. No VM is touched during preparation. Six Python preparation
checks pass; PHP lint/execution and independent review remain pending.

The full-source graph is ready (generation 2026-09-25T12:19:00Z); all six evidence
paths have matching metadata/no recorded gap, and complete source was directly
read. This is best-effort graph coverage, not proof that Riak is unused.
Cross-project ai-memory retrieval for RiakCache returned no matching history;
the existing provider investigation remains authoritative repository evidence.

Real provider/backend integration remains unresolved as documented in
[riak-provider.md](riak-provider.md). Original74 also rejects the source, so a
candidate load cannot be called original74 functional parity. No release or
whole-application gate is closed by this held syntax experiment.

## Native observation: alias-only candidate rejected

Actual full-source execution on both PHP7.4 and PHP8.3 returns exit255, empty
stdout and native compiler fatal errors for **both** variants. Original source
fails at the reserved import alias (line26). The candidate advances to line207,
then fails because the resolved `Riak\Object` parameter class name itself is
reserved. None of the reflection/namespace/stats checks is reached. The alias
spelling precedent from upstream is therefore **not a sufficient repair**.

The [PHP reserved-name list](https://www.php.net/manual/en/reserved.other-reserved-words.php)
includes `object`; the actual compiler results, rather than assumptions based on
upstream spelling, establish this failure for our precise sources/runtimes.
Source/probe/runner identities are checked pre/post by the immutable stage runner,
and native runtime snapshots match before/after. The baseline74 snapshot helper
retains its old exp11 artifact-context field; that field is not Riak source
attestation. The separate pinned Riak manifest provides source identity.

Evidence: `evidence/riak-alias/primary-observations.json`, `primary-result.json`
and per-process native output files. The held patch is **rejected for selection**;
it is retained as a failed experiment, not integrated into any ZIP. A real
provider compatibility/design decision is needed before changing the resolved
provider type or replacing static typing with runtime checks. No existing driver
or extension is removed, no error is waived, and the seven exp11 compiler
rejections remain unchanged. Independent native83 rejection verification is
assigned separately; no independent runtime completion is implied yet.

Actual Cursor CLI independently executed **both native83 variants** and terminated
exit0 as an executor. Each PHP process still exits255 as expected for the failed
candidate experiment. Native stdout/stderr exactly match primary83; all14 staged
files and runtime snapshots match before/after and the primary identities. See
`cursor-codex-validation.json` and Cursor public evidence. PHP7.4 primary evidence
is not relabeled independently repeated. Candidate rejection is confirmed; the
executor's zero status is not application or patch acceptance.
