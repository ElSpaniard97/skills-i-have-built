---
name: daily-security-report
description: Daily automated security audit (system + repos + infra) with approval-gated fix application. Posts to Discord at 2:00 AM CST.
version: 1.0.0
---

# Daily Security Report

Runs a daily local security audit across the host, repositories, SSH/firewall/account posture, and GitHub CLI auth state. The report is written to `~/.hermes/security-reports/` and can be delivered by Hermes cron to Discord.

## Setup

Run the installer once, manually:

```bash
bash ~/.hermes/skills/security/daily-security-report/scripts/install_tools.sh
```

The installer is idempotent and may use `sudo apt-get` plus `pipx`. It is not run by cron.

Repository scanning uses `references/repos.txt`. If that file is empty, the first scan writes `~/hermes` plus discovered `.git` repositories under `/home/zeke` with depth up to 4.

## Cron

Do not create cron from this skill directly. Use `CRON_SETUP.md` for the Hermes cron parameters. The intended schedule is `0 2 * * *` in America/Chicago.

## Running Manually

```bash
bash ~/.hermes/skills/security/daily-security-report/scripts/run_all.sh
cat ~/.hermes/security-reports/latest.md
```

## Applying Fixes

Fix application is approval-gated:

```bash
python3 ~/.hermes/skills/security/daily-security-report/scripts/apply_fix.py 2026-04-28 --ids 1,3,5
python3 ~/.hermes/skills/security/daily-security-report/scripts/apply_fix.py 2026-04-28 --all-auto
```

Sudo fixes are never auto-applied. For findings requiring sudo, `apply_fix.py` writes a pending sudo command file under `~/.hermes/security-reports/`, posts the exact command to Discord if configured, marks the finding `pending_sudo: true`, and exits without running it.

Discord posting uses `DISCORD_BOT_TOKEN` first, then `DISCORD_WEBHOOK_URL`. If neither is set, reports are still written locally and Hermes cron can deliver `latest.md`.
