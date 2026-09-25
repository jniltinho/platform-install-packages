# Pending authorized runtime commands

No VM ownership/execution during preparation. XML worker owns labs. Obtain explicit
exclusive baseline74 grant before any staging. Native83 VM is not used.

1. Verify frozen-r3.sha256 and primary source manifest; use fresh remote directory
   `/home/vagrant/php-generator-debug-v1` (refuse existing). Stage the exact four
   archive-derived source subtrees from `/tmp/php83-generator-debug-v1-r2` and frozen
   generator-debug-v1/probe.php and run.sh. Do not modify historical stages.
2. Actual72 observations:
   `python3 tools/php83/template-generation/generator-debug-v1/collect.py --phase generate doc/php83/evidence/template-generation/generator-debug-v1/primary-generation.json`
   Expected collector exit2 observation, not acceptance.
3. Validate exact outputs/diagnostics/matrix:
   `python3 tools/php83/template-generation/generator-debug-v1/validate.py doc/php83/evidence/template-generation/generator-debug-v1/primary-generation.json doc/php83/evidence/template-generation/generator-debug-v1/primary-generation-validation.json`
   Expected0 only after actual evidence passes. Stop if mismatch, no repair during run.
4. Hash actual primary-generation.json into REPORT_SHA, then derive literal fixtures:
   `python3 tools/php83/template-generation/generator-debug-v1/prepare_arity.py doc/php83/evidence/template-generation/generator-debug-v1/primary-generation.json "$REPORT_SHA" doc/php83/evidence/template-generation/generator-debug-v1/primary-arity-fixtures`
   This reruns strict generation validation; no fixture is prepared from synthetic
   observations or unvalidated source. Extracts seven actual numeric definitions.
5. Stage exact zero.php, one.php plus frozen arity-run.sh in fresh
   `/home/vagrant/php-generator-debug-arity-v1`, refusing preexisting stage.
6. Execute four isolated numeric calls:
   `python3 tools/php83/template-generation/generator-debug-v1/collect_arity.py doc/php83/evidence/template-generation/generator-debug-v1/primary-generation.json "$REPORT_SHA" doc/php83/evidence/template-generation/generator-debug-v1/primary-arity-fixtures doc/php83/evidence/template-generation/generator-debug-v1/primary-arity.json`
   Exact4, exit0 only for typed integer0/1 constants, true return, zero diagnostics,
   no exceptions and identical pinned source/runtime identities before/after.

Tiny numeric literal fixtures never include or execute a generated script. After
primary review, obtain independent actual CLI repeat under serialized lab ownership.
No source ZIP promotion, SQL, backend or application acceptance.
