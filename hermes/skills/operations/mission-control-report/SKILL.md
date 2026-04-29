---
name: mission-control-report
description: Generate a structured JSON + Markdown operations summary covering system status, active projects, agent runs, warnings, and open loops. Feeds the Mission Control GUI dashboard and Discord/Telegram delivery targets.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [operations, dashboard, reporting, status, mission-control]
    category: operations
    related_skills: [linux-system-health, daily-security-report, obsidian-memory-curator]
---

# Mission Control Report

## Trigger
Use this skill when the user asks for a mission-control summary, operations brief, dashboard snapshot, agent activity report, or status of active projects and scheduled jobs.

## Required Inputs
- Report scope: `full` (all sections) or named subset (`system`, `agents`, `projects`, `jobs`).
- Time window: default last 24h for events; default current state for status.
- Output target: chat reply, local file (`~/.hermes/reports/`), Discord, or Telegram.

## Procedure
1. **Collect system status (read-only)**
   - Host health summary: uptime, load, disk, memory pressure (call `linux-system-health` in summary mode if available, else run `uptime && free -h && df -h` directly).
   - Gateway state: read `~/.hermes/gateway_state.json`.
2. **Collect agent activity (read-only)**
   - Query Mission Control API (`GET /api/agents`) for registered agents and their statuses.
   - Query `GET /api/tasks?status=in_progress` for active task count.
3. **Collect scheduled job state (read-only)**
   - Read `~/.hermes/cron/jobs.json` for upcoming job schedule and last-run status.
4. **Collect project summary (read-only)**
   - List active project directories or Mission Control projects with open tasks.
5. **Collect warnings and open loops (read-only)**
   - Any `Warning` or `Critical` flag from system, failed cron runs, or stuck tasks.
6. **Build report**
   - Compose Markdown report using the output format below.
   - Compose companion JSON payload using the same data.
7. **Deliver**
   - Return in chat if interactive.
   - Optionally write to `~/.hermes/reports/mission-control-YYYY-MM-DD.md` and `.json`.
   - Optionally post Markdown summary to Discord `#setup → mission-control` thread (ID: `1497643238767460382`) via `discord/mission-control-report` script.

## Guardrails
- Do **not** restart services, kill processes, or modify tasks without approval.
- Do **not** expose raw secrets or tokens in the report.
- Do **not** claim agents are online/offline unless API or state-file evidence was collected.
- If the Mission Control API is unreachable, note the gap and continue with available data.

## Output Format

### Markdown

```markdown
# Mission Control Report
- Timestamp:
- Window:
- Scope:
- Overall Status: Healthy | Warning | Critical

## 1) System
- Host Status:
- Load / Memory / Disk:
- Gateway:

## 2) Agents
- Registered:
- Online:
- Offline / Unknown:

## 3) Active Tasks
- In Progress:
- Blocked:
- Overdue:

## 4) Scheduled Jobs
- Next Run:
- Last Run Status:
- Failed Jobs:

## 5) Active Projects
- Project:
- Open Tasks:
- Last Activity:

## 6) Warnings & Open Loops
- [Severity] Description — Recommended action

## 7) Recommendations
1.
2.
3.

## Verification
- Data sources:
- API reachable:
- Gaps/blind spots:
```

### JSON payload (companion)

```json
{
  "timestamp": "",
  "window": "",
  "overall_status": "Healthy | Warning | Critical",
  "system": { "status": "", "load": "", "memory": "", "disk": "", "gateway": "" },
  "agents": { "registered": 0, "online": 0, "offline": 0 },
  "tasks": { "in_progress": 0, "blocked": 0, "overdue": 0 },
  "jobs": { "next_run": "", "last_run_status": "", "failed": [] },
  "projects": [],
  "warnings": [],
  "recommendations": []
}
```

## Verification
A run passes only if:
- All seven sections are present (or explicitly marked unavailable with reason).
- At least one evidence source per section is cited.
- Overall status is justified by at least one concrete finding.
- JSON payload is valid and mirrors the Markdown data.
- No destructive action was taken.

## Sample Prompt
"Generate a full Mission Control Report for the last 24h. Include system status, agents, active tasks, scheduled jobs, and open loops. Output Markdown and JSON."

## Notes
- The Discord `discord/mission-control-report` script is a complementary delivery mechanism; this skill defines the data model and procedure.
- The JSON payload is designed to feed the future Mission Control GUI dashboard.
- When running as a cron job, write output to `~/.hermes/reports/` and deliver to Discord.
