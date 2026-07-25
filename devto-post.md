# Has Anyone Measured How LLM Output Quality Degrades Across Multiple Compactions?

I have a question that I haven't been able to answer on my own. Hoping someone here has more resources or ideas.

## The Observation

After ~70 sessions with DeepSeek V4 (1M context), I noticed something odd. When Claude Code compacts my session, output quality doesn't just go down linearly. There's a moment — usually after the second compaction — where the model briefly gets *better*. Then it declines and never recovers.

Maybe I'm imagining it. Maybe it's specific to my model, my prompts, my workflow. But I can't shake the thought: **what if context compaction has a curve, and nobody has mapped it?**

## What I Found (Not Much)

I searched for benchmarks that measure multi-round compaction degradation. Here's what exists:

- **RULER**: Measures how performance drops as *static* input grows longer. Nothing about what happens after you compress and re-compress.
- **Context Rot** (Chroma 2025): 18 models tested, all degrade with more tokens. Again, static.
- **Multi-turn evaluation**: Tests whether models drift across conversation turns. Doesn't touch compaction.

Parameter compression (pruning, quantization) has well-mapped scaling laws. The Lottery Ticket Hypothesis (ICLR 2019) and Compression Laws for LLMs (2025) tell you exactly where the performance peak sits. Context summarization — the thing that happens every time your agent runs `/compact` — has no such curve.

## Why This Might Matter

If the curve is real, you could:
- Know exactly when to start a fresh session (before the decline hits)
- Compare models on a new dimension: who maintains quality longest across compactions?
- Give LLM providers a concrete target: "your compaction quality drops 20% faster than competitor X"

Right now, none of the major benchmark suites (MMLU, HELM, BigBench, RULER) include a "compaction persistence" metric. If context windows keep growing and sessions keep getting longer, this gap gets bigger every year.

## What I'm Asking

I built a tiny monitor ([compact-counter](https://github.com/YuhaoLin2005/compact-counter-concept)) and a rough [experiment framework](https://github.com/YuhaoLin2005/compact-counter-concept/blob/master/EXPERIMENT.md) — 50 lines of Python, 10 benchmark tasks, 0-5 rubric. It's not polished. It's a starting point.

What I'd love:
1. Someone with a Claude Opus / GPT-5 / Gemini account to try reproducing this
2. Feedback on whether the methodology makes sense or is fundamentally flawed
3. If this is a real thing, ideas for how to measure it properly

I don't have the compute or the stats background to do this alone. But if enough people contribute data points across different models, we might find out whether this curve exists — and if it does, maybe it's useful to more people than just me.

## References

- Frankle & Carbin, "The Lottery Ticket Hypothesis" (ICLR 2019)
- "Compression Laws for Large Language Models" (2025)
- RULER: What's the Real Context Size of Your Long-Context Language Models? (COLM 2024)
- Chroma Research, "Context Rot" (2025)
