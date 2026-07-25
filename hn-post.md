# Show HN: LLM context compression follows a peak-then-decline curve — here's how to test it

After 70+ sessions with DeepSeek V4 (1M context), I noticed context compression isn't linear degradation. There's a **"回光返照" (brief resurgence)** at compression 2, followed by irreversible decline:

```
Quality: ████╲╱███╲╲╲╲ (peak at compression 2, then monotonic decline)
```

Academic papers (RCC ICLR 2025, ACON ICLR 2026) study single compression events. Nobody has studied what happens across multiple rounds.

I built a [monitoring tool](https://github.com/YuhaoLin2005/compact-counter-concept) + [experiment framework](https://github.com/YuhaoLin2005/compact-counter-concept/blob/master/EXPERIMENT.md) so anyone can test this on their model. The hypothesis is specific enough to be falsified — run 10 benchmark tasks after each compression, plot the curve, see if it holds.

Curious if Claude Opus / GPT-5 / Gemini users see the same pattern. Different models, different compression algorithms — maybe different curves entirely.
