---
name: hermes-cost-report
description: Generate a local ClaudeClaw cost report from claudeclaw.db token_usage records. Despite the historical name, this version reads ClaudeClaw state, not Hermes state.
version: 1.0.0
author: ClaudeClaw
---

# ClaudeClaw Cost Report

Use this skill for recurring local cost reports.

## Procedure

1. Run `python3 /home/zeke/claudeclaw/skills/hermes-cost-report/scripts/cost_report.py --since-days 2`.
2. Return the script stdout verbatim as the final answer.
3. Do not post externally. The scheduler stores the final answer in the Reports tab.

## Notes

- Default database: `/home/zeke/claudeclaw/store/claudeclaw.db`.
- Override with `--db` or `CLAUDECLAW_DB`.
