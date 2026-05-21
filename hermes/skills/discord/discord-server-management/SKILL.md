---
name: discord-server-management
description: Create, edit, and delete Discord channels, categories, and threads using the Discord REST API. Use this skill whenever the user asks to create or manage Discord channels, categories, or server structure.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [Discord, Channels, Server, Management, API]
---

# Discord Server Management

Create, edit, and delete Discord channels, categories, and threads using the Discord REST API via curl.

## Setup

Terminal subprocesses do not inherit gateway env vars. Always load credentials by reading directly from the `.env` file:

```bash
DISCORD_BOT_TOKEN=$(grep "^DISCORD_BOT_TOKEN=" ~/.hermes/.env | cut -d= -f2 | tr -d '\n\r')
DISCORD_GUILD_ID=$(grep "^DISCORD_GUILD_ID=" ~/.hermes/.env | cut -d= -f2 | tr -d '\n\r')
```

Run these two lines at the start of every Discord API command block. All requests then use:
```
Authorization: Bot $DISCORD_BOT_TOKEN
Content-Type: application/json
```

The active Hermes Discord server observed in this environment is `1499784767137251490` (`Hermes server`). If a stored `DISCORD_GUILD_ID` is missing or stale, verify the current guild with a known-good bot token via `GET /users/@me/guilds` before managing channels. Do not assume old guild ID `1497587108850958387`.

---

## 1. List Channels in a Guild

```bash
curl -s \
  -H "Authorization: Bot $DISCORD_BOT_TOKEN" \
  https://discord.com/api/v10/guilds/$DISCORD_GUILD_ID/channels \
  | python3 -c "
import sys, json
types = {0:'text', 2:'voice', 4:'category', 5:'announcement', 15:'forum', 16:'media'}
for c in sorted(json.load(sys.stdin), key=lambda x: (x.get('position',0))):
    t = types.get(c['type'], str(c['type']))
    parent = f\" (parent: {c.get('parent_id','')})\" if c.get('parent_id') else ''
    print(f\"  {c['id']}  [{t:12}]  {c['name']}{parent}\")"
```

## 3. Create a Text Channel

```bash
curl -s -X POST \
  -H "Authorization: Bot $DISCORD_BOT_TOKEN" \
  -H "Content-Type: application/json" \
  https://discord.com/api/v10/guilds/$DISCORD_GUILD_ID/channels \
  -d '{
    "name": "my-new-channel",
    "type": 0,
    "topic": "Channel topic here"
  }' | python3 -c "
import sys, json
c = json.load(sys.stdin)
print(f\"Created: #{c['name']} (id: {c['id']})\")"
```

## 4. Create a Voice Channel

```bash
curl -s -X POST \
  -H "Authorization: Bot $DISCORD_BOT_TOKEN" \
  -H "Content-Type: application/json" \
  https://discord.com/api/v10/guilds/$DISCORD_GUILD_ID/channels \
  -d '{
    "name": "General Voice",
    "type": 2,
    "bitrate": 64000,
    "user_limit": 0
  }' | python3 -c "
import sys, json
c = json.load(sys.stdin)
print(f\"Created voice: {c['name']} (id: {c['id']})\")"
```

## 5. Create a Category

```bash
curl -s -X POST \
  -H "Authorization: Bot $DISCORD_BOT_TOKEN" \
  -H "Content-Type: application/json" \
  https://discord.com/api/v10/guilds/$DISCORD_GUILD_ID/channels \
  -d '{
    "name": "MY CATEGORY",
    "type": 4
  }' | python3 -c "
import sys, json
c = json.load(sys.stdin)
print(f\"Created category: {c['name']} (id: {c['id']})\")"
```

## 6. Create a Channel Inside a Category

Get the category's ID first (from list channels), then:

```bash
CATEGORY_ID="category_channel_id"

curl -s -X POST \
  -H "Authorization: Bot $DISCORD_BOT_TOKEN" \
  -H "Content-Type: application/json" \
  https://discord.com/api/v10/guilds/$DISCORD_GUILD_ID/channels \
  -d "{
    \"name\": \"my-channel\",
    \"type\": 0,
    \"parent_id\": \"$CATEGORY_ID\"
  }" | python3 -c "
import sys, json
c = json.load(sys.stdin)
print(f\"Created: #{c['name']} under category {c.get('parent_id')} (id: {c['id']})\")"
```

## 7. Edit a Channel (rename, change topic, reorder)

```bash
CHANNEL_ID="channel_id_to_edit"

curl -s -X PATCH \
  -H "Authorization: Bot $DISCORD_BOT_TOKEN" \
  -H "Content-Type: application/json" \
  https://discord.com/api/v10/channels/$CHANNEL_ID \
  -d '{
    "name": "new-channel-name",
    "topic": "Updated topic"
  }' | python3 -c "
import sys, json
c = json.load(sys.stdin)
print(f\"Updated: #{c['name']} (id: {c['id']})\")"
```

## 8. Delete a Channel

```bash
CHANNEL_ID="channel_id_to_delete"

curl -s -X DELETE \
  -H "Authorization: Bot $DISCORD_BOT_TOKEN" \
  https://discord.com/api/v10/channels/$CHANNEL_ID \
  | python3 -c "
import sys, json
c = json.load(sys.stdin)
print(f\"Deleted: #{c['name']}\")"
```

## Channel Type Reference

| Type | Value | Description |
|------|-------|-------------|
| Text | 0 | Standard text channel |
| Voice | 2 | Voice channel |
| Category | 4 | Category (groups channels) |
| Announcement | 5 | Announcement channel |
| Forum | 15 | Forum channel |
| Media | 16 | Media channel |

## Error Handling

If a curl response contains `"code"` and `"message"`, it's an API error:

```bash
# Check for errors
RESPONSE=$(curl -s ...)
if echo "$RESPONSE" | python3 -c "import sys,json; d=json.load(sys.stdin); exit(0 if 'code' in d else 1)" 2>/dev/null; then
  echo "Error: $(echo $RESPONSE | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('message','unknown'))")"
fi
```

Common errors:
- `50013` — Missing Permissions (bot needs Manage Channels in server)
- `10003` — Unknown Channel (channel ID doesn't exist)
- `50035` — Invalid form body (bad JSON payload)
