---
name: hermes-gateway-setup
description: Install, configure, and troubleshoot the Hermes messaging gateway for Discord, Telegram, Slack, WhatsApp, and other platforms. Covers bot token validation, systemd service management, and platform allowlisting.
version: 1.0.0
metadata:
  hermes:
    tags: [gateway, discord, telegram, slack, messaging, bot, systemd, authentication, allowlist]
    related_skills: [discord, slack, telegram]
---

# Hermes Gateway Setup & Troubleshooting

## Overview

The Hermes Gateway is a systemd service that runs messaging platform integrations (Discord, Telegram, Slack, WhatsApp, Signal, etc.). It connects bot tokens to the Hermes agent and acts as the bridge between messaging platforms and the local Hermes agent.

**Key fact:** The gateway runs as a separate long-lived service. If bots show "offline" on Mission Control or don't respond in chat, the gateway is likely not running or misconfigured.

## Prerequisites

- Hermes agent installed and working (`hermes --version`)
- Valid bot token(s) for the platform(s) you want to enable
- Environment variables configured in `~/.hermes/.env`

## Quick Start

### 1. Check Gateway Status

```bash
hermes gateway status
```

Expected output if running:
```
● hermes-gateway.service - Hermes Agent Gateway...
  Active: active (running)
```

Expected if not running:
```
✗ Gateway is not running
```

### 2. Install Gateway as a Service

```bash
hermes gateway install
systemctl --user start hermes-gateway.service
```

Or, to install as a system-wide service (requires sudo, survives logout):

```bash
sudo hermes gateway install --system
```

### 3. Enable the Service (Optional — usually auto-done by install)

```bash
systemctl --user enable hermes-gateway.service
```

### 4. Verify It's Running

```bash
hermes gateway status
```

You should see `Active: active (running)` and a process ID.

## Configure Messaging Platforms

### Interactive Setup (Recommended)

```bash
hermes gateway setup
```

This walks you through platform selection and prompts for tokens. **Note:** This is TTY-interactive and will pause for input.

### Manual .env Configuration

Edit `~/.hermes/.env` directly and add the following sections:

#### Discord

```bash
# Discord Bot Token — from Discord Developer Portal
# https://discord.com/developers/applications
DISCORD_BOT_TOKEN=your_token_here
DISCORD_ALLOWED_USERS=your_discord_id_here  # Comma-separated user IDs
DISCORD_REPLY_TO_MODE=reply  # or thread, mention
GATEWAY_ALLOW_ALL_USERS=false  # Set true for open access (not recommended)
```

#### Telegram

```bash
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_ALLOWED_USERS=123456789  # Your user ID from @userinfobot
TELEGRAM_HOME_CHANNEL=  # Chat ID for cron delivery (optional)
```

#### Slack

```bash
SLACK_BOT_TOKEN=xoxb-...
SLACK_APP_TOKEN=xapp-...
SLACK_ALLOWED_USERS=U123ABC456  # Slack user IDs
```

### Reload the Gateway

After updating .env, restart the service:

```bash
hermes gateway restart
sleep 3
hermes gateway status
```

## Troubleshooting

### Bot Token Invalid or Expired

**Error:** `LoginFailure: Improper token has been passed.` or `401 Unauthorized`

**Cause:** The bot token is invalid, expired, or doesn't exist.

**Fix:**
1. Go to the platform's developer portal:
   - Discord: https://discord.com/developers/applications
   - Telegram: https://t.me/BotFather
   - Slack: https://api.slack.com/apps
2. Verify the bot exists and is enabled
3. **Reset/regenerate the token** (each platform's process differs)
4. Copy the new token to `~/.hermes/.env`
5. Restart gateway: `hermes gateway restart`

### Gateway Service Won't Start (Exit Code 75 / TEMPFAIL)

**Error:** `hermes-gateway.service: Main process exited, code=exited, status=75/TEMPFAIL`

**Cause:** Usually a network issue or invalid token. Run in foreground to see actual error:

```bash
timeout 30 hermes gateway run
```

Look for lines like:
- `discord connect timed out` → Network issue or invalid token
- `LoginFailure: Improper token` → Invalid token (see above)
- `No messaging platforms enabled` → No platforms configured in .env

**Fix steps:**
1. Run `timeout 30 hermes gateway run` to see the actual error
2. Check token validity (see above)
3. Verify `~/.hermes/.env` has at least one `{PLATFORM}_BOT_TOKEN` set
4. Check network connectivity: `curl https://discord.com` (or appropriate API endpoint)
5. Restart: `hermes gateway restart`

### "No Messaging Platforms Enabled" Warning

**Warning:** `WARNING gateway.run: No messaging platforms enabled.`

**Cause:** `~/.hermes/.env` has no valid platform tokens.

**Fix:**
1. Open `~/.hermes/.env`
2. Find or add `DISCORD_BOT_TOKEN=`, `TELEGRAM_BOT_TOKEN=`, etc.
3. Fill in actual token values
4. Restart: `hermes gateway restart`

### "No User Allowlists Configured" Warning

**Warning:** `WARNING gateway.run: No user allowlists configured. All unauthorized users will be denied.`

**Cause:** No `DISCORD_ALLOWED_USERS`, `TELEGRAM_ALLOWED_USERS`, etc., are set, and `GATEWAY_ALLOW_ALL_USERS` is not `true`.

**Fix (choose one):**

Option A: Allowlist specific users (recommended for security):
```bash
DISCORD_ALLOWED_USERS=132133748533415534  # Your Discord ID
TELEGRAM_ALLOWED_USERS=123456789
```

Option B: Allow all users (development only):
```bash
GATEWAY_ALLOW_ALL_USERS=true
```

Then restart: `hermes gateway restart`

### Check Live Logs

To see real-time gateway output:

```bash
journalctl --user -u hermes-gateway -f
```

Stop with Ctrl+C. For full journal history:

```bash
journalctl --user -u hermes-gateway -n 100 --no-pager
```

### Gateway Runs but Bots Show "Offline" on Mission Control

**Cause:** The gateway service is running, but the bots have not yet connected or their heartbeat has timed out.

**Fix:**
1. Verify gateway is running: `hermes gateway status`
2. Check logs: `journalctl --user -u hermes-gateway -f`
3. Wait 30–60 seconds (connection can be slow)
4. Restart gateway: `hermes gateway restart`
5. On Mission Control dashboard, refresh the page (F5)

## Service Management

### Managing Multiple Discord Bots (Archer, Achilles, EPSN, Jenko, Spartan King)

If you have multiple Discord bot accounts that need to run in parallel:

**Current limitation:** Hermes Gateway supports only ONE Discord bot token at a time in `~/.hermes/.env`.

**Recommended workflow for swapping bots:**

1. **Identify which bot to activate** (e.g., Spartan King)
2. **Update .env with that bot's token:**
   ```bash
   sed -i 's/^DISCORD_BOT_TOKEN=.*/DISCORD_BOT_TOKEN=<new_token>/' ~/.hermes/.env
   ```
3. **Restart the gateway:**
   ```bash
   hermes gateway restart
   ```
4. **Verify bot is online** — Check Discord member list or test with a mention
5. **To switch to a different bot,** repeat steps 1–4 with the next token

**Alternative (advanced):** Run multiple gateway instances on different ports with different .env files (requires manual systemd configuration — not covered here).

**Best practice:** If you need persistent multi-bot operation, use the Discord API directly from scripts rather than the gateway, or pick a single "primary" bot to run via gateway and automate the others separately.

### Start

```bash
hermes gateway start
# or: systemctl --user start hermes-gateway.service
```

### Stop

```bash
hermes gateway stop
# or: systemctl --user stop hermes-gateway.service
```

### Restart (Reloads .env)

```bash
hermes gateway restart
```

⚠ **Warning:** Restarting kills any running agent tasks. Approve interactively or use `--accept-hooks` to auto-approve.

### Uninstall Service

```bash
hermes gateway uninstall
# or: sudo hermes gateway uninstall --system
```

This removes the systemd service but does NOT delete .env or config.

### Run in Foreground (for testing)

```bash
hermes gateway run
```

Press Ctrl+C to stop. Useful for debugging since you see all logs directly.

## Pitfalls

1. **Token mismatch across platforms:** If you have multiple bots (e.g., Archer, Achilles, EPSN for Discord), each needs its own token in .env. The gateway does NOT support multiple Discord bots simultaneously via a single .env — you must run separate gateway instances or choose one primary bot. **See "Managing Multiple Discord Bots" below for the recommended workflow.**

2. **Multiple bot instances cannot coexist in gateway:** Attempting to run multiple gateway services with different Discord bot tokens (e.g., `hermes-gateway.service` for Spartan King, `hermes-gateway-jenko.service` for Jenko) will fail because Discord's API enforces one bot connection per token, and the gateway framework doesn't support parallel bot connections. Each service restart kills the previous bot's connection. **This is a hard architectural limitation — the workaround is sequential token swaps (see "Managing Multiple Discord Bots") or external discord.py scripts instead of the Hermes gateway.**

3. **Forgot to restart after .env edit:** Changes to `~/.hermes/.env` do NOT take effect until the gateway service is restarted. `hermes gateway restart` is required.

4. **Running hermes CLI while gateway is active:** The gateway and the CLI share the same agent state. If both try to connect to Discord simultaneously, one will fail. Keep either the CLI or the gateway running, not both in the same session for the same platform.

4. **Token already in use by another gateway instance:** Error: `Discord bot token already in use (PID XXXXX). Stop the other gateway first.` — Two gateway processes are trying to use the same token. Stop one: `hermes gateway stop` or kill the other PID, then restart.

5. **Allowlist prevents all messages:** If you set `DISCORD_ALLOWED_USERS` but miss your own ID, the bot will silently ignore your messages. Double-check the allowlist and test with `hermes gateway run` in foreground to see rejection logs.

6. **systemd linger not enabled:** If you log out, the user service may stop (depends on systemd linger). Check with `systemctl --user show-environment | grep DBUS_SESSION_BUS_ADDRESS`. Re-enable with `loginctl enable-linger` if needed.

## Verification Checklist

- [ ] `hermes gateway status` shows `Active: active (running)`
- [ ] `~/.hermes/.env` has at least one `{PLATFORM}_BOT_TOKEN=...` set
- [ ] `~/.hermes/.env` has `{PLATFORM}_ALLOWED_USERS` or `GATEWAY_ALLOW_ALL_USERS=true`
- [ ] No errors in `journalctl --user -u hermes-gateway -n 20`
- [ ] Test in foreground: `timeout 30 hermes gateway run` shows no `ERROR` or `LoginFailure` lines
- [ ] Bot responds to messages in the platform (Discord/Telegram/etc.)
- [ ] Mission Control dashboard shows bot status as "online" after 30–60 seconds

## References

- **[Multi-Bot Token Swap Workflow](references/multi-bot-token-swap.md)** — How to swap between multiple Discord bots (Archer, Achilles, EPSN, etc.) using sed and restart
- **[Discord Token Validation & LoginFailure Errors](references/discord-token-validation.md)** — Token format, regeneration, and error recovery
- [Hermes CLI Gateway Docs](https://claude-code.nousresearch.com/docs)
- [Discord Developer Portal](https://discord.com/developers/applications)
- [Discord.py Troubleshooting](https://discordpy.readthedocs.io)
