# Dual-Pool Adversarial Review: A Methodology for AI Code Review

## Problem

AI code review tools use abstract roles (Saboteur, Security Auditor, New Hire). These produce generic feedback: "consider adding error handling," "this could be more readable." The findings are directionally correct but lack specificity — they don't tell you WHAT to change or WHY.

Real code review by real engineers works differently. Linus Torvalds doesn't say "be more defensive." He says "eliminate the special case entirely" — and that produces a specific, actionable change. The difference between abstract and specific review is the difference between advice you nod at and advice that changes your code.

**The gap:** AI code review lacks the specificity that comes from documented, searchable engineering principles applied by named experts with distinct viewpoints.

## Architecture

The dual-pool system organizes reviewers into two pools that are cross-orchestrated across rounds:

**Fixed Pool (Convergence):** Curated personas matched to the user's expertise, personality, and goals. Stable, deep, and familiar with the author's context. Managed by Patty McCord (Netflix's Chief Talent Officer) and Ed Catmull (Pixar's Braintrust) — managers who recruit teams per task rather than using fixed templates.

**Random Pool (Divergence):** Fresh personas discovered via web search each session. No preset list — the manager defines search keywords based on what the task needs. This pool catches blind spots that the fixed pool, familiar with the author, systematically misses.

**Cross-Orchestration:** Each round draws a new manager, who recruits workers from either pool. At most 2 workers carry over from the previous round. This balances continuity with fresh perspectives.

### Round Structure

1. Manager analyzes task → decides depth and required roles
2. Manager recruits 2 engineers + 1 product/designer
3. Each worker web-searches their own principles FIRST, extracts 3-5 verbatim quotes
4. Workers review through ONLY pre-extracted quotes — no retrofitting
5. Cross-persona deduplication with severity promotion
6. Output: structured report with cited findings, concurrences, and verdict

### Triage

| Task scope | Rounds | Cost |
|-----------|--------|------|
| Single-file, no user-facing impact | 1 round | ~3 web searches |
| Multi-file, architectural change | 2 rounds | ~6 web searches |
| Security-critical or identity-related | 3+ rounds | ~9+ web searches |

## Core Rules

### Quote-First Review

The critical innovation: quotes are extracted BEFORE reviewing, not searched to support pre-formed opinions. This prevents confirmation bias — the tendency to find quotes that support an opinion you already formed.

Each worker searches `"[Name] [topic] principles"`, extracts 3-5 verbatim quotes, then reviews the code through ONLY those quotes. Findings that don't map to a pre-extracted quote are rejected.

### Symmetric Burden

Both findings and non-findings carry equal verification cost:

- **Finding:** Must cite 1+ specific, searchable quote from the named person
- **Zero findings:** Must cite 3+ quotes the code successfully satisfies, with explanation of HOW

This prevents both fake findings (expensive to fabricate) and lazy "everything looks fine" (also expensive). The symmetry forces genuine engagement regardless of outcome.

### Severity Promotion

| Level | Definition | Action |
|-------|-----------|--------|
| BLOCKER | 2+ concurrences on CRITICAL, or security/data-loss | Fix before any further work |
| CRITICAL | Wrong result, data loss, security hole | Fix before merge |
| WARNING | Fragile, misleading, likely future bugs | Should fix; explain if deferred |
| NOTE | Improvement, doesn't affect correctness | Optional; record for follow-up |

2+ personas independently finding the same issue promotes it one level. This is the concurrence multiplier — cross-validation that turns individual observations into consensus findings.

### Integrity Check

After each round: "Would this person actually say this, or am I projecting?" If a finding can't be traced to a specific, verbatim quote from that person's documented principles, it's likely invented.

## Validation: The System Reviews Itself

The strongest test of any review system is whether it can find issues in its own design.

After community feedback identified a flaw (mandatory findings forcing invented issues), the skill was updated and run through its own adversarial review. An independent code-reviewer subagent found **16 issues** in the skill file itself:

| Severity | Count | Examples |
|----------|-------|---------|
| Critical | 1 | Skill referenced non-existent parent file — structurally broken |
| High | 6 | "Credible-only findings" was a loophole; quote gate incentivized retrofitting; contradictory rules; "Intercom PM" not a named person |
| Medium | 5 | Persona count inconsistency, static summaries undermining real-time search, product pool exhaustion |
| Low | 4 | Search query variance, Step 0 entrenching mental model |

All 16 issues were fixed. **The system reviewing itself and finding structural flaws in its own design is the strongest validation possible.**

## Comparison with Existing Approaches

| | Standard Code Review | Abstract-Role Adversarial | This System |
|---|---|---|---|
| Reviewer identity | Generic "reviewer" | Abstract role (Saboteur, etc.) | Named engineer with cited principles |
| Specificity | Depends on reviewer | Low — generic advice | High — specific, quotable, attributable |
| Blind spot coverage | Single perspective | Multiple abstract perspectives | Fixed + random pools with cross-orchestration |
| Evolution | None | None | Personas promoted/demoted/audited per session |
| Self-validation | None | None | System reviews itself |

## Risk Analysis

**Cost:** Each round requires 3 web searches (one per persona). For a 3-round review, that's ~9 searches plus the token cost of the review itself. This is inappropriate for trivial changes.

**Mitigation:** The triage system ensures small changes get 1 round, large changes get 2-3. The user should not use this for single-line typo fixes.

**False negatives:** Even with symmetric burden, a reviewer might still miss issues. Mitigation: cross-persona concurrence promotion and random pool diversity.

**False positives:** The quote-first rule and integrity check eliminate most fake findings. Remaining risk: a real quote applied to the wrong context. Mitigation: independent concurrence requirement for severity promotion.

## Reproducibility

1. Install the skill: `skills/named-persona-adversarial-review/SKILL.md`
2. Invoke: `/adversarial-review --personas named --rounds N`
3. The manager handles pool selection, recruitment, and cross-round continuity
4. Output is a structured report with cited findings, concurrences, and verdict

The methodology is MIT-licensed and available at [github.com/YuhaoLin2005/dual-pool-review](https://github.com/YuhaoLin2005/dual-pool-review).

## References

- De Bono, "Six Thinking Hats" — parallel thinking with distinct perspectives
- Kahneman, "Thinking Fast and Slow" — System 2 forcing through structured review
- McCord, "How Netflix Reinvented HR" — manager-as-recruiter model
- Catmull, "Creativity, Inc." — Braintrust model for creative review
- Torvalds, various LKML posts — "good taste" as elimination of special cases
- Feynman, "Cargo Cult Science" — "you are the easiest person to fool"
