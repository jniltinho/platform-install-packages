# Riak provider prerequisite — unresolved, no waiver

The unchanged bundled `vendor/aws/Doctrine/Common/Cache/RiakCache.php` is one of
seven retained baseline compiler rejections. Its exact source and original/exp10
identity are already recorded in the [remaining syntax plan](remaining-baseline-syntax-plan.md).
Graph generation2026-09-25T12:19:00Z remains ready; the exact file has matching
coverage metadata and no recorded gap. A class-level zero-edge trace is not proof
that this driver is unreachable. [Coverage](evidence/riak-provider/coverage.json).

## Provider identity and actual laboratory observation

Doctrine's [1.8 documentation](https://www.doctrine-project.org/projects/doctrine-cache/en/1.8/index.html#riakcache)
identifies the native `riak` extension as the dependency. Its linked upstream is
[php-riak/php_riak](https://github.com/php-riak/php_riak), not an interchangeable
modern HTTP client. The resolved upstream master commit on2026-09-25 is
`8144814d8b655e5b6b12f9fe39961245a5e915f1` (commit date2017-03-13).
[Retrieved-file identities](evidence/riak-provider/upstream-identities.json)
pin README, CI, license, extension header and object implementation bytes.

At that commit the [CI matrix](https://github.com/php-riak/php_riak/blob/8144814d8b655e5b6b12f9fe39961245a5e915f1/.travis.yml)
contains PHP5.3–5.6, not PHP8.3. The native object implementation registers the
`Riak\Object` class and uses legacy Zend API macros. This is a compatibility
risk requiring a real build/runtime investigation, not proof that every possible
fork is incompatible. No extension was compiled, installed or enabled here.

A fresh [native PHP8.3 lab inventory](evidence/riak-provider/native83-inventory.json)
actually ran on `kaltura-php83-lab`, PHP8.3.6 with its configured CLI INI. It reports
`extension_loaded('riak') = false`, no declared Riak classes, and both Bucket and
Object unavailable using `class_exists(..., false)` without invoking autoload.
This observation is limited to that host/SAPI/configuration, not all providers,
the PHP7.4 baseline, production or the copied runtime. No backend access occurred.

## Minimal source repair is not provider acceptance

[Doctrine1.8.2's actual source](https://github.com/doctrine/cache/blob/1.8.2/lib/Doctrine/Common/Cache/RiakCache.php)
uses an explicit `RiakObject` import alias and retains the resolved provider type.
That supports the proposed narrow alias spelling repair; it does not authorize
replacing this bundled component wholesale. The newer file also contains other
changes, including different sibling indexing, which must not be smuggled into an
alias-only patch. Neither original74 behavior parity nor backend functionality
can be inferred from successfully linting a candidate.

Next evidence needed: isolated candidate syntax/reflection checks against real
parent/interfaces, read-only baseline provider inventory, and a pinned provider
build/compatibility decision before any real backend tests. Until then, backend
integration is NOT_EXECUTED/provider unavailable in the inspected lab. Do not
remove the driver, substitute a stub, label it unused from graph absence, or waive
this finding to obtain a green whole-source report. Other migration work continues;
this is not a declaration that the entire goal is blocked.

### Follow-up correction: an import alias alone is insufficient

The held [alias experiment](riak-alias.md) now actually executes the complete
original/candidate source on native PHP7.4 and PHP8.3. Both candidate processes
still terminate with a compiler fatal: the resolved `Riak\Object` argument type
is reserved at line207, after the renamed import no longer fails at line26.
Thus the upstream alias spelling cited above does not establish a compiling
repair. No candidate is selected; native provider/backend work remains open.
