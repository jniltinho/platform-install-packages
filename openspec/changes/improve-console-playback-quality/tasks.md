## 1. Playback selection

- [x] 1.1 Implement deterministic selection of ready, entry-owned MP4/H.264 flavors; verify table tests cover resolution, original preference, bitrate, ties, wrong entry, invalid ID, incompatible codec/format, unready and empty candidates.
- [x] 1.2 Integrate explicit flavor selection into authenticated streaming without changing HTTPS or redirect policy; verify handler tests cover list failure, unavailable candidates, ownership, Range/HEAD and HTTP/HTTPS manifest URLs.

## 2. Deployment and media acceptance

- [x] 2.1 Run Go lint, CGO-disabled tests, race tests and frontend checks; build a package and upgrade only .20, verifying configuration, users and existing media remain intact.
- [x] 2.2 Upload the downloaded 1080p60 fight as an additional labelled demo; verify READY and ffprobe on the delivered stream reports 1920×1080 and approximately 60 fps, not merely on the local source.
- [x] 2.3 Verify real browser playback/fullscreen and HTTP 206 seeking on .20, and confirm existing 720p media selects its best compatible asset instead of 360p.

## 3. Documentation and integration

- [x] 3.1 Document best-quality progressive playback, bandwidth trade-offs and exact validation evidence; verify links and update CHANGELOG.
- [ ] 3.2 Coordinate a branch/PR from main with Claude, verify CI, synchronize the completed delta and archive this change; publish only an agreed unused console version tag after merge.

### Evidence

See kaltura-console/docs/validation.md, Playback quality acceptance. rc10 .20: Full HD source and delivered stream 1920×1080 at60000/1001fps; browser playback/fullscreen and Range206 passed. Existing720p entry nowdelivers720p60. Full E2E and make lint test package passed. Only integration/release closure remains.
