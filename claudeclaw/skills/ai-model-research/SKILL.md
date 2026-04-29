---
name: ai-model-research
description: Produce a source-backed AI model research briefing from recent vendor posts, papers, model cards, community signals, and selected video transcripts. Output is saved locally through the ClaudeClaw Reports tab.
version: 1.0.0
author: ClaudeClaw
---

# AI Model Research

Use this skill for weekly or ad hoc AI model briefings. Keep all output local to ClaudeClaw unless the user explicitly requests another destination.

## Procedure

1. Run `python3 /home/zeke/claudeclaw/skills/ai-model-research/scripts/fetch_sources.py --lookback-days 7 > /tmp/claudeclaw-ai-candidates.json`.
2. Run `python3 /home/zeke/claudeclaw/skills/ai-model-research/scripts/dedupe.py < /tmp/claudeclaw-ai-candidates.json > /tmp/claudeclaw-ai-new-items.json`.
3. Rank new items by significance: model release, major benchmark, research paper, operationally useful tooling, then commentary.
4. Read primary sources for the top items and extract capabilities, benchmarks, pricing, availability, and caveats.
5. For high-signal videos, use available transcript tooling and summarize in 2-3 sentences each.
6. Cross-check the highest-impact items with community signal such as Hacker News Algolia.
7. Fill the report structure in `templates/report.md`.
8. Return the final markdown report as the final answer. Do not include external delivery instructions.

## Output

Return a local markdown briefing suitable for the ClaudeClaw Reports tab.
