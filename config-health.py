#!/usr/bin/env python3
"""
Stop hook + manual check: rule execution health monitor.
Two modes:
  --hook   Silent stop-hook: count rule markers in transcript, log to JSONL,
           update pending-verifications.md. Never blocks (exit 0 always).
  --check  Manual dashboard: tri-color health overview.
           🟢 normal (folded) / 🟡 attention / 🔴 broken.

Install: cp to ~/.claude/scripts/config-health.py
Configure: Add to settings.json hooks.Stop BEFORE quality-gate.py
"""
from __future__ import annotations

import sys
import os
import re
import json
import datetime
import logging
from typing import Optional

# ---- Configuration ----
# Rules to track and their transcript markers
RULES = {
    'THINK':    r'\[✓THINK\]',
    'CONTEXT':  r'\[✓CONTEXT\]',
    'DELIVERY': r'\[✓DELIVERY\]',
}

# How many recent sessions to check for "verified" status
VERIFICATION_WINDOW = 3

# Minimum tool calls for a session to be "complex enough" to expect rule markers
MIN_TOOL_CALLS_FOR_CHECK = 5

# Minimum edits for DELIVERY check (only care about delivery after code changes)
MIN_EDITS_FOR_DELIVERY = 3

# Health log: one JSONL record per session
HEALTH_LOG = os.path.expanduser('~/.claude/session-data/rule-health.jsonl')

# Pending verifications file (relative to project memory dir)
PENDING_FILE = 'pending-verifications.md'

# ---- End Configuration ----
# SYNC: Three code blocks below are duplicated in quality-gate.py:
#   1. get_project_memory_dir() function
#   2. JSON transcript_path parsing (in hook_mode)
#   3. LIBS dictionary (in check_five_libs, already noted inline)
# Update quality-gate.py when changing any of these.

logging.basicConfig(
    stream=sys.stderr,
    format='%(levelname)s: %(message)s',
    level=logging.WARNING,  # Silent on clean
)
log = logging.getLogger('config-health')


# SYNC: Duplicated in quality-gate.py. Update both when changing.
def get_project_memory_dir() -> Optional[str]:
    """Find current project's memory directory."""
    cwd = os.environ.get('CLAUDE_PROJECT_DIR', os.getcwd())
    safe = cwd.replace(':', '-').replace('\\', '-').replace('/', '-')
    mem = os.path.expanduser(f'~/.claude/projects/{safe}/memory')
    if os.path.isdir(mem):
        return mem
    return None


def count_tool_calls(text: str) -> int:
    """Count tool invocations in transcript."""
    return len(re.findall(r'"name":\s*"(?:Edit|Write|Bash|Read|Grep|Glob|Agent|Skill|WebSearch|WebFetch|Task)"', text))


def count_edits(text: str) -> int:
    """Count Edit/Write tool invocations in transcript."""
    return len(re.findall(r'"name":\s*"(?:Edit|Write)"', text))


def count_markers(text: str) -> dict[str, int]:
    """Count [✓RULE] markers in transcript."""
    counts = {}
    for rule, pattern in RULES.items():
        counts[rule] = len(re.findall(pattern, text))
    return counts


def parse_pending_verifications(filepath: str) -> list[dict]:
    """Parse pending-verifications.md table into list of rows.
    Returns empty list if file missing or unparseable."""
    if not os.path.exists(filepath):
        return []
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except (OSError, UnicodeDecodeError):
        return []

    rows = []
    in_table = False
    for line in content.splitlines():
        line = line.strip()
        if line.startswith('| 规则 |'):
            in_table = True
            continue
        if in_table and line.startswith('|---'):
            continue
        if in_table and line.startswith('| ') and not line.startswith('| 规则'):
            cols = [c.strip() for c in line.split('|')[1:-1]]
            if len(cols) >= 6:
                rows.append({
                    'rule': cols[0],
                    'expected': cols[1],
                    'condition': cols[2],
                    'since': cols[3],
                    'source': cols[4],
                    'status': cols[5],
                })
        elif in_table and line.startswith('##'):
            in_table = False
    return rows


def read_health_history() -> list[dict]:
    """Read rule-health.jsonl, return list of recent records."""
    if not os.path.exists(HEALTH_LOG):
        return []
    records = []
    try:
        with open(HEALTH_LOG, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        records.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue
    except OSError:
        return []
    return records


def check_rule_passing(rule: str, history: list[dict], window: int = VERIFICATION_WINDOW) -> bool:
    """Check if rule has passed in the last `window` sessions.
    'Pass' means at least 1 marker found in a session with >= MIN_TOOL_CALLS_FOR_CHECK tool calls."""
    recent = [h for h in history[-window:] if h.get('tool_calls', 0) >= MIN_TOOL_CALLS_FOR_CHECK]
    if len(recent) < window:
        return False  # Not enough data yet
    return all(h.get(rule, 0) >= 1 for h in recent)


def write_health_record(counts: dict[str, int], tool_calls: int, edits: int) -> None:
    """Append a health record to the JSONL log. Dedupes: skips if last entry <60s old."""
    try:
        os.makedirs(os.path.dirname(HEALTH_LOG), exist_ok=True)

        # Dedup: skip if last entry is within 60s (same session, duplicate hook fire)
        if os.path.exists(HEALTH_LOG):
            try:
                with open(HEALTH_LOG, 'r', encoding='utf-8') as f:
                    lines = [l for l in f if l.strip()]
                if lines:
                    last = json.loads(lines[-1])
                    last_ts = datetime.datetime.fromisoformat(last['ts'])
                    now = datetime.datetime.now()
                    if (now - last_ts).total_seconds() < 60:
                        return  # Duplicate — same session
            except (json.JSONDecodeError, KeyError, ValueError, OSError):
                pass  # Corrupt log → continue to write

        now = datetime.datetime.now()
        record = {
            'ts': now.isoformat(),
            'date': now.strftime('%Y-%m-%d'),
            'time': now.strftime('%H:%M'),
            'tool_calls': tool_calls,
            'edits': edits,
            **counts,
        }
        with open(HEALTH_LOG, 'a', encoding='utf-8') as f:
            f.write(json.dumps(record, ensure_ascii=False) + '\n')
    except OSError as e:
        log.warning('Cannot write health record: %s', e)


def update_pending_file(mem_dir: str, counts: dict[str, int], tool_calls: int, edits: int) -> None:
    """Update pending-verifications.md based on current health data."""
    pending_path = os.path.join(mem_dir, PENDING_FILE)
    if not os.path.exists(pending_path):
        return  # File doesn't exist yet — nothing to update

    history = read_health_history()
    rows = parse_pending_verifications(pending_path)

    # Determine which rules should be tracked
    rules_to_track = set()
    for rule in RULES:
        count = counts.get(rule, 0)
        if rule == 'DELIVERY':
            relevant = edits >= MIN_EDITS_FOR_DELIVERY
        else:
            relevant = tool_calls >= MIN_TOOL_CALLS_FOR_CHECK

        if relevant and count == 0:
            rules_to_track.add(rule)

    # Check which tracked rules are now passing
    verified = set()
    for row in rows:
        rule = row['rule']
        if rule in RULES and row['status'] in ('🔴 待验证', '🟡 观察中'):
            if check_rule_passing(rule, history):
                verified.add(rule)
        # Keep rules that are still active
        if row['status'] not in ('🟢 已验证', '⚫ 已放弃'):
            rules_to_track.add(rule)

    # Rebuild the file
    try:
        with open(pending_path, 'r', encoding='utf-8') as f:
            original = f.read()
    except OSError:
        return

    # Find and update the table
    lines = original.splitlines()
    new_lines = []
    in_table = False
    table_done = False
    today = datetime.date.today().isoformat()

    for line in lines:
        stripped = line.strip()

        if stripped.startswith('| 规则 |'):
            in_table = True
            new_lines.append(line)
            continue
        if in_table and stripped.startswith('|---'):
            new_lines.append(line)
            continue
        if in_table and stripped.startswith('##'):
            in_table = False
            table_done = True

        if in_table and stripped.startswith('| ') and not stripped.startswith('| 规则'):
            cols = [c.strip() for c in stripped.split('|')[1:-1]]
            if len(cols) >= 6:
                rule = cols[0]
                if rule in verified:
                    # Mark verified, will be auto-deleted next time
                    cols[5] = '🟢 已验证'
                    new_lines.append('| ' + ' | '.join(cols) + ' |')
                elif rule in rules_to_track and cols[5] not in ('🔴 待验证', '🟡 观察中'):
                    # Update existing row's status if not already tracked
                    new_lines.append(line)
                else:
                    new_lines.append(line)
                continue

        if table_done:
            new_lines.append(line)
            continue
        if not in_table:
            new_lines.append(line)

    # Remove 🟢 已验证 rows (they auto-delete after one session of being verified)
    final_lines = []
    in_table = False
    for line in new_lines:
        stripped = line.strip()
        if stripped.startswith('| 规则 |'):
            in_table = True
            final_lines.append(line)
            continue
        if in_table and stripped.startswith('|---'):
            final_lines.append(line)
            continue
        if in_table and stripped.startswith('##'):
            in_table = False

        if in_table and stripped.startswith('| ') and not stripped.startswith('| 规则'):
            cols = [c.strip() for c in stripped.split('|')[1:-1]]
            if len(cols) >= 6 and '🟢 已验证' in cols[5]:
                continue  # Auto-delete verified items

        final_lines.append(line)

    new_content = '\n'.join(final_lines) + '\n'

    try:
        with open(pending_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
    except OSError as e:
        log.warning('Cannot update pending verifications: %s', e)


def hook_mode() -> None:
    """Stop hook: monitor rule execution, silently log, update pending verifications."""
    raw = sys.stdin.read()

    # Stop-hook contract: echo stdin to stdout
    sys.stdout.write(raw)

    # Resolve transcript — decode structured JSON with transcript_path
    # SYNC: Duplicated in quality-gate.py. Update both when changing.
    transcript = raw
    try:
        payload = json.loads(raw)
        if isinstance(payload, dict) and 'transcript_path' in payload:
            tp = os.path.expanduser(payload['transcript_path'])
            if os.path.exists(tp):
                with open(tp, 'r', encoding='utf-8') as f:
                    transcript = f.read()
    except (json.JSONDecodeError, TypeError, OSError):
        pass

    # Count stuff
    tool_calls = count_tool_calls(transcript)
    edits = count_edits(transcript)
    counts = count_markers(transcript)

    # Write health record
    write_health_record(counts, tool_calls, edits)

    # Update pending verifications if we have a memory dir
    mem_dir = get_project_memory_dir()
    if mem_dir:
        update_pending_file(mem_dir, counts, tool_calls, edits)

    # Always exit 0 — this is a monitor, never a gate
    sys.exit(0)


# ---- Check mode (manual dashboard) ----

def check_five_libs(mem_dir: str) -> dict:
    """Check if five learning libraries have today's updates.
    Returns {name: status} where status is '🟢', '🟡', or '🔴'."""
    # Same library definitions as quality-gate.py
    LIBS = {
        'ratings-tracker': 'ratings-tracker.md',
        'decisions-log': 'decisions/log.md',
        'growth-log': 'growth-log/',
        'output-index': 'output-index.md',
        'tooling-capabilities': 'tooling_capabilities.md',
    }
    today = datetime.date.today()
    results = {}
    for name, path in LIBS.items():
        full = os.path.join(mem_dir, path)
        try:
            if os.path.isdir(full):
                found = False
                for dirpath, _dirnames, filenames in os.walk(full):
                    for f in filenames:
                        fp = os.path.join(dirpath, f)
                        try:
                            mt = datetime.datetime.fromtimestamp(os.path.getmtime(fp)).date()
                            if mt == today:
                                found = True
                                break
                        except OSError:
                            continue
                    if found:
                        break
                results[name] = '🟢' if found else '🔴'
            elif os.path.exists(full):
                try:
                    mt = datetime.datetime.fromtimestamp(os.path.getmtime(full)).date()
                    results[name] = '🟢' if mt == today else '🔴'
                except OSError:
                    results[name] = '🔴'
            else:
                results[name] = '🔴'
        except OSError:
            results[name] = '🔴'
    return results


def check_rule_health() -> dict:
    """Check rule execution rates from health log.
    Returns summary dict with per-rule stats."""
    history = read_health_history()
    if not history:
        return {'status': '🔴', 'detail': 'No health data yet'}

    # Last VERIFICATION_WINDOW sessions
    relevant = [h for h in history[-VERIFICATION_WINDOW:]
                if h.get('tool_calls', 0) >= MIN_TOOL_CALLS_FOR_CHECK]

    rule_stats = {}
    for rule in RULES:
        passes = sum(1 for h in relevant if h.get(rule, 0) >= 1)
        total = len(relevant)
        rate = f'{passes}/{total}' if total > 0 else 'N/A'
        if total >= VERIFICATION_WINDOW and passes == total:
            icon = '🟢'
        elif total > 0 and passes > 0:
            icon = '🟡'
        else:
            icon = '🔴'
        rule_stats[rule] = f'{icon} {rate}'

    return {
        'status': '🟢' if all('🟢' in v for v in rule_stats.values()) else '🟡',
        'rules': rule_stats,
        'total_sessions': len(history),
    }


def check_config_integrity() -> dict:
    """Check that core config files exist and are minimally parseable."""
    home = os.path.expanduser('~/.claude')
    files = {
        'CLAUDE.md': os.path.join(home, 'CLAUDE.md'),
        'SOUL.md': os.path.join(home, 'SOUL.md'),
        'INTERFACE.md': os.path.join(home, 'INTERFACE.md'),
        'BODY.md': os.path.join(home, 'BODY.md'),
    }
    missing = []
    for name, path in files.items():
        if not os.path.exists(path):
            missing.append(f'🔴 {name}: missing')
        elif os.path.getsize(path) < 10:
            missing.append(f'🔴 {name}: empty/corrupt')

    if missing:
        return {'status': '🔴', 'missing': missing}
    return {'status': '🟢', 'detail': 'All 4 core files present'}


def check_pending_count(mem_dir: str) -> dict:
    """Count pending verification items."""
    pending_path = os.path.join(mem_dir, PENDING_FILE)
    if not os.path.exists(pending_path):
        return {'status': '🟢', 'count': 0, 'detail': 'No pending verifications file'}

    rows = parse_pending_verifications(pending_path)
    active = [r for r in rows if r['status'] in ('🔴 待验证', '🟡 观察中')]
    count = len(active)

    if count == 0:
        return {'status': '🟢', 'count': 0, 'detail': 'All clear'}
    elif count <= 3:
        return {'status': '🟡', 'count': count, 'items': [r['rule'] for r in active]}
    else:
        return {'status': '🔴', 'count': count, 'items': [r['rule'] for r in active]}


def check_session_cost() -> dict:
    """Get session cost summary from session-cost.py data."""
    cumulative_path = os.path.expanduser('~/.claude/session-data/cumulative.json')
    if not os.path.exists(cumulative_path):
        return {'status': '🟡', 'detail': 'No cumulative data'}
    try:
        with open(cumulative_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        sessions = data.get('total_sessions', 0)
        total_edits = data.get('total_edits', 0)

        if sessions >= 30:
            tier = '🔴 L3 — auto-generate optimization report'
        elif sessions >= 15:
            tier = '🟡 L2 — analyze patterns'
        elif sessions >= 5:
            tier = '🟢 L1 — observe'
        else:
            tier = '🟢 L0 — collecting'

        return {
            'status': '🟢' if sessions < 15 else ('🟡' if sessions < 30 else '🔴'),
            'sessions': sessions,
            'edits': total_edits,
            'tier': tier,
        }
    except (json.JSONDecodeError, KeyError, OSError):
        return {'status': '🔴', 'detail': 'Cumulative data corrupt'}


def check_mode() -> None:
    """Manual health dashboard: tri-color overview."""
    print('=== Config Health ===')
    print()

    # 1. Config file integrity (critical — blocks everything else)
    print('## Core Files')
    integrity = check_config_integrity()
    if integrity['status'] == '🔴':
        for m in integrity.get('missing', []):
            print(f'  {m}')
    else:
        print(f'  {integrity["status"]} {integrity["detail"]}')
    print()

    # 2. Five learning libraries (today's updates)
    mem_dir = get_project_memory_dir()
    if mem_dir:
        print('## Learning Libraries (today)')
        libs = check_five_libs(mem_dir)
        stale_count = sum(1 for v in libs.values() if v == '🔴')
        for name, status in libs.items():
            print(f'  {status} {name}')
        if stale_count >= 3:
            print(f'  ⚠ {stale_count}/5 stale — delivery gate would BLOCK')
        elif stale_count > 0:
            print(f'  ⚡ {stale_count}/5 stale')
        print()
    else:
        print('## Learning Libraries')
        print('  🔴 No project memory directory')
        print()

    # 3. Rule execution health
    print('## Rule Execution Health')
    rule_health = check_rule_health()
    if isinstance(rule_health.get('rules'), dict):
        for rule, stat in rule_health['rules'].items():
            print(f'  {stat} {rule}')
        print(f'  ({rule_health["total_sessions"]} total sessions tracked)')
    else:
        print(f'  {rule_health["status"]} {rule_health.get("detail", "")}')
    print()

    # 4. Pending verifications
    if mem_dir:
        print('## Pending Verifications')
        pending = check_pending_count(mem_dir)
        if pending['status'] == '🟢':
            print(f'  {pending["status"]} {pending["detail"]}')
        else:
            print(f'  {pending["status"]} {pending["count"]} items pending')
            for item in pending.get('items', []):
                print(f'    - {item}')
        print()
    else:
        print('## Pending Verifications')
        print('  🟡 No memory dir — cannot check')
        print()

    # 5. Session cost tier
    print('## Session Cost')
    cost = check_session_cost()
    if 'sessions' in cost:
        print(f'  {cost["status"]} {cost["sessions"]} sessions · {cost.get("edits", 0)} edits')
        print(f'  {cost["tier"]}')
    else:
        print(f'  {cost["status"]} {cost.get("detail", "")}')
    print()

    # Summary
    statuses = [integrity['status']]
    if mem_dir:
        lib_status = '🟢' if stale_count == 0 else ('🟡' if stale_count < 3 else '🔴')
        statuses.append(lib_status)
    statuses.append(rule_health.get('status', '🟡'))
    if mem_dir:
        statuses.append(pending['status'])
    statuses.append(cost['status'])

    all_green = all(s == '🟢' for s in statuses)
    any_red = any(s == '🔴' for s in statuses)

    print('---')
    if all_green:
        print('🟢 All systems normal')
    elif any_red:
        print('🔴 Issues detected — review above')
    else:
        print('🟡 Some attention needed — review above')


# ---- Main ----

def main() -> None:
    if '--check' in sys.argv:
        check_mode()
    else:
        hook_mode()


if __name__ == '__main__':
    main()
