# pip install self-audit: A Zero-Dependency CLI for AI Output Quality

AI agents pass tests while producing sloppy thinking. They say "should work" without evidence. They present partial work as complete. They embellish.

I built a tiny tool that catches this. It takes any text and checks four dimensions: Completeness, Consistency, Groundedness, and Honesty.

```bash
pip install self-audit
echo "Should work fine. Ready to ship." | self-audit --verbose
# Completeness: FIXED
# Groundedness: FIXED  [should work fine]
# FAIL
```

Zero dependencies. Python 3.8+. Stdlib only. 60 lines of core logic.

The four dimensions are grounded in Anthropic's Constitutional AI framework — Completeness (helpfulness), Groundedness (harmlessness), Honesty (truthfulness), Consistency (rule alignment). It's also available as a Claude Code skill for agent-native use.

GitHub: https://github.com/YuhaoLin2005/self-audit
Claude Code skill PR: https://github.com/anthropics/skills/pull/1361
