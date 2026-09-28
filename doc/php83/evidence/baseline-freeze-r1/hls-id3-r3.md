# Optional source-supported timed-ID3 stream

The real R2 diagnostic reported three streams: one H264 video (640x360, 25fps, 250 frames), one AAC audio (44100Hz, two channels), and one OTHER stream. That receipt **does not identify the third stream** and remains a failed observation.

The independently authenticated nginx-vod-module 1.33 producer initializes a null-track metadata stream before checking whether ID3 data is empty. Its MPEG-TS encoder adds an ID3 PMT descriptor/stream type 0x15 for that stream. Official FFmpeg n6.1.1 source maps this metadata to DATA/TIMED_ID3 and codec name `timed_id3`. See the separate source report and pins. These are source semantics, not installed binary/build attestation or proof that the previously observed OTHER was ID3.

R3 adds exact closed diagnostic DATA/TIMED_ID3 labels. Acceptance permits two AV streams plus **at most one** auxiliary stream with both literal `codec_type=data` and `codec_name=timed_id3`. Every other extra stream remains rejected. Existing video/audio codec, dimension bounds, finite FPS, frame count, duration and sample/channel predicates stay in place. Host success projection independently joins the newly observed diagnostic labels/cardinality to the accepted auxiliary count; arbitrary OTHER cannot become success.

The decoder still maps exactly one video and one audio stream with -xerror and requires successful exit with no stderr/stdout. The output explicitly says `decoded_stream_scope=ONE_VIDEO_ONE_AUDIO`, `auxiliary_metadata_payload_verified=false`, and no profile-golden or dynamic-library cohort acceptance. Advertised empty ID3 data is not required to have decoded frames and is not silently claimed as validated payload.

New stage `/var/lib/kaltura-baseline-hls-delivery8444-r3`, previous failed unit `baseline-freeze-f137c16d.service` inactive, same exact successful context proof. Root executes only after independent review. No configuration/profile changes, source-code deployment, automatic workload retry or retrospective promotion of R1/R2 is included.
