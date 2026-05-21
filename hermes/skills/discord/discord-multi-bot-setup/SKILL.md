---
name: discord-multi-bot-setup
description: |
  Set up and deploy multiple independent Discord bots using standalone discord.py scripts.
  Manage bot lifecycle with a launcher process and systemd service for auto-restart and boot persistence.
  Supports mixed response modes: respond-all (primary bot) + mention-only (auxiliary bots).
  Supports channel-aware routing: bots auto-respond in their dedicated channel + war-room (+ threads), mention-only elsewhere.
trigger: |
  User wants to run multiple Discord bots simultaneously with different tokens and response behaviors.
  Existing Hermes gateway framework can only handle ONE bot at a time — this skill is for standalone setups.
inputs:
  - Bot tokens (one per bot, from Discord Developer Portal)
  - Bot names and desired response mode (respond_all or mention_only)
  - Server ID and channel IDs for testing
  - Python environment path (venv recommended)
outputs:
  - 5+ independent Python bot scripts in ~/.hermes/discord-bots/
  - launcher.py managing all bots as separate processes
  - systemd service file for auto-restart and boot persistence
  - status.py for checking bot health
  - Comprehensive README and setup guide
status: stable
tested: true
notes: |
  discord.py v2.7.1 has intents quirks: use `intents.dm_messages` not `direct_messages`.
  Each bot runs independently with its own token — no shared gateway connection.
  Launcher auto-restarts crashed bots; systemd ensures service survives reboots.
---

## Setup Steps

### 1. Create Directory Structure

```bash
mkdir -p /home/zeke/.hermes/discord-bots
cd /home/zeke/.hermes/discord-bots
```

### 2. Create Bot Scripts

Create `spartan_king.py` (respond-all mode):

```python
import discord
from discord.ext import commands
import os

DISCORD_TOKEN = os.getenv("SPARTAN_KING_TOKEN", "YOUR_TOKEN_HERE")
bot_name = "Spartan King"

intents = discord.Intents.default()
intents.message_content = True
intents.guild_messages = True
intents.dm_messages = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"✓ {bot_name} connected as {bot.user}")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    
    # Respond to all messages
    await message.reply(
        f"🤖 *{bot_name} responding to your message*",
        mention_author=False
    )
    
    await bot.process_commands(message)

bot.run(DISCORD_TOKEN)
```

Create `jenko.py` (mention-only mode):

```python
import discord
from discord.ext import commands
import os

DISCORD_TOKEN = os.getenv("JENKO_TOKEN", "YOUR_TOKEN_HERE")
bot_name = "Jenko"

intents = discord.Intents.default()
intents.message_content = True
intents.guild_messages = True
intents.dm_messages = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"✓ {bot_name} connected as {bot.user}")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    
    # Only respond when mentioned
    if bot.user.mentioned_in(message):
        await message.reply(
            f"🤖 *{bot_name} responding to your mention*",
            mention_author=False
        )
    
    await bot.process_commands(message)

bot.run(DISCORD_TOKEN)
```

Repeat for `archer.py`, `achilles.py`, `epsn.py` (same template as jenko.py, change bot_name and token env var).

### 3. Create Launcher Script

Create `launcher.py` to manage all 5 bots as independent processes:

```python
#!/usr/bin/env python3
import subprocess
import time
import signal
import sys
import os

VENV_PYTHON = "/home/zeke/.hermes/hermes-agent/venv/bin/python3"
BOT_DIR = "/home/zeke/.hermes/discord-bots"
LOG_FILE = f"{BOT_DIR}/launcher.log"

BOTS = [
    {"script": "spartan_king.py", "name": "Spartan King"},
    {"script": "jenko.py", "name": "Jenko"},
    {"script": "archer.py", "name": "Archer"},
    {"script": "achilles.py", "name": "Achilles"},
    {"script": "epsn.py", "name": "EPSN"},
]

processes = {}

def log(msg):
    with open(LOG_FILE, "a") as f:
        f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {msg}\n")
    print(msg)

def start_bot(bot_config):
    script_path = os.path.join(BOT_DIR, bot_config["script"])
    cmd = [VENV_PYTHON, script_path]
    try:
        process = subprocess.Popen(cmd, cwd=BOT_DIR)
        processes[bot_config["name"]] = process.pid
        log(f"✓ Started {bot_config['name']} (PID {process.pid})")
        return process
    except Exception as e:
        log(f"✗ Failed to start {bot_config['name']}: {e}")
        return None

def monitor_bots():
    while True:
        for bot_config in BOTS:
            bot_name = bot_config["name"]
            if bot_name not in processes:
                log(f"⚠ {bot_name} not running, restarting...")
                start_bot(bot_config)
            else:
                pid = processes[bot_name]
                try:
                    os.kill(pid, 0)  # Check if process exists
                except OSError:
                    log(f"⚠ {bot_name} (PID {pid}) crashed, restarting...")
                    del processes[bot_name]
                    start_bot(bot_config)
        time.sleep(5)

def signal_handler(sig, frame):
    log("Shutting down launcher...")
    for bot_name, pid in processes.items():
        try:
            os.kill(pid, signal.SIGTERM)
            log(f"Terminated {bot_name} (PID {pid})")
        except:
            pass
    sys.exit(0)

if __name__ == "__main__":
    log("=== Discord Bot Launcher Started ===")
    
    # Start all bots
    for bot_config in BOTS:
        start_bot(bot_config)
        time.sleep(1)
    
    # Monitor and restart
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)
    
    try:
        monitor_bots()
    except KeyboardInterrupt:
        signal_handler(None, None)
```

### 4. Create systemd Service

Create `/home/zeke/.config/systemd/user/hermes-discord-bots.service`:

```ini
[Unit]
Description=Hermes Discord Multi-Bot Launcher
After=network.target

[Service]
Type=simple
ExecStart=/home/zeke/.hermes/hermes-agent/venv/bin/python3 /home/zeke/.hermes/discord-bots/launcher.py
WorkingDirectory=/home/zeke/.hermes/discord-bots
Environment="PATH=/home/zeke/.hermes/hermes-agent/venv/bin:/usr/local/bin:/usr/bin:/bin"
Environment="VIRTUAL_ENV=/home/zeke/.hermes/hermes-agent/venv"
Environment="HERMES_HOME=/home/zeke/.hermes"
Restart=on-failure
RestartSec=5
KillMode=mixed
KillSignal=SIGTERM
TimeoutStopSec=30
StandardOutput=journal
StandardError=journal
# NOTE: Do NOT add User= here — user-level services already run as the owning user.
# Adding User= causes exit code 216/GROUP and a crash loop.

[Install]
WantedBy=default.target
```

### 5. Enable & Start Service

```bash
systemctl --user daemon-reload
systemctl --user enable hermes-discord-bots.service
systemctl --user start hermes-discord-bots.service
systemctl --user status hermes-discord-bots.service
```

### 6. Create Status Script

Create `status.py` to verify all bots are running:

```python
#!/usr/bin/env python3
import subprocess
import re

bots = ["spartan_king.py", "jenko.py", "archer.py", "achilles.py", "epsn.py"]

print("Discord Bot Status")
print("-" * 50)

for bot_script in bots:
    result = subprocess.run(
        ["pgrep", "-f", bot_script],
        capture_output=True,
        text=True
    )
    
    if result.stdout.strip():
        pid = result.stdout.strip().split()[0]
        bot_name = bot_script.replace(".py", "").title()
        print(f"✓ {bot_name:20} (PID {pid})")
    else:
        bot_name = bot_script.replace(".py", "").title()
        print(f"✗ {bot_name:20} NOT RUNNING")

print("-" * 50)
```

## Monitoring & Troubleshooting

### View Live Logs

```bash
journalctl --user -u hermes-discord-bots -f
```

### Check Process Status

```bash
ps aux | grep discord-bots | grep -v grep
python3 /home/zeke/.hermes/discord-bots/status.py
```

### Manual Testing

```bash
# Test one bot in foreground
cd /home/zeke/.hermes/discord-bots
/home/zeke/.hermes/hermes-agent/venv/bin/python3 spartan_king.py
```

## Pitfalls

1. **discord.py v2.7.1 intents**: Use `intents.dm_messages` NOT `intents.direct_messages` (deprecated).
2. **MESSAGE_CONTENT intent**: Must enable in Discord Developer Portal for bot to read message content.
3. **Bot permissions**: Add bot to Discord server and verify "Send Messages" permission.
4. **Token security**: Never commit tokens to git. Use env vars for sensitive tokens.
5. **Process stalling**: If launcher stops restarting bots, check systemd service logs.
6. **User= in user-level systemd services**: NEVER put `User=zeke` in `~/.config/systemd/user/*.service` files. User-level services already run as the owning user. The `User=` directive causes exit code 216/GROUP and a crash loop. Only use `User=` in system-level services under `/etc/systemd/system/`.
7. **Thread parent_id vs Category parent_id**: For threads, `channel.parent_id` is the text channel the thread belongs to. For regular text channels, `parent_id` is the category. Use `getattr(channel, 'parent_id', None)` defensively — DM channels may not have it.
8. **Channel-aware bots must scope respond-all**: If a bot formerly responded to ALL messages everywhere, adding dedicated channels means it should STOP auto-responding in other bots' channels. Always add the channel-aware guard even to respond-all bots.
9. **Duplicate launcher/process sets cause stale behavior**: if multiple `launcher.py` or duplicate bot processes are running, Discord behavior appears inconsistent (old code still replying, mention rules seemingly ignored). Before debugging logic, enforce a single process set:
   - `systemctl --user stop hermes-discord-bots.service`
   - `pkill -f '/home/zeke/.hermes/discord-bots/(launcher.py|spartan_king.py|jenko.py|archer.py|achilles.py|epsn.py)'`
   - `systemctl --user start hermes-discord-bots.service`
   - verify with `pgrep -af '/home/zeke/.hermes/discord-bots/(launcher.py|spartan_king.py|jenko.py|archer.py|achilles.py|epsn.py)'`
10. **Launcher subprocess PIPE deadlock can make bots appear offline while still running**: if `launcher.py` starts bot children with `stdout=PIPE`/`stderr=PIPE` and does not continuously drain those pipes, bot processes can stall once buffers fill. Symptom: process exists but Discord shows offline/non-responsive. Use inherited stdio (no PIPE) and rely on journald (`journalctl --user -u hermes-discord-bots.service -f`).
11. **Token-hardening changes must be staged**: converting a bot from hardcoded token fallback to env-only token can instantly take that bot offline if the systemd service environment is missing the variable (e.g., `JENKO_TOKEN`). Before enforcing env-only:
   - verify variable is present in service runtime (`systemctl --user show-environment` / service `Environment=` / sourced env file)
   - deploy code change
   - restart service and immediately verify `<bot>.py` PID + "✓ ... is online" log line
   - if missing, roll back token enforcement first, then migrate credentials safely.
12. **Isolated Hermes homes need OAuth credentials**: if bots use `HERMES_HOME=/home/zeke/.hermes/discord-homes/<bot>` and Hermes CLI OAuth fallback, each isolated home must have access to the main credentials it needs.
   - Codex symptom: Discord reply says `<Bot>: hermes exit code 1`, and reproducing with `HERMES_HOME=... hermes chat ... --provider openai-codex` prints `No Codex credentials stored`. Fix: replace stale per-bot regular auth files with symlinks to the main auth file: back up `/home/zeke/.hermes/discord-homes/<bot>/auth.json`, remove it, then `ln -s /home/zeke/.hermes/auth.json /home/zeke/.hermes/discord-homes/<bot>/auth.json`. Verify with `[ -L .../auth.json ]` because a copied regular file can look valid but still fail refresh/provider lookup.
   - Google Workspace symptom: bot cannot use Drive/Gmail/Calendar/Docs/Sheets even though the main Hermes profile can. Fix both credential links: `ln -s /home/zeke/.hermes/google_token.json /home/zeke/.hermes/discord-homes/<bot>/google_token.json` and `ln -s /home/zeke/.hermes/google_client_secret.json /home/zeke/.hermes/discord-homes/<bot>/google_client_secret.json`.
   - Smoke tests: `HERMES_HOME=/home/zeke/.hermes/discord-homes/<bot> hermes chat -Q -q 'Reply exactly OK' --provider openai-codex -m gpt-5.5`; for Google, run the google-workspace setup `--check` or a Drive search from that same `HERMES_HOME`.
   - no bot service restart is required for credential-file symlink fixes; the next Hermes subprocess sees the files.
   - read `references/isolated-home-oauth.md` for the full reproduction/fix/verification sequence.
13. **Single-bot fresh-token rotation**: when a previously disabled bot gets a fresh token, verify it via Discord REST first, update only that bot's token source, flip only that bot's launcher `enabled` flag, remove only that bot from `status.py` `DISABLED_BOTS`, compile, restart, and verify the online log line. Include a normal `User-Agent` header for REST token verification; bare Python clients can get Discord `403 error code: 1010` even for a valid token. Prefer the helper script `scripts/rotate_disabled_bot_token.py` for repeat rotations; see `references/rotating-disabled-bot-token.md`.
14. **Plan rollouts need activation proof, not just running proof**: for multi-agent fleet plan changes, compare bot process start times with code mtimes. If processes started before the modified files, the old code image is still active even if all bots are online. If service restart is blocked/denied, report that the code is written/compiled and channels/tokens are verified, but the user must manually restart to activate new runtime behavior. See `references/ten-agent-fleet-plan-rollout.md`.
15. **Generated Python string escaping**: when generating bot scripts/modules from another Python script, embedded `\n` inside generated f-strings must be escaped as `\\n`. Literal newlines inside a generated quoted string cause unterminated f-string/string syntax errors. Run the per-file compiler loop from `references/ten-agent-fleet-plan-rollout.md` before restart.
16. **Spartan King should not compete in war-room fan-out**: when all bots respond to `#war-room`, Spartan can time out or post out of order if it launches the same slow Hermes CLI fallback as the specialist bots. For “Spartan responds last” behavior, special-case only Spartan: do not answer the original human war-room message immediately; create a pending summary keyed by the human message ID; allow Spartan to observe bot messages in war-room despite the normal `message.author.bot` ignore; collect bot replies by `message.reference.message_id`; after all expected agents reply or a quiet/max timeout expires, make one Spartan summarization call and reply to the original message. Also raise Spartan’s timeout/max_tokens because the final summary includes the captured responses. Verify activation by comparing process start time to modified file mtime; a compile-only rollout does not change live Discord behavior.
17. **Fleet-wide timeout messages are a shared-runtime bug, not one bad bot**: if EPSN/Archer/Hellen/etc. show `Timeout (>20s|45s|240s)` while logs show `No openai API key found. Falling back to Hermes CLI OAuth path`, all bots are spawning expensive `hermes chat` subprocesses through the shared integration. Current fleet policy: bots should not send user-visible timeout messages at all. Fix at the shared integration/config layer, not per bot: remove `asyncio.wait_for` around `HermesAgent.chat`, call `subprocess.run(..., timeout=None)` in both `run_hermes_cli` and `_call_via_hermes_cli`, make `_acquire_cli_slot(None)` wait indefinitely, keep the cross-process slot limiter in `hermes_integration.py` (lock files under `~/.hermes/discord-bots/.cli-slots`, default 4 concurrent CLI calls), compile all bot files, smoke-test the affected isolated home, restart `hermes-discord-bots.service`, and verify all process start times are newer than modified files plus no timeout/error logs after restart. Tradeoff: a genuinely hung Hermes subprocess will keep typing/waiting until manually killed or the process crashes; this is intentional for this fleet preference.
19. **Inter-agent task handoff is allowed only through routed task headers, not blanket bot-message processing**: Discord agents must be able to assign work to each other, but the fix is not to let every bot respond to every bot message. Keep the self-message guard (`message.author == bot.user`) and allow bot-authored messages only when they are in the target bot's own channel/thread and start with a routed header such as `**AGENT TASK**`, `**SK DISPATCH**`, `**SECURITY ESCALATION**`, or `**LEGAL ESCALATION**`. Human messages that explicitly say send/tell/forward/assign/delegate work to another agent should create an `AGENT TASK` in that agent's private channel with recent context. If restart is denied after code changes, do not retry; report that code is compiled but not active until restart, and use Discord REST only for urgent delivery. See the class-level `discord-agent-handoff` skill for the protocol and `references/harvey-epsn-msa-handoff-2026-05-11.md` in that skill for the concrete failure/fix.

20. **Discord response style is a shared fleet quality control**: if users complain that a bot dumped raw diffs, long legal text, local metadata, or unreadable blocks, patch the shared prompt/config first rather than every bot. Use `/home/zeke/.hermes/discord-bots/bot_config.py`: put global markdown/summary/open-items/recommended-next-step rules in `RESPONSE_RULES`, role-specific formats in `ROLE_RESPONSE_STYLES`, then append the role section in `get_system_prompt(bot_name)`. Keep EPSN MSA/legal-document replies in the approved AnchorLink Tech MSA Review format. Compile, restart only with approval, and verify process start times are newer than `bot_config.py`. See `references/discord-response-style-rollout.md`.

## Integration with Hermes AI

To integrate Hermes AI responses, replace the placeholder message handler:

```python
# Current (placeholder)
await message.reply(f"🤖 *{bot_name} responding*", mention_author=False)

# With Hermes (sketch)
from hermes_api import HermesAgent
agent = HermesAgent(model="claude-haiku")
response = await agent.chat(message.content)
await message.reply(f"🤖 {response}", mention_author=False)
```

## Channel-Aware Routing (Dedicated Bot Channels)

When each bot has its own Discord channel (e.g. `#spartan-king`, `#jenko`) plus a shared `#war-room`,
update the `on_message` handler so bots auto-respond in their own channel without @mention.

### Pattern: Channel-Aware on_message

Add channel ID constants at the top of each bot script:

```python
BOT_NAME = "Jenko"
MY_CHANNEL_ID = 1499833622348435709  # #jenko channel
WAR_ROOM_ID = 1499833636063678495    # #war-room channel
```

Replace the mention-only guard with channel-aware routing:

```python
@bot.event
async def on_message(message: discord.Message):
    if message.author == bot.user:
        return
    if message.author.bot:
        return

    # Check if we're in our own channel, a thread within it, or war-room
    channel = message.channel
    parent_id = getattr(channel, 'parent_id', None)
    in_own_channel = (channel.id == MY_CHANNEL_ID or parent_id == MY_CHANNEL_ID)
    in_war_room = (channel.id == WAR_ROOM_ID or parent_id == WAR_ROOM_ID)
    mentioned = bot.user in message.mentions

    # Respond if: in own channel/thread, in war-room/thread, or @mentioned anywhere
    if not (mentioned or in_own_channel or in_war_room):
        return

    # Strip mention if present
    content = message.content.replace(f"<@{bot.user.id}>", "").strip()

    # ... handle commands and generate response ...
```

### Key Details

- **Thread detection**: `getattr(channel, 'parent_id', None)` returns the parent channel ID for threads. Regular channels return `None` or the category ID — but thread parent_id points to the text channel, so checking `parent_id == MY_CHANNEL_ID` catches all threads under that channel.
- **War Room**: All bots check for `WAR_ROOM_ID` so any message there gets responses from all bots.
- **Strict channel mode (recommended for this workspace)**: auxiliary bots (Jenko/Archer/Achilles/EPSN) must NOT reply in `#general` or other bots' channels, even when @mentioned. They should only reply in their own assigned channel (and its threads) plus `#war-room`.
- **Command scope hardening**: apply the same channel gate before handling `!model` so auxiliary bots cannot process model-switch commands from `#general` or unrelated channels.
- **Spartan King scope**: Spartan should not be global respond-all. Scope it to `#spartan-king` + `#war-room`, and optionally allow `#general` via `GENERAL_CHANNEL_ID` env var.
- **Scope control**: Even "respond-all" bots (like Spartan King) should use this pattern to avoid responding in other bots' dedicated channels.
- **Per-bot brain isolation**: route each bot's Hermes CLI calls through bot-specific `HERMES_HOME` roots (example: `~/.hermes/discord-homes/spartan`, `.../jenko`, etc.) so skills, cron jobs, and memory remain isolated per bot.
- **Order-of-operations**: perform channel-scope checks first, then run `!model` command handling. This prevents command execution from unauthorized channels.

### Channel Creation

Use the discord-channel-management skill to create the channels with permission overwrites. The pattern:
- Deny `SEND_MESSAGES` for `@everyone` role
- Add explicit allow overwrite per bot (type 1 = member)
- For war-room, add overwrite for each bot
- Server owner bypasses all overwrites automatically

See `references/channel-aware-bot-routing.md` for the full on_message implementation.

### Global No-Mention Mode (all bots respond without @mention)

If the user wants every bot to respond without mention anywhere (not just dedicated channels), simplify each bot's `on_message` gate:

```python
@bot.event
async def on_message(message: discord.Message):
    if message.author == bot.user:
        return
    if message.author.bot:
        return

    # No mention gating
    content = message.content.strip()
    if not content:
        return

    # ... generate response ...
```

Apply this to all bot scripts (`spartan_king.py`, `jenko.py`, `archer.py`, `achilles.py`, `epsn.py`) to keep behavior consistent.

## Jenko-style Bot-Scoped Cron (Per-Bot HERMES_HOME)

When using per-bot isolation (`~/.hermes/discord-homes/<bot>`), create and manage cron jobs through that bot home so jobs cannot leak across bots.

```bash
# Example: Jenko isolated cron context
export HERMES_HOME=/home/zeke/.hermes/discord-homes/jenko

# Tuesday finance report at 10:00
hermes cron create '0 10 * * 2' \
  "Create a finance snapshot for the last 12 hours (not 24h). Keep it concise." \
  --name jenko-tuesday-finance-10am \
  --deliver 'discord:#jenko'

# Monday+Thursday trading advisory at 10:00
hermes cron create '0 10 * * 1,4' \
  "Create a stock-trading advisory for the last 12 hours (not 24h). Keep it concise." \
  --name jenko-mon-thu-trading-10am \
  --deliver 'discord:#jenko'
```

Verification sequence:
1. `HERMES_HOME=... hermes cron list` (confirm schedule + delivery target)
2. `HERMES_HOME=... hermes cron run <job_id>`
3. `HERMES_HOME=... hermes cron tick`
4. Confirm output appears in the intended Discord channel/thread.
5. For thread-only delivery, verify target format is `discord:<channel_id>:<thread_id>` and send a one-off test post before closing.

Cost-efficiency defaults for recurring finance reports:
- Explicit 12h window in prompt (avoid broader fetch scope)
- Hard word/line limits (e.g., <=110-130 words)
- Fixed section schema (reduces verbose drift)
- "No material update" fallback for low-signal windows

Pitfalls:
1. `--deliver discord` may fail with "no delivery target resolved" in isolated homes.
2. `--deliver discord:#jenko` may still 404 in some isolated-home setups; prefer `discord:<channel_id>` and set `channels.discord.home` + `channels.discord.enabled` inside that bot home.
3. Thread-only delivery is not discoverable from `send_message list` in some environments (list may show channels only). For thread routing, require explicit thread ID from user (or parse from Discord thread URL), then set deliver target to `discord:<channel_id>:<thread_id>`.
4. Cron CLI expects prompt as positional argument (`hermes cron create <schedule> <prompt>`), not `--prompt`.
5. Thread delivery requires full target format `discord:<channel_id>:<thread_id>`. Using only thread id (for example `discord:<thread_id>`) can silently miss the intended thread.
6. If manual `cron tick` appears silent, inspect new `session_cron_<jobid>_*.json` files under that bot home.
7. In per-bot isolated homes, scheduled jobs may not fire unless that exact `HERMES_HOME` is being ticked regularly. If only the main gateway scheduler is active, add a user-level systemd timer that runs `HERMES_HOME=/home/zeke/.hermes/discord-homes/<bot> hermes cron tick` every minute.
8. Prompt text with malformed currency tokens (for example, accidental `$` truncation or "Sub-0") can bleed into generated section headers/constraints. Prefer plain text constraints like "below 50 USD" when editing cron prompts through shell wrappers.
9. If `hermes cron run <job_id>` succeeds but `cron list` never updates `last_run_at`, check `systemctl --user status hermes-cron-<bot>.service` for a long-running `hermes cron tick`. A single blocked run can hold the oneshot service in `activating` and prevent subsequent timer ticks from completing.
10. For finance/trading cron jobs, external quote/news providers can fail mid-run (`ModuleNotFoundError` for optional libs, Yahoo 401/429, Stooq API-key captcha requirements). Build/report prompts with a mandatory fallback mode: if live data fetch fails, post a risk-first continuity bulletin to Discord instead of hanging or returning nothing.

## Files Reference

See `references/` for:
- Systemd service configuration
- launcher.py source
- Bot script templates
- `oauth-mode-and-process-dedup.md` (OAuth migration pitfalls + duplicate-process cleanup)
- `strict-channel-command-gating.md` (authorized-channel gate before replies and `!model` commands)
- `bot-scoped-cron-finance-patterns.md` (per-bot HERMES_HOME cron creation, explicit Discord channel delivery, and token-efficient finance report prompts)
- `thread-only-stock-trading-cron.md` (thread-target delivery format, ID sourcing, and validation flow for recurring stock reports)
- `cron-live-data-fallback-and-hang.md` (diagnose stuck cron ticks + enforce fallback-post behavior when market data providers fail)
- `bot-only-change-rollout-guardrails.md` (safe rollout/verification/rollback sequence when updating one bot under shared launcher)
- `mission-control-cron-skills-sync.md` (include global + per-bot cron/skills in Mission Control, including CLI-indexed skills, with OAuth-only-friendly DB sync pattern)
- `isolated-home-oauth.md` (diagnose/fix per-bot `HERMES_HOME` Codex OAuth failures: missing `auth.json`, smoke tests, no restart needed)
- `rotating-disabled-bot-token.md` (safe one-bot token rotation: REST verify with User-Agent, update script fallback, enable launcher/status, restart, verify online)
- `ten-agent-fleet-plan-rollout.md` (roll out a user-provided multi-agent fleet plan: shared runtime modules, channel renames, per-agent skills/souls, REST verification, compile loop, and stale-process/restart caveat)
- `discord-response-style-rollout.md` (fleet-wide Discord markdown/style rules, EPSN MSA response template, shared `bot_config.py` rollout pattern, and verification commands)
- `scripts/rotate_disabled_bot_token.py` (helper for repeated fresh-token rotations; read token from stdin or `DISCORD_NEW_TOKEN`, verify, patch one bot, compile, and optionally restart)
