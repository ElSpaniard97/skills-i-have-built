---
name: discord-bot-model-switching
type: guide
summary: Switch Discord bot AI models from Discord chat — supports Anthropic and OpenAI
trigger: |
  User wants Discord bots to switch between AI models (Claude, GPT, Codex).
  User wants to add a new AI provider or model to Discord bots.
  User asks about the !model command in Discord.
description: |
  All 5 Discord bots support runtime model switching via the !model command.
  Supports Anthropic (Claude) and OpenAI (GPT/Codex) providers.
  Models are defined in bot_config.py — add new ones there.
  Each bot maintains its own model state independently.
---

## Discord Commands

| Command | Effect |
|---------|--------|
| `!model` | Show current model |
| `!model list` | List all available models |
| `!model haiku` | Switch to Claude Haiku (fast, cheap) |
| `!model sonnet` | Switch to Claude Sonnet (balanced) |
| `!model opus` | Switch to Claude Opus (smartest) |
| `!model codex` | Switch to GPT-5.5 via OpenAI |
| `!model gpt4o` | Switch to GPT-4o |
| `!model o3` | Switch to OpenAI o3 (reasoning) |

For mention-only bots (Archer, Jenko, Achilles, EPSN), prefix with mention:
  `@Archer !model codex`

Spartan King responds to all messages, so just type `!model codex` directly.

## Architecture

```
bot_config.py              ← MODELS dict defines available models + providers
    ↓
hermes_integration.py      ← HermesAgent.switch_model() changes provider at runtime
    ↓                         _call_anthropic() / _call_openai() route per provider
bot files (5x)             ← handle_model_command() parses !model from Discord
```

## Adding a New Model

Edit `/home/zeke/.hermes/discord-bots/bot_config.py`, add to MODELS dict:

```python
MODELS = {
    ...
    "newmodel": ("openai", "gpt-5-turbo", "GPT-5 Turbo — description"),
}
```

Then restart: `systemctl --user restart hermes-discord-bots.service`

## Adding a New Provider

1. Add provider config to PROVIDERS dict in bot_config.py
2. Add API key to ~/.hermes/.env
3. Add a `_call_<provider>()` method to HermesAgent in hermes_integration.py
4. Update `_call_api()` routing in hermes_integration.py

## Enforce Codex Across All Bots (Persistent Default)

When the user wants all 5 bots to use Codex by default (not just per-chat runtime switches):

1) Edit `/home/zeke/.hermes/discord-bots/bot_config.py`
2) Set:
   `DEFAULT_MODEL = "codex"`
3) Restart service:
   `systemctl --user restart hermes-discord-bots.service`
4) Verify effective default in Python:

```bash
python3 - <<'PY'
import sys
sys.path.insert(0,'/home/zeke/.hermes/discord-bots')
from bot_config import get_default_model_info, DEFAULT_MODEL
print('DEFAULT_MODEL='+DEFAULT_MODEL)
print('DEFAULT_PROVIDER_MODEL='+'/'.join(get_default_model_info()))
PY
```

Expected output includes:
- `DEFAULT_MODEL=codex`
- `DEFAULT_PROVIDER_MODEL=openai/gpt-5.5`

5) Optional live Discord check:
- Spartan King: `!model`
- Mention-only bots: `@BotName !model`

## OAuth-only OpenAI setup nuance

If `OPENAI_API_KEY` is not present, these bots fall back to Hermes CLI in `hermes_integration.py` (`_call_via_hermes_cli`) and map provider `openai` → `openai-codex`. This still routes responses through Codex/OAuth, but with CLI fallback behavior.

## Notes

- Model switches are per-bot and per-process — restarting the service resets to default
- Each bot can be on a different model simultaneously
- Default model is set by DEFAULT_MODEL in bot_config.py
- OpenAI models use max_completion_tokens (not max_tokens) — handled automatically
- Some OpenAI reasoning models (o3) don't support temperature — handled with fallback

## File Locations
- Config: `/home/zeke/.hermes/discord-bots/bot_config.py`
- Integration: `/home/zeke/.hermes/discord-bots/hermes_integration.py`
- Service: `systemctl --user restart hermes-discord-bots.service`
