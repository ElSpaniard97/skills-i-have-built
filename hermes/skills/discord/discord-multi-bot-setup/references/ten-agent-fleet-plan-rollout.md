# Ten-agent Discord fleet plan rollout

Use this reference when applying a user-provided fleet architecture plan across an existing Hermes Discord multi-bot deployment.

## Pattern that worked

1. Extract/review the plan first (PDF -> `pdftotext -layout`) and map it onto the existing deployment rather than blindly replacing the launcher.
2. Keep the existing standalone `discord.py` architecture under `/home/zeke/.hermes/discord-bots` and add shared fleet modules instead of duplicating logic in every bot.
3. Centralize stable plan content in:
   - `bot_config.py` for models, per-agent settings, safety rules, and role prompts.
   - `fleet_runtime.py` for shared channel maps, prefix stripping, dispatch parsing, escalation hooks, and audit logging.
   - `souls/*.md` plus each isolated `~/.hermes/discord-homes/<bot>/SOUL.md` for role/personality detail.
4. Store bot tokens in `/home/zeke/.hermes/discord-bots/.env`, `chmod 600`, and load that file in `launcher.py` before spawning child scripts. Do not print token values in summaries or verification output.
5. Keep launcher child stdio inherited (no `stdout=PIPE`/`stderr=PIPE`) and rely on journald plus per-agent log files.
6. Apply per-agent skills by copying class-level skill directories into each isolated bot home under `~/.hermes/discord-homes/<bot>/skills/`, then write a concise `SKILL_INDEX.md` so the lane is inspectable.

## Channel + identity verification

Use Discord REST to verify tokens and channels without exposing secrets:

```python
import urllib.request, json
base = 'https://discord.com/api/v10'
req = urllib.request.Request(
    base + '/users/@me',
    headers={'Authorization': f'Bot {token}', 'User-Agent': 'HermesFleetVerifier/1.0'},
)
```

Also verify each assigned channel with `GET /channels/<channel_id>`. For channel renames, use `PATCH /channels/<channel_id>` with `{ "name": "expected-name" }`, rate-limited between requests. Include a normal `User-Agent`; Discord can reject bare Python clients.

## Compile and runtime verification sequence

1. Run a per-file compiler loop instead of only `python3 -m py_compile *.py` so all syntax errors are surfaced:

```bash
python3 - <<'PY'
from pathlib import Path
import py_compile, sys
root = Path('/home/zeke/.hermes/discord-bots')
failed = []
for p in sorted(root.glob('*.py')):
    try:
        py_compile.compile(str(p), doraise=True)
        print('OK', p.name)
    except Exception as e:
        print('FAIL', p.name, e)
        failed.append(p.name)
sys.exit(1 if failed else 0)
PY
```

2. Import `HermesAgent` for every bot and print only non-secret state: home path, model, temperature, max tokens.
3. Run `python3 /home/zeke/.hermes/discord-bots/status.py`.
4. Check journald for `✓ <Bot> is online`, `Guilds: 1`, and `Synced ... command(s)` lines.
5. Compare process start time to code modification time. If process start is older than code mtime, the new behavior is written/compiled but not active until service restart.

## Important pitfall: denied restarts leave stale code active

If `systemctl --user restart hermes-discord-bots.service` is blocked or denied by the tool approval layer, do not claim the new runtime behavior is active. Report clearly:

- Current bots are online with the old process image.
- New files compile and are ready.
- User must manually restart the service to activate the new code.

Then provide:

```bash
systemctl --user restart hermes-discord-bots.service
python3 /home/zeke/.hermes/discord-bots/status.py
journalctl --user -u hermes-discord-bots.service -n 120 --no-pager
```

## Python generation pitfall

When generating Python files from Python scripts, escape embedded newlines inside generated f-strings as `\\n`, not literal newlines. Common failures:

- `await message.reply(f"...\n...")` accidentally generated as a multiline unterminated f-string.
- `return "\n".join(lines)` accidentally generated as `return "` newline `".join(lines)`.
- `f.write(... + "\n")` accidentally generated as a multiline unterminated string.

After generation, always run the per-file compiler loop above before restart.
