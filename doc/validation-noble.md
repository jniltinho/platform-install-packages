# Ubuntu Noble AIO validation

Evidence collected on the `aio` VM (`deb/noble`, http://192.168.56.20) after a clean `vagrant up aio`. Screenshots were taken with `agent-browser` (1440x900).

## Real video test

- Source: *Big Buck Bunny* (Blender Foundation, CC BY 3.0), downloaded from YouTube with `yt-dlp` as H.264 720p MP4 (9:56, 81 MB).
- Uploaded through the API (`uploadToken.add` → `uploadToken.upload` → `media.add` → `media.addContent`). The steps are described in [kaltura-api-noble.md](kaltura-api-noble.md).
- The entry became READY in about 80 seconds. All the required flavors were transcoded: source 720p, 360p, 480p, 540p and 720p (see `kmc-05-entry-flavors.png`).
- It plays in the KMC preview through HLS served by nginx VOD (`kmc-03b-entry-player-playing.png`).

## External clients (criare)

- **kaltura-console** (Laravel 13, PHP 8.3) was run in a `php:8.3-cli` container pointed at the AIO:
  - `KALTURA_SERVICE_URL=http://192.168.56.20/api_v3`, `KALTURA_PARTNER_ID=102`, `KALTURA_PLAYBACK_HOST=http://192.168.56.20`.
  - It works unchanged against 18.20: login, dashboard, media list, upload form, entry details with the progressive player via its proxy and the flavor table, and health (all checks green).
  - Screenshots are in [prints/kaltura-console](prints/kaltura-console).
- **kaltura-legacy-gateway** is **not needed**. It only preserved the old `kaltura.wifimax.com.br` host: an nginx alias from `/kaltura-api/` to `api_v3` plus a PHP proof of concept with hard-coded URLs. Clients talk to `http://<host>/api_v3/` directly.

## Known limitations seen in the UI

- **Analytics** (`kmc-19-analytics.png`) shows *Internal server error*. The analytics screens need the KAVA/DWH backend (Druid/pentaho), which is out of scope for this AIO.
- The Flash-era tools (legacy KMC, KCW, KDP) are not installed.

## Admin Console

| Screen | Screenshot |
|---|---|
| Login | [![admin-console-01-login.png](prints/admin-console-01-login.png)](prints/admin-console-01-login.png) |
| Publishers | [![admin-console-02-publishers.png](prints/admin-console-02-publishers.png)](prints/admin-console-02-publishers.png) |
| Add publisher | [![admin-console-03-add-publisher.png](prints/admin-console-03-add-publisher.png)](prints/admin-console-03-add-publisher.png) |
| Publishers usage | [![admin-console-04-publishers-usage.png](prints/admin-console-04-publishers-usage.png)](prints/admin-console-04-publishers-usage.png) |
| Users | [![admin-console-05-users.png](prints/admin-console-05-users.png)](prints/admin-console-05-users.png) |
| Add user | [![admin-console-06-add-user.png](prints/admin-console-06-add-user.png)](prints/admin-console-06-add-user.png) |
| User roles | [![admin-console-07-user-roles.png](prints/admin-console-07-user-roles.png)](prints/admin-console-07-user-roles.png) |
| My settings | [![admin-console-08-my-settings.png](prints/admin-console-08-my-settings.png)](prints/admin-console-08-my-settings.png) |
| Ui confs | [![admin-console-09-ui-confs.png](prints/admin-console-09-ui-confs.png)](prints/admin-console-09-ui-confs.png) |
| Batch entry investigation | [![admin-console-10-batch-entry-investigation.png](prints/admin-console-10-batch-entry-investigation.png)](prints/admin-console-10-batch-entry-investigation.png) |
| Batch entry lifecycle | [![admin-console-11-batch-entry-lifecycle.png](prints/admin-console-11-batch-entry-lifecycle.png)](prints/admin-console-11-batch-entry-lifecycle.png) |
| Batch failed tasks | [![admin-console-12-batch-failed-tasks.png](prints/admin-console-12-batch-failed-tasks.png)](prints/admin-console-12-batch-failed-tasks.png) |
| Batch in progress tasks | [![admin-console-13-batch-in-progress-tasks.png](prints/admin-console-13-batch-in-progress-tasks.png)](prints/admin-console-13-batch-in-progress-tasks.png) |
| Batch setup | [![admin-console-14-batch-setup.png](prints/admin-console-14-batch-setup.png)](prints/admin-console-14-batch-setup.png) |
| Dev test console | [![admin-console-15-dev-test-console.png](prints/admin-console-15-dev-test-console.png)](prints/admin-console-15-dev-test-console.png) |
| Dev api documentation | [![admin-console-16-dev-api-documentation.png](prints/admin-console-16-dev-api-documentation.png)](prints/admin-console-16-dev-api-documentation.png) |
| Dev xml schema | [![admin-console-17-dev-xml-schema.png](prints/admin-console-17-dev-xml-schema.png)](prints/admin-console-17-dev-xml-schema.png) |
| Dev client libs | [![admin-console-18-dev-client-libs.png](prints/admin-console-18-dev-client-libs.png)](prints/admin-console-18-dev-client-libs.png) |
| Dev apc | [![admin-console-19-dev-apc.png](prints/admin-console-19-dev-apc.png)](prints/admin-console-19-dev-apc.png) |
| Dev memcache | [![admin-console-20-dev-memcache.png](prints/admin-console-20-dev-memcache.png)](prints/admin-console-20-dev-memcache.png) |
| Dev flavor params | [![admin-console-21-dev-flavor-params.png](prints/admin-console-21-dev-flavor-params.png)](prints/admin-console-21-dev-flavor-params.png) |
| Dev system helper | [![admin-console-22-dev-system-helper.png](prints/admin-console-22-dev-system-helper.png)](prints/admin-console-22-dev-system-helper.png) |
| Config configuration maps | [![admin-console-23-config-configuration-maps.png](prints/admin-console-23-config-configuration-maps.png)](prints/admin-console-23-config-configuration-maps.png) |
| Config audit trail | [![admin-console-24-config-audit-trail.png](prints/admin-console-24-config-audit-trail.png)](prints/admin-console-24-config-audit-trail.png) |
| Publisher configure | [![admin-console-25-publisher-configure.png](prints/admin-console-25-publisher-configure.png)](prints/admin-console-25-publisher-configure.png) |
| Publisher widgets | [![admin-console-26-publisher-widgets.png](prints/admin-console-26-publisher-widgets.png)](prints/admin-console-26-publisher-widgets.png) |
| Publisher delivery profile | [![admin-console-27-publisher-delivery-profile.png](prints/admin-console-27-publisher-delivery-profile.png)](prints/admin-console-27-publisher-delivery-profile.png) |
| Publisher remote storage | [![admin-console-28-publisher-remote-storage.png](prints/admin-console-28-publisher-remote-storage.png)](prints/admin-console-28-publisher-remote-storage.png) |
| Publisher virus scan | [![admin-console-29-publisher-virus-scan.png](prints/admin-console-29-publisher-virus-scan.png)](prints/admin-console-29-publisher-virus-scan.png) |
| Publisher distribution profiles | [![admin-console-30-publisher-distribution-profiles.png](prints/admin-console-30-publisher-distribution-profiles.png)](prints/admin-console-30-publisher-distribution-profiles.png) |
| Publisher generic providers | [![admin-console-31-publisher-generic-providers.png](prints/admin-console-31-publisher-generic-providers.png)](prints/admin-console-31-publisher-generic-providers.png) |
| Publisher drop folders | [![admin-console-32-publisher-drop-folders.png](prints/admin-console-32-publisher-drop-folders.png)](prints/admin-console-32-publisher-drop-folders.png) |

## KMC (kmc-ng)

| Screen | Screenshot |
|---|---|
| Login | [![kmc-01-login.png](prints/kmc-01-login.png)](prints/kmc-01-login.png) |
| Content entries | [![kmc-02-content-entries.png](prints/kmc-02-content-entries.png)](prints/kmc-02-content-entries.png) |
| Entry metadata | [![kmc-03-entry-metadata.png](prints/kmc-03-entry-metadata.png)](prints/kmc-03-entry-metadata.png) |
| Entry player playing | [![kmc-03b-entry-player-playing.png](prints/kmc-03b-entry-player-playing.png)](prints/kmc-03b-entry-player-playing.png) |
| Entry thumbnails | [![kmc-04-entry-thumbnails.png](prints/kmc-04-entry-thumbnails.png)](prints/kmc-04-entry-thumbnails.png) |
| Entry flavors | [![kmc-05-entry-flavors.png](prints/kmc-05-entry-flavors.png)](prints/kmc-05-entry-flavors.png) |
| Entry access control | [![kmc-06-entry-access-control.png](prints/kmc-06-entry-access-control.png)](prints/kmc-06-entry-access-control.png) |
| Entry scheduling | [![kmc-07-entry-scheduling.png](prints/kmc-07-entry-scheduling.png)](prints/kmc-07-entry-scheduling.png) |
| Entry captions | [![kmc-08-entry-captions.png](prints/kmc-08-entry-captions.png)](prints/kmc-08-entry-captions.png) |
| Entry related | [![kmc-09-entry-related.png](prints/kmc-09-entry-related.png)](prints/kmc-09-entry-related.png) |
| Entry distribution | [![kmc-10-entry-distribution.png](prints/kmc-10-entry-distribution.png)](prints/kmc-10-entry-distribution.png) |
| Entry users | [![kmc-11-entry-users.png](prints/kmc-11-entry-users.png)](prints/kmc-11-entry-users.png) |
| Content moderation | [![kmc-12-content-moderation.png](prints/kmc-12-content-moderation.png)](prints/kmc-12-content-moderation.png) |
| Content playlists | [![kmc-13-content-playlists.png](prints/kmc-13-content-playlists.png)](prints/kmc-13-content-playlists.png) |
| Content syndication | [![kmc-14-content-syndication.png](prints/kmc-14-content-syndication.png)](prints/kmc-14-content-syndication.png) |
| Content categories | [![kmc-15-content-categories.png](prints/kmc-15-content-categories.png)](prints/kmc-15-content-categories.png) |
| Content upload control | [![kmc-16-content-upload-control.png](prints/kmc-16-content-upload-control.png)](prints/kmc-16-content-upload-control.png) |
| Content bulk upload | [![kmc-17-content-bulk-upload.png](prints/kmc-17-content-bulk-upload.png)](prints/kmc-17-content-bulk-upload.png) |
| Studio | [![kmc-18-studio.png](prints/kmc-18-studio.png)](prints/kmc-18-studio.png) |
| Analytics | [![kmc-19-analytics.png](prints/kmc-19-analytics.png)](prints/kmc-19-analytics.png) |
| Settings account | [![kmc-20-settings-account.png](prints/kmc-20-settings-account.png)](prints/kmc-20-settings-account.png) |
| Settings integration | [![kmc-21-settings-integration.png](prints/kmc-21-settings-integration.png)](prints/kmc-21-settings-integration.png) |
| Settings access control | [![kmc-22-settings-access-control.png](prints/kmc-22-settings-access-control.png)](prints/kmc-22-settings-access-control.png) |
| Settings transcoding | [![kmc-23-settings-transcoding.png](prints/kmc-23-settings-transcoding.png)](prints/kmc-23-settings-transcoding.png) |
| Settings custom data | [![kmc-24-settings-custom-data.png](prints/kmc-24-settings-custom-data.png)](prints/kmc-24-settings-custom-data.png) |
| Settings my user | [![kmc-25-settings-my-user.png](prints/kmc-25-settings-my-user.png)](prints/kmc-25-settings-my-user.png) |
| Settings account info | [![kmc-26-settings-account-info.png](prints/kmc-26-settings-account-info.png)](prints/kmc-26-settings-account-info.png) |
| Admin users | [![kmc-27-admin-users.png](prints/kmc-27-admin-users.png)](prints/kmc-27-admin-users.png) |
| Admin roles | [![kmc-28-admin-roles.png](prints/kmc-28-admin-roles.png)](prints/kmc-28-admin-roles.png) |
| Create upload menu | [![kmc-29-create-upload-menu.png](prints/kmc-29-create-upload-menu.png)](prints/kmc-29-create-upload-menu.png) |

## kaltura-console (Laravel) against the AIO

| Screen | Screenshot |
|---|---|
| Login | [![01-login.png](prints/kaltura-console/01-login.png)](prints/kaltura-console/01-login.png) |
| Dashboard | [![02-dashboard.png](prints/kaltura-console/02-dashboard.png)](prints/kaltura-console/02-dashboard.png) |
| Media list | [![03-media-list.png](prints/kaltura-console/03-media-list.png)](prints/kaltura-console/03-media-list.png) |
| Media upload | [![04-media-upload.png](prints/kaltura-console/04-media-upload.png)](prints/kaltura-console/04-media-upload.png) |
| Media show bbb | [![05-media-show-bbb.png](prints/kaltura-console/05-media-show-bbb.png)](prints/kaltura-console/05-media-show-bbb.png) |
| System health | [![06-system-health.png](prints/kaltura-console/06-system-health.png)](prints/kaltura-console/06-system-health.png) |

## Go console validation (2026-09-25 UTC)

The Go rewrite is installed alongside Kaltura on the existing noble `aio` VM
at `http://192.168.56.20:8080`. It uses partner 102 and its own SQLite database;
no Laravel or Kaltura server data was migrated or removed.

Validated locally with console packages `0.1.0~rc1` and `0.1.0~rc2`:

- `.deb` fresh install, hardened systemd service, `/healthz` and login HTTP 200.
- Package upgrade retained the exact configuration checksum, local user and
  existing authenticated browser session, changed the service PID, and served
  the upgraded version.
- `kaltura-console/tests/e2e.sh` exited 0 after login, both upload transfer phases,
  Kaltura processing to READY, HTML5 playback, Range 206 (1024 bytes and matching
  Content-Range), edit/delete, local-user creation/role/password/delete, health,
  English navigation, logout/revocation, zero computed border radius and mobile
  layouts at 360 px. Only generated test media/users were deleted.
- MariaDB last-admin concurrency test passed five repetitions over independent
  connection pools in a separate `kconsole_test_*` database. Migrations ran
  repeatedly without changing the Kaltura schema.
- Go tests passed with CGO disabled and with race detection; frontend production
  build, TypeScript/ESLint/radius lint and 11 Vitest tests passed.

Screenshots: [`prints/kaltura-console-go/`](prints/kaltura-console-go/).
Code, operator documentation and diagrams: [`../kaltura-console/README.md`](../kaltura-console/README.md).
The console GitHub workflow is separate from the server DEB/RPM workflows.
No public release has been published by this validation. Ubuntu 26.04 server
packaging and Rocky Linux 9 server packaging are separate workstreams.
