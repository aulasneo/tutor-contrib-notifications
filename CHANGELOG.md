# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Unreleased

- Align local development automation with the branding plugin by adding dev/test requirements, expanding the `Makefile`, and modernizing build checks.
- Replace the previous CI setup with branding-style GitHub Actions for test and publish workflows.
- Restrict supported Python versions to 3.11+ in package metadata and ignore generated Tutor local test artifacts.

## Version 20.0.0 (2026-03-17)

- Mark this repository as deprecated starting with Ulmo in favor of `openedx/tutor-contrib-platform-notifications`

## Version 19.0.1 (2025-07-16)

- Fix weekly digest job

## Version 20.0.0 (2026-03-17)

- Add Tutor 20.x / Open edX Teak compatibility metadata
- Fix Kubernetes notification CronJobs to use the standard LMS job environment
- Add configuration toggles for notification waffle flags
- Fix CI compile checks for the current project layout

## [Version 19.0.0 (2025-05-16)]

### Added
- Initial implementation of Tutor notifications plugin
- Kubernetes job patches for notifications
- LMS settings integration
- MFE production settings configuration
- Notification task initialization script

### Changed
- Updated README documentation

### Fixed
- Initial setup and configuration issues

[Version 19.0.0 (2025-05-16)]: https://github.com/aulasneo/tutor-contrib-notifications/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/aulasneo/tutor-contrib-notifications/compare/v0.0.0...v0.1.0
