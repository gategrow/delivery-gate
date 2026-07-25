# I Let 24 Famous Engineers Review My Methodology. Here's What Happened.

I spent tonight building a methodology for turning personal tools into open source contributions. Before publishing it, I decided to let the methodology review itself.

The results changed how I think about AI-assisted code review.

## The Method: Named-Persona Adversarial Review

The core idea is simple: instead of asking an AI to "review this code as a security engineer" (which produces generic, shallow feedback), you **web-search actual engineers' documented philosophies** and role-play as them.

Not "be a security auditor." Be **Linus Torvalds**, who said good code is when the special case disappears. Be **Ken Thompson**, who said each program should do one thing well. Be **Richard Feynman**, who said the easiest person to fool is yourself.

Two engineers + one product person per round. Three rounds minimum. Nine genuinely different perspectives.

## The Experiment

I applied this to my own [open-source-flywheel](https://github.com/YuhaoLin2005/open-source-flywheel) methodology. Eight rounds. Twenty-four persona views.

**Round 1: Torvalds immediately found a flaw.** "Your 'When NOT to Use' table repeats the same rules as your Pre-Flight checklist. Merge them. A good data structure eliminates the special case." He was right. Gone.

**Round 2: Feynman asked the hardest question.** "You only show successes. Where are the failures?" The methodology had three ✅ cases and one ❌. Without documented failures, it was unfalsifiable — the worst kind of cargo cult science. I added three failure cases.

**Round 3: Kahneman called out overconfidence.** "Self-assessment of originality is inherently biased. Ask someone else to answer your Pre-Flight questions." Added immediately.

**Rounds 4-5: Carmack wanted time estimates.** "What does this cost?" Musk wanted first-principles decomposition. Beck wanted respect for maintainers. All actionable, all added.

**Round 6: Bret Victor, Don Norman, and Eric Ries independently flagged the same thing.** The methodology had no feedback loop. Extract → Find → Harden → Launch → ... nothing. Three legends of design and lean startup, across different decades, pointing at the exact same gap. When Normans, Ries, and Victor agree, you listen. I added a fifth step: LEARN.

**Rounds 7-8: Brooks confirmed we're not selling a silver bullet.** "Essential complexity can't be eliminated, only managed." Knuth confirmed the structure was right. Ritchie and Berners-Lee confirmed it was simple enough.

## What Changed

Between v1 and v8, the methodology went from 8.3KB to 4KB while gaining:
- A fifth step (LEARN — the feedback loop)
- Pre-flight bias protection (ask someone else)
- Bot-check (verify target repo has automated review)
- Time estimates per step
- Three documented failure cases
- 24-persona review badge (yes, the methodology wears its own review count)

## Why This Matters

Single-modal LLMs have a fundamental problem: when they review their own output, they share the same mental model, the same blind spots, the same tendency to say "looks good."

Named-persona review compensates for this. By grounding each review perspective in **real, searchable, citable philosophy**, you force the model to switch contexts in ways that abstract roles can't. Ken Thompson actually said "do one thing well." You can look it up. That constraint produces different findings than "review this as a senior architect."

## The Meta-Lesson

A methodology that can review itself is more trustworthy than one that can't. My methodology found 8 bugs in itself before I published it. Yours should too.

If you maintain an open source project and want to try this on your own work: the [named-persona-adversarial-review](https://github.com/alirezarezvani/claude-skills/pull/866) skill is available as a PR to claude-skills. Or just search for your favorite engineer's philosophy and role-play. The method is free.

---

*24 personas, 8 rounds, 5 steps. Thanks to de Bono for the theoretical foundation, alirezarezvani for the adversarial-reviewer format, and Feynman for reminding me I'm the easiest person to fool.*
