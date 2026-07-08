# Delivery Gate — Semantic Quality Gate for Claude Code

> ✅ **This module has been merged into [affaan-m/ECC](https://github.com/affaan-m/ECC) (200K+★) via [PR #2377](https://github.com/affaan-m/ECC/pull/2377) & [#2378](https://github.com/affaan-m/ECC/pull/2378), merged by maintainer [affaan-m](https://github.com/affaan-m).** Zero-config loading proposal [PR #2365](https://github.com/affaan-m/ECC/pull/2365) additionally reviewed by core maintainer with positive feedback.

A **Stop hook** that blocks Claude from finishing until quality checks pass. Unlike verification-loop (which checks build/test/lint), this checks **thinking quality**: did Claude assume something untested? Did it skip documenting a lesson? Is disk space dangerously low?

200 lines of Python. Stdlib only. Deterministic — regex pattern matching + file timestamps, no AI inference.

## What It Checks

1. **Rationalization patterns** — Detects "pre-existing bug", "skip tests for now", "tests are broken but we'll fix later"
2. **Learning capture** — Were any of 5 project memory files updated today?
3. **Disk space** — Blocks if home-directory filesystem is below 15GB
4. **Complex task detection** — Counts Edit/Write calls (3+ = complex)

When a complex task completes and no learning was captured → blocks stop (exit 2).

## Why

Claude Code's built-in checks cover code quality (build → type → lint → test). But there's a different failure mode: the agent produces working code while the **thinking was sloppy** — untested assumptions, skipped lessons, rationalized shortcuts.

Over 50 sessions of "ship and forget," the human hasn't grown. This hook enforces the habit: complex task → must capture learning.

## Install

```bash
# 1. Copy the hook script
cp quality-gate.py ~/.claude/scripts/

# 2. Add to settings.json
# {
#   "hooks": {
#     "Stop": [
#       {
#         "hooks": [{
#           "type": "command",
#           "command": "python3 ~/.claude/scripts/quality-gate.py",
#           "timeout": 5000
#         }]
#       }
#     ]
#   }
# }
```

## Learning Libraries

Create these files in your project's memory directory (`~/.claude/projects/<project>/memory/`):

```
memory/
├── ratings-tracker.md       # Skill ratings over time
├── decisions/log.md         # Decision log with review dates
├── growth-log/              # Daily learning entries (directory)
├── output-index.md          # Index of all session outputs
└── tooling_capabilities.md  # Known tools inventory
```

The hook checks if at least one file in each library was updated today. Customize `LIBS` dict to match your workflow.

## Configuration

Edit `quality-gate.py`:

| Variable | Default | Purpose |
|----------|---------|---------|
| `RATIONALIZE` | 4 patterns | Regex patterns for rationalization |
| `LIBS` | 5 libraries | Files/dirs to check for today's updates |
| `MIN_CHARS` | 40 | Minimum transcript length to trigger |
| `COMPLEX_THRESHOLD` | 3 | Edit/Write calls to classify as complex |
| `DISK_WARN_GB` | 50 | Warn below this |
| `DISK_CRIT_GB` | 15 | Block below this |

## Examples

**Normal session — allowed:**
```
edit_count=2 (< 3, not complex) → exit 0
```

**Complex task, learning captured — allowed:**
```
edit_count=5 (complex) → checks LIBS → growth-log updated today → exit 0
```

**Complex task, no learning — BLOCKED:**
```
edit_count=4 (complex) → checks LIBS → all 5 stale → exit 2
stderr: "Blocked: complex task completed but no learning captured today."
```

**Low disk space — BLOCKED:**
```
disk_free=12GB < 15GB critical → exit 2
stderr: "Blocked: disk space at 12GB (threshold: 15GB)."
```

## Compatibility

- Python 3.8+ (uses `from __future__ import annotations`)
- Cross-platform: Windows, macOS, Linux
- Zero dependencies beyond stdlib

## Quality

This code went through 4 rounds of automated code review (CodeRabbit + Greptile) with 9 real bugs found and fixed:
- Missing stdin→stdout pass-through (broke hook harness contract)
- Python 3.8 crash (`list[str]` not subscriptable before 3.9)
- Non-recursive directory scan (missed nested files)
- Unhandled OSError exceptions (crash on permission errors)
- Plus type annotations, logging, naming, and documentation fixes

## Relationship to ECC

This module originated from the Hermes Workspace self-model pipeline and was validated through the ECC open-source community:

| PR | Contribution | Status |
|----|-------------|--------|
| [#2377](https://github.com/affaan-m/ECC/pull/2377) | Growth-log learning capture module | ✅ Merged by **affaan-m** |
| [#2378](https://github.com/affaan-m/ECC/pull/2378) | Stop Hook quality gating integration | ✅ Merged by **affaan-m** |
| [#2365](https://github.com/affaan-m/ECC/pull/2365) | Zero-config delivery-gate plugin loader | 📝 Reviewed — "this is solid work" |

The quality-gate.py in this repo is the reference standalone implementation. The merged version in ECC was adapted for the project's plugin architecture.

## Related Reading

- 📄 [Hermes Workspace — full methodology & n=30 experiment](https://github.com/YuhaoLin2005/hermes-workspace)
- 📝 [How I Built a File-Timestamp-Based Feedback Loop to Enforce AI Output Quality](https://dev.to/yuhaolin2005/how-i-built-a-file-timestamp-based-feedback-loop-to-enforce-ai-output-quality-1ibc)
- 🇨🇳 [我是如何用确定性脚本构建 AI 输出质量的机械反馈环的](https://juejin.cn/post/7659251251616776219)

## License

MIT
