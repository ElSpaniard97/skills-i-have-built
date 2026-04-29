---
name: mission-control-report
description: Generate a local ClaudeClaw operations summary from ClaudeClaw dashboard state. This port does not query Hermes gateway state.
version: 1.0.0
author: ClaudeClaw
---

# Mission Control Report

Use this skill for a ClaudeClaw operations snapshot.

## Procedure

1. Read ClaudeClaw local state through available APIs or direct database reads:
   - `/api/tasks` for scheduled tasks and mission queue.
   - `/api/tokens` for token usage.
   - `/api/agents` for registered ClaudeClaw agents.
   - `store/claudeclaw.db` for reports, audit log, and hive mind if APIs are unavailable.
2. Include system status using read-only commands such as `uptime`, `free -h`, and `df -h`.
3. Compose a markdown report with these sections:
   - System
   - Agents
   - Scheduled Jobs
   - Recent Reports
   - Token Usage
   - Warnings and Open Loops
   - Recommendations
4. Return the markdown as the final answer. The scheduler stores it in the ClaudeClaw Reports tab.

## Guardrails

- Do not query Hermes gateway files or APIs.
- Do not post externally.
- Do not take destructive or corrective action unless explicitly approved.
