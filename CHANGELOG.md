# Changelog

All notable changes to this project are documented here.
Format: [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), versioning: [SemVer](https://semver.org/).

## [Unreleased]

## [1.1.1] - 2026-10-17

### Fixed
- CHANGELOG.md shipped in 1.1.0 with unresolved merge-conflict markers and without its 1.1.0 heading.
- CI now fails if any tracked file contains merge-conflict markers.

## [1.1.0] - 2026-10-17

### Added
- Gitflow walkthrough with real command output (`docs/GITFLOW_WALKTHROUGH.md`).
- `scripts/gitflow_sandbox.sh`: 8 self-contained git demos.
- Git cheat sheet and test-prep questions.

## [1.0.1] - 2026-10-17

### Fixed
- `unique` no longer reports blank values as duplicates (#5).

## [1.0.0] - 2026-10-17

### Added
- CSV loader with delimiter sniffing and BOM handling.
- Validation rules: `not_null`, `unique`, `in_range`, `matches`, and a `run_rules` registry.
- `dqcheck` CLI (`python -m dqcheck data.csv --rules rules.json`).
- Text report: violations sorted by row, per-rule summary and a PASS/FAIL line.
- `--format json` output for CI pipelines and dashboards.

### Fixed
- Invalid or unreadable rules files exit with code 2 and a clear message.

[Unreleased]: https://github.com/mohdibrahim77/week7-gitflow-simulation/compare/v1.1.1...develop
[1.1.1]: https://github.com/mohdibrahim77/week7-gitflow-simulation/compare/v1.1.0...v1.1.1
[1.1.0]: https://github.com/mohdibrahim77/week7-gitflow-simulation/compare/v1.0.1...v1.1.0
[1.0.1]: https://github.com/mohdibrahim77/week7-gitflow-simulation/compare/v1.0.0...v1.0.1
[1.0.0]: https://github.com/mohdibrahim77/week7-gitflow-simulation/releases/tag/v1.0.0
