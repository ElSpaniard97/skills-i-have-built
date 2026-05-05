# Identity Bleed: Bots Responding as "Claude Code"

## Problem
Discord bots powered by Hermes CLI subprocess respond with messages like:
- "I'm Claude Code, Anthropic's CLI agent"
- "I should clarify: I'm Claude, Anthropic's AI assistant"
- Meta-commentary about Hermes infrastructure, memory, skills, etc.

Instead of staying in character as the bot persona (Spartan King, Archer, etc.).

## Root Cause
The Hermes CLI (`hermes -z "message"`) loads by default:
1. System prompt declaring "You are Claude Code"
2. SOUL.md / persona file
3. AGENTS.md from CWD
4. Memory (persistent facts about the user/environment)
5. Preloaded skills

All of these inject identity at the **system prompt level**. The bot's context
(e.g., "You are Spartan King") is passed as a **user message** via `-z`, which
the model treats as lower priority than system instructions.

## Fix (Two-Part)

### 1. Add `--ignore-rules` to CLI call
```python
cmd = [self.hermes_bin, "-z", message, "-m", self.model, "--yolo", "--ignore-rules"]
```
The `--ignore-rules` flag strips: AGENTS.md, SOUL.md, .cursorrules, memory,
and preloaded skills. This removes the competing identity.

### 2. Strengthen context prompts
Weak: `"You are Spartan King, a helpful Discord bot."`
Strong:
```python
context = (
    f"You are {BOT_NAME}, a bold warrior-king. "
    f"NEVER say you are Claude, an AI assistant, or mention Hermes/infrastructure. "
    f"Stay in character as {BOT_NAME} at all times. "
    f"Keep responses concise (under 2000 chars) for Discord. "
    f"User: {message.author.name}"
)
```

Key elements of a strong context:
- Specific personality description (not just "helpful bot")
- Explicit denial instruction ("NEVER say you are Claude")
- Character lock ("Stay in character at all times")

## Files Changed (May 2026)
- `/home/zeke/.hermes/discord-bots/hermes_integration.py` — added `--ignore-rules`
- All 5 bot files — strengthened context prompts with unique personalities
- `/home/zeke/.config/systemd/user/hermes-discord-bots.service` — removed `User=zeke`

## Hermes CLI Relevant Flags
- `--ignore-rules` — skip AGENTS.md, SOUL.md, memory, preloaded skills
- `--ignore-user-config` — skip ~/.hermes/config.yaml
- `--yolo` — skip tool confirmations (needed for non-interactive subprocess)
- `-z "prompt"` — one-shot prompt/response mode
- `-m MODEL` — model override
