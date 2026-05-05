# Multi-Bot Token Swap Workflow

## Context

When you have multiple Discord bot accounts (e.g., Archer, Achilles, EPSN, Jenko, Spartan King) that share the same Hermes Gateway setup, you cannot run them all simultaneously. Instead, you swap which bot token is active via .env, then restart the gateway.

This document captures the exact procedure and common pitfalls from session 2026-05-01.

## Prerequisites

- Gather all bot tokens from Discord Developer Portal
- Write them down or store in a password manager
- Know which bot corresponds to which token
- Gateway installed and configured: `hermes gateway status`

## Step-by-Step Token Swap

### 1. Update the Token (Non-Interactive)

Use `sed` to replace the token without requiring TTY input:

```bash
sed -i 's/^DISCORD_BOT_TOKEN=.*/DISCORD_BOT_TOKEN=<NEW_TOKEN>/' ~/.hermes/.env
```

**Example (Spartan King):**
```bash
sed -i 's/^DISCORD_BOT_TOKEN=.*/DISCORD_BOT_TOKEN=REDACTED_DISCORD_BOT_TOKEN/' ~/.hermes/.env
```

### 2. Verify the Update

```bash
grep "DISCORD_BOT_TOKEN" ~/.hermes/.env | head -1
```

Expected output:
```
DISCORD_BOT_TOKEN=REDACTED_DISCORD_BOT_TOKEN
```

### 3. Restart the Gateway

```bash
hermes gateway restart
```

Monitor the restart (optional):
```bash
sleep 2 && hermes gateway status
```

Expected output:
```
● hermes-gateway.service - Hermes Agent Gateway...
  Active: active (running) since ...
```

### 4. Verify Bot is Online in Discord

- Open Discord and look at the member list for the server your bot is in
- The bot should show as "Online" (not "Offline")
- Try mentioning the bot; it should respond (if allowlist permits)

### 5. Test in Foreground (Optional, for Debugging)

If the bot doesn't appear online, run the gateway in foreground to see errors:

```bash
timeout 10 hermes gateway run 2>&1 | grep -i "discord\|error\|login"
```

**Likely errors:**
- `LoginFailure: Improper token has been passed.` — Invalid token; regenerate in Discord Developer Portal
- `discord connect timed out after 30s` — Network issue or invalid token
- No errors but bot still offline — Wait 30–60 seconds; gateway connection is slow

## Common Pitfalls

### Pitfall 1: Token Already in Use

**Error:**
```
Discord bot token already in use (PID XXXXX). Stop the other gateway first.
```

**Cause:** Two gateway processes are running with the same token.

**Fix:**
```bash
hermes gateway stop
sleep 2
hermes gateway start
```

Or kill the stale PID:
```bash
kill -9 XXXXX
hermes gateway start
```

### Pitfall 2: Forgot to Restart After .env Edit

Changes to `.env` do NOT take effect until `hermes gateway restart`. If the bot doesn't switch, you likely didn't restart.

### Pitfall 3: .env Has Multiple DISCORD_BOT_TOKEN Entries

If you've edited .env multiple times and added new entries instead of replacing, you may have duplicates:

```bash
grep "DISCORD_BOT_TOKEN" ~/.hermes/.env
```

If you see more than one line, remove the old one(s):
```bash
# Backup first
cp ~/.hermes/.env ~/.hermes/.env.bak

# Remove all DISCORD_BOT_TOKEN lines and re-add one
grep -v "DISCORD_BOT_TOKEN" ~/.hermes/.env.bak > ~/.hermes/.env
echo "DISCORD_BOT_TOKEN=<YOUR_TOKEN>" >> ~/.hermes/.env
```

### Pitfall 4: Token is Incorrect or Expired

**Error:** `LoginFailure: Improper token has been passed.`

**Fix:** Regenerate the token in Discord Developer Portal:
1. Go to https://discord.com/developers/applications
2. Select the bot's application
3. Click **Bot** → **Reset Token**
4. Copy the new token
5. Update .env and restart

## Token Format Validation

A valid Discord bot token has this format:
```
REDACTED_DISCORD_BOT_TOKEN
```

- Starts with `M...` (base64)
- Contains exactly two `.` separators
- ~60–80 characters long

If your token is missing parts or looks malformed, regenerate it.

## Session Log Reference

**Session:** 2026-05-01 10:01–10:13 CDT

**Bots configured:**
- Spartan King: `REDACTED_DISCORD_BOT_TOKEN` ✓ Online

**Bots pending:**
- Archer
- Achilles
- EPSN
- Jenko

**Workflow used:**
1. `sed -i` to update token in .env (non-interactive)
2. Verify with `grep`
3. `hermes gateway restart`
4. Confirm gateway status with `hermes gateway status`

This approach works well for swapping bots in a loop or via automation scripts.
