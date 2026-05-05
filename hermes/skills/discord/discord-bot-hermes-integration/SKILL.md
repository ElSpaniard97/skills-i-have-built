---
name: discord-bot-hermes-integration
type: guide
summary: Integrate AI into Discord bots via direct Anthropic SDK (system prompt for character identity)
trigger: |
  User wants Discord bots to respond with AI-generated replies.
  User is building multi-bot systems where each bot runs independently.
  User needs response formatting, chunking, error handling for Discord limits.
  Bot is breaking character or responding as "Claude Code" instead of its persona.
description: |
  Provides a reusable HermesAgent class that calls the Anthropic API directly
  with a proper system prompt for reliable character identity. Includes
  response formatting, message chunking (Discord 2000-char limit), timeout
  management, and graceful error handling. Works for both single-bot and
  multi-bot (independent process) architectures.

  IMPORTANT: Uses direct Anthropic SDK, NOT Hermes CLI subprocess. The CLI
  approach was abandoned because Hermes injects its own identity (Claude Code
  persona, memory, SOUL.md, AGENTS.md) which overrides bot character even
  with --ignore-rules. Direct API with system= parameter is the only reliable
  way to maintain bot identity.
---

## Integration Overview

### Architecture
- **HermesAgent**: async wrapper calling Anthropic API directly via Python SDK
- **HermesFormatter**: Discord-specific response formatting and chunking
- **Direct API model**: Each `hermes.chat()` calls `anthropic.Anthropic().messages.create()` in an executor
- **System prompt**: Bot personality is sent as `system=` parameter (highest authority for identity)
- **Timeout**: 30s default (configurable per bot)
- **Response limit**: 1800 chars per message (reserves 200 for formatting, stays under Discord's 2000-char hard limit)

### Why Direct API Instead of Hermes CLI?
The Hermes CLI (`hermes -z`) injects its own identity at the system level:
- System prompt: "You are Claude Code, Anthropic's CLI agent"
- SOUL.md persona file
- AGENTS.md from CWD
- Persistent memory
- Preloaded skills

Even with `--ignore-rules`, the model intermittently breaks character (especially after
multiple messages). The CLI's `-z` flag sends everything as a user message, which is
lower priority than the system prompt. Direct API with `system=` is the only reliable
approach for maintaining bot identity.

### API Key Loading
The integration reads `ANTHROPIC_API_KEY` from the environment or from `~/.hermes/.env`.
No separate config needed — it piggybacks on the existing Hermes API key.

## Implementation

### HermesAgent Class

```python
import logging
import asyncio
import os
from typing import Optional, Tuple

logger = logging.getLogger("HermesIntegration")

# Load API key from hermes .env or environment
_API_KEY = os.environ.get("ANTHROPIC_API_KEY")
if not _API_KEY:
    _env_path = os.path.expanduser("~/.hermes/.env")
    if os.path.exists(_env_path):
        with open(_env_path) as f:
            for line in f:
                line = line.strip()
                if line.startswith("ANTHROPIC_API_KEY=") and not line.startswith("#"):
                    _API_KEY = line.split("=", 1)[1].strip()
                    break

class HermesAgent:
    """Interface to AI via Anthropic API directly (bypasses Hermes CLI identity)."""

    def __init__(self, model: str = "claude-haiku-4-5-20251001", timeout: int = 30):
        self.model = model
        self.timeout = timeout
        self._client = None

    def _get_client(self):
        """Lazy-init the Anthropic client."""
        if self._client is None:
            import anthropic
            self._client = anthropic.Anthropic(api_key=_API_KEY)
        return self._client

    async def chat(
        self,
        message: str,
        context: Optional[str] = None,
    ) -> Tuple[str, bool]:
        """
        Send message to AI with a proper system prompt for character identity.

        Args:
            message: User message content
            context: System prompt defining the bot's character/identity

        Returns:
            (response_text, success_bool)
        """
        try:
            loop = asyncio.get_event_loop()
            result = await asyncio.wait_for(
                loop.run_in_executor(None, self._call_api, message, context),
                timeout=self.timeout,
            )
            response_text, success = result
            if success and len(response_text) > 1800:
                response_text = response_text[:1800] + "\n... (truncated)"
            return response_text, success
        except asyncio.TimeoutError:
            return f"⏱️ AI timeout (>{self.timeout}s)", False
        except Exception as e:
            return f"❌ Error: {str(e)[:100]}", False

    def _call_api(self, message: str, system_prompt: Optional[str] = None) -> Tuple[str, bool]:
        """Synchronous Anthropic API call (runs in executor)."""
        try:
            client = self._get_client()
            kwargs = {
                "model": self.model,
                "max_tokens": 1024,
                "messages": [{"role": "user", "content": message}],
            }
            if system_prompt:
                kwargs["system"] = system_prompt

            response = client.messages.create(**kwargs)
            text = response.content[0].text.strip() if response.content else ""
            return (text, True) if text else ("No response generated", False)
        except Exception as e:
            logger.error(f"API call error: {e}")
            return str(e)[:200], False
```

### HermesFormatter Class

```python
class HermesFormatter:
    """Format and chunk Hermes responses for Discord."""
    
    @staticmethod
    def format_response(bot_name: str, response: str, success: bool) -> str:
        """Format response with bot name prefix."""
        if success:
            return f"**{bot_name}:**\n{response}"
        else:
            return f"**{bot_name}:** ⚠️ {response}"
    
    @staticmethod
    def chunk_response(response: str, max_chunk: int = 1900) -> list:
        """Split long responses into Discord message chunks."""
        if len(response) <= max_chunk:
            return [response]
        
        chunks = []
        current = ""
        
        for line in response.split('\n'):
            if len(current) + len(line) + 1 > max_chunk:
                if current:
                    chunks.append(current)
                current = line
            else:
                current += '\n' + line if current else line
        
        if current:
            chunks.append(current)
        
        return chunks
```

### Example: Using in a discord.py Bot

```python
import discord
from discord.ext import commands
from hermes_integration import HermesAgent, HermesFormatter

BOT_NAME = "Spartan King"
BOT_PERSONALITY = (
    f"You are {BOT_NAME}, a bold and confident warrior-king Discord bot. "
    f"You speak with authority, camaraderie, and the spirit of a Spartan leader. "
    f"Keep responses concise and natural for Discord chat. "
    f"NEVER mention Claude, Anthropic, AI, language models, Hermes, or any infrastructure. "
    f"You ARE {BOT_NAME}. Respond naturally as this character would."
)

bot = commands.Bot(intents=discord.Intents.default())
hermes = HermesAgent(timeout=30)

@bot.event
async def on_message(message: discord.Message):
    if message.author == bot.user or message.author.bot:
        return
    
    try:
        async with message.channel.typing():
            response, success = await hermes.chat(
                message=message.content,
                context=BOT_PERSONALITY,  # Sent as system= parameter to API
            )
        
        formatted = HermesFormatter.format_response(BOT_NAME, response, success)
        chunks = HermesFormatter.chunk_response(formatted)
        
        for chunk in chunks:
            await message.reply(chunk, mention_author=False)
            
    except Exception as e:
        await message.reply(f"❌ Error: {str(e)[:100]}", mention_author=False)
```

## Configuration

### Default Settings
- **Model**: `claude-haiku-4-5-20251001` (fast, efficient)
- **Timeout**: 30 seconds
- **Max response**: 1800 chars (accounts for formatting overhead)
- **Chunking**: Auto-split if >1900 chars

### Customization
```python
# Faster but less capable
hermes = HermesAgent(model="claude-haiku-4-5-20251001", timeout=20)

# Slower but more capable
hermes = HermesAgent(model="claude-opus-4-6", timeout=60)

# Custom system prompt
response, success = await hermes.chat(
    message="What's Python?",
    context="You are a tutor. Explain simply."
)
```

## OAuth-Only Mode Compatibility (May 2026 update)

When the user switches Hermes providers (Claude/Codex) from API keys to OAuth, direct SDK calls in this integration fail unless provider API keys are still present in environment/.env.

Observed behavior in this environment:
- `ANTHROPIC_API_KEY` missing + direct Anthropic SDK call => auth resolution failure
- Anthropic OAuth token from `~/.hermes/auth.json` is not accepted by Anthropic SDK for messages API (`OAuth authentication is currently not supported`)
- `hermes chat --provider anthropic` may fail with 429 usage-tier limits in some setups (`Extra usage is required for long context requests`)
- `hermes chat --provider openai-codex -m gpt-5.5` works in OAuth mode

Recommended resilient pattern:
1. Keep direct SDK path for API-key setups (fastest, strongest persona control).
2. If provider API key is missing, automatically fallback to Hermes CLI:
   - `hermes chat -Q -q <prompt> --provider <provider> -m <model>`
   - map OpenAI provider name `openai` -> CLI provider `openai-codex`
3. Use a larger timeout for fallback path (45s minimum) to account for CLI startup/retries.
4. For OAuth-only deployments, set default model to a known-working OAuth route (e.g., Codex `gpt-5.5`) unless Anthropic key is restored.

Tradeoff:
- CLI fallback is more robust for OAuth-only credentials, but character fidelity can be weaker than direct SDK `system=` control.

## Critical Gotchas

### 1. Discord Bot Token Validation (BLOCKER)
**Symptom**: Bot crashes on startup with no on_ready/on_message calls.
**Root cause**: Invalid or expired Discord bot token.
**Diagnosis**: Test token directly — don't just check string length:
```python
import discord, asyncio
async def test_token(token):
    client = discord.Client(intents=discord.Intents.default())
    try:
        await client.login(token)
        print(f"OK: {client.user}")
        await client.close()
    except discord.LoginFailure as e:
        print(f"FAILED: {e}")
asyncio.run(test_token("YOUR_TOKEN"))
```
**Fix**: Regenerate token at https://discord.com/developers/applications

### 2. Identity Bleed — Bot Responds as "Claude Code" (CRITICAL)
**Symptom**: Bot replies with "I'm Claude Code, Anthropic's CLI agent" or meta-commentary.
**Root cause progression** (discovered May 2026):
- **Attempt 1 — `--ignore-rules` on CLI**: Strips persona/memory/skills but model STILL
  breaks character intermittently (especially after multiple messages), because `-z` sends
  context as a user message, not a system prompt. The model treats its built-in training
  identity as higher priority than user-level instructions.
- **Attempt 2 (working fix) — Direct Anthropic SDK**: Call `client.messages.create()` with
  `system=BOT_PERSONALITY`. The system parameter is the highest-authority identity instruction.
  No CLI middleware, no competing identity injections.

**Key lesson**: For character bots, you MUST control the system prompt directly. Any CLI
wrapper that injects its own system prompt will cause identity conflicts.

### 3. Anthropic API Key Loading
**Symptom**: "Authentication error" or empty responses.
**Root cause**: API key not found in environment or `~/.hermes/.env`.
**Fix**: Ensure `ANTHROPIC_API_KEY=sk-ant-...` exists in `~/.hermes/.env` or is exported.

### 4. Async/Await Timing
**Symptom**: Message replies appear out of order or timeout.
**Root cause**: Not awaiting the API call or wrapping in asyncio.wait_for.
**Fix**: Always use `await asyncio.wait_for(executor(...), timeout=...)`.

### 5. Discord's 2000-Char Limit
**Symptom**: Long responses silently fail to send.
**Root cause**: Exceeding Discord's hard 2000-char message limit.
**Fix**: Use HermesFormatter.chunk_response() to split long responses.

### 6. User= in User-Level systemd Services
**Symptom**: Service exits immediately with code 216/GROUP, crash-loops.
**Root cause**: `User=zeke` in `~/.config/systemd/user/*.service` is invalid —
user-level services already run as the owning user.
**Fix**: Remove the `User=` line. Only use `User=` in system-level services under `/etc/systemd/system/`.

## Testing

```python
# Test integration standalone
import asyncio
from hermes_integration import HermesAgent, HermesFormatter

async def test():
    agent = HermesAgent()
    response, success = await agent.chat("What is 2+2?")
    print(f"Success: {success}, Response: {response}")
    
    formatted = HermesFormatter.format_response("TestBot", response, success)
    chunks = HermesFormatter.chunk_response(formatted)
    print(f"Chunks: {len(chunks)}")

asyncio.run(test())
```

## Performance Notes

- **Response time**: 2-5s average (Haiku), 5-10s for complex reasoning
- **Timeout**: 30s is safe buffer; most responses complete in <10s
- **Parallelism**: Each bot can call Hermes independently (subprocess-per-call scales)
- **Token cost**: ~100-200 input + 50-150 output per message
- **Resource**: ~50-55 MB per discord.py bot process; Hermes subprocess adds ~100-150 MB temporarily

## Related Skills
- `discord-multi-bot-setup` — deploying multiple independent discord.py bots
- `discord-server-management` — managing channels, permissions
- `native-mcp` — if you want to use MCP servers instead of CLI subprocess
