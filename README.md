# Delivery Gate — Dual-Layer Mechanical Gate for Claude Code

A **two-layer Stop hook system** that monitors process and enforces output — using only deterministic checks: regex markers, file timestamps, and disk usage. No AI inference.

```
config-health（Process Monitor）→ tracks rule execution → soft feedback (never blocks)
         ↓
quality-gate（Output Enforcer）→ checks output completeness → hard block (≥3 stale → exit 2)
         ↓
       Delivery
```

| Dimension | config-health | quality-gate |
|-----------|--------------|--------------|
| **Problem** | Doing it right | Done doing it |
| **Checks** | Process (rule markers) | Output (five-library mtime) |
| **Method** | Regex counting `[✓RULE]` | File timestamps |
| **Blocks** | Never blocks (exit 0) | ≥3 stale → hard block |
| **Cost** | Normal path: zero tokens | Only surfaces on anomaly |
| **Trigger** | Every Stop | Every Stop (after config-health) |

## Why Two Layers

A single-layer gate is either too soft (reminders → ignored) or too hard (frequent blocks → bypassed). Two layers each do one job:

- **Process layer (soft):** Rule execution rate low? Remind but don't block — might be exploring, experimenting
- **Output layer (hard):** Five libraries not updated? Block — delivery must be complete, non-negotiable

The boundary isn't "importance" — it's **"can this be fixed later?"** Missed rule execution can be retroactively marked. Missed output records are lost forever.

## What's Inside

### config-health.py — Process Monitor

| Check | Mechanism | On Hit |
|-------|-----------|--------|
| Rule marker counting | Regex `[✓THINK]` `[✓CONTEXT]` `[✓DELIVERY]` in transcript | Log to JSONL, update pending-verifications.md |
| Verification tracking | 3-session window per rule | Verified → auto-remove from pending list |
| Config integrity | Core files exist + non-empty | Dashboard alert (manual check only) |
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

Manual health dashboard:
```bash
python3 ~/.claude/scripts/config-health.py --check
```

## Community

delivery-gate is a community project — contributions and feedback welcome.

- **Found a bug?** [Open an issue](https://github.com/YuhaoLin2005/delivery-gate/issues/new?template=bug_report.md)
- **Have an idea?** [Request a feature](https://github.com/YuhaoLin2005/delivery-gate/issues/new?template=feature_request.md)
- **Want to contribute?** Read [CONTRIBUTING.md](CONTRIBUTING.md) — good first issues are tagged and waiting
- **Deep dive:** [checkgrow](https://github.com/YuhaoLin2005/checkgrow) explains the methodology behind the mechanical gate

Maintained by [@YuhaoLin2005](https://github.com/YuhaoLin2005)

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

## The Dual-Layer Principle

> **"The boundary between soft and hard is not importance — it's whether it can be fixed later."**

This architecture transplants three existing practices into AI config management:
- **TDD verifiability**: Rules embed their own success criteria (`[✓THINK]` markers) — following isn't a vague promise, it's a countable binary
- **Unix silence**: "No news is good news" → normal path consumes zero context tokens
- **Control theory feedback loop**: config-health.py → pending-verifications.md → startup read → AI focuses → verification passes → auto-delete

## Limitations

The mechanical gate enforces **habits** and **completeness**, not content quality. It checks that you captured learning, not whether the learning is correct. For reasoning quality, pair with [self-audit](https://github.com/YuhaoLin2005/self-audit).

## Compatibility

- Python 3.8+
- Windows, macOS, Linux
- Zero dependencies beyond stdlib

## Quality

4 rounds of CodeRabbit + Greptile review on quality-gate.py caught 9 real bugs:
- Missing stdin→stdout pass-through
- Python 3.8 crash (`list[str]` not subscriptable)
- Non-recursive directory scan
- Unhandled OSError exceptions

## Related

- [checkgrow](https://github.com/YuhaoLin2005/checkgrow) — Full AI quality toolkit (delivery-gate is the mechanical layer)
- [self-audit](https://github.com/YuhaoLin2005/self-audit) — Four-dimension reasoning quality audit
- [dual-pool-review](https://github.com/YuhaoLin2005/dual-pool-review) — Multi-persona adversarial review methodology

## License

MIT
