# Single-Modal LLMs Have a Blind Spot. Here's How to Fix It.

If you use Claude Code, Cursor, or any AI coding agent, you know the problem: you ask the AI to review its own work, and it says "looks good." Every time.

The AI isn't being lazy. It's sharing the same mental model that produced the code. It literally can't see what's wrong — the blind spots are baked in.

## Why "Review this as a senior engineer" Fails

Generic role-playing produces generic findings. The AI fills in what it *thinks* a senior engineer would say, which is usually:
- "Consider adding error handling"
- "Maybe add more comments"
- "The variable name could be clearer"

Useful? Sometimes. But it misses the real bugs — the ones a human reviewer with a genuinely different perspective would catch.

## What Actually Works: Named-Persona Review

Here's the method. It takes 5 minutes and costs nothing.

**Step 1: Pick three named people, not generic roles.**

| Instead of | Use |
|-----------|-----|
| "Review as a security engineer" | "Review as **Linus Torvalds**" |
| "Check for maintainability" | "Check as **Ken Thompson**" |
| "Think about the user" | "Think as **Steve Jobs**" |

Why? Because Linus Torvalds has an actual documented philosophy: "Good taste is when the special case disappears. Eliminate the edge case by changing the data structure." That produces *different findings* than "check for security."

**Step 2: Search for their real philosophy before role-playing.**

```
Search: "Linus Torvalds engineering philosophy code review"
Search: "Ken Thompson Unix philosophy simplicity"
Search: "Steve Jobs product design principles"
```

Take 60 seconds per person. Extract 3-5 actual criteria from their documented words. Now role-play.

**Step 3: Each person MUST find at least one issue.**

No exceptions. If Ken Thompson finds nothing wrong with your code, you're not thinking like Ken Thompson. Go back and look harder.

**Step 4: Run the Feynman check.**

After the review, ask: "Would Richard Feynman actually say what I just said, or am I projecting?" Feynman's actual rule: "The first principle is that you must not fool yourself, and you are the easiest person to fool."

## Recommended Starter Pack

For your first try, use these three:

1. **Linus Torvalds** — Data structures, logic, correctness. Search for "good taste."
2. **Ken Thompson** — Architecture, API design, simplicity. Search for "do one thing well."
3. **Steve Jobs** — User experience, first impressions, clarity. Search for "design is how it works."

Two engineers + one product person. Five minutes. You'll find bugs you'd never catch reviewing as yourself.

## Why This Works (The Science)

de Bono's *Six Thinking Hats* (1985) established that parallel multi-perspective thinking produces better decisions than single-perspective analysis. Kahneman's *Thinking, Fast and Slow* (2011) showed that forcing System 2 (analytical) thinking overcomes the biases of System 1 (intuitive).

Named-persona review is a **System 2 forcing function.** By grounding each perspective in real, searchable philosophy, it prevents the AI from defaulting to generic "looks good" mode.

This is especially valuable for **single-modal LLMs** — models that can only process text. They lack the diverse sensory input that helps humans notice different things. Multi-perspective review compensates for that gap.

## Try It Now

Take any PR, code review, or document you're working on. Paste this prompt:

```
Review the following using Named-Persona Adversarial Review:

PERSONA 1: Ken Thompson (Unix philosophy)
- Search: "Ken Thompson Unix philosophy do one thing well"
- Find: 3-5 criteria from his actual words
- Review the code. MUST find ≥1 issue.

PERSONA 2: Linus Torvalds (Linux/git)
- Search: "Linus Torvalds good taste code review"
- Find: 3-5 criteria from his actual words
- Review the code. MUST find ≥1 issue.

PERSONA 3: Steve Jobs (Apple)
- Search: "Steve Jobs simplicity design principles"
- Find: 3-5 criteria from his actual words
- Review the code from a user's perspective. MUST find ≥1 issue.

OUTPUT: Structured report with CRITICAL/WARNING/NOTE findings.
PROMOTION: Issues caught by 2+ personas get severity upgrade.
HONESTY CHECK: Would these people actually say this?

<your code here>
```

That's it. You just ran a multi-perspective review. No API keys, no agents, no cost. Just better quality.

## Go Deeper

- [Named-Persona Adversarial Review](https://github.com/alirezarezvani/claude-skills/pull/866) — Full skill for Claude Code
- [open-source-flywheel](https://github.com/YuhaoLin2005/open-source-flywheel) — Methodology for turning personal tools into battle-tested contributions (itself reviewed by 24 named personas)
- de Bono, *Six Thinking Hats* (1985)
- Kahneman, *Thinking, Fast and Slow* (2011)
