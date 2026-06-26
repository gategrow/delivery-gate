#!/usr/bin/env python3
"""
Stop hook: quality gate with delivery check.
Detects incomplete work, stale learning logs, and low disk space.
Blocks Claude from stopping when a complex task completed without learning capture.

Install: cp this file to ~/.claude/scripts/quality-gate.py
Configure: Add to settings.json hooks.Stop
"""
from __future__ import annotations

import sys
import os
import re
import datetime
import shutil
import logging
from typing import Optional

# ---- Configuration ----
# Patterns that indicate rationalized incompleteness
RATIONALIZE = [
    r'(?:this|that)\s+is\s+a\s+pre[- ]existing\s+(?:issue|bug)\b(?!\s+(?:that|which|and))',
    r'skipping\s+(?:tests?|lint|coverage|type[- ]check)\s+for\s+now',
    r'(?:tests?|coverage)\s+(?:are|is)\s+(?:failing|broken)\s+but\s+(?:I|we)\'ll\s+(?:fix|address)',
    r'(?:not\s+addressing|won\'t\s+fix|leaving)\s+the\s+(?:failing|broken)\s+(?:test|build)',
]

# Files to check for today's updates (relative to project memory dir)
# Customize these to match your learning-capture workflow
LIBS = {
    'ratings-tracker': 'ratings-tracker.md',
    'decisions-log': 'decisions/log.md',
    'growth-log': 'growth-log/',          # directory — any file updated today counts
    'output-index': 'output-index.md',
    'tooling-capabilities': 'tooling_capabilities.md',
}

MIN_CHARS = 40          # minimum transcript length to trigger checks
COMPLEX_THRESHOLD = 3   # Edit/Write calls to classify as "complex task"
DISK_WARN_GB = 50       # warn when free space below this
DISK_CRIT_GB = 15       # block stop when below this
# ---- End Configuration ----

# Configure stderr logger per coding guidelines
logging.basicConfig(
    stream=sys.stderr,
    format='%(levelname)s: %(message)s',
    level=logging.WARNING,
)
log = logging.getLogger('quality-gate')


def get_project_memory_dir() -> Optional[str]:
    """Find the current project's memory directory.
    Returns None if no memory directory exists for this project.
    Does NOT fall back to other projects (privacy boundary)."""
    cwd = os.environ.get('CLAUDE_PROJECT_DIR', os.getcwd())
    safe = cwd.replace(':', '').replace('\\', '-').replace('/', '-')
    mem = os.path.expanduser(f'~/.claude/projects/{safe}/memory')
    if os.path.isdir(mem):
        return mem
    return None


def check_disk() -> Optional[int]:
    """Check free space on the disk containing the home directory.
    Works cross-platform: macOS, Linux, Windows.
    Returns free GB, or None if the home directory is unavailable
    (e.g. on a headless CI runner without a real home dir)."""
    try:
        home = os.path.expanduser('~')
        free_gb = shutil.disk_usage(home).free // (2**30)
        return free_gb
    except (FileNotFoundError, PermissionError, OSError):
        # Home dir not accessible — log and continue without disk check
        log.warning('cannot check disk space (home dir inaccessible)')
        return None


def check_stale_libs(mem_dir: str) -> list[str]:
    """Return list of library names not updated today."""
    today = datetime.date.today()
    stale: list[str] = []
    try:
        for name, path in LIBS.items():
            full = os.path.join(mem_dir, path)
            if os.path.isdir(full):
                has_today = False
                # Use os.walk to handle nested subdirectories (e.g. growth-log/2026/06-26.md)
                for dirpath, _dirnames, filenames in os.walk(full):
                    for f in filenames:
                        fp = os.path.join(dirpath, f)
                        try:
                            mt = datetime.datetime.fromtimestamp(os.path.getmtime(fp)).date()
                            if mt == today:
                                has_today = True
                                break
                        except OSError:
                            continue  # skip unreadable files
                    if has_today:
                        break
                if not has_today:
                    stale.append(name)
            elif os.path.exists(full):
                try:
                    mt = datetime.datetime.fromtimestamp(os.path.getmtime(full)).date()
                    if mt != today:
                        stale.append(name)
                except OSError:
                    stale.append(name)  # can't check → treat as stale
            else:
                stale.append(name)
    except OSError as e:
        log.warning('cannot check stale libs in %s: %s', mem_dir, e)
        return []  # inconclusive — don't block on filesystem errors
    return stale


def count_edits(text: str) -> int:
    """Count Edit/Write tool invocations in the last assistant response."""
    tail = text[-8000:]
    return len(re.findall(r'(?:Edit|Write)\s+', tail))


def main() -> None:
    raw = sys.stdin.read()

    # Stop-hook contract: echo stdin to stdout so the harness can forward the payload
    sys.stdout.write(raw)

    # 1. Disk check FIRST — must always run, regardless of transcript length
    disk_free = check_disk()
    if disk_free is not None:
        if disk_free < DISK_CRIT_GB:
            log.warning('Blocked: disk space at %dGB (threshold: %dGB). Free space before continuing.',
                        disk_free, DISK_CRIT_GB)
            sys.exit(2)
        if disk_free < DISK_WARN_GB:
            log.warning('WARN: disk space %dGB free', disk_free)

    # 2. Short session — skip remaining checks
    if len(raw) < MIN_CHARS:
        sys.exit(0)

    tail = raw[-8000:]

    # 3. Rationalization pattern detection
    hits = []
    for p in RATIONALIZE:
        m = re.search(p, tail, re.IGNORECASE)
        if m:
            hits.append(m.group(0)[:80])
    if hits:
        log.warning('quality-gate: %s', hits)

    # 4. Learning capture check
    mem_dir = get_project_memory_dir()
    edit_count = count_edits(raw)
    is_complex = edit_count >= COMPLEX_THRESHOLD

    if mem_dir:
        stale = check_stale_libs(mem_dir)
    else:
        # No memory dir → user hasn't opted into learning capture yet.
        # Don't block them — the hook should only enforce what was set up.
        stale = []

    # Build warning message
    parts = []
    if is_complex:
        status_icons = ['X' if s in stale else 'O' for s in LIBS]
        parts.append(
            f'\n  Complex task ({edit_count} edits). '
            f'Check: [{"][".join(f"{k}:{v}" for k,v in zip(LIBS.keys(), status_icons))}]'
        )
    if stale:
        parts.append(f'  Stale ({len(stale)}): {", ".join(stale)}')

    if parts:
        log.warning('\n'.join(parts))

    # 5. Block if complex task completed without learning capture
    if is_complex and len(stale) >= len(LIBS):
        log.warning('Blocked: complex task completed but no learning captured today.')
        log.warning('Update at least one library (e.g. growth-log) before stopping.')
        sys.exit(2)

    sys.exit(0)


if __name__ == '__main__':
    main()
