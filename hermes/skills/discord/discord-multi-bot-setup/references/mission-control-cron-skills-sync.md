# Mission Control inclusion for per-bot cron + skills (OAuth-only friendly)

Context: Mission Control may show Discord agents online but omit per-bot cron jobs/skills when bots run from isolated homes under `~/.hermes/discord-homes/<bot>`.

## What to include
- Global Hermes cron: `~/.hermes/cron/jobs.json`
- Per-bot cron: `~/.hermes/discord-homes/*/cron/jobs.json`
- Global skills: `~/.hermes/skills`
- Per-bot skills: `~/.hermes/discord-homes/*/skills`
- CLI-indexed per-bot skills (`HERMES_HOME=<bot-home> hermes skills list`) for cases where disk layout is sparse (`.hub` folders, generated catalog entries).

## Proven implementation pattern
1. Patch Mission Control API aggregation:
   - `src/app/api/cron/route.ts`: aggregate cron list from main + `discord-homes/*` jobs.json.
   - `src/app/api/skills/route.ts`: include `discord-homes/*/skills` roots.
   - `src/lib/skill-sync.ts`: include same `discord-homes/*/skills` roots for scheduler sync.
2. Keep OAuth-only posture by avoiding API key ingestion path; sync directly to local MC SQLite if needed.
3. Extend local bridge script (`/home/zeke/.hermes/scripts/discord_mc_oauth_sync.py`) to:
   - keep bot runtime status updated,
   - mirror cron jobs into MC `tasks` (e.g., tag `cron,mission-control`),
   - upsert per-bot skills into MC `skills` (including CLI-indexed skills).

## Verification commands
```bash
python3 /home/zeke/.hermes/scripts/discord_mc_oauth_sync.py

python3 - <<'PY'
import sqlite3
conn=sqlite3.connect('/home/zeke/hermes-mission-control/.data/mission-control.db')
print('skills by source:')
for row in conn.execute("select source, count(*) from skills group by source order by source"):
    print(row)
print('cron mirrored tasks:', conn.execute("select count(*) from tasks where tags like '%cron,mission-control%'").fetchone()[0])
conn.close()
PY
```

## Operational pitfalls
- Mission Control restarts can fail with `EADDRINUSE` on `:3001` if an orphan `next-server` remains after timeout stop. Kill old PID and restart service.
- Some bot homes show valid skills in `hermes skills list` but no `SKILL.md` directories; add CLI-indexed ingestion to avoid false "missing skills" in MC.
- If `curl /api/*` checks are blocked by auth, validate inclusion from DB counts/logs first, then UI.
