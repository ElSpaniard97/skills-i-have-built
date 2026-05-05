# Why Multiple Discord Bots Cannot Run Simultaneously via Hermes Gateway

## Problem Statement

You have 5 Discord bots (Spartan King, Jenko, Archer, Achilles, EPSN) that need to listen to the same Discord server(s) with different response behaviors:

- **Spartan King:** Responds to ALL messages
- **Jenko, Archer, Achilles, EPSN:** Respond ONLY when @mentioned

**Naive approach (fails):** Create 5 systemd services (`hermes-bot-spartan-king.service`, `hermes-bot-jenko.service`, etc.), each with its own `DISCORD_BOT_TOKEN`, all running simultaneously.

**Result:** Only one bot connects; the others fail with "Discord bot token already in use" errors, and starting one kills the other.

## Why It Fails: Technical Reasons

### 1. Discord Gateway Connection Limits

Discord maintains a **single WebSocket gateway connection per bot token**. When a bot token connects to Discord, it:
- Opens a persistent WebSocket to Discord's gateway
- Receives events (messages, reactions, etc.) on that connection
- Must stay connected to receive real-time updates

The Hermes gateway framework is built around this single-connection model. It creates **one gateway runner process** that opens **one WebSocket** per configured platform.

### 2. Hermes Gateway Architecture

```
Hermes Gateway Process (single instance)
    ├── Discord module
    │   ├── Token: REDACTED_DISCORD_BOT_TOKEN
    │   └── WebSocket → Discord API (single connection)
    ├── Telegram module
    ├── Slack module
    └── ...
```

**Key constraint:** One `DISCORD_BOT_TOKEN` per gateway process. If you try to run two gateway processes with different tokens, they **interfere with each other** — the second process detects the first is using the token and exits.

### 3. The Conflict You Encountered

**Attempt:** Start `hermes-bot-spartan-king.service` with token A, then start `hermes-bot-jenko.service` with token B simultaneously.

**What happens:**
1. `hermes-bot-spartan-king` starts, connects Spartan King bot to Discord
2. `hermes-bot-jenko` starts, tries to connect Jenko bot
3. Jenko gateway process runs fine... for ~2 seconds
4. Spartan King gateway detects a conflict (shared port, same agent state directory)
5. One or both crash with exit code 1 or 75 (TEMPFAIL)
6. systemd auto-restart logic triggers, causing a race condition
7. Net result: Bots flicker online/offline, neither is stable

**Error observed:**
```
ERROR gateway.platforms.base: [Discord] Discord bot token already in use (PID 60188). 
Stop the other gateway first.
```

## Viable Solutions

### Solution 1: Sequential Token Swap (Recommended for Most Users)

Run a single gateway instance. When you need to switch bots, update the token and restart:

```bash
# Active Spartan King
sed -i 's/^DISCORD_BOT_TOKEN=.*/DISCORD_BOT_TOKEN=<spartan_king_token>/' ~/.hermes/.env
hermes gateway restart

# Later, switch to Jenko
sed -i 's/^DISCORD_BOT_TOKEN=.*/DISCORD_BOT_TOKEN=<jenko_token>/' ~/.hermes/.env
hermes gateway restart
```

**Pros:**
- Simple, no extra infrastructure
- Works with existing Hermes tooling
- One gateway service to manage

**Cons:**
- Only one bot online at a time
- If you need multiple bots online simultaneously, this doesn't help

**Use case:** Scheduled tasks or manual switching ("Let me talk to Archer for a minute").

### Solution 2: Standalone Discord.py Scripts (Best for Simultaneous Operation)

Instead of using the Hermes gateway, create independent Discord.py bot scripts for each bot. Each runs as its own process:

```bash
# Terminal 1
python bot_spartan_king.py

# Terminal 2
python bot_jenko.py

# Terminal 3
python bot_archer.py
```

**Pros:**
- All 5 bots can run simultaneously
- Each bot is independent (crash in one doesn't affect others)
- Full control over response logic (Spartan King responds to all; others mention-only)
- Scales to any number of bots

**Cons:**
- Not integrated with Hermes gateway
- Requires writing discord.py code (not covered by Hermes CLI)
- No built-in Hermes agent integration (would need custom glue code)

**Example structure:**
```python
import discord
from discord.ext import commands

class SpeedtestBot(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user:
            return
        
        # Spartan King: respond to all
        if message.channel.name == "general":
            await message.reply("Spartan King here!")
        
        await self.bot.process_commands(message)

# Run one bot per script
if __name__ == "__main__":
    token = "<SPARTAN_KING_TOKEN>"
    bot = commands.Bot(command_prefix="!", intents=discord.Intents.default())
    asyncio.run(bot.add_cog(SpeedtestBot(bot)))
    bot.run(token)
```

### Solution 3: Custom Multi-Bot Gateway Runner (Advanced)

Write a custom Python script that:
1. Reads all 5 bot tokens from a config file
2. Spawns 5 separate Python processes (using `subprocess` or similar)
3. Each process runs a standalone discord.py bot
4. Monitors and restarts crashed bots

**Pros:**
- Integrated with your infrastructure
- Centralizes bot management

**Cons:**
- Requires Python development
- Needs systemd socket/ipc coordination
- No built-in Hermes support

## Recommendation for Your Setup (Spartan King + 4 Mention-Only Bots)

Given your use case, I recommend **Solution 1 (Sequential Swap) if bots rarely need to be online simultaneously**, or **Solution 2 (Standalone discord.py) if they all need to be online at the same time.**

If all 5 bots truly need to listen and respond simultaneously in the same Discord server(s), Discord.py scripts are the right choice. You can still invoke Hermes agents from within the bot code by calling `hermes` CLI or using the Hermes Python SDK.

## References

- [Discord Gateway Documentation](https://discord.com/developers/docs/topics/gateway)
- [Discord.py Multiple Bots Example](https://discordpy.readthedocs.io/en/stable/faq.html)
- Hermes session 2026-05-01: Attempted multi-gateway setup, confirmed limitation

## Session Context

**Date:** 2026-05-01  
**Goal:** Run Spartan King, Jenko, Archer, Achilles, EPSN simultaneously  
**Outcome:** Gateway framework limitation confirmed; recommended alternatives documented  
**Tokens obtained:** Spartan King ✓, Jenko ✓, others pending  
