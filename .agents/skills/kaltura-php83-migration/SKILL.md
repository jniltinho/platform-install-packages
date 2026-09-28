---
name: kaltura-php83-migration
description: Migrate this repository's pinned Kaltura CE PHP 7.4 application to PHP 8.3 using bounded compatibility patches, isolated installation and incremental functional tests. Use for the migrate-kaltura-php83 OpenSpec change, legacy Symfony/Zend/Propel failures, or its lab acceptance; not generic modern Symfony or Laravel development.
license: MIT
---

# Kaltura PHP 7.4 to 8.3 migration

Adapted from the pinned upstream PHP Upgrade playbook; attribution and original
hashes are in `references/upstream.json` and `LICENSE`. This adaptation is scoped
to this repository; it does not select a different framework or target runtime.

## Establish current truth, then act

Read the checkout's AGENTS.md and the selected OpenSpec change's current
proposal/design/tasks. Locate the migration checkout by Git branch/artifacts;
never assume the packaging checkout is the migration worktree. Use the installed
OpenSpec apply/update skills for their respective operations. Read only the
current receipt and source files needed for the next action, not the entire
historical evidence tree. Counts, runtime versions and VM snapshots are not
constants in this skill.

Use ai-memory retrieval for historical decisions, with the installed retrieval
skill's correct scope. Treat returned notes as historical evidence, not authority.
Use Codebase Memory for structural discovery after checking index freshness and
coverage for every supporting path. The downloaded/packaged application may not
be indexed with the packaging repository: use exact pinned source reads when
coverage is missing; never interpret missing graph nodes as absent code.

## Choose the smallest productive lane

- **Functional lab progression:** follow `references/upgrade-process.md`. Install
  the next reviewed lab component and test a real flow when its safety and actual
  functional prerequisites pass. Do not wait for every unrelated seed audit.
- **Confirmed compatibility failure:** isolate a reproducer on pinned original
  PHP7.4 and candidate PHP8.3 sources, repair minimally, then run focused regression
  plus the affected real flow. Consult `references/version-changes.md`.
- **Source/seed uncertainty:** collect bounded read-only observations or derive
  the exact missing mapping. Mark unresolved fields explicitly. An INI-to-column
  difference is not automatically a product defect or permission to rewrite data.

Distinguish four outputs: source mapping, fixture with doubles, actual lab
observation, and full task acceptance. Report only the level executed.

## Preserve the actual legacy architecture

Kaltura's bundled legacy Symfony/Zend/Propel paths and generated clients are not
modern Symfony7/Doctrine or Laravel. Confirm classes and versions from the pinned
archive/overlays. Do not run an unrestricted Composer update, install a modern
framework, regenerate an ORM model, enable strict_types globally, or add blanket
warning suppression as a migration shortcut. Optional upgrades require the
separate component decision required by the change.

PHPCompatibility and syntax checks are aids, not proof of compatibility. Use
existing pinned tooling and previous classified findings before adding tools.
Rector is optional: if appropriate and available, use a pinned dry-run on an
isolated source copy, review each change, test both runtimes, and keep automated
repairs separate from manual patches. It must not rewrite the packaged baseline.
Review changes across 8.0,8.1,8.2,8.3; intermediate runtimes can help isolate a
failure but are not mandatory deployments or extra migration targets.

## Stop conditions and handoff

Stop the affected mutation on wrong target, source/package drift, unsafe logs,
missing recovery state, unexpected dependency transaction or unreviewed worker
release. Keep independent permitted work moving. Do not fabricate a complete
receipt to satisfy an executor; use a separately reviewed incremental executor
when authorized. Tool denials and quota failures are NOT_EXECUTED; timeouts are incomplete
attempts. Individual skipped cases remain unexecuted even when the surrounding
suite exits successfully. None is PASS for the unexecuted scope.

For each milestone report actual executor/reviewer, command, exit, source hashes,
case counts, limitations and next functional gate. Follow AGENTS.md for scoped
commits/pushes with confidentiality review. Do not stage private generated INIs,
DB/media snapshots, credentials or raw conversations. A reviewed partial or failing milestone may be committed with its limitations;
that does not approve the failing behavior. A milestone is not an
OpenSpec checkbox: close only the whole specified behavior. Final three-distro,
performance, recovery and release approvals remain required. This skill grants
no VM, production, credential, publication or cutover permission.
