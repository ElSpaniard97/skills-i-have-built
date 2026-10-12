---
name: llm-cost-optimization
description: "Analyze and reduce LLM API or agent spend: measure where cost goes (by model, source, day, session, cache reads), find the dominant drivers, and apply the highest-impact levers (model routing, cheaper models for scheduled jobs, prompt caching and pruning, batch processing) while watching quality. Use when the user's Claude/OpenAI/agent bill is too high, they ask where their tokens or money are going, want a cost report with recommendations, or are designing a new LLM setup and want it cost-aware from day one."
---

# LLM Cost Optimization

A measure → diagnose → change → monitor loop. In one real agent setup it cut projected spend from about $467/month to about $90/month without quality loss, mainly through model routing.

## Step 1: Measure the baseline (at least 7 days)
Get usage data from whatever the user has: the Anthropic Console usage and cost export, the Usage & Cost Admin API, OpenAI usage exports, a self-hosted agent's token log or database, or Claude Code's `/cost` for a single session. Build:
- Total spend, daily average, and monthly projection (`total / days * 30`).
- By model: input, output, cache-write and cache-read tokens and cost.
- By source: chat, bots, scheduled jobs, API callers.
- By day (to spot spikes) and the top sessions by cost.

Before changing anything, check the current config, because earlier optimizations may already be live.

## Step 2: Find the drivers (ask in order)
1. Is one model more than 70% of spend? → model routing.
2. Are cache reads more than 30% of that model's cost? → prompt pruning.
3. Is scheduled/background work more than 15% of spend? → pin those jobs to cheaper models.
4. Is any single session more than 10% of spend? → session hygiene (shorter sessions, clearing context between tasks).
5. Are there large non-urgent workloads? → the Batches API (about half price) for anything that can wait.

## Step 3: Apply the levers
- **Model routing (usually the biggest win):** default to the mid tier (Sonnet) and reserve the top tier (Opus) for explicit requests or hard reasoning; use the small tier (Haiku) for classification, routing, and short summaries. Look up current per-token prices on the provider's pricing page; never hardcode them.
- **Scheduled jobs:** routine reports and digests rarely need the top tier. Pin each job's model explicitly.
- **Prompt caching and pruning:** cache stable system prompts and tool definitions; then shrink what is cached. Large static inventories (skill lists, tool catalogs, long examples) are re-read every turn. Count tokens with the provider's token-counting endpoint (for Claude, `messages.count_tokens`), not an OpenAI tokenizer, and gate or lazy-load the biggest blocks.
- **Output length:** set sensible `max_tokens` and ask for concise formats where long prose isn't needed.

Roll out one lever at a time, in a low-stakes channel first, and keep the expensive model reachable by explicit request.

## Step 4: Monitor
Wait 24–48 hours before judging impact: the analysis session itself is expensive and the baseline window still contains pre-change traffic. Set up a recurring cost report and watch spend trend, task failure or retry rate, and new spikes. If quality drops, roll back only the change that caused it.

## Recommendations must be quantified
Every recommendation cites a number from the report, for example "Opus is 97% of spend ($60.63); routing casual chat to Sonnet would cut that substantially." Vague advice like "consider optimizing" gets ignored.

## Anti-patterns
- Switching everything to the cheapest model: quality collapses. Use tiers.
- Pruning prompts so hard that tool use breaks: test changes before rollout.
- A one-time audit with no recurring report: costs drift as features and pricing change.
- Hardcoded prices in report code: keep them in a separate pricing file.

## Pitfalls
- Model names differ by provider and gateway (for example `anthropic/...` on OpenRouter); normalize before aggregating.
- Cache token columns are often null in homegrown logs; take them from API response usage fields.
- Config changes to system prompts usually apply only to new sessions.

## Output Format
```markdown
# LLM Cost Report — (window)
- Total: $X · Daily avg: $X · Monthly projection: $X
## By model / By source / By day / Top sessions
## Drivers found
## Recommendations (each with the number that justifies it)
## Changes applied (if any) and how to roll back
```

## Success metrics (30 days after)
Cost reduction %, quality hold rate (tasks succeeding without retry), and escalation rate if cheap-to-expensive fallback was added (under 5% is healthy).
