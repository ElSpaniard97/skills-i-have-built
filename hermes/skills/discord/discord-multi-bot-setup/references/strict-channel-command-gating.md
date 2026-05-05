# Strict channel + command gating pattern (Discord multi-bot)

Use this when bots must be prevented from responding or processing commands in unauthorized channels.

## Policy

- Spartan King: allowed in `#spartan-king`, `#war-room`, and optional `#general` via `GENERAL_CHANNEL_ID`.
- Jenko/Archer/Achilles/EPSN: allowed only in own channel + `#war-room` (including threads).
- `!model` must be subject to the same gate as normal replies.

## Implementation pattern

```python
channel = message.channel
parent_id = getattr(channel, 'parent_id', None)
in_own_channel = (channel.id == MY_CHANNEL_ID or parent_id == MY_CHANNEL_ID)
in_war_room = (channel.id == WAR_ROOM_ID or parent_id == WAR_ROOM_ID)

# Spartan only (optional):
GENERAL_CHANNEL_ID = int(os.getenv("GENERAL_CHANNEL_ID", "0"))
in_general = bool(GENERAL_CHANNEL_ID) and (
    channel.id == GENERAL_CHANNEL_ID or parent_id == GENERAL_CHANNEL_ID
)

allowed = (in_own_channel or in_war_room)             # aux bots
# allowed = (in_own_channel or in_war_room or in_general)  # Spartan

if not allowed:
    return

content = message.content.strip()
if content.startswith("!model"):
    # safe to handle here because channel already authorized
    ...
```

## Verification checklist

1. Post plain text in `#general`: only Spartan should answer (and only if GENERAL_CHANNEL_ID set).
2. Run `!model` in `#general`: auxiliary bots must ignore.
3. Post in each bot's own channel: only that bot responds (plus any explicit war-room policy).
4. Post in `#war-room`: all configured bots respond.
5. Verify single process set after restart:
   `pgrep -af '/home/zeke/.hermes/discord-bots/(launcher.py|spartan_king.py|jenko.py|archer.py|achilles.py|epsn.py)'`

## Common regression

If old behavior persists, duplicate launcher/process sets are usually the cause. Do stop + pkill + start before re-testing.