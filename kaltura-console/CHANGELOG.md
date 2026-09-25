# Changelog

All notable changes to Kaltura Console are documented here.
The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

## [0.1.0] — 2026-09-25

First release of the standalone Go console with an embedded web interface.

### Fixed
- Preserve HTTPS in progressive media redirects when the delivery host uses TLS.
- Stream uploads with an exact multipart Content-Length for PHP-FPM on Rocky 9.
- Namespace prefixed session cookies so old root cookies cannot reactivate a login after logout.

### Changed
- Smooth page transitions matching painel-golang (150 ms fade, 6 px entrance),
  with persistent navigation, a stable internally scrolling card and reduced-motion support.

### Added
- Configurable application URL prefix for UI, assets, API, media and health routes,
  with prefix-scoped session cookies and one reusable frontend build.
- Standalone HTTPS with an operator-supplied certificate/key or a persistent
  ten-year self-signed fallback; explicit rotation and unsafe-material rejection.
- Serve-time HTTPS, TLS path/directory and base-path flags overriding environment
  and file settings; root HTTP defaults remain unchanged.
- Go console with embedded Vue frontend and the square-corner criarenet theme.
- Local administrator/viewer accounts, revocable sessions, CSRF and login lockout.
- Media library, dashboard, staged streaming uploads, playback proxy and health checks.
- Cobra CLI, SQLite without CGO, optional MariaDB, systemd and nfpm packages.
