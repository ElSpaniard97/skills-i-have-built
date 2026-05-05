# Bot-Scoped Cron Finance Patterns (Jenko)

Context: per-bot isolation via `HERMES_HOME=/home/zeke/.hermes/discord-homes/<bot>`.

## Known-good cron creation/edit patterns

Important CLI syntax reminder:
- `hermes cron create <schedule> <prompt>` (prompt is positional)
- `hermes cron create ... --prompt ...` is invalid for this CLI

```bash
# Tuesday finance report (10:00 every Tuesday)
HERMES_HOME=/home/zeke/.hermes/discord-homes/jenko \
hermes cron create '0 10 * * 2' \
"Generate a neat Tuesday finance snapshot using only last 12h (not 24h). Include concise sections and links." \
--name jenko-tuesday-finance-10am \
--deliver 'discord:1499833622348435709'

# Mon/Thu trading report (10:00 Monday and Thursday)
HERMES_HOME=/home/zeke/.hermes/discord-homes/jenko \
hermes cron create '0 10 * * 1,4' \
"Generate a balanced stock brief using only last 12h (not 24h). Exactly 5 stocks with price/outlook/thesis/risk + links." \
--name jenko-mon-thu-trading-10am \
--deliver 'discord:1499833622348435709'
```

## Delivery reliability hierarchy (Discord)

If cron delivery fails, use this order:

1) Explicit channel ID in job deliver target (most reliable)
```bash
HERMES_HOME=/home/zeke/.hermes/discord-homes/jenko \
hermes cron edit <job_id> --deliver 'discord:1499833622348435709'
```

2) Ensure isolated home has Discord home channel config
```bash
HERMES_HOME=/home/zeke/.hermes/discord-homes/jenko hermes config set channels.discord.home 1499833622348435709
HERMES_HOME=/home/zeke/.hermes/discord-homes/jenko hermes config set channels.discord.enabled true
```

3) Re-run + tick + verify
```bash
HERMES_HOME=/home/zeke/.hermes/discord-homes/jenko hermes cron run <job_id>
HERMES_HOME=/home/zeke/.hermes/discord-homes/jenko hermes cron tick
HERMES_HOME=/home/zeke/.hermes/discord-homes/jenko hermes cron list
```

## Failure signatures and fixes

Observed signatures:
- `no delivery target resolved for deliver=discord`
- `Discord API error (404)` when using `discord:#jenko` in isolated homes

Fixes:
- Prefer `discord:<channel_id>` in job `--deliver`
- Set `channels.discord.home` and `channels.discord.enabled` in that bot's isolated `config.yaml`

## Report format templates (cost-efficient + user-readable)

Use explicit formatting constraints to avoid drift and verbosity.

### Tuesday finance snapshot template
- Window: last 12h only
- 120-180 words
- Sections:
  1) Executive Summary (2 bullets)
  2) Market and Macro (2 bullets)
  3) What Matters This Week (2 bullets)
  4) Must-Read Links (exactly 3 links: 2 articles + 1 YouTube)

### Mon/Thu balanced stock template
- Window: last 12h only
- 180-260 words
- Exactly 5 stocks
- Per-stock one-line schema:
  - `TICKER | Current Price: $X.XX | Outlook: Bullish/Neutral/Cautious | Thesis: ... | Risk: ...`
- Include a mini ASCII graph if reliable 12h relative performance is available; otherwise output exactly:
  - `Mini Graph: N/A.`

## Verification + evidence

```bash
HERMES_HOME=/home/zeke/.hermes/discord-homes/jenko hermes cron list
HERMES_HOME=/home/zeke/.hermes/discord-homes/jenko hermes cron run <job_id>
HERMES_HOME=/home/zeke/.hermes/discord-homes/jenko hermes cron tick
```

Cron run transcripts are stored under:
- `/home/zeke/.hermes/discord-homes/jenko/sessions/session_cron_<jobid>_*.json`

Use these transcripts to recover generated report output when delivery troubleshooting is needed.
