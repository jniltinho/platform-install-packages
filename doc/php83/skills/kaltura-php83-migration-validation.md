# Project skill validation — 2026-09-28

Installed skill: `.agents/skills/kaltura-php83-migration/`, exposed in the local
Codex skill directory through a symlink to this versioned source. Upstream was
installed using the bundled GitHub skill installer at commit
b593433ffcb227bd4034f94d5dee6e2a48859e76, then rewritten for this project's scope.
MIT attribution/license and original source hashes are retained. No upstream
install commands, network tools or migration scripts are bundled for execution.

## Adaptations

- Preserve pinned legacy Kaltura/Symfony/Zend/Propel, not modern Symfony/Doctrine.
- Replace generic Composer/framework upgrades with minimal reviewed patches.
- Make Rector optional, pinned and dry-run only before reviewed application.
- Do not require intermediate deployments or claim every deprecation becomes
  fatal in the next minor release, or claim unsupported analyzer coverage rates.
- Prioritize incremental real lab flows while preserving safety and final gates.
- Route history through ai-memory and structural discovery through verified graph
  coverage; missing packaged-source coverage requires exact source reads.
- Separate source mappings, doubles, read-only observations and full acceptance.

## Validation executed

1. Bundled quick_validate.py on both the repository directory and the installed
   symlink: exit0, valid frontmatter/name/structure.
2. Independent Codex forward evaluation, read-only, supplied the skill and AGENTS
   plus six realistic requests without intended answers. All six returned the
   appropriate bounded next actions and limits: broad framework replacement,
   partial SQL vs task closure, held incremental installation, missing graph
   coverage, outer CLI success with nested failures/skips, and the real media flow.
3. Two clarity suggestions were incorporated: distinguish individual skipped
   cases from failed attempts; allow reviewed partial/failing milestone history
   without implying acceptance. No behavior-changing expansion was introduced.
4. No VM, DB, application migration or performance experiment was performed for
   skill validation. This proves structural validity and useful decision guidance
   in six scenarios, not faster execution or PHP compatibility by itself.

Expected practical value: reduce wrong-framework advice, redundant inventory,
false completion and loss of provenance. Measure future usefulness through actual
lab work; no speedup percentage or application acceptance is asserted.
