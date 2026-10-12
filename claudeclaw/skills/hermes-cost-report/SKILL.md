---
name: hermes-cost-report
description: Generate a local ClaudeClaw token and cost report from the token_usage table in claudeclaw.db, broken down by model and agent. Use when the scheduled cost report runs or the user asks how much ClaudeClaw has spent, token usage for the last few days, or which agent/model is costing the most. Despite the historical name, this version reads ClaudeClaw state, not Hermes state.
version: 1.1.0
author: ClaudeClaw
---

# ClaudeClaw Cost Report

Use this skill for recurring or ad hoc local cost reports. The name is kept for compatibility with existing scheduled tasks.

## Procedure

1. Run `python3 "${CLAUDECLAW_HOME:-$HOME/claudeclaw}/skills/hermes-cost-report/scripts/cost_report.py" --since-days 2`.
   - Change `--since-days` if the user asks for a different window (for example 7 for a weekly view).
2. Return the script stdout verbatim as the final answer. Do not round, re-total, or re-price the numbers.
3. Do not post externally. The scheduler stores the final answer in the Reports tab.

## Notes

- Default database: `${CLAUDECLAW_HOME:-$HOME/claudeclaw}/store/claudeclaw.db`. Override with `--db` or `CLAUDECLAW_DB`.
- If the script errors (missing database, missing table), return the error and the database path it tried instead of an empty report.
