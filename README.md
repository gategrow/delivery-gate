# Delivery Gate

> 🧩 **Digital Twin OS · 输出层质量门禁** — 自我净化闭环的最后一道物理拦截闸.
> A Stop hook for Claude Code. Two Python scripts, zero dependencies, deterministic checks only.

```
config-health（Process Monitor）→ tracks rule execution → soft feedback (never blocks)
         ↓
quality-gate（Output Enforcer）→ checks output completeness → hard block (≥3 stale → exit 2)
         ↓
       Delivery
```

## Why Two Layers

A single-layer gate is either too soft (reminders → ignored) or too hard (frequent blocks → bypassed). Two layers each do one job:

- **Process layer (soft):** Rule execution rate low? Remind but don't block — might be exploring, experimenting
- **Output layer (hard):** Learning logs not updated? Block — delivery must be complete, non-negotiable

The boundary: **can it be fixed later?** Missed rule execution can be retroactively marked. Missed output records are lost forever.

## What's Inside

### config-health.py — Process Monitor

| Check | Mechanism | On Hit |
|-------|-----------|--------|
| Rule marker counting | Regex `[✓THINK]` `[✓CONTEXT]` `[✓DELIVERY]` in transcript | Log to JSONL, update pending-verifications.md |
| Verification tracking | 3-session window per rule | Verified → auto-remove from pending list |
| Config integrity | Core files exist + non-empty | Dashboard alert |
| Session cost tier | Cumulative sessions count | Dashboard tier (L0-L3) |

### quality-gate.py — Output Enforcer

| Check | Mechanism | On Hit |
|-------|-----------|--------|
| Stale learning libraries | File modification timestamps | Block if ≥3 stale OR growth-log stale after complex task |
| Disk space < 15GB | `shutil.disk_usage` | Block (exit 2) |
| Rationalization patterns | Regex on transcript tail | Warning only (never blocks alone) |

## Install

```bash
cp config-health.py ~/.claude/scripts/
cp quality-gate.py ~/.claude/scripts/
```

Add to `~/.claude/settings.json` (order matters — config-health first):

```json
{
  "hooks": {
    "Stop": [
      {
        "type": "command",
        "command": "python3 ~/.claude/scripts/config-health.py --hook",
        "timeout": 5000
      },
      {
        "type": "command",
        "command": "python3 ~/.claude/scripts/quality-gate.py",
        "timeout": 5000
      }
    ]
  }
}
```

```bash
# Manual health dashboard
python3 ~/.claude/scripts/config-health.py --check
```

## Configuration

### config-health.py

| Variable | Default | Purpose |
|----------|---------|---------|
| `RULES` | THINK/CONTEXT/DELIVERY | Rules to track with regex markers |
| `VERIFICATION_WINDOW` | 3 | Sessions needed for rule to "pass" |
| `MIN_TOOL_CALLS_FOR_CHECK` | 5 | Minimum tools to consider session complex |
| `MIN_EDITS_FOR_DELIVERY` | 3 | Minimum edits to expect DELIVERY marker |

### quality-gate.py

| Variable | Default | Purpose |
|----------|---------|---------|
| `RATIONALIZE` | 4 patterns | Regex patterns for rationalization detection |
| `LIBS` | 5 libraries | Files/dirs to check for today's updates |
| `COMPLEX_THRESHOLD` | 3 | Edit/Write calls to classify as complex |
| `DISK_CRIT_GB` | 15 | Block below this |

## Limitations

This checks **process completeness** (did you update your logs?), not **output correctness** (is the code right?). It's a reminder system for habits and learning capture — it doesn't verify code quality or catch logic bugs. For output consistency checks, pair with [self-audit](https://github.com/gategrow/self-audit).

## Part of [gategrow](https://github.com/gategrow)

| Repo | What |
|------|------|
| **[checkgrow](https://github.com/gategrow/checkgrow)** | Unified quality framework — start here |
| **[delivery-gate](https://github.com/gategrow/delivery-gate)** | Stop hook for Claude Code |
| **[self-audit](https://github.com/gategrow/self-audit)** | `pip install`-able four-dimension audit |
| **[session-cost](https://github.com/gategrow/session-cost)** | L0→L3 layered cost tracking |
| **[dual-pool-review](https://github.com/gategrow/dual-pool-review)** | Named-persona adversarial review methodology |

## License

MIT