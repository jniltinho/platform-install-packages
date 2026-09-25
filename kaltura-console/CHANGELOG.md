# Changelog

All notable changes to Kaltura Console are documented here.
The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

### Changed
- Smooth page transitions matching painel-golang (150 ms fade, 6 px entrance),
  with persistent navigation, a stable internally scrolling card and reduced-motion support.

### Added
- Go console with embedded Vue frontend and the square-corner criarenet theme.
- Local administrator/viewer accounts, revocable sessions, CSRF and login lockout.
- Media library, dashboard, staged streaming uploads, playback proxy and health checks.
- Cobra CLI, SQLite without CGO, optional MariaDB, systemd and nfpm packages.
