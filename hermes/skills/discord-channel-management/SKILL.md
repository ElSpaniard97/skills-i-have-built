---
name: "discord-channel-management"
description: "Manage Discord channels via the Discord API, including creating, editing, and deleting channels."
category: "discord"
metadata:
  hermes:
    tags: [discord, channels, api, configuration, setup]
    related_skills: [discord]
---

# Discord Channel Management & Setup

## Overview

This skill enables setup and management of Discord bots, tokens, and channels using the Discord API and Hermes config. It covers both credential configuration (one-time setup) and channel operations (CRUD).

## Trigger Conditions

Use this skill when:
- Setting up Discord bot credentials for the first time
- Extracting Discord tokens/IDs from documentation or screenshots
- Creating, editing, deleting, or listing Discord channels
- Validating Discord bot permissions and access

## Part 1: Discord Credential Setup (One-Time)

### Step 1: Collect Required Credentials

From Discord Developer Portal or reference documentation, gather:
- **Bot Token** — long alphanumeric string with format like `ODk4MjI...` (base64-like) or `MTA0OTc4...` (encrypted)
- **Guild ID** (Server ID) — numeric ID of the target Discord server
- **User ID** (optional) — numeric Discord user ID for owner/admin reference

Source: Discord Developer Portal → Applications → Your Bot → Token + Server Settings → Server ID

### Step 2: Apply Credentials via Hermes Config

Use `hermes config set` to persist credentials (preferred over env vars for local setup):

```bash
hermes config set channels.discord.token "YOUR_BOT_TOKEN"
hermes config set channels.discord.server_id "GUILD_ID_NUMBER"
hermes config set channels.discord.user_id "DISCORD_USER_ID"
```

Alternative (environment variables, less preferred):
```bash
export DISCORD_BOT_TOKEN="YOUR_BOT_TOKEN"
export DISCORD_GUILD_ID="GUILD_ID_NUMBER"
```

### Step 3: Verify Configuration

```bash
hermes config show | grep -A 5 "discord:"
```

Should show:
```
channels:
  discord:
    token: <masked token>
    server_id: <numeric id>
    user_id: <numeric id>
```

Verify bot is reachable:
```bash
curl -H "Authorization: Bot $DISCORD_BOT_TOKEN" \
  https://discord.com/api/v10/users/@me
```

Success response: JSON with bot user info (id, username, avatar, etc.)

---

## Part 2: Channel Operations

### Create a Channel

```bash
curl -X POST "https://discord.com/api/v10/guilds/{GUILD_ID}/channels" \
  -H "Authorization: Bot $DISCORD_BOT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "channel-name",
    "type": 0,
    "topic": "optional description"
  }'
```

**Channel Types:**
- `0` = Text channel
- `2` = Voice channel
- `4` = Category
- `13` = Stage

### Create a Channel with Permission Overwrites (Bot-Exclusive Channels)

To restrict who can send messages in a channel, use `permission_overwrites` in the create payload.
Each overwrite targets a role (type 0) or member/bot (type 1) with explicit allow/deny bit flags.

**Discord Permission Bits (commonly needed):**
- `SEND_MESSAGES` = `0x800` (2048)
- `VIEW_CHANNEL` = `0x400` (1024)
- `READ_MESSAGE_HISTORY` = `0x10000` (65536)
- `ADD_REACTIONS` = `0x40` (64)
- `EMBED_LINKS` = `0x4000` (16384)
- `ATTACH_FILES` = `0x8000` (32768)

**Example: Bot-exclusive channel (only one bot can respond):**

```bash
# Deny SEND_MESSAGES for @everyone (role ID = guild ID), allow for one bot
curl -X POST "https://discord.com/api/v10/guilds/{GUILD_ID}/channels" \
  -H "Authorization: Bot $DISCORD_BOT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "bot-name",
    "type": 0,
    "parent_id": "CATEGORY_ID",
    "topic": "Only BotName responds here.",
    "permission_overwrites": [
      {"id": "GUILD_ID", "type": 0, "deny": "2048", "allow": "0"},
      {"id": "BOT_USER_ID", "type": 1, "allow": "117824", "deny": "0"}
    ]
  }'
```

Notes:
- `117824` = VIEW + SEND + HISTORY + REACTIONS + EMBEDS + ATTACH combined
- `type: 0` = role overwrite, `type: 1` = member/bot overwrite
- Server owner bypasses all permission overwrites automatically — no explicit allow needed
- These overwrites also apply to **threads** created within the channel (threads inherit parent channel permissions)

**Example: Shared channel (multiple bots can respond):**

Add one member overwrite per bot, all with the same allow bits:

```json
"permission_overwrites": [
  {"id": "GUILD_ID", "type": 0, "deny": "2048", "allow": "0"},
  {"id": "BOT1_USER_ID", "type": 1, "allow": "117824", "deny": "0"},
  {"id": "BOT2_USER_ID", "type": 1, "allow": "117824", "deny": "0"},
  {"id": "BOT3_USER_ID", "type": 1, "allow": "117824", "deny": "0"}
]
```

### Extract Bot User ID from Token

The first segment of a Discord bot token (before the first `.`) is the bot's user ID base64-encoded:

```python
import base64
token_first_segment = "MTQ5ODM0NTIwNjg5NzE4MDcwMw"
padded = token_first_segment + "=" * (4 - len(token_first_segment) % 4)
bot_user_id = base64.b64decode(padded).decode()
# e.g. "1498345206897180703"
```

This avoids needing a separate API call to `/users/@me` for each bot.

### List Channels in Guild

```bash
curl -H "Authorization: Bot $DISCORD_BOT_TOKEN" \
  https://discord.com/api/v10/guilds/{GUILD_ID}/channels | jq .
```

Extract channel IDs from response.

### Edit a Channel

```bash
curl -X PATCH "https://discord.com/api/v10/channels/{CHANNEL_ID}" \
  -H "Authorization: Bot $DISCORD_BOT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "new-channel-name",
    "topic": "new topic"
  }'
```

### Delete a Channel

```bash
curl -X DELETE "https://discord.com/api/v10/channels/{CHANNEL_ID}" \
  -H "Authorization: Bot $DISCORD_BOT_TOKEN"
```

---

## Hermes Cron + Thread Delivery (Operational Pattern)

When a report/job is posting to a parent channel but should post into a specific Discord thread, use this sequence:

1) **Pause misrouted job first** (prevents repeated bad posts):
```bash
HERMES_HOME=/home/zeke/.hermes/discord-homes/<bot> hermes cron pause <job_id>
```

2) **Get the thread target ID from Discord URL**
- Open the target thread and copy URL.
- URL shape is typically:
  - `https://discord.com/channels/<guild_id>/<thread_id>` (thread-as-channel URL), or
  - `https://discord.com/channels/<guild_id>/<parent_channel_id>/<thread_id>`
- Use the last numeric segment as `thread_id` when present.

3) **Set cron deliver target explicitly**
- Preferred explicit forms supported by Hermes:
  - `discord:<thread_id>`
  - `discord:<parent_channel_id>:<thread_id>`

Example:
```bash
HERMES_HOME=/home/zeke/.hermes/discord-homes/jenko \
  hermes cron edit 7ffa05e79e8c --deliver discord:1499967305969565696
```

4) **Resume and verify**
```bash
HERMES_HOME=/home/zeke/.hermes/discord-homes/<bot> hermes cron resume <job_id>
HERMES_HOME=/home/zeke/.hermes/discord-homes/<bot> hermes cron list
```

5) **Send a routing test message immediately**
- Use `send_message` to the exact target and confirm message_id.

## Pitfalls

1. **Token Format Confusion** — Do NOT assume all tokens look the same. Hermes-managed bots often have base64-like encoding. Always copy the FULL token from your reference source.

2. **Bot Permissions Missing** — Bot must have `MANAGE_CHANNELS` permission in the server. Add via Discord Server Settings → Roles → Bot Role → Permissions.

3. **API Version Mismatch** — Use `/v10/` (current) not `/v8/`. v8 is deprecated.

4. **Guild ID vs. Channel ID** — Requests to create channels use `guild_id`; requests to edit/delete use `channel_id`. They are different identifiers.

5. **Config vs. Environment Variables** — Hermes prioritizes `channels.discord.*` config over env vars. If you set both, config wins. Be consistent.

6. **Missing Server ID** — If you don't have the server ID, use this to list servers the bot can see:
   ```bash
   curl -H "Authorization: Bot $DISCORD_BOT_TOKEN" \
     https://discord.com/api/v10/users/@me/guilds | jq '.[] | {id, name}'
   ```

7. **Shell Escaping with JSON Payloads** — Complex JSON with nested arrays (like `permission_overwrites`) breaks when inlined in shell strings. Write the payload to a temp file and use `curl -d @/tmp/payload.json` instead.

8. **Permission Overwrites on Threads** — Threads inherit their parent channel's permission overwrites. You do NOT need to set overwrites on threads separately. A bot allowed to send in `#jenko` can also send in any thread under `#jenko`.

9. **Idempotency** — Always list existing channels before creating to avoid duplicates. The API happily creates multiple channels with the same name.

---

## Verification Checklist

- [ ] Token successfully validates with `/users/@me` endpoint
- [ ] Guild ID matches the server where bot is installed
- [ ] Bot has `MANAGE_CHANNELS` permission
- [ ] API calls use `/v10/` (not v8)
- [ ] Channel creation response includes `id` field
- [ ] Edits/deletes return 204 No Content or 200 OK

---

## External References

- See `references/discord-token-structures.md` for credential format examples
- See `references/discord-thread-routing-for-cron.md` for thread-only cron delivery troubleshooting and verified command sequence
- Discord API Docs: https://discord.com/developers/docs/intro
- Hermes Config: `hermes config set <key> <value>`
