# Contributing to delivery-gate

Thanks for your interest! delivery-gate is a dual-layer mechanical gate for AI agent output quality — two Python scripts (~400 lines total) that run as Claude Code Stop hooks.

## Development Setup

Zero dependencies, zero build. Copy the scripts and run them:

```bash
cp config-health.py quality-gate.py ~/.claude/scripts/
python3 config-health.py --check   # health dashboard
python3 quality-gate.py            # gate check
```

## Testing

There is no test suite yet (see [#1](issues) for `good first issue`). Manual verification:

```bash
# Config health dashboard (never blocks, exit 0 always)
python3 config-health.py --check

# Quality gate (blocks when ≥3 libraries stale)
python3 quality-gate.py
echo $?  # 0 = pass, 2 = block

# Hook mode (silent on success)
python3 config-health.py --hook
python3 quality-gate.py
```

## Code Standards

- **Python 3.8+** — no f-string `=` debug syntax, no `str.removeprefix()`
- **Stdlib only** — zero pip dependencies
- **stdin/stdout contract** — scripts read nothing from stdin; stdout is reserved for results; stderr for diagnostics
- **Exit code convention** — `0` = pass (or soft warning), `2` = hard block
- **Keep it small** — the entire project is ~400 lines. A PR adding >100 lines needs strong justification

## PR Process

1. **Open an issue first** — describe what you want to change and why
2. Fork and create a feature branch
3. Keep changes focused — one concern per PR
4. Test manually with `--check` and default modes
5. Link the issue in your PR description

## Project Philosophy

- **Mechanical, not semantic** — checks use regex and mtime, never AI judgment
- **Silent on success** — normal path produces zero output (zero token cost)
- **Soft on process, hard on output** — config-health never blocks; quality-gate does at a defined threshold
