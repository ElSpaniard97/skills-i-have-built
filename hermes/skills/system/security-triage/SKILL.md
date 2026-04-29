---
name: security-triage
description: Defensive security triage for the Linux host and project repos. Inspects logs, open ports, firewall state, failed logins, and package posture. Produces a weekly severity-ranked report with evidence and remediation checklists. Defensive use only — no offensive guidance.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [security, linux, defensive, triage, firewall, logs, hardening]
    category: security
    related_skills: [linux-system-health, daily-security-report, github-repo-review]
---

# Security Triage

## Trigger
Use this skill when the user asks for a security posture check, security audit, firewall review, failed login analysis, open port scan, or weekly security report for the Linux host or project repositories. Also use when `linux-system-health` surfaces a `Critical` or `Warning` security signal.

## Required Inputs
- Scope: `host` (Linux system), `repos` (GitHub/local), or `full` (both).
- Time window for log analysis: default last 7 days.
- Output target: chat reply, local file (`~/.hermes/security-reports/`), or Discord.

## Procedure
1. **Establish baseline (read-only)**
   - Record hostname, kernel version, OS release, and report timestamp.
2. **Check open ports and listening services (read-only)**
   - `ss -tlnp` or `netstat -tlnp` — identify unexpected listeners.
   - Cross-reference against known-good service list.
3. **Check firewall state (read-only)**
   - `ufw status verbose` or `iptables -L -n` — confirm rules are active.
   - Flag any overly permissive rules (e.g. `0.0.0.0/0` allow on sensitive ports).
4. **Check failed login attempts (read-only)**
   - `journalctl -u ssh --since "7 days ago" | grep -i "failed\|invalid\|refused"` (or equivalent for the window).
   - Count unique source IPs, identify brute-force patterns.
   - `lastb | head -20` for tty/console failures if available.
5. **Check sudo and privilege escalation (read-only)**
   - `journalctl | grep -i sudo` for unusual escalation events.
   - Review `/var/log/auth.log` or `secure` for anomalies.
6. **Check package and update posture (read-only)**
   - `apt list --upgradable 2>/dev/null | grep -i security` (or distro equivalent).
   - Flag unpatched security advisories.
7. **Check for world-writable or SUID anomalies (read-only, targeted)**
   - Spot-check common sensitive paths; do not run full filesystem scan without approval.
8. **Repo hygiene check (read-only, if scope includes repos)**
   - Check for `.env` files accidentally tracked, hardcoded secrets patterns, or exposed tokens.
   - Use `git log --all --oneline | head -20` and `git ls-files | grep -E '\.env|secret|token|key'` per repo.
9. **Score and rank findings**
   - Assign each finding: `Critical`, `High`, `Medium`, `Low`, or `Informational`.
   - Prioritize by exploitability and exposure surface.
10. **Produce remediation checklist**
    - For each finding: evidence snippet, remediation command or action, approval requirement, and follow-up check.

## Guardrails
- **Defensive use only.** No exploit payloads, offensive scanning, or red-team guidance.
- Do **not** modify firewall rules, kill connections, or rotate credentials without explicit approval.
- Do **not** run broad filesystem scans (`find / ...`) without approval — target specific paths only.
- Do **not** expose raw credential or token values in the report; redact to first 4 characters + `****`.
- Do **not** claim a finding is resolved unless a verification check confirmed it.
- Do **not** auto-apply any fix; always present proposed command and await approval.
- Sudo-required fixes must be flagged explicitly and never auto-run.

## Output Format

```markdown
# Security Triage Report
- Host:
- Timestamp:
- Window:
- Scope: Host | Repos | Full
- Overall Posture: Secure | At Risk | Critical

## 1) Open Ports & Listening Services
- Findings:
- Unexpected listeners:

## 2) Firewall State
- Status: Active | Inactive | Unknown
- Permissive rules flagged:

## 3) Failed Login Analysis
- Total failed attempts (window):
- Unique source IPs:
- Brute-force patterns:

## 4) Privilege Escalation Review
- Unusual sudo events:
- Auth log anomalies:

## 5) Package & Update Posture
- Unpatched security updates:
- Last full upgrade:

## 6) File & Permission Anomalies
- Checked paths:
- Findings:

## 7) Repo Hygiene (if in scope)
- Repos checked:
- Secret exposure risk:
- Tracked sensitive files:

## 8) Findings (Ranked)
| Severity | Finding | Evidence | Remediation | Approval Required |
|----------|---------|----------|-------------|-------------------|
| Critical | ...     | ...      | ...         | Yes/No            |

## 9) Remediation Checklist
- [ ] [Critical] <action> — `<exact command>` — requires approval: Yes/No
- [ ] [High] ...

## Verification
- Commands executed:
- Evidence collected:
- Gaps / blind spots:
- Confidence:
```

## Verification
A run passes only if:
- Sections 1–6 are all present (or explicitly marked not applicable with reason).
- Every finding has a severity, evidence snippet, and remediation action.
- No state-changing command was executed.
- Secrets/tokens in evidence are redacted.
- Overall posture is justified by at least one `High` or `Critical` finding, or explicitly stated as clean with evidence.

## Sample Prompt
"Run a full security triage on this Linux host for the last 7 days. Check open ports, firewall, failed logins, sudo events, package posture, and repo hygiene. Return the standard Security Triage Report with ranked findings and remediation checklist."

## Notes
- Complements `security/daily-security-report` (automated script runner). This skill defines the interactive triage workflow and structured output format.
- For automated weekly runs, this skill's output format is the target; the cron job invokes it and routes the report to Discord and `~/.hermes/security-reports/`.
- If `ufw` is not installed, fall back to `iptables -L -n` and note the gap.
