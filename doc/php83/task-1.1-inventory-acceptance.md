# Task 1.1 — reproducible source inventory acceptance

Change: `migrate-kaltura-php83`. Scope: inventory only, not feasibility, runtime
acceptance, redistribution compliance or task 5.4 completion.

## Acceptance evidence

- Pinned original Rigel archive SHA256
  `58d534d09b3b75c9a8333957268c884f79032638b2d44a278b1992fda1b0ab28`:
  15,175 regular members extracted exclusively and every file hash verified;
  186,369,136 source bytes. No application code executed.
- Original/package identity join: 13,454 packaged PHP paths, 11,782 identical
  originals, 2 changed originals and 1,670 additional package-owned PHP paths.
  Every owner and source revision is retained. Non-PHP rows do not claim absence
  from a PHP-only package index.
- Dependency inventory: 20 vendor-directory attribution records, all 4,999 vendor
  file identities, 12 non-vendor notice scopes, literal declarations and explicit
  unresolved component revision/license dispositions. MaxMind's 35 source files
  additionally match two official commit-pinned sources and Apache-2.0 declarations.
- Generated/client inventory: 179 original path candidates, 37 generated-header
  records, 3 explicitly declared client scopes, 112 packaged generator PHP files
  and 714 broader package client-path candidates. These overlapping counts are
  not a count of independently executed clients.
- PHP entrypoints: original member/classification registry and 5,537 invocation
  candidates, joined with 18,336 historical package entrypoint candidates.
  Bounded scan omissions and dynamic/regex limitations are explicit, not PASS.
- Build-path selection: 13 source-anchored route declarations distinguish selected
  Noble/Ubuntu26.04/EL9 workflow paths, installation/CLI/cron/plugin/web routes,
  explicitly historical Naos targets and alternative unselected build paths.
  This is source selection evidence, not a claim of live activation.

## Reproduction and independent validation

Use `evidence/inventory-closure-r1/report.md` and its publication manifest.
The deterministic compressed registry decompresses to SHA256
`4cd9212e48d806ce7a5cdf852712f4f685cd32182add9a0ec0dacd46567ed162`.
The independent complete extraction/inventory rebuild was byte-identical.
The final inventory suite has 17 passing tests; corrected notice census has
8 independently passing tests and a byte-identical rebuild. MaxMind independent
comparison matches all 35 files; five negative cases reject invalid inputs.
Route generation has five author tests; independent final scope review is
recorded under `evidence/task11-independent-scope-r1/`.

Actual Claude CLI independently executed the original notice census (exit0,
5 tests/rebuild/comparison), exposing three issues corrected and independently
retested in R2. Other Claude/OpenCode inventory/route attempts were incomplete;
Cursor could not authenticate. These attempts are not relabeled as passes.

## Meaning of completion and remaining obligations

This accepts a reproducible inventory with explicit known and unknown metadata;
it does not turn unknown versions/licenses into verified declarations, claim
exhaustive dynamic reachability, or approve distribution without notices.
Nested/vendor attribution uncertainties and original bundle omissions remain
recorded in the inventories for feasibility/component/source-change and release
review. Static findings, compatibility/runtime/client execution and full detailed
coverage remain their separate tasks. Original application/released packages,
production `.20`, held workers and publication gates were not changed.

Task 1.2 is next: complete the isolated published-PHP7.4 baseline protocol and
actual functional workload, keeping its approved privacy overlay explicitly
separate from a published-intact baseline. Short untimed media success is not
full baseline, HTTPS/HLS/long-fixture or timing acceptance.
