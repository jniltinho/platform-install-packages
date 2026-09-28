# Curated packaging route selection

This source-only supplement supplies 13 anchored declarations, not an exhaustive PHP entrypoint inventory. It reuses the checksum-verified authorized-real-r1 archive inventory and joins five exact packaged cron/init candidates with their original package owners. The consolidated inventory separately owns original ZIP per-file discovery.

Current CI explicitly selects Noble/Ubuntu 26.04 DEB builders and EL9 RPM. The native batch start invokes PHP under a maintenance guard; its `ps/awk` process-search line is not an invocation. Front declares API cron installation but explicitly comments out cleanup cron. Packaged DWH/Kava templates alone do not establish activation. DB postinst declares plugin/default/permission/content installation calls. The reviewed Apache template supplies API routing, with its stats query condition retained. Client-generator unpacking proves packaging input, not all generated clients' execution. Naos/Jessie/Wheezy installer text is explicit historical targeting; alternative build_all is not selected by this workflow, but neither is asserted globally unused.

Current migration source bytes, hashed in sources.json and checked at generation, are authority. Original-sibling graph coverage is retained separately; generation 2026-09-25T19:28:02Z is best effort and includes not-tracked/missing files. No graph completeness or cross-worktree freshness claim is made.

## Reproduce

From the migration checkout:

```
PYTHONDONTWRITEBYTECODE=1 python3 tools/php83/entrypoint-inventory-r1/test_inventory.py -v
PYTHONDONTWRITEBYTECODE=1 python3 tools/php83/entrypoint-inventory-r1/build.py --output /an/absent/output.json
```

Five author tests passed (exit0): deterministic generation, false completion flags, changed source hash, missing anchor, missing archive candidate. Original build exit0; output SHA cab11981558027198246f05322940585bad9ed2c7ef4b4ef3126d65d0e849a50. Output creation is exclusive. Source pins are revision evidence, not signatures or protections against an actor editing both manifest and sources.

No indexed script, package hook, network, VM, DB, service, or installer was executed. Private installed overlays are not identified by repository hook hashes. Runtime reachability, all plugin entrypoints, generated-client use, and full task1.1 closure remain unverified. The actual Claude review attempt is recorded separately; its terminal result must not be inferred from these author tests.

Actual Claude CLI: stdin prompt after `--allowedTools Read Bash`, `timeout 70s claude -p --max-turns 5 --output-format json`; terminal exit1, `error_max_turns`, no permission denials. No final review verdict or independently observable test output was returned. This attempt is INCOMPLETE, not a review/test PASS. All four frozen hashes rechecked successfully afterward. No automatic retry or denial bypass.
