# PRIVATE_MARKER_LOGGED: source-only triage

Root reported actual original progressive3GET/sourcehash/ranges success but overall PRIVATE_MARKER_LOGGED. Further authenticated traffic is stopped. This report contains no VM/log reads and does not determine actual cause.

## Source-supported hypothesis, not an exemption
Current frozen url_privacy.inspect enrolls every twice-decoded path segment of length>=16 as a private token candidate before rejecting auth-bearing URL shapes. Length does not establish credential semantics. Native filename construction can legitimately exceed16:

- kAssetUtils.class.php SHA4ee947a8fe89b6ee9fc5e5f97b641f4dbf411a47666892d4d90950bfc011e03b lines49–68: entry.getName plus optional asset.getName, return extension.
- flavorAsset.php SHA18973d5b14c451199f16dcb45b7f9ee758bcd7733264ab01612dc40be5ae3bf0 lines231–252: sanitizes filename and appends extension, adds `/fileName/<filename>` to delivery parameters. Lines325–330 asset name comes from flavorParams.getName, not a token generator.
- DeliveryProfileVod.php SHAe9058bbd6cc16aa79a928ddf91ef80e819481f43404ed7d3fddb35ec4b310494 lines45–90: `/p/<partner>/sp/<subpartner>/serveFlavor/entryId/<entry>` + version string + `/flavorId/<asset>` +urlParams. Lines143–154 asset version v, optional partner/entry cache versions pv/ev. This is assetversion2, not entryversion0.
- DeliveryProfileHttp.php SHAb447f0a817631ec0193d091df1a52a6a8d6508349f9000e11feab3163e4fd669 adds `/name/a.<extension>`.
- serveFlavorAction.class.php SHA9e4d7470625adb3288b7692cbd093c8a0162f8bf781f72495c03524c79bb7610 reads fileName471 and puts it in Content-Disposition501–503. Targeted logger reads do not establish where the actual matched string was logged; logging origin remains diagnostic work.

## Why not ignore all filenames/long segments
DeliveryProfileVod188–215 can invoke a configured tokenizer before returning a URL; native download fallback can mint another KS. A filename position alone is not a proof the actual value is benign, nor is zero query sufficient to exclude path signatures. Original current KS, partner secret and prefixes/encodings remain forbidden without exceptions.

## Minimal diagnostic conclusion required
Using already saved private boundaries only, report matching candidate provenance (original secret/KS vs URL-added candidate), fixed path-position category (filename/other), and boolean equality to independently source-derived expected synthetic filename. Do not export candidate, URL, log line, credential hash or arbitrary filename. Keep unknown candidates flagged. Classifying a filename as public requires exact expected fixture/source equality and a closed route; never infer that from length alone or from match occurrence. Failure receipt remains immutable even if diagnostic later shows a false-positive classifier. New request only after reviewed correction and privacy approval.


## Later bounded observation: hypothesis not confirmed
Root's `baseline-freeze-r1/progressive443-readonly-diagnostic.json` reports374 files/28,766,542 bytes scanned from saved start offsets, six other long segments in application route candidates and zero filename long segments. This does **not** support treating the observed matches as the filename hypothesis above. No prior private pattern reconstruction, no journal scan, no API replay, and no raw data export occurred. Both cause_confirmed and privacy_pass remain false. The original BATCH_PRIVACY/PRIVATE_MARKER_LOGGED failure is preserved; no credential/public-segment classification, exemption or resumption is justified from this shape-only diagnostic. The next classifier must keep unknown values blocked and distinguish fixed public route literals from credentials using exact source evidence, not arbitrary length exceptions.
