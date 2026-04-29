---
name: linux-system-health
description: Monitor Linux host health and produce a daily operations report with failed services, disk, memory, network, and update posture. Report-first, no service changes.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [linux, observability, host-health, operations, diagnostics]
---

# Linux System Health

## Trigger
Use this skill when the user asks to check Linux host health, diagnose machine status, generate a daily/weekly host report, or validate uptime/service/disk/memory/network/update posture.

## Required Inputs
- Scope: local machine (default) or explicit target host.
- Output destination: chat reply, markdown file, or scheduled report target.
- Time window for log checks (default: last 24h).

## Procedure
1. **Collect baseline host facts (read-only):**
   - `date`, `uptime`, kernel/OS summary.
2. **Check resource pressure (read-only):**
   - CPU load from `uptime`
   - Memory from `free -h`
   - Disk from `df -h`
3. **Check service state (read-only):**
   - `systemctl --failed`
   - Identify critical failures only.
4. **Check recent system errors (read-only):**
   - `journalctl -p 3 -xb` (or last 24h equivalent) and summarize top recurring errors.
5. **Check network posture (read-only):**
   - `ip addr`, default route, DNS resolution check, and one basic connectivity check.
6. **Check update posture (read-only):**
   - Pending package updates and security update signal where available.
7. **Generate report:**
   - Assign status: `Healthy`, `Warning`, or `Critical`.
   - Include evidence snippets and recommended next actions.

## Guardrails
- Do **not** restart services.
- Do **not** install or upgrade packages.
- Do **not** edit configs, firewall, or systemd units.
- Do **not** run destructive cleanup commands.
- If remediation is needed, propose exact commands and wait for user approval.

## Output Format
Return markdown with this exact structure:

```markdown
# Linux System Health Report
- Host:
- Timestamp:
- Window:
- Overall Status: Healthy | Warning | Critical

## 1) Availability
- Uptime:
- Load:

## 2) Resources
- Memory:
- Disk:
- Capacity Risks:

## 3) Services
- Failed Units:
- Critical Impact:

## 4) Logs & Errors
- Top Errors:
- Frequency/Recency:

## 5) Network
- Interface/Route Summary:
- Connectivity/DNS:

## 6) Updates
- Pending Updates:
- Security Posture:

## 7) Recommended Next Steps
1.
2.
3.

## Verification
- Commands executed:
- Evidence captured:
- Confidence:
```

## Verification
A run passes only if:
- All six sections (Availability, Resources, Services, Logs, Network, Updates) are present.
- At least one command-backed evidence line exists per section.
- Overall status is justified by concrete findings.
- No state-changing command was executed.

## Sample Prompt
"Run Linux System Health for this machine for the last 24h and return the standard markdown report. Report-only mode."

## Notes
- Prefer concise, evidence-based summaries over raw logs.
- If command permissions are limited, explicitly note gaps in `Verification`.
