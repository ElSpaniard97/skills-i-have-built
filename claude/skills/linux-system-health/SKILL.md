---
name: linux-system-health
description: "Run read-only Linux host health checks (uptime and load, memory, disk, failed systemd units, recent errors in the journal, network and DNS, pending updates) and produce a Healthy/Warning/Critical operations report with evidence. Use when the user asks to check on a Linux server or this machine, why a box is slow, whether services are failing or the disk is filling up, or for a daily/weekly host health report. Report-first: never restarts services or installs packages."
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
   - Disk from `df -h -x tmpfs -x devtmpfs -x squashfs` and inodes from `df -i` (flag anything over 85%)
3. **Check service state (read-only):**
   - `systemctl --failed`
   - Identify critical failures only.
4. **Check recent system errors (read-only):**
   - `journalctl -p 3 --since "24 hours ago" --no-pager | tail -200` (adjust to the requested window) and summarize the top recurring errors by unit.
   - If the journal is not readable without sudo, say so in `Verification` rather than skipping silently.
5. **Check network posture (read-only):**
   - `ip -br addr`, `ip route show default`, `getent hosts github.com` (DNS), and one connectivity check such as `curl -sS -o /dev/null -w '%{http_code}' https://github.com`.
6. **Check update posture (read-only):**
   - Pending package updates and security update signal where available: `apt list --upgradable 2>/dev/null` (Debian/Ubuntu), `dnf check-update --security` (Fedora/RHEL), and `[ -f /var/run/reboot-required ] && cat /var/run/reboot-required` for a pending reboot.
7. **Generate report:**
   - Assign status: `Healthy`, `Warning`, or `Critical`.
   - Include evidence snippets and recommended next actions.

## When you can't run commands on the host
If this session has no shell on the machine in question (for example in a claude.ai chat), give the user the exact read-only commands from the procedure as one copy-paste block, ask them to paste the output back, and build the report from that output. Mark anything you could not see as a blind spot.

## Guardrails
- Do **not** restart services.
- Do **not** install or upgrade packages.
- Do **not** edit configs, firewall, or systemd units.
- Do **not** run destructive cleanup commands.
- If remediation is needed, propose exact commands and wait for user approval.

## Output Format

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
- Pair with `security-triage` when status is `Warning` or `Critical`.
