# Auxiliary ID3 PMT stream: source-backed distinction

## Exact producer source

Public nginx-vod-module tag1.33 resolves to commit `1750eb08021e362859887fdfe842ed6a4997f576`, as recorded in the prior segment-source evidence. The three additional source files here were fetched over HTTPS from that commit, bounded to1MiB each, SHA256-recorded and Git blob SHA1 verified against the commit tree. They were not executed or compiled. License is preserved in the adjacent segment-source evidence.

The source distinguishes **announcing an ID3 stream in the PMT** from **writing ID3 payload frames**:

1. `ngx_http_vod_hls.c:1155` defaults `output_id3_timestamps` to0. Its muxer configuration at345–350 sets ID3 data empty when this option is disabled (file hash is in the prior segment-source manifest).
2. [hls_muxer.c](https://github.com/kaltura/nginx-vod-module/blob/1750eb08021e362859887fdfe842ed6a4997f576/vod/hls/hls_muxer.c):440–447 unconditionally initializes the auxiliary ID3 stream before finalizing MPEG-TS stream headers. Within the initializer, lines168–175 call the stream initializer with a NULL track **before** lines179–183 return for empty ID3 data.
3. The same file119–145 forwards that NULL track into the MPEG-TS encoder.
4. [mpegts_encoder_filter.c](https://github.com/kaltura/nginx-vod-module/blob/1750eb08021e362859887fdfe842ed6a4997f576/vod/hls/mpegts_encoder_filter.c):1330–1350 maps NULL track to MEDIA_TYPE_NONE and adds it to the stream table. Lines614–618 select the ID3 PMT template. Lines119–122 define stream type0x15 and the ID3 metadata descriptor. Thus an advertised auxiliary stream is source-supported even when no ID3 frames are emitted.

## Consumer naming (separate reference, not installed-build proof)

Official FFmpeg `n6.1.1` [libavformat/mpegts.c](https://github.com/FFmpeg/FFmpeg/blob/n6.1.1/libavformat/mpegts.c) maps the ID3 registration/metadata descriptor to AVMEDIA_TYPE_DATA and AV_CODEC_ID_TIMED_ID3. [libavcodec/codec_desc.c](https://github.com/FFmpeg/FFmpeg/blob/n6.1.1/libavcodec/codec_desc.c) names that codec `timed_id3` with DATA type. Bounded exact excerpts and whole-source SHA256 identities are in `ffmpeg-name-mapping.json`. This reference establishes the meaning of the names, **not** the exact installed FFmpeg source version/build correspondence.

## Narrow validator consequence

The actual diagnostic reported only OTHER/OTHER, which is insufficient to identify the observed third stream. A subsequent bounded closed diagnostic must explicitly recognize `codec_type=data` AND `codec_name=timed_id3` before accepting that auxiliary form. Unknown data, subtitles, additional audio/video, duplicate metadata streams or more than one auxiliary stream remain rejected.

A conservative source-supported shape is one H264 video plus one AAC audio, optionally one DATA/timed_id3 descriptor; every existing numeric bound and A/V decode requirement remains. This does not establish ID3 payload correctness, gold-reference equivalence, complete dynamic-library cohort, complete response-secret coverage or application acceptance. No VM/API/media request or private probe output was read by this source-analysis lane.
