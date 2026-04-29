# Hermes Cron Setup

Create the Hermes cron job with these exact parameters:

```json
{
  "schedule": "0 2 * * *",
  "prompt": "Run `bash ~/.hermes/skills/security/daily-security-report/scripts/run_all.sh` then read the generated markdown at `~/.hermes/security-reports/latest.md` and send it to the Security thread.",
  "deliver": "discord:1498647342142722198",
  "enabled_toolsets": ["terminal", "file"]
}
```

If your Hermes environment exposes the Python MCP cron client, run the equivalent create call:

```bash
python3 - <<'PY'
from mcp_cronjob import create
create(
    schedule="0 2 * * *",
    prompt="Run `bash ~/.hermes/skills/security/daily-security-report/scripts/run_all.sh` then read the generated markdown at `~/.hermes/security-reports/latest.md` and send it to the Security thread.",
    deliver="discord:1498647342142722198",
    enabled_toolsets=["terminal", "file"],
)
PY
```

Fallback Linux crontab entry, if Hermes cron is unavailable:

```cron
0 2 * * * TZ=America/Chicago bash /home/zeke/.hermes/skills/security/daily-security-report/scripts/run_all.sh
```
