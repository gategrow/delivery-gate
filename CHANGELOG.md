# Changelog

All notable changes to delivery-gate will be documented in this file.

## [Unreleased]

### Added
- `--version` in both scripts prints the version and exits without running hook or dashboard checks.
- **config-health.py** — process-layer soft monitor. Counts `[✓MARKER]` rule execution, writes `rule-health.jsonl`, auto-manages `pending-verifications.md`. Never blocks (exit 0 always). Three modes: `--hook` (silent), `--check` (dashboard), `--full` (detailed).
- **quality-gate.py** — output-layer hard gate. Checks five-library mtime. Blocks at ≥3 stale. Rationalization detection. Disk threshold check.

### Changed
- Execution order: config-health runs before quality-gate in Stop hooks
- Architecture: dual-layer mechanical gate (process-soft + output-hard)
- **quality-gate.py**: Added `import json` + structured JSON payload parsing (transcript_path resolution) for newer Claude Code versions
- **quality-gate.py**: Extended blocking condition — `len(stale) >= 3` OR `growth-log` stale after complex task
- **quality-gate.py**: Per-library OSError handling — one bad path no longer fails all library checks
- **quality-gate.py**: count_edits uses JSON structure pattern (`"name":\s*"(?:Edit|Write)"`) for more accurate edit counting

## [1.0.0] - 2026-06-27

### Added
- Initial release: quality-gate.py as standalone Claude Code Stop hook
- Five-library staleness check (persona/growth-log/decisions/output-index/ratings)
- Rationalization pattern detection
- Disk space threshold warning
- Exit code convention (0=pass, 2=block)
- README with install instructions and configuration guide
