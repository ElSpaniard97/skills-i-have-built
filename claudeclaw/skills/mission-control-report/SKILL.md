---
name: mission-control-report
description: Generate a read-only ClaudeClaw operations snapshot covering host status, registered agents, scheduled jobs, recent reports, token usage, and open warnings, from the ClaudeClaw dashboard API or claudeclaw.db. Use when the scheduled mission control report runs or the user asks for a ClaudeClaw status, ops summary, "how is everything running", or what is scheduled. This port does not query Hermes gateway state.
version: 1.1.0
author: ClaudeClaw
---

# Mission Control Report

Use this skill for a ClaudeClaw operations snapshot.

## Procedure

1. Read ClaudeClaw state through the dashboard API (`http://localhost:3142`, pass `token=$DASHBOARD_TOKEN`):
   - `/api/tasks` for scheduled tasks and the mission queue.
   - `/api/tokens` for token usage.
   - `/api/agents` for registered agents.
   - `/api/reports?limit=10` for recent reports.
   If the API is unreachable, fall back to read-only queries on `${CLAUDECLAW_HOME:-$HOME/claudeclaw}/store/claudeclaw.db` and say so in the report.
2. Collect host status with read-only commands: `uptime`, `free -h`, `df -h /`.
3. Compose a markdown report with these sections:
   - System
   - Agents
   - Scheduled Jobs (flag any overdue `next_run` or failed last run)
   - Recent Reports
   - Token Usage
   - Warnings and Open Loops
   - Recommendations (at most three, each tied to a finding above)
4. Return the markdown as the final answer. The scheduler stores it in the ClaudeClaw Reports tab.

## Guardrails

- Do not query Hermes gateway files or APIs.
- Do not post externally.
- Do not take destructive or corrective action unless explicitly approved.
- Never print `DASHBOARD_TOKEN` or any other secret in the report.

## Verification

Every section is present (or marked "unavailable" with the reason), and each warning cites the API field or command output it came from.
