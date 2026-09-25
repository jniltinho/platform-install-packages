# Held experiments — not part of any active archive

The Registry cast experiment is retained solely for review and reproduction.
The active `../manifest.json` does not list it. Do not add it through wildcard
patch discovery.

The latest extended fixture compares dynamic property assignment plus
`offsetExists` on ArrayObject flags 0–3. On flag 2, PHP 7.4 original returns false
for the property-written key while the PHP 8.3 cast candidate returns true;
on flag 3, the corresponding result flips from true to false. This needs a
semantic/API-impact decision and wider tests, not a silent exclusion of the
failing fixture. No claim is made that these low-level legacy semantics are ideal.

The original `array_key_exists($index, $this)` still fails on PHP 8.3; excluding
this patch therefore leaves a known compatibility blocker. No application-wide
acceptance is asserted for the JSON-only ZIP.
