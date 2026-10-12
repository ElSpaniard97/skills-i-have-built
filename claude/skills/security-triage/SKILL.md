---
name: security-triage
description: "Defensive, read-only security triage for a Linux host and local project repos: listening ports, firewall state, failed and brute-force logins, sudo activity, pending security updates, risky permissions, and secrets committed to git. Produces a severity-ranked report with evidence and an approval-gated remediation checklist. Use when the user asks for a security audit or posture check, is worried a server was compromised, sees suspicious logins, wants a firewall or open-port review, or when linux-system-health flags a security warning. Defensive use only."
---


# Security Triage

## Trigger
Use this skill when the user asks for a security posture check, security audit, firewall review, failed login analysis, open port scan, or security report for the Linux host or project repositories. Also use when `linux-system-health` surfaces a `Critical` or `Warning` security signal.

## Required Inputs
- Scope: `host` (Linux system), `repos` (GitHub/local), or `full` (both).
- Time window for log analysis: default last 7 days.
- Output target: chat reply (default) or a markdown file the user names.

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
   - `journalctl -u ssh -u sshd --since "7 days ago" --no-pager | grep -iE "failed|invalid|refused"` (the unit is `ssh` on Debian/Ubuntu and `sshd` on most other distros).
   - Count unique source IPs, identify brute-force patterns.
   - `sudo lastb | head -20` for tty/console failures if available (needs root; if you cannot run it, list it as a blind spot).
5. **Check sudo and privilege escalation (read-only)**
   - `journalctl | grep -i sudo` for unusual escalation events.
   - Review `/var/log/auth.log` (Debian/Ubuntu) or `/var/log/secure` (RHEL/Fedora) for anomalies; these usually need sudo to read.
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

## When you can't run commands on the host
If this session has no shell on the machine in question (for example in a claude.ai chat), give the user the exact read-only commands from the procedure as one copy-paste block, ask them to paste the output back, and build the report from that output. Mark anything you could not see as a blind spot.

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

## 9) Remediation Checklist
- [ ] [Critical] (action) — `(exact command)` — requires approval: Yes/No

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
- Overall posture is justified by at least one concrete finding or explicitly stated as clean with evidence.

## Sample Prompt
"Run a full security triage on this Linux host for the last 7 days. Check open ports, firewall, failed logins, sudo events, package posture, and repo hygiene. Return the Security Triage Report with ranked findings and remediation checklist."

## Notes
- If `ufw` is not installed, fall back to `iptables -L -n` and note the gap.
- Redact all credential/token values in output — even partial exposure is a risk.
