---
name: hermes-cost-report
description: Generate a markdown report of Hermes session costs from ~/.hermes/state.db. Computes per-token cost from a configurable pricing JSON. Use when the user asks for a cost report, usage summary, or spend analysis.
version: 1.0.0
author: Hermes Agent
license: MIT
---

# Hermes Cost Report

This skill generates a markdown cost report from the Hermes SQLite state database at `~/.hermes/state.db`. It reads session token usage, computes local estimated costs from per-token pricing, and summarizes spend by model, source, day, and highest-cost sessions.

Invoke it with:

```bash
python3 ~/.hermes/skills/reporting/hermes-cost-report/scripts/cost_report.py --since-days N
```

`N=0` means all-time. The default is `--since-days 2`.

The report is written as markdown to stdout.

Pricing is loaded from `scripts/pricing.json` by default. Override it with:

```bash
python3 ~/.hermes/skills/reporting/hermes-cost-report/scripts/cost_report.py --pricing /path/to/pricing.json
```

The report includes these sections:

- Header with reporting period and total estimated cost
- By Model
- By Source
- By Day
- Top 5 sessions by cost
- Brief Notes and analysis context
- Recommendations — data-driven optimization tips with monthly projection and quick actions.

Pitfall: the Hermes DB cost columns are currently `NULL`; this script computes costs locally from token counts and pricing. It does not rely on `estimated_cost_usd` or `actual_cost_usd`.

To update prices, edit `scripts/pricing.json`. Prices are stored as USD per 1M tokens.
