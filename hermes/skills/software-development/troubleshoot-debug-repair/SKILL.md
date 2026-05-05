---
name: troubleshoot-debug-repair
description: Troubleshoot, debug, diagnose, and repair broken ClaudeClaw features, services, dashboards, agents, chat flows, cron jobs, reports, APIs, databases, and local integrations. Use when something is failing, regressed, misconfigured, unavailable, throwing errors, returning empty data, or needs root-cause analysis and a verified fix.
version: 1.0.0
allowed-tools: Bash Read Write
---

# Troubleshoot, Debug, Diagnose, and Repair

## Trigger
Use this skill when the user asks to troubleshoot, debug, diagnose, repair, fix, investigate, triage, restore, or verify a broken ClaudeClaw behavior. Common targets: dashboard tabs, chat, agents, scheduled tasks, reports, skills, database rows, API routes, bot delivery, startup, ports, environment config, and local service health.

## Operating Mode
- Default: diagnose first, then repair only after the failure mode is understood.
- Prefer the smallest fix that restores behavior.
- Keep unrelated files and user data untouched.
- If the request involves destructive actions, credentials, external posting, or service restarts outside ClaudeClaw, ask for approval first.

## Procedure
1. **Capture the symptom**
   - Record the exact user-visible failure, affected surface, timestamp, URL/command if relevant, and expected behavior.
   - If screenshots or logs are provided, inspect them before guessing.
2. **Reproduce or isolate**
   - For UI failures: call the backing API route directly with `curl`.
   - For API failures: inspect route code, config loading, database access, and process logs.
   - For scheduler/report failures: check `scheduled_tasks`, `reports`, cron expression validity, agent IDs, and skill paths.
   - For chat/agent failures: check `/api/agents`, agent registry initialization, `agent.yaml`, agent directories, session rows, and model/provider config.
3. **Collect evidence**
   - Use read-only commands first: `rg`, `sed`, `sqlite3`, `curl`, `ss -ltnp`, `npm test`, `npm run build`.
   - Save key command outputs mentally for the final report; do not dump secrets.
4. **Identify root cause**
   - Name the failing boundary: UI rendering, API route, database schema/data, scheduler logic, config/env, service startup, dependency, or external provider.
   - Distinguish primary cause from incidental findings.
5. **Repair**
   - Patch code with the narrowest change.
   - For data repair, use explicit SQL against the intended database only.
   - For service repair, rebuild first, then restart only the affected ClaudeClaw process.
6. **Verify**
   - Run `npm run build` after TypeScript changes.
   - Run `npm test` unless the change is purely content-only.
   - Re-hit the exact failing endpoint or workflow.
   - For UI fixes, confirm the API returns sane data and the dashboard process is restarted if needed.
7. **Report**
   - State root cause, files changed, verification results, and any residual risk.

## ClaudeClaw Quick Checks

Use these as starting points when relevant:

```bash
curl -s "http://localhost:3142/api/agents?token=$DASHBOARD_TOKEN"
curl -s "http://localhost:3142/api/tasks?token=$DASHBOARD_TOKEN"
curl -s "http://localhost:3142/api/reports?token=$DASHBOARD_TOKEN&limit=5"
sqlite3 store/claudeclaw.db ".schema scheduled_tasks"
sqlite3 store/claudeclaw.db ".schema reports"
sqlite3 store/claudeclaw.db "select id,name,agent_id,status,deliver_mode,next_run from scheduled_tasks order by next_run limit 20;"
ss -ltnp
npm run build
npm test
```

If the dashboard is launched directly with `npm run dashboard`, ensure startup initializes both:
- `initDatabase()`
- `initOrchestrator()`

## Guardrails
- Do not delete, reset, or overwrite database files without explicit approval.
- Do not expose tokens from `.env`, URLs, logs, screenshots, or database rows.
- Do not restart unrelated services.
- Do not run full production cron jobs just to test plumbing when a synthetic report or dry-run can verify the path.
- Do not mark a fix complete until the original failure path has been rechecked.

## Output Format

```markdown
# Troubleshooting Report
- Symptom:
- Scope:
- Root Cause:
- Fix Applied:

## Evidence
- Command/API checks:
- Files inspected:

## Verification
- Build:
- Tests:
- Workflow/API:

## Residual Risk
- None | Items to watch:
```

## Verification Standard
A repair passes only if:
- The original symptom is reproduced or clearly isolated.
- Root cause is specific enough to explain the observed behavior.
- The fix is scoped to the failing boundary.
- Build/tests or equivalent checks pass.
- The user-facing workflow is verified after the fix.
