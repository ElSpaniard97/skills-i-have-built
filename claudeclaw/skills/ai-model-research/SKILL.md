---
name: ai-model-research
description: Produce a source-backed AI model research briefing (new model releases, benchmarks, papers, pricing and availability changes, community reaction) from the last N days of vendor posts, papers, model cards, Hacker News/Reddit signal, and selected video transcripts. Use when the user asks for an AI news roundup, weekly model briefing, "what's new in AI/LLMs", what changed with a specific model, or when the scheduled AI research report runs. Output is a local markdown report for the ClaudeClaw Reports tab.
version: 1.1.0
author: ClaudeClaw
---

# AI Model Research

Use this skill for weekly or ad hoc AI model briefings. Keep all output local to ClaudeClaw unless the user explicitly requests another destination.

## Inputs
- Lookback window: default 7 days (`--lookback-days`). Use 1 for a daily brief.
- Focus (optional): a vendor, model family, or topic to weight more heavily.

## Procedure

`SKILL_DIR` is this skill's folder (default `${CLAUDECLAW_HOME:-$HOME/claudeclaw}/skills/ai-model-research`).

1. Fetch candidates:
   `python3 "$SKILL_DIR/scripts/fetch_sources.py" --lookback-days 7 > /tmp/claudeclaw-ai-candidates.json`
   Fetch failures for individual feeds are logged to stderr and are not fatal; note them under Gaps.
2. Drop items already reported in earlier runs:
   `python3 "$SKILL_DIR/scripts/dedupe.py" < /tmp/claudeclaw-ai-candidates.json > /tmp/claudeclaw-ai-new-items.json`
   Seen-state lives in `~/.claudeclaw/state/ai-research-seen.json` (override with `AI_RESEARCH_STATE`). It is separate from the Hermes copy of this skill, so the two systems do not hide items from each other.
3. Rank new items by significance: model release > major benchmark/eval > research paper > operationally useful tooling > commentary.
4. Read the primary source for each top item (vendor post, model card, paper abstract). Extract capabilities, benchmark numbers, pricing, availability (API, open weights, regions), and caveats. Never report a number you did not see in a source.
5. For high-signal videos, use available transcript tooling and summarize in 2-3 sentences each. Skip this section if no transcript tooling works.
6. Cross-check the highest-impact items with community signal (Hacker News Algolia, Reddit) and note real disagreement or reported problems.
7. Fill the structure in `templates/report.md`. Every claim gets a link to its source.
8. Return the final markdown report as the final answer.

## Guardrails
- Do not post or deliver the report anywhere outside ClaudeClaw unless the user asks.
- Separate vendor claims from independent results; label vendor-reported benchmarks as such.
- If fewer than three new items survive dedupe, say it was a quiet period rather than padding with old or low-signal items.

## Verification
A run passes only if every item has a working source link, the dedupe step ran (or its failure is noted), and the report lists any feeds that failed to fetch.

## Output

A local markdown briefing following `templates/report.md`, plus a short "Gaps" line naming failed feeds or skipped sections.
