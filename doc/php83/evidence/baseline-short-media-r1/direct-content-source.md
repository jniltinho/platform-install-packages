# Direct FileSync content path: source contract, not incident diagnosis

Local source reads only. Original archive SHA58d534d09b3b75c9a8333957268c884f79032638b2d44a278b1992fda1b0ab28. No API/VM/log access. The later shape diagnostic describes filesystem/content candidates; it does not reconstruct the original private match set.

## Exact formation

- `alpha/lib/model/asset.php` SHA34f9e81972369706ea01f5e8a3ba19cd6999d2f6804f25ccdf89cac0bf74933d, generateFileName364–384: entryId + '_' + assetId + '_' + version + extension (special ISM/SMIL tags take separate branches). For already bound original MP4/version2, the expected basename is exactly `0_wzmt2sfy_0_ewuu0o46_2.mp4`, not an arbitrary regex family.
- Same file generateFilePathArr403–424: internal storage is `/content/entry/data/` plus `/` plus numeric shard directory plus `/` and generated basename. Original implementation can produce a doubled separator; it does not introduce a credential. External storage is a separate `/entry/<type>/...` branch and is not implicitly allowed.
- `alpha/apps/kaltura/lib/myContentStorage.class.php` SHA090d3232baca0482cf7cf52f7011eb896270f3e18e778fdee7e2171421c3f2a9,137–139: shards are int(intId/1000000) and int(intId/1000)%1000. Without verified entry.intId, do not claim source derivation of exact numeric values. Existing verified FileSync path can bind those observed shard values without inventing a new query.
- `alpha/lib/model/DeliveryProfileVod.php` SHAe9058bbd6cc16aa79a928ddf91ef80e819481f43404ed7d3fddb35ec4b310494,302–305: doGetFileSyncUrl returns FileSync.file_path.268–270 joins host.278–293 can apply a configured tokenizer, so signed/prefixed forms remain rejected unless separately authorized; this is not evidence the currently selected profile is this class.

## Minimal forward-only validation design

Use the already privately verified stored file/Sync315/partner102/asset/version2/source hash and size. Require fixed original basename, exactly two canonical numeric shard components under `/opt/kaltura/web/content/entry/data/`, and the existing reader's no-follow/trusted-path guarantees. Derive an expected content URL path by removing exactly `/opt/kaltura/web` from that verified normalized path. Require native API-returned HTTPS443 URL path to equal that exact expected path, not merely match a generic basename regex. If explicitly supporting source-generated doubled separators, compare canonical containment while rejecting raw dot, percent, backslash and control components; never rewrite/transmit a different URL. Query/auth-marker/current-credential/prefix/encoding checks remain unconditional.

This mapping additionally needs the active baseline Apache Alias `/content`→`/opt/kaltura/web/content` identity join; a migration-template Alias alone is not proof of the baseline active configuration. A successful exact source-body download supports delivered bytes, not a universal routing or authorization claim.

Only after this complete identity join can the exact known basename be classified as public media identity rather than a length-derived suspected token. Unknown long segments remain rejected. Do not strip arbitrary trailing punctuation from URL input; a log parser's trailing delimiter must be separately source/framing established. The original PRIVATE_MARKER_LOGGED failure remains immutable and unresolved until original-pattern provenance evidence establishes cause; a forward classifier correction is not retrospective privacy acceptance.
