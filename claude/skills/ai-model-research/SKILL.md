---
name: ai-model-research
description: "Produce a source-backed AI model research briefing (new model releases, benchmarks, papers, pricing and availability changes, community reaction) covering the last N days. Use when the user asks for an AI news roundup, a weekly model briefing, \"what's new in AI/LLMs\", what changed with a specific model or vendor, or how a new model compares to others. Every claim links to a primary source; vendor claims are labeled as such."
---

# AI Model Research

## Inputs
- Lookback window: default 7 days. Use 1 day for a daily brief.
- Focus (optional): a vendor, model family, or topic to weight more heavily.

## Procedure
1. **Gather candidates** with web search and fetch, limited to the lookback window. Check, at minimum: vendor blogs and changelogs (Anthropic, OpenAI, Google DeepMind, Meta AI, Mistral, xAI, DeepSeek, Qwen), Hugging Face trending models and papers, arXiv cs.CL/cs.LG highlights, LMArena and other public leaderboards, and Hacker News front-page AI threads.
2. **Deduplicate**: merge items that point at the same release or paper; prefer the primary source URL over coverage of it.
3. **Rank by significance**: model release > major benchmark/eval > research paper > operationally useful tooling > commentary.
4. **Read the primary source** for each top item (vendor post, model card, paper abstract). Extract capabilities, benchmark numbers, pricing, availability (API, open weights, regions), and caveats. Never report a number you did not see in a source.
5. **Cross-check** the highest-impact items against community signal (Hacker News, Reddit r/LocalLLaMA and r/MachineLearning) and note real disagreement or reported problems.
6. **Write the report** in the format below.

## Guardrails
- Separate vendor-reported results from independent evaluations, and label which is which.
- If fewer than three meaningful items fall in the window, say it was a quiet period rather than padding with older or low-signal items.
- Do not present rumors or leaks as releases; put them under "What to Watch" with the source.

## Output Format
```markdown
# AI Model Briefing — <date range>

## Major Releases
- **<Model> (<vendor>)** — what it is, key numbers, price/availability. [source]

## Benchmarks & Evals
## Notable Research
## Community Signal
## Worth Watching (videos/talks, optional)
## What to Watch Next

## Gaps
- Sources that could not be reached or sections skipped.
```

## Verification
A briefing passes only if every item has a working source link, every number traces to a source, and the Gaps section is present.
