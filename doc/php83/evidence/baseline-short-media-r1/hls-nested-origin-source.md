# Nested HLS origin: source-only finding

The R2 native observation reports HTTP 200, a 201-byte HLS master with one
STREAM-INF and one URI, rejected with ORIGIN before any nested request. This
is not a successful HLS playback or privacy-wide acceptance.

Pinned original archive SHA256:
`58d534d09b3b75c9a8333957268c884f79032638b2d44a278b1992fda1b0ab28`.
Exact archive members were read directly; no graph completeness is claimed.

## Producer mapping

- `DeliveryProfileAppleHttp.php:22–27` calls buildHttpFlavorsArray; its asset
  URL method (10–14) adds `/file/playlist.m3u8`.
- `DeliveryProfileVod.php:320–328` builds each flavor with getFlavorHttpUrl.
  `getUrlPrefix` (333–335) returns stored profile URL. At 371–381 the builder
  strips an existing HTTP(S) scheme and prefixes dynamic mediaProtocol while
  retaining the configured host and port. An HTTPS request therefore does not
  establish that the nested URI uses the API origin or port 443.
- `playManifestAction.class.php:1089–1124` updates mediaProtocol; a recognized
  HTTP-family protocol is retained, otherwise request protocol is selected.
- `kManifestRenderers.php:1033–1058` renders STREAM-INF followed by the flavor
  URL. It does not enforce the parent's origin. Its 205–211 substitution may
  add an opaque playbackContext. Tokenizers/contributors are additional scope;
  no unsigned-route assumption is permitted solely from URI position.
- Native optional AUDIO/CLOSED-CAPTIONS EXT-X-MEDIA tags (953–1026) are not
  supported by the current restricted parser. None was reported in R2, so
  broadening tag support does not address the observed ORIGIN rejection.

## Next observation, not permission to fetch

Resolve the bounded reference privately and report only closed scheme,
expected-host boolean, effective-port enum, userinfo/query/fragment booleans,
reference count and completeness. Enroll returned private candidates in failure
scans even when parsing rejects them. Do not export a URL, body, arbitrary tag,
path or token hash. Keep the original HTTPS/host/port rejection and zero nested
requests. A configured HTTP endpoint or alternate port is a hypothesis until
observed; do not rewrite it or treat a public-looking route as credential-free.

## Source identities

- `alpha/lib/model/DeliveryProfileVod.php`: `e9058bbd6cc16aa79a928ddf91ef80e819481f43404ed7d3fddb35ec4b310494`
- `alpha/lib/model/DeliveryProfileAppleHttp.php`: `75698c78c6d2675b192bf61165826dec321486b17c61ff73b4d2c6e4d882ceda`
- `alpha/lib/model/DeliveryProfile.php`: `2fa1974f9feb7479b00f3c60eb3c44b80039acb187c2e913d4e7bd4fee5c269f`
- `alpha/apps/kaltura/lib/kManifestRenderers.php`: `0eae1dcf29f46d4c459b3f749cfd3222550181f40139a8aec04001074871df14`
- `alpha/apps/kaltura/modules/extwidget/actions/playManifestAction.class.php`: `24832b13f6721daf9df703c0d7ccb68e509459d4699056f794b806533abcd678`
