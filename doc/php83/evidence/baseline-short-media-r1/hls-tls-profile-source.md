# Separate lab HLS TLS profile: source contract, not execution

Actual root observations: HTTP88 responds, TLS88 rejects TLS; native HTTPS
nested reference retains port88. Preserve HTTP88 and Apache443/8443. No URL
rewrite, protocol downgrade, hook replay or database write performed here.

## Intended packaging configuration

Local `deb/kaltura-nginx/debian/postinst:33–55` renders an optional separate
SSL server using ssl.conf.template; it includes the same server.conf as HTTP.
`doc/nginx-ssl-config.md` explicitly pairs this with delivery_profile.url port
configuration. Its broad SQL example is documentation, NOT an approved bounded
migration command. Default8443 conflicts with this lab's existing Apache;
8444 is a proposed separately observed-free port, not yet attested here.

## Selection and cloning

Exact original archive (58d534d09b3b75c9a8333957268c884f79032638b2d44a278b1992fda1b0ab28):
- DeliveryProfile73–97: null mediaProtocols supports all protocols; explicit
  comma-list filters the requested protocol in supportsDeliveryDynamicAttributes.
- DeliveryProfilePeer551–615 filters candidates then selects a full-support
  profile. Defaults387–432 require global partner/default unless explicit
  whitelist. Partner overrides and ACL delivery lists are additional inputs.
- Default HLS template is1001/type61,url @HOST@:@PORT@/hls, mediaProtocols absent.
  This is NOT proof actual selected profile is1001.
- VodPackagerHls extends AppleHttp but emits `/index.m3u8`, not the generic
  Apple's `/file/playlist.m3u8` suffix. Its host/protocol building is inherited.
- Native cloneToNew58–65 copies, sets parentId=original,isDefault=false, and
  immediately saves. It cannot be assumed selectable as a new default.
- Generated copyInto1873–1915 copies all18 non-ID columns (type, timestamps,
  partner,name,systemName,description,url,hostName,isDefault,parentId,
  recognizer,tokenizer,status,streamerType,mediaProtocols,customData,priority)
  and sets new/idNULL. Native doInsert supplies auto-increment at1273–1278.
  Do not guess MAX(id)+1. URL setter240–243 derives hostName via parse_url.
- Generated postInsert1354–1358 invalidates query cache; postSave1329–1335
  emits object-saved event; save1233 updates instance pool. Direct SQL bypasses
  this lifecycle. No claim that commit alone makes the new selection visible.
- API update rejects defaults (DeliveryProfileService48–50). Generic external
  clone/add is not a shortcut around the selected default's policy.

## Small bounded proposal requiring actual row observation

Observe selected ID/type/url/protocols/default/partner/parent/status/priority,
nullness of tokenizer/recognizer and exact private row identity, plus relevant
partner/ACL override selection. Then preserve original HTTP row identity and
port88, restrict it to http, and add a protocol-disjoint equivalent https row
for8444 under an explicitly reviewed selection strategy. Preserve all other
fields privately, reject unexpected opaque configuration, record inserted ID
and exact before/after identity for rollback. Do not silently make an inactive
or unselected clone default. Native cache lifecycle or separately reviewed
invalidation is required; then fresh native context must select the intended
row and emit the correct HTTPS8444 URL without rewriting. Snapshot/private
row rollback and listener/privacy verification remain prerequisites.

## Evidence scope

Codebase index belongs to sibling packaging checkout, generation
2026-09-25T19:28:02Z. App model paths have missing freshness; SSL template is
untracked by graph. Conclusions use exact direct source, not graph completeness.
No VM, DB, API or service actions, no final configuration approval.

## SHA256 identities
- Local `deb/kaltura-nginx/debian/postinst`: `46b06bd8f1f5900425a3aee9af4303f0724b34b0b46d9ccda04f021633684c9a`
- Local `deb/kaltura-nginx/debian/ssl.conf.template`: `a03132ddec157145e936e6ab4c7324b14af09ae8014580145098a277ddebefea`
- Local `doc/nginx-ssl-config.md`: `79e4d837692b16bc70669fae49c3f5093af60b96524174c2995d3636fe254c02`
- Archive `alpha/lib/model/DeliveryProfile.php`: `2fa1974f9feb7479b00f3c60eb3c44b80039acb187c2e913d4e7bd4fee5c269f`
- Archive `alpha/lib/model/DeliveryProfilePeer.php`: `dbfd0df052c0f3a5246ac3300f1dab8862793163d395c6a0677976ce4817f84f`
- Archive `alpha/lib/model/om/BaseDeliveryProfile.php`: `0bd05e4a212e2e914cb6bc476e3bd85f680b25dcc9e5aca6a908fb68a2e3150a`
- Archive `alpha/lib/model/DeliveryProfileVodPackagerHls.php`: `664b7d41cc60728c329ae3eb38409c02e5d83a54a0be12d02416af8dfd2e6241`
- Archive `api_v3/services/DeliveryProfileService.php`: `e9752bbb235e74b7bbc4262d41acf39a79a26aae8466944acafa3b9d14421967`
- Archive `deployment/base/scripts/init_data/07.DeliveryProfileVodPackagerHls.template.ini`: `fb67a248b04e299210d6e0953fefbab456f7da2c2df07eb4cda3cd921fc9c7d1`
