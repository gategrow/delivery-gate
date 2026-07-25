---
name: growth-log
description: "Use when completing a complex task, after a failure or mistake, when the delivery gate flags stale learning logs, or when reviewing what was learned over a period. Teaches how to write growth logs that extract reusable patterns — not diary entries."
metadata:
  origin: ECC
---

# Growth Log Skill

> **The problem:** Most developers write "fixed a bug in X" as a growth log. That's a diary entry, not a learning artifact. A real growth log extracts the *pattern* so you recognize it next time.
>
> **This skill teaches:** How to write growth logs that compound across sessions.

## When to Activate

Activate this skill:
- After completing a complex task (multi-file, new feature, architecture change)
- After a failure, mistake, or "that was harder than expected" moment
- When the delivery gate flags stale learning libraries
- When you want to review what you've learned over a period

**When NOT to activate:** Trivial changes (typo fixes, single-line tweaks, config value changes with no debugging). The threshold: *did this task involve debugging, redoing, rollback, or a non-obvious decision?* If yes → write an entry. If no → skip.

## The Three Rules

### Rule 1: Failures > Achievements

A failure is nutritionally denser than a success. One bug that took 2 hours to find teaches more than 3 features that worked first try.

**Bad:** "Successfully implemented the login flow."
**Good (web dev):** "Login flow: session token wasn't persisting because the cookie `SameSite` defaulted to `Lax` in Chrome 128+. Pattern: always explicitly set `SameSite=None; Secure` when cross-origin. Signal to recognize: auth breaks after browser upgrade or when crossing origin boundaries (localhost:3000 → api.example.com)."
**Good (data pipeline):** "CSV import failed silently on empty rows because `pandas.read_csv(dropna=False)` keeps zero-width rows that `len()` counts as valid. Pattern: always `df.dropna(how='all', inplace=True)` before row-count validation."

### Rule 2: The Bole Principle (伯乐原则)

Before writing a new entry, ask: *"Is this fundamentally the same as something I already recorded?"*

Same root cause, different symptom → **merge**, don't duplicate.
New root cause → new entry.

**How to check:** Before writing, search existing entries for keywords from your root cause. Example: `grep -ri 'capture' growth-log/` or maintain a one-line `patterns-index.md` listing every entry's pattern sentence. If you find a match, add your new symptom as an additional example under the existing entry rather than creating a duplicate.

**Example:** "Forgot to update output-index after creating a file" and "Forgot to update ratings-tracker after a task" — same root cause (no automatic capture trigger). Merge into one entry about "post-task capture gaps."

### Rule 3: Must Be Transferable

Every entry must answer: *"Next time I face a similar situation, what do I do differently?"*

If you can't write that sentence, you haven't extracted the pattern yet.

**How to extract a pattern from a concrete event:**
1. State what happened in one sentence ("The deployment broke because...")
2. Ask "why?" iteratively until you reach root cause (usually 3-5 whys)
3. Generalize: "What class of problem is this?" (not "Chrome 128 bug" but "browser default change breaking existing behavior")
4. Formulate as: "Next time I see [signal], I will [action]."
5. Name the signal: what specific observable tells you this pattern is active?

## Entry Template

**Scope:** One entry per distinct root cause. Typical length: 4-8 sentences. If it takes >2 minutes to write, you're narrating events instead of extracting a pattern. If <30 seconds, you haven't gone deep enough.

```markdown
## [Title: the pattern, not the event]

### Context
- What was I trying to do?
- What went wrong / what worked surprisingly well?

### Root Cause / Core Insight
- The underlying mechanism, not just the symptom

### The Pattern (transferable)
- Next time [similar situation], I will [specific action].
- Signal to recognize: [what observable tells me this pattern is active?]

### Related
- [entry-name](../growth-log/YYYY-MM-DD.md) (relative Markdown links)
```

## Entry Types

All four types use the template above. The type determines which sections carry the most weight:

| Type | When to Use | Emphasis | Example Title |
|------|------------|----------|---------------|
| **Failure** | Something broke, needed debugging, or required rework | Root Cause | "Config inheritance ≠ behavior inheritance across sessions" |
| **Methodology** | A repeatable process emerged from the work | Context / Pattern | "PPT → open-book exam study guide: three-layer structure" |
| **Pattern Discovery** | A reusable insight about tools, systems, or thinking | Pattern section | "PR description template: describe the gap, not the feature" |
| **Capability Change** | A measurable skill improvement | Context (before vs after) | "Git: from clone/push to independent PR with 12 commits" |

## File Convention

Store entries in a `growth-log/` directory. Name files as `YYYY-MM-DD.md` (ISO date). Each file can hold multiple entries separated by `---` horizontal rules. One file per day, regardless of how many entries.

Example structure:
```
memory/
  growth-log/
    2026-06-25.md   (3 entries from that day)
    2026-06-26.md   (2 entries: one failure, one methodology)
    2026-06-28.md   (1 entry)
  patterns-index.md  (one-line summaries: "SameSite cookies → explicit SameSite=None;Secure")
```

## Integration with Delivery Gate

The delivery gate (`quality-gate.py`) checks that growth-log files were modified today via filesystem mtime after any code change. This skill teaches *what to write*, not just *that the file was touched*.

```
Code change → delivery gate checks growth-log file mtime →
  if stale (no file modified today): block, ask "what did you learn?"
  if fresh (file touched today): pass (this skill ensures the content is actually useful)
```

The gate provides infrastructure (freshness enforcement); this skill provides methodology (content quality). Having the gate without the methodology leads to empty/timestamp-only entries; having the methodology without the gate leads to forgotten captures.

## Library Structure

For systematic learning capture, organize into 5 libraries:

| Library | Content | Update Trigger |
|---------|---------|---------------|
| `growth-log/` | Methodologies, failures, patterns | After any complex task with debugging/redoing |
| `decisions/log.md` | Choices + options + logic + outcome + review date | After any irreversible decision |
| `ratings-tracker.md` | Quantified abilities (0-5 scale) | When a skill demonstrably improves |
| `output-index.md` | File locations across sessions | After creating any deliverable |
| `tooling_capabilities.md` | Available tools inventory | After adding/removing any tool |

## Quality Checklist

Before finalizing a growth log entry:

- [ ] Does the title name the *pattern*, not the event?
- [ ] Is there a "Next time I will..." sentence?
- [ ] Is the "Signal to recognize" specific enough to trigger the pattern next time? (e.g., "auth breaks after browser upgrade" not "something goes wrong")
- [ ] Did I search existing entries for duplicates before writing? (Bole Principle)
- [ ] Is the root cause distinguished from the symptom?
- [ ] Are related memories cross-linked (relative Markdown links or wikilinks)?
- [ ] Is the entry 4-8 sentences? Shorter = too shallow; longer = narrating events.

## Anti-Patterns

- ❌ "Fixed bug in payment module" (event, not pattern — and too trivial to log)
- ❌ Copying the git commit message verbatim (different purpose: commits describe what changed, growth logs extract why it matters)
- ❌ Writing an entry for every commit or every session (only when a pattern emerges)
- ❌ Skipping the transferable sentence (without it, it's just a diary — this is the non-negotiable core)
- ❌ Duplicating the same pattern under different titles (violates Bole Principle — search before writing)
