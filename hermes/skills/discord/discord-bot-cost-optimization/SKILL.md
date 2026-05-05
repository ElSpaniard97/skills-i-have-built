---
name: discord-bot-cost-optimization
type: guide
summary: Centralized cost and response optimization for all Discord bots
trigger: |
  User wants to reduce API costs for Discord bots.
  User wants shorter/simpler bot responses.
  User wants to change bot model, token limits, or response style.
  User wants to add/edit a bot personality.
description: |
  All Discord bot response behavior is controlled from a single config file:
  ~/.hermes/discord-bots/bot_config.py
  
  This is the ONLY file you need to edit to change how bots respond.
  Changes apply to ALL bots after a service restart.
  Works with any AI model/provider — the config is model-agnostic.
---

## Architecture

```
bot_config.py          ← EDIT THIS (model, max_tokens, temp, personalities, response rules)
    ↓
hermes_integration.py  ← reads config, calls Anthropic API with system prompt
    ↓
spartan_king.py        ← imports get_system_prompt(BOT_NAME) from bot_config
archer.py              ← same pattern
jenko.py               ← same pattern
achilles.py            ← same pattern
epsn.py                ← same pattern
```

## Quick Changes

### Change response length / cost
Edit `~/.hermes/discord-bots/bot_config.py`:
```python
MAX_TOKENS = 150    # lower = cheaper + shorter (default: 150)
TEMPERATURE = 0.7   # lower = more predictable
MODEL = "claude-haiku-4-5-20251001"  # cheapest option
```

### Change response style for ALL bots
Edit `RESPONSE_RULES` in bot_config.py. This string is appended to every bot's system prompt.

### Add or edit a bot personality
Edit `PERSONALITIES` dict in bot_config.py. Key = BOT_NAME (must match the bot file).

### Switch AI model
Change `MODEL` in bot_config.py. Works with any Anthropic model name.
To switch providers entirely (e.g. OpenAI), you'd need to update hermes_integration.py's `_call_api()`.

## After Any Change
```bash
systemctl --user restart hermes-discord-bots.service
systemctl --user status hermes-discord-bots.service
```

## Cost Optimization Levers

| Lever | Setting | Impact |
|-------|---------|--------|
| Model | MODEL = "claude-haiku-4-5-20251001" | Cheapest Anthropic model |
| Output tokens | MAX_TOKENS = 150 | Hard cap on response length |
| System prompt size | Keep PERSONALITIES short | Fewer input tokens per call |
| Response rules | RESPONSE_RULES enforces brevity | Model self-limits output |
| Temperature | TEMPERATURE = 0.7 | No direct cost impact, but lower = less rambling |

## File Locations
- Config: `/home/zeke/.hermes/discord-bots/bot_config.py`
- Integration: `/home/zeke/.hermes/discord-bots/hermes_integration.py`
- Bot files: `/home/zeke/.hermes/discord-bots/{spartan_king,archer,jenko,achilles,epsn}.py`
- Service: `~/.config/systemd/user/hermes-discord-bots.service`
- Launcher: `/home/zeke/.hermes/discord-bots/launcher.py`

## Templates

- `templates/bot_config.py` — drop-in config file with all defaults and the get_system_prompt() function. Copy to `~/.hermes/discord-bots/bot_config.py` and customize.

## Related Skills
- `discord-bot-model-switching` — switch models from Discord chat (!model command)
- `discord-bot-hermes-integration` — the AI integration module architecture

## Pitfalls
1. **Bot name must match**: The key in PERSONALITIES dict must exactly match BOT_NAME in the bot file
2. **Restart required**: Config changes don't hot-reload — must restart the systemd service
3. **Token != chars**: MAX_TOKENS=150 ≈ 100-200 chars depending on content
4. **System prompt cost**: Every message pays for the system prompt input tokens — keep personalities SHORT
5. **Direct API required**: Bot config feeds system prompts to the Anthropic SDK directly. Do NOT route through Hermes CLI — it injects its own identity and overrides bot character (see discord-bot-hermes-integration skill for details)
