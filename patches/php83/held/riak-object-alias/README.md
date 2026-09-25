# Rejected alias-only experiment — do not select

`RiakCache-alias.patch` changes four lexical alias sites only. Actual native PHP
7.4 and 8.3 still reject its resolved `Riak\Object` argument type at line207.
The original fails earlier at the reserved import alias on line26. The patch is
retained solely as negative experimental evidence; it is not in exp11 or an
approved migration manifest. Do not substitute a stub or remove type constraints
merely to obtain a green compiler result.

Exact input/output/patch identities: `tools/php83/riak-alias/source-pins.json`.
Primary and actual Cursor native83 verification: `doc/php83/riak-alias.md` and
`doc/php83/evidence/riak-alias/`. Provider/backend compatibility remains open.
