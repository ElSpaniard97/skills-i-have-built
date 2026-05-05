# Discord Bot Token Validation & Debugging

## The Silent Failure Pattern

### Symptom
Bot process starts but crashes immediately. Logs show:
```
[INFO] discord.client: logging in using static token
(no further output, process exits)
```

No `on_ready()` log. No `on_message()` events received. Bot appears "offline" in Discord.

### Root Cause
Invalid or expired Discord bot token. Discord API authentication fails with `401 Unauthorized` before discord.py calls any event handlers.

### Why It's Deceptive
- No exception is raised in your bot code
- The crash happens in discord.py's internal connection logic
- Integration code (on_message handler, Hermes calls) is never reached
- Looks like "bot is running but not responding" when actually "bot cannot authenticate"

## Diagnosis Flow

### Step 1: Verify Process is Running
```bash
ps aux | grep bot_name | grep -v grep
```
✓ Process exists → auth failure (token issue)
✗ Process missing → bot crashed on startup

### Step 2: Check Token Format
```bash
grep "DISCORD_TOKEN.*=" /path/to/bot.py
```
Token should be: `<digits>.<long_base64_string>.<longer_base64_string>`

Example of INVALID format (demo/placeholder):
```
REDACTED_DISCORD_BOT_TOKEN
```

### Step 3: Verify Token on Discord Developer Portal
```
https://discord.com/developers/applications
```
- Click bot application
- Go to "Bot" section
- If token doesn't match your file, it's expired/rotated
- Click "Reset Token" to generate new one

### Step 4: Check Discord Permissions
Bot must have these permissions in the server:
- ✓ Send Messages
- ✓ Read Message History  
- ✓ View Channels

Go to: Server Settings → Roles → (Bot Role Name) → Permissions

### Step 5: Update Token & Restart
```bash
# Update bot file with valid token (line 18-24 typically)
nano /path/to/bot.py

# Restart bot
systemctl --user restart <bot-service>

# Check logs for successful auth
journalctl --user -u <bot-service> -n 20
```

Expected log after valid token:
```
[INFO] discord.client: logging in using static token
[INFO] BotName: ✓ BotName is online as BotName#1234
[INFO] BotName: Guilds: 1
```

## Token Lifecycle

| Event | Discord Action | Bot Behavior |
|-------|---|---|
| Token first generated | Valid for use | Bot authenticates ✓ |
| Token reset (new one) | Old token invalidated | Bot crashes 401 ✗ |
| Token leaked/rotated | Discord invalidates | Bot crashes 401 ✗ |
| Embedding in code | Read by bot.py | Works until invalidated |

## Prevention

### Option 1: Environment Variables (Recommended)
```bash
export SPARTAN_KING_TOKEN="your_token_here"
export JENKO_TOKEN="your_token_here"
```

Bot code reads:
```python
DISCORD_TOKEN = os.getenv("SPARTAN_KING_TOKEN") or "fallback_placeholder"
```

Advantage: Don't commit real tokens to files.

### Option 2: .env File (docker-compose style)
```bash
# .env
SPARTAN_KING_TOKEN=actual_token_here
JENKO_TOKEN=actual_token_here
```

Bot code:
```python
from dotenv import load_dotenv
load_dotenv()
DISCORD_TOKEN = os.getenv("SPARTAN_KING_TOKEN")
```

### Option 3: Direct File Update (Simple, Less Secure)
Edit bot file directly, replace token.

## Testing Token Validity Before Startup

```python
# Minimal test script
import discord
import asyncio

TOKEN = "your_token_here"

async def test_token():
    client = discord.Client(intents=discord.Intents.default())
    
    @client.event
    async def on_ready():
        print(f"✓ Token valid! Connected as {client.user}")
        await client.close()
    
    try:
        await client.start(TOKEN)
    except discord.errors.LoginFailure:
        print("✗ Token invalid or expired (401 Unauthorized)")
    except Exception as e:
        print(f"✗ Other error: {e}")

asyncio.run(test_token())
```

Run this before deploying bots. If it prints "✓ Token valid!", your token is good.

## Multi-Bot Token Management

For systems with 5+ bots, use a config file:

```yaml
# bots.yaml
bots:
  spartan_king:
    token: ${SPARTAN_KING_TOKEN}
    intents: [message_content, guild_messages]
  jenko:
    token: ${JENKO_TOKEN}
    intents: [message_content, guild_messages]
```

Then load in launcher:
```python
import yaml
import os

with open("bots.yaml") as f:
    config = yaml.safe_load(f)

for bot_name, settings in config["bots"].items():
    token = os.getenv(settings["token"].replace("${", "").replace("}", ""))
    # Start bot with token
```

This centralizes token management and makes rotation easier.
