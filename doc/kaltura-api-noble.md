# Kaltura API quick reference (Ubuntu Noble AIO)

Every example below was run with `curl` against the Vagrant AIO (`deb/noble`, http://192.168.56.20) on Kaltura CE Rigel-18.20.0. Responses are shortened.

The API is `api_v3`. Each call is an HTTP POST (or GET) to `/api_v3/` with at least `service`, `action` and, except for `system.ping`, a KS (Kaltura Session). `format=1` returns JSON, `format=2` (the default) returns XML. Object parameters are flattened as `object:field=value`, for example `entry:name=...` or `filter:entryIdEqual=...`.

```bash
API=http://192.168.56.20/api_v3
PID=102                      # your partner id
ADMIN_SECRET=...             # from the Admin Console (Publishers → Actions → Configure) or the DB
```

On the AIO VM you can read the secrets from the DB:

```bash
mysql -N -uroot -pkaltura-root kaltura -e "select id, secret, admin_secret from partner where id=$PID"
```

## Health: `system.ping`

```bash
curl -s "$API/?service=system&action=ping&format=1"
```
```json
true
```

With the default XML format the body is `<xml><result>1</result>...</xml>`.

## Session: `session.start`

- `type=2` gives an ADMIN session and `type=0` a USER session.
- `expiry` is in seconds and defaults to 86400.
- Partner `-2` is the Admin Console system partner.

```bash
KS=$(curl -s -d "service=session&action=start&format=1&partnerId=$PID&secret=$ADMIN_SECRET&type=2&userId=admin" $API/ | tr -d '"')
```
```json
"M2ZkZjZmMmE1OGQ5YzYwNzg0NjI4ZWI2NTAyZjNjM2I2NzA4ZTJiYXwtMjstMjsxNzkwMzg1MTM0OzI7..."
```

## Partners

Create a partner with `partner.register`. It needs a partner `-2` admin KS. The CMS password must satisfy the password rules: 8–14 characters, a digit, a lowercase letter and a symbol, and it must not contain the user's name or e-mail. This is exactly what `/opt/kaltura/bin/create_partner.php` does:

```bash
php /opt/kaltura/bin/create_partner.php "$MINUS2_ADMIN_SECRET" user@example.com 'Vid30#Test' http://192.168.56.20
# prints the new partner id, e.g. 102
```

Read a partner with `partner.get`:

```bash
curl -s -d "service=partner&action=get&format=1&ks=$KS&id=$PID" $API/
```
```json
{ "id": 102, "name": "Linux Rules", "adminEmail": "sanity@kaltura.local", "status": 1,
  "secret": "b7131ec0…", "adminSecret": "0c72e172…", "defConversionProfileType": 1001, … }
```

## Upload a video

There are three steps: create an upload token, upload the file into it, then create an entry and attach the token.

### 1. `uploadToken.add`

```bash
TOK=$(curl -s -d "service=uploadToken&action=add&format=1&ks=$KS" $API/ | python3 -c 'import json,sys;print(json.load(sys.stdin)["id"])')
```

### 2. `uploadToken.upload` (multipart, field `fileData`)

```bash
curl -s -F service=uploadToken -F action=upload -F format=1 -F ks=$KS \
     -F uploadTokenId=$TOK -F fileData=@video.mp4 $API/
```
```json
{ "id": "0_c96c9533ce6c61f0dd432a66f7988bda", "partnerId": 102, "status": 2,
  "fileName": "video.mp4", "uploadedFileSize": "154798", "objectType": "KalturaUploadToken" }
```

`status` 2 means FULL_UPLOAD. For large files, send chunks with `resume=1`, `resumeAt=<offset>` and `finalChunk=0|1`.

### 3. `media.add` + `media.addContent`

```bash
ENTRY=$(curl -s -d "service=media&action=add&format=1&ks=$KS&entry:objectType=KalturaMediaEntry&entry:mediaType=1&entry:name=My video" $API/ \
        | python3 -c 'import json,sys;print(json.load(sys.stdin)["id"])')
curl -s -d "service=media&action=addContent&format=1&ks=$KS&entryId=$ENTRY&resource:objectType=KalturaUploadedFileTokenResource&resource:token=$TOK" $API/
```
```json
{ "id": "0_kcq0zl3b", "name": "My video", "mediaType": 1, "status": 1,
  "dataUrl": "http://192.168.56.20/p/102/sp/10200/playManifest/entryId/0_kcq0zl3b/format/url/protocol/http",
  "thumbnailUrl": "http://192.168.56.20/p/102/sp/10200/thumbnail/entry_id/0_kcq0zl3b/version/0", … }
```

`baseEntry.addFromUploadedFile` (`entry:objectType=KalturaBaseEntry&uploadTokenId=$TOK&type=-1`) does the same in one call. `/opt/kaltura/bin/upload_test.php` uses it.

Entry `status` values (`alpha/lib/enums/entryStatus.php` in 18.20):

| Value | Meaning |
|---|---|
| -2 | ERROR_IMPORTING |
| -1 | ERROR_CONVERTING |
| 0 | IMPORT |
| 1 | PRECONVERT (transcoding) |
| 2 | READY |
| 3 | DELETED |
| 4 | PENDING |
| 5 | MODERATE (deprecated) |
| 6 | BLOCKED (deprecated) |
| 7 | NO_CONTENT |

## Entries

`baseEntry.get`:

```bash
curl -s -d "service=baseEntry&action=get&format=1&ks=$KS&entryId=$ENTRY" $API/
```
```json
{ "id": "0_kcq0zl3b", "status": 2, "duration": 10, "msDuration": 10008,
  "width": 640, "height": 360, "flavorParamsIds": "0,2", … }
```

`baseEntry.list`, newest first:

```bash
curl -s -d "service=baseEntry&action=list&format=1&ks=$KS&filter:orderBy=-createdAt&pager:pageSize=2" $API/
```
```json
{ "objects": [ { "id": "0_kcq0zl3b", "name": "My video", "status": 2, … }, … ],
  "totalCount": …, "objectType": "KalturaBaseEntryListResponse" }
```

`media.list` accepts a `KalturaMediaEntryFilter`, for example `filter:nameLike=...`, `filter:statusIn=2` or `filter:mediaTypeEqual=1`. `media.update` and `media.delete` take `entryId`.

## Flavors: `flavorAsset.list`

```bash
curl -s -d "service=flavorAsset&action=list&format=1&ks=$KS&filter:entryIdEqual=$ENTRY" $API/
```
```json
{ "objects": [
  { "id": "0_lsifcdil", "flavorParamsId": 0, "isOriginal": true, "width": 640, "height": 360,
    "bitrate": 123, "videoCodecId": "avc1", "status": 2, "tags": "source,web" },
  { "id": "0_c3gqtxiw", "flavorParamsId": 2, "isOriginal": false, "width": 640, "height": 360,
    "bitrate": 180, "videoCodecId": "avc1", "status": 2 } ], … }
```

Flavor status values: 2 is READY, 1 is CONVERTING, 4 is NOT_APPLICABLE (skipped because the source is smaller than the flavor), and -1 is ERROR.

## Playback URLs (no KS needed for public entries)

HLS through nginx VOD. The master playlist points to the packager on port 88:

```bash
curl -sL "http://192.168.56.20/p/$PID/sp/${PID}00/playManifest/entryId/$ENTRY/format/applehttp/protocol/http/a.m3u8"
```
```
#EXTM3U
#EXT-X-STREAM-INF:PROGRAM-ID=1,BANDWIDTH=207126,RESOLUTION=640x360
http://192.168.56.20:88/hls/p/102/sp/10200/serveFlavor/entryId/0_kcq0zl3b/v/2/ev/2/flavorId/0_c3gqtxiw/name/a.mp4/index.m3u8
```

Progressive MP4 (`format/url`) answers with a redirect to `serveFlavor`:

```bash
curl -sI "http://192.168.56.20/p/$PID/sp/${PID}00/playManifest/entryId/$ENTRY/format/url/protocol/http/a.mp4"
```
```
HTTP/1.1 302 Found
location: http://192.168.56.20/p/102/sp/10200/serveFlavor/entryId/0_kcq0zl3b/v/2/ev/2/flavorId/0_c3gqtxiw/forceproxy/true/name/a.mp4
```

Thumbnail:

```bash
curl -s -o thumb.jpg "http://192.168.56.20/p/$PID/sp/${PID}00/thumbnail/entry_id/$ENTRY/width/320"
# 200 image/jpeg
```

## End-to-end check

`deb/noble/sanity.sh` runs this whole flow as a single check: ping, session, a partner created once, upload of a generated MP4, wait for READY, then the HLS manifest and one segment. Run it with:

```bash
vagrant ssh aio -c 'sudo bash /vagrant/deb/noble/sanity.sh'
```
