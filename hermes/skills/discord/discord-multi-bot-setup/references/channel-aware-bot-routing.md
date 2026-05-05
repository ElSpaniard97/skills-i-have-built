# Channel-Aware Bot Routing — Full Implementation

## Context

When running 5+ Discord bots on one server, each bot gets a dedicated channel
where it auto-responds without @mention. A shared "war-room" channel lets all
bots respond. Threads inherit their parent channel's behavior.

## Channel Layout (as of May 2026)

Category: "Bot Channels"
- #spartan-king (ID: 1499833617462067342) — Spartan King only
- #jenko        (ID: 1499833622348435709) — Jenko only
- #archer       (ID: 1499833625657737348) — Archer only
- #epsn         (ID: 1499833629386211470) — EPSN only
- #achilles     (ID: 1499833632318033931) — Achilles only
- #war-room     (ID: 1499833636063678495) — All bots

Guild: Hermes server (ID: 1499784767137251490)
Owner: Zeke (ID: 1321337485334155347) — bypasses all permission overwrites

## Bot User IDs (extracted from token first segment via base64)

- Spartan King: 1498345206897180703
- Jenko:        1493681289503445052
- Archer:       1499783569738956921
- EPSN:         1496588371525370048
- Achilles:     1497621035674239318

## on_message Routing Logic

```python
# Constants at top of each bot file
MY_CHANNEL_ID = <this_bot_channel_id>
WAR_ROOM_ID = 1499833636063678495

@bot.event
async def on_message(message: discord.Message):
    if message.author == bot.user:
        return
    if message.author.bot:
        return

    channel = message.channel
    parent_id = getattr(channel, 'parent_id', None)
    in_own_channel = (channel.id == MY_CHANNEL_ID or parent_id == MY_CHANNEL_ID)
    in_war_room = (channel.id == WAR_ROOM_ID or parent_id == WAR_ROOM_ID)
    mentioned = bot.user in message.mentions

    if not (mentioned or in_own_channel or in_war_room):
        return

    content = message.content.replace(f"<@{bot.user.id}>", "").strip()
    # ... rest of handler
```

## Permission Overwrites Pattern

Each channel denies SEND_MESSAGES for @everyone, then adds explicit member
overwrites for the allowed bot(s):

```json
{
  "permission_overwrites": [
    {"id": "GUILD_ID", "type": 0, "deny": "2048", "allow": "0"},
    {"id": "BOT_USER_ID", "type": 1, "allow": "117824", "deny": "0"}
  ]
}
```

- 2048 = SEND_MESSAGES
- 117824 = VIEW_CHANNEL + SEND_MESSAGES + READ_MESSAGE_HISTORY + ADD_REACTIONS + EMBED_LINKS + ATTACH_FILES
- type 0 = role, type 1 = member

## Thread Behavior

Threads inherit parent channel permission overwrites. No additional setup needed.
The `parent_id` check in the routing logic catches messages in threads:
- Thread in #jenko → `channel.parent_id == JENKO_CHANNEL_ID` → Jenko responds
- Thread in #war-room → `channel.parent_id == WAR_ROOM_ID` → all bots respond
