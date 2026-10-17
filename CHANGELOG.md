# Changelog

All notable changes to this project are documented here.
Format: [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), versioning: [SemVer](https://semver.org/).

## [Unreleased]

### Added
- CSV loader with delimiter sniffing and BOM handling.
- Validation rules: `not_null`, `unique`, `in_range`, `matches`, and a `run_rules` registry.
- `dqcheck` CLI (`python -m dqcheck data.csv --rules rules.json`).
- Text report: violations sorted by row, per-rule summary and a PASS/FAIL line.
- `--format json` output for CI pipelines and dashboards.

### Fixed
- Invalid or unreadable rules files exit with code 2 and a clear message.
