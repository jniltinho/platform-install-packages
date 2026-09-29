# Lab conversion profile for Decision 7 (1080p60 + 360p25) — design and read-only inventory

Operator decision (2026-09-29): option 1 — create a lab conversion profile that explicitly delivers
1080p60 and 360p25, identical in the 7.4 and 8.3 labs; mutation reviewed first. Lab only.

## Read-only inventory (`flavor-params-probe-r1.json`, sha256 0c2a764a7182b63c9db40ec5630a76688d1ea5081d7a886b26c26298802657da)
`flavor_params_probe.py` (pinned profile_socket transport, READ ONLY transaction): 21 video/thumb
params, all system (partner 0), every `frame_rate=0` (source) and none with `maxFrameRate` in
custom_data. Partner 102 profiles: 14 Default (params 0,2,3,4,5,6,7,19) and 13 Passthrough_Live.
Short fixture on profile 14: params 2,3,4 READY at 640x360@25 (source raster), 5–7 NOT_APPLICABLE.
So 360p25 is already delivered by the default profile; 1080p60 is not.

## Source basis
`infra/cdl/kdl/KDLFlavor.php:1363-1400` evaluateTargetVideoFramerate: frameRate 0 → source fps capped
by `_maxFrameRate` if >0 else `KDLConstants::MaxFramerate`; 60 is truncated to 30. `KalturaFlavorParams`
exposes writable `maxFrameRate` (api_v3/lib/types/conversionProfile/KalturaFlavorParams.php:197,276).

## Proposed mutation (to be reviewed before execution)
1. Clone system params 7 (HD/1080, h264h 4000, web,mbr,dash) into a partner-102 params
   `lab_decision7_1080p60` with `maxFrameRate=60` (all other writable fields copied).
2. Create partner-102 profile `lab_decision7` = profile 14's params with 7 replaced by the clone.
   Profile 14 and the partner default remain untouched; uploads pass conversionProfileId explicitly.
3. Re-upload both fixtures on `lab_decision7` and verify delivered 1080p60 / 360p25.
Admin KS is required; admin secret/KS are added to every privacy audit pattern set.
