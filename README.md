# Delivery Gate — Mechanical Quality Gate for Claude Code

A **Stop hook** that checks session hygiene before Claude can finish — using only deterministic checks: file timestamps, regex patterns, and disk usage. No AI inference.

This is a **mechanical** gate. It doesn't evaluate whether your thinking was good — it checks whether you captured what you learned. For reasoning quality, pair it with `self-audit`.

200 lines of Python. Stdlib only. 4 rounds of automated review found 9 bugs.

## What It Checks

| Check | Mechanism | On Hit |
|-------|-----------|--------|
| Rationalization patterns | Regex on transcript | Warning only (never blocks) |
| Stale learning libraries | File modification timestamps | Blocks if >=3 stale OR growth-log stale after complex task |
| Disk space < 15GB | `shutil.disk_usage` | Block (exit 2) |

Rationalization detection warns about patterns like "skip tests for now" and "pre-existing bug." It never blocks on its own — regex heuristics can false-positive. The blocking conditions are: disk critical, or the learning libraries weren't touched after a complex session.

## Why

Claude Code's built-in checks cover code quality (build → type → lint → test). A different failure mode goes unchecked: the agent ships working code while neglecting session hygiene — learning not captured, shortcuts rationalized, disk running out.

The hook enforces the habit: complex task → must touch learning libraries.

## Install

```bash
cp quality-gate.py ~/.claude/scripts/
```

Add to `~/.claude/settings.json`:
```json
{
  "hooks": {
    "Stop": [{
      "hooks": [{
        "type": "command",
        "command": "python3 ~/.claude/scripts/quality-gate.py",
        "timeout": 5000
      }]
    }]
  }
}
```

## Configuration

Edit `quality-gate.py`:

| Variable | Default | Purpose |
|----------|---------|---------|
| `RATIONALIZE` | 4 patterns | Regex patterns for rationalization detection |
| `LIBS` | 5 libraries | Files/dirs to check for today's updates |
| `COMPLEX_THRESHOLD` | 3 | Edit/Write calls to classify as complex |
| `DISK_WARN_GB` | 50 | Warn below this |
| `DISK_CRIT_GB` | 15 | Block below this |

## Limitations

The hook enforces the **habit** of touching learning libraries, not the quality of what was written. If `output-index.md` gets updated but `growth-log` is skipped, the hook passes. This is by design — mechanical gates check machine-verifiable facts. For content quality, use `self-audit`.

## Compatibility

- Python 3.8+
- Windows, macOS, Linux
- Zero dependencies beyond stdlib

## Quality

4 rounds of CodeRabbit + Greptile review caught 9 real bugs:
- Missing stdin→stdout pass-through
- Python 3.8 crash (`list[str]` not subscriptable)
- Non-recursive directory scan
- Unhandled OSError exceptions

## Related

- [checkgrow](https://github.com/YuhaoLin2005/checkgrow) — Full AI quality toolkit (delivery-gate is one component)
- [self-audit](https://github.com/YuhaoLin2005/self-audit) — Four-dimension reasoning quality audit
- [ECC PR #2378](https://github.com/affaan-m/ECC/pull/2378) — Active upstream contribution

## License

MIT
