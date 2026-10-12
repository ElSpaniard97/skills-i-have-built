---
name: daily-security-report
description: Run the scripted local defensive security scan (system, repos, infrastructure) and return a severity-ranked markdown report for the ClaudeClaw Reports tab. Use when the scheduled daily security report runs, or when the user asks for "today's security report", a quick automated security scan, or the latest security findings. For a hands-on investigation of a specific concern, use security-triage instead.
version: 1.1.0
author: ClaudeClaw
---

# Daily Security Report

Scripted, report-only defensive checks. The scanners write JSON; `generate_report.py` turns it into markdown.

## Procedure

1. Run `bash "${CLAUDECLAW_HOME:-$HOME/claudeclaw}/skills/daily-security-report/scripts/run_all.sh"`.
   - Report directory: `$CLAUDECLAW_SECURITY_REPORT_DIR`, default `${CLAUDECLAW_HOME:-$HOME/claudeclaw}/store/security-reports`.
   - Individual scanner failures are written to `/tmp/sec_{system,repos,infra}.err` and do not stop the run.
2. Read `latest.md` in the report directory.
3. If any `/tmp/sec_*.err` file is non-empty, add a short "Scanner gaps" note under the report naming which scanner failed and the first error line.
4. Return the full markdown report as the final answer.

## Guardrails

- Report-only. Do not modify firewall, packages, users, processes, or repositories without explicit approval, even when a finding includes a `fix_command`.
- Do not run `scripts/apply_fix.py`: it is a Hermes-era helper that posts to Discord, which this skill must not do. Propose fixes in the report instead.
- Do not post externally.
- Redact any secret or token value that appears in evidence (first 4 characters + `****`).

## Verification

A run passes only if `latest.md` was regenerated in this run (check its timestamp), every finding has a severity, and scanner failures are reported rather than hidden.
