# Rank positive contract: prepared, not executed

## Decision

Prefer adding this24-case contract to the next owned full API lab flow after
privacy fixes, not provisioning a second miniature AIO/schema just to remove one
deprecation. No patch/default removal is selected. SQL/runtime work is not started.
The existing exp12 API socket fixture is reusable isolation infrastructure but
its permission/session schema does not include entry/kvote/kshow. Full application
rank acceptance would need authorization/context and lifecycle behavior as well.

## Verified real dependency and caller contract

Graph ready generation2026-09-25T12:19:00Z (231336nodes/800641edges). Class search
found exactly four positive kvote/Basekvote/peer nodes; method search finds the
actual addKvote at myStatisticsMgr318–323. Coverage of12 relied files is saved;
SQL files are partial, so exact table ranges are directly retained/read in
schema-candidates.json rather than inferred from graph. No exhaustive/dead-code
claim. Full source pins are joined to immutable exp12 ZIP in source-identities.

- KalturaEntryService1836–1852 retrieves actual entry, validates type/rank,
  builds actual kvote, uses getKuser()->getId(), then saves.
- BaseEntry anonymousRankAction passes null type and disables actual response
  cache; Media passes MEDIA_CLIP; Mixing passes MIX. All use three positional
  arguments to the protected method. Public actions expose entryId/rank.
- KalturaBaseService298–316 uses a private cached kuser, otherwise creates one
  through real kuserPeer and validates status. A focused fixture could inject an
  actual hydrated kuser via Reflection, explicitly excluding creation/auth paths;
  prefer authenticated real API context when reusing the full lab.
- kvote14–30 invokes actual myStatisticsMgr before Basekvote save. Statistics
  modifies entry votes/total_rank/rank and queues dirty objects. MIX may load
  kshow; actual deferred saveAllModified is a separate lifecycle action. In-memory
  statistics are not evidence that an entry row was persisted.
- Basekvote doSave910–974 delegates actual INSERT to kvotePeer and sets returned
  primary key. No fake peer/model/statistics or overridden save is acceptable.

## Smallest execution proposal

Use separate seeded entries/users under an explicitly owned synthetic partner,
not existing user's content. Full original74 baseline versus selected exp12 on83
first, no candidate patch. Execute the24 cases in cases.json: six positional
positive boundary ranks1/5, six invalid0/6, three valid named83-only public calls,
two type mismatch, one missing entry, five original83 omissions and metadata.
PHP74 must never parse named-call syntax; its shared positional cohort is15
cases plus separately recorded metadata (not pretending all24 run on74).
Record exact result types/API exception codes, all diagnostics/raw stderr,
kvote count+entry/user/rank/status values before/after, entry object statistics,
entry database statistics before/after actual request teardown, and untouched
control rows. Positive cases expect null return and one real inserted vote;
errors/omissions expect no vote write. Auto IDs/timestamps require declared
narrow provenance treatment, never blanket output normalization.

Prefer full API calls for real auth/serialization/lifecycle; the protected
Reflection omission checks remain separately scoped. Capture metadata/default
availability before any future patch; no metadata generator parity assumed.
The prepared matrix is input design, not runtime evidence or an implemented
SQL runner. Five local tests only validate its inventory.

## Reuse trade-off / concrete blockers

Existing API socket runner starts isolated MariaDB under a unique tempdatadir,
checks @@datadir, and binds only a synthetic Unix socket. This can be reused if
full-lab API coverage remains unavailable, but new schemas must not be invented.
The exact shipped source DDL uses legacy `Type=InnoDB`; kvote's kuser_id foreign
key names kshow(id), matching old generated relationship naming. Do not silently
rewrite these to make a test pass. Compare the actual deployed baseline schema
and generated peer fields before selecting any minimal new DDL. Current API
fixture has kuser/partner but no entry/kvote/kshow; adding3tables is not yet proven
sufficient because real hooks/context/teardown may access further tables.

Therefore cost of a new socket model harness is materially higher and risks
schema drift/partial lifecycle claims. Next smallest runnable step, after named
lab handoff: a read-only schema/model compatibility inventory and one synthetic
real API rank request in the existing full lab, within approved privacy guards.
Then fill the24 rows and independent repeat. No broad schema expansion, backend
repair, source patch, package/release or VM action is authorized by this plan.

## Actual local independent review

Claude's bounded120s review timed out (exit124), so it is not counted as executed
review/tests. Actual OpenCode free then completed (exit0), executed the five
inventory tests and reviewed plan/matrix. It confirmed24 planned rows and15
shared74 positional cases, and the narrower reuse decision. Its public execution
report is opencode-public.json. No runtime evidence was produced by either CLI.
