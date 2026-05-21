# Rotating a Fresh Token for a Disabled Discord Bot

Use this when one bot in the multi-bot launcher is already configured but disabled because its prior token failed Discord verification.

## Workflow

Fast path: use the bundled helper script when rotating one already-configured disabled bot:

```bash
printf '%s' "$NEW_TOKEN" \
  | python3 /home/zeke/.hermes/skills/discord/discord-multi-bot-setup/scripts/rotate_disabled_bot_token.py <bot-slug> --token-stdin --apply

systemctl --user restart hermes-discord-bots.service
sleep 15
/home/zeke/.hermes/hermes-agent/venv/bin/python3 /home/zeke/.hermes/discord-bots/status.py
```

Use the manual steps below when the helper does not match local file structure.

1. Verify the new token without printing it:
   - Call `GET https://discord.com/api/v10/users/@me`
   - Use header `Authorization: Bot <token>`
   - Include a normal `User-Agent` header. Discord may return `403 error code: 1010` to bare urllib/default clients even when the token is valid.
   - Expected success includes bot id, username, discriminator, and `bot: true`.

2. Update only that bot's token source:
   - Example file: `/home/zeke/.hermes/discord-bots/hector.py`
   - Preserve the existing `os.getenv("<BOT>_TOKEN", "...")` pattern unless deliberately migrating credentials.
   - Never print or summarize the token value.

3. Enable only that bot in `/home/zeke/.hermes/discord-bots/launcher.py`:
   - Change the bot block from `"enabled": False` to `"enabled": True`.
   - Do not enable other disabled bots unless their tokens have been verified.

4. Update `/home/zeke/.hermes/discord-bots/status.py`:
   - Remove the bot name from `DISABLED_BOTS`.
   - Leave still-invalid bots in the disabled set so status remains honest.

5. Verify before and after restart:
   - Compile all bot scripts:
     `/home/zeke/.hermes/hermes-agent/venv/bin/python3 -m py_compile /home/zeke/.hermes/discord-bots/*.py`
   - Restart the user service:
     `systemctl --user restart hermes-discord-bots.service`
   - Wait ~15 seconds and inspect service status/logs.
   - Run:
     `/home/zeke/.hermes/hermes-agent/venv/bin/python3 /home/zeke/.hermes/discord-bots/status.py`

## Success Evidence

Look for a log line like:

```text
✓ Hector is online as Hector#4720
Model: gpt-5.5 (openai)
Guilds: 1
Synced 0 command(s)
```

Status should show the newly enabled bot with a PID while still showing any remaining invalid-token bots as disabled.

## Pitfalls

- Do not treat Discord `403 error code: 1010` from a bare HTTP client as token failure; retry with a proper `User-Agent` first.
- Do not start invalid-token bots just to test them under systemd; they can crash-loop the launcher logs. Verify tokens via REST first.
- Do not mark all bots as enabled after receiving one fresh token. Rotate and verify one bot at a time.
- Do not expose token values in command output, summaries, skills, memory, or logs.