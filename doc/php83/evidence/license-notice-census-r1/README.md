# Vendor notice census and pinned MaxMind attribution

The original Rigel ZIP remains unchanged. The census records all 4,999 vendor
file identities and bounded display excerpts, not legal approval or absence of
licenses. R1 was independently rebuilt by the actual Claude CLI (terminal 0,
5 tests and byte comparison passed). Its three review findings were corrected
in R2: LF line numbering, explicit replacement-decoding disclosure and complete
scans of prefixed/suffixed notice names. Eight root tests passed. Independent Codex R2 execution also passed all eight
tests and reproduced identical report bytes; its receipt is in the sibling
`task11-independent-scope-r1` directory. Actual Cursor read-only attempt ended
exit1 (authentication required); it is NOT_EXECUTED, not a passing review.

`reviewed-r2.json` supersedes `primary.json`; the earlier report remains an
identity-pinned historical input to the initial supplemental join. Neither
inherits license terms across neighboring files. Nested components must be
identified separately, not inferred from the first vendor directory.

`maxmind-attribution.json` records 35 exact byte matches with two official pinned
upstream archives, their commit-specific Apache-2.0 declarations and license
hashes. This establishes a source-to-declaration correspondence, not a uniquely
proven original version. The original bundle lacks these license texts;
redistribution notice handling remains a separate packaging/release obligation.
No package or application source was upgraded or executed.

## Reproduction

Run from the migration checkout, selecting an absent output path:

```sh
python3 -B -m unittest discover -s tools/php83/license-notice-census-r1 -v
python3 -B tools/php83/license-notice-census-r1/build.py --archive /tmp/kaltura-php83-audit/Rigel-18.20.0.zip --output /tmp/census-new.json
python3 -B tools/php83/license-notice-census-r1/compare_upstream.py --original /tmp/kaltura-php83-audit/Rigel-18.20.0.zip --upstream-dir ../platform-install-packages-php83-artifacts/upstream-attribution-r1 --output /tmp/maxmind-new.json
```

Upstream downloads are external read-only evidence, pinned in the comparator.
No private logs, installed configurations, credentials or VM artifacts belong
in this evidence directory. These reports alone do not close OpenSpec task 1.1.
