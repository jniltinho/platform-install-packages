# Closed native serveFlavor observation-to-GET join

The successful no-GET receipt `route-observer-native-r1.json` establishes the selected native route family, owned identity and exact privately computed public filename. It does not validate the previous fixed-order regex. No historical failure is reclassified.

Pinned literal source (not a graph-based conclusion):
- `vendor/symfony/controller/sfRouting.class.php:575–588` converts wildcard path components into key/value parameters, then `parse_str`; ordering is not significant.
- `alpha/apps/kaltura/config/routing.yml:176–177` selects `/:module/:action/*`.
- The already pinned enabled Apache configuration rewrites `/serveFlavor/...` to `/index.php/extwidget/serveFlavor/...`.
- `serveFlavorAction.class.php:394–395,471,521` obtains entryId, flavorId, fileName and v by named request parameter.
- `FlavorAssetService.php:609–664` supplies no filename override in our exact getUrl request. `flavorAsset.php:233–252` computes and appends the sanitized filename without URL encoding. The separate `kAssetUtils::getDownloadRedirectUrl` encoding path does not apply to this request.

The new guard consumes every pair, permits only the four required fields plus numeric pv/ev and exact name/a.mp4, rejects duplicate/unknown/odd/empty structure, and compares the exact tenant, entry, asset, asset version and private source-derived filename. It rejects encoding, query, fragment, userinfo, unknown origin and current credential/full-prefix occurrences before accepting. It never rewrites the URL. A filename containing `+` is rejected because native `parse_str` would convert it to a space.

Only this exact source-proven public route ceases to be heuristically classified as a credential merely because its filename is long. Actual secret/KS full and prefixes remain in all privacy scans. Rejected routes enroll every candidate and preserve the existing finite failure audit and closed provenance. The raw URL and names stay memory-only.

## Root execution, after independent approval

Run `python3 -B tools/php83/baseline-freeze-r1/run_serve_progressive.py --check`, then the same command with `--output` naming a new exclusive sibling-artifact directory. The runner requires old unit `baseline-freeze-a1776f1a.service` inactive and fresh stage `/var/lib/kaltura-baseline-serve-progressive-r1`. Four newly pinned source files must match on .74 before authentication and again at postcheck. API remains HTTPS8443; the three original progressive requests use unchanged native HTTPS443 URL and pinned CA. All TLS log inventories, quiet windows, original scan starts, finite caps and common-end checks remain.

Executed locally: 13 focused tests, including all 24 required-pair permutations and adversarial cases; 157 aggregate tests. No VM or network execution by the author. This is not decoded playback, HLS, measured performance, complete baseline freeze or task acceptance.
