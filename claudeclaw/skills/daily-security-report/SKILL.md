---
name: daily-security-report
description: Run local defensive checks and return a markdown security report for ClaudeClaw Reports. No external delivery.
version: 1.0.0
author: ClaudeClaw
---

# Daily Security Report

Use this skill for local, defensive security reporting.

## Procedure

1. Run `bash /home/zeke/claudeclaw/skills/daily-security-report/scripts/run_all.sh`.
2. Read `/home/zeke/claudeclaw/store/security-reports/latest.md`.
3. Return the full markdown report as the final answer.

## Guardrails

- Report-only mode.
- Do not modify firewall, packages, users, processes, or repositories without explicit approval.
- Do not post externally.
