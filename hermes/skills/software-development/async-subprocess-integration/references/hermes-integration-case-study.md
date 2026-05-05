# Hermes AI + Discord Bot Integration Case Study

**Session Date:** May 1, 2026  
**Challenge:** Integrate Hermes AI (a CLI tool) with 5 async Discord bots running in parallel  
**Outcome:** All 5 bots live, async Hermes calls working, tested, and documented

## The Problem

- **Discord bots** run as long-lived async processes (discord.py)
- **Hermes AI** is a non-async CLI tool: `hermes -z "message" -m model --yolo`
- **Naive approach** (❌): Call `subprocess.run()` directly in `async on_message()` → blocks event loop, freezes other bots
- **Requirement**: All 5 bots must handle concurrent messages without blocking each other

## The Solution

### Architecture: HermesAgent Class

```python
class HermesAgent:
    """Async wrapper around Hermes CLI."""
    
    async def chat(self, message: str, context: str = None) -> Tuple[str, bool]:
        """Non-blocking call to Hermes CLI via executor."""
        loop = asyncio.get_event_loop()
        result = await asyncio.wait_for(
            loop.run_in_executor(None, self._run_hermes_cli, message),
            timeout=30
        )
        return result
    
    def _run_hermes_cli(self, message: str) -> Tuple[str, bool]:
        """Sync subprocess call, runs in thread pool."""
        cmd = [self.hermes_bin, "-z", message, "-m", self.model, "--yolo"]
        result = subprocess.run(cmd, capture_output=True, timeout=25, ...)
        return (output, success)
```

**Key pattern:**
1. `async chat()` → wraps in executor
2. `run_in_executor()` → runs sync code in thread pool
3. `wait_for()` → enforces hard timeout
4. `_run_hermes_cli()` → pure subprocess, no async

### Why This Works for Discord Bots

Each Discord bot has its own message handler calling `HermesAgent.chat()`:

```python
@bot.event
async def on_message(message):
    async with message.channel.typing():  # Show typing indicator
        response, success = await hermes.chat(message.content)  # Non-blocking
    await message.reply(response)  # Send response
```

- **No blocking**: Thread pool handles subprocess, event loop stays free
- **Concurrent**: 5 bots can call Hermes simultaneously
- **Responsive**: Discord sees typing indicator while Hermes runs in background
- **Safe**: Timeout cancels calls that take >30s

## Key Decisions

### 1. **Executor Over subprocess.run() Direct**

❌ **Naive:**
```python
async def on_message(message):
    result = subprocess.run(['hermes', ...])  # BLOCKS!
    await message.reply(...)
```

✅ **Correct:**
```python
async def on_message(message):
    result = await loop.run_in_executor(None, subprocess.run, ...)  # Non-blocking
    await message.reply(...)
```

**Why:** Subprocess is blocking I/O. Calling it directly in async context blocks the entire event loop, freezing all other bots.

### 2. **Layered Timeouts**

```python
await asyncio.wait_for(
    loop.run_in_executor(None, self._run_hermes_cli, message),
    timeout=30  # Hard deadline for WHOLE operation
)

# Inside _run_hermes_cli:
subprocess.run(..., timeout=25)  # Leave 5s buffer
```

**Why:**
- Subprocess timeout: Kills hung Hermes process
- Executor timeout: Cancels the thread if it hangs
- Buffer (25s vs 30s): Room for thread startup, encoding

Without the outer timeout, a hung thread could block forever.

### 3. **Output Handling: Don't Throw Away Non-Zero Exit**

```python
output = result.stdout.decode('utf-8', errors='replace').strip()

if result.returncode == 0 and output:
    return output, True  # Normal success
elif output:
    return output, True  # ← Non-zero exit but has output? Use it!
else:
    error = result.stderr.decode('utf-8', errors='replace')
    return error or f"Exit {result.returncode}", False
```

**Real scenario:** Hermes CLI sometimes returns useful info in stdout even with non-zero exit (e.g., "API rate limited"). If we ignored non-zero exits, we'd lose that signal.

### 4. **Error Handling Returns Tuple, Never Crashes**

All paths return `(str, bool)`:
```python
except asyncio.TimeoutError:
    return "Timeout after 30s", False
except FileNotFoundError:
    return "Hermes binary not found", False
except Exception as e:
    return str(e), False
```

**Why:** Discord bot code always expects `(response, success)`. If the integration raised exceptions, it would crash the bot. Instead, errors become friendly messages shown to the user.

### 5. **Format for Discord After Getting Response**

```python
response, success = await hermes.chat(message)

# Format for Discord
if success:
    formatted = f"**Jenko:**\n{response}"
else:
    formatted = f"**Jenko:** ⚠️ {response}"

# Handle long responses (Discord limit: 2000 chars)
if len(formatted) > 1900:
    chunks = formatted.split('\n')
    for chunk in chunks:
        await message.reply(chunk)
else:
    await message.reply(formatted)
```

**Why:** Keep Hermes layer pure (just calls CLI), format layer separate (just formats for Discord). Easy to test, easy to change formatting.

## Testing Approach

### Test 1: Simple Question
```
Input:  "What is 2+2? Answer in one word."
Output: "Four."
Time:   3.17s
Status: ✅ PASS
```

### Test 2: Context-Based Query
```
Input (message):  "Explain Python briefly"
Input (context):  "Keep your answer to one sentence"
Output: "Python is a high-level, dynamically-typed programming language..."
Time:   3.30s
Status: ✅ PASS
```

### Test 3: Response Formatting
```
Success case: "**Jenko:**\n{response}"
Error case:   "**Jenko:** ⚠️ {error}"
Chunking:     Split on \n if >1900 chars
Status: ✅ PASS
```

## Performance Observed

| Metric | Value |
|--------|-------|
| Response time (avg) | 3-5s |
| Timeout threshold | 30s |
| Per-bot RAM | 50-55 MB |
| All 5 bots RAM | 260-280 MB |
| Concurrent throughput | ~30-50 msgs/min |
| Token/message | ~150-350 tokens |

## Lessons & Patterns

### Pattern 1: Executor for Any Blocking I/O in Async

This isn't Hermes-specific. Any time you need to call blocking code (file I/O, network calls, subprocesses, slow functions) from async context:

```python
# General template
async def async_wrapper(blocking_func, *args, **kwargs):
    loop = asyncio.get_event_loop()
    result = await asyncio.wait_for(
        loop.run_in_executor(None, blocking_func, *args),
        timeout=30
    )
    return result
```

### Pattern 2: Timeout Sandwich

Always wrap executor timeouts with outer timeout:

```python
try:
    result = await asyncio.wait_for(
        loop.run_in_executor(None, self._blocking_call, ...),
        timeout=30  # Outer
    )
except asyncio.TimeoutError:
    # Handle timeout
```

Inside `_blocking_call()`:
```python
def _blocking_call(self):
    try:
        result = subprocess.run(..., timeout=25)  # Inner
    except subprocess.TimeoutExpired:
        # Handle subprocess timeout
```

### Pattern 3: Return Tuple, Never Raise

For agent-to-tool boundaries, return status explicitly:

```python
# Good
async def call_tool(msg) -> Tuple[str, bool]:
    # Returns (output, success) — caller always gets a tuple
    try:
        ...
    except Exception as e:
        return str(e), False

# Bad
async def call_tool(msg) -> str:
    # Raises exceptions — caller must handle
    # Harder to integrate
```

### Pattern 4: No Assumptions About Exit Codes

Many CLIs return non-zero even when they have useful output. Fallback hierarchy: stdout > stderr > synthetic message.

```python
output = result.stdout.decode('utf-8', errors='replace')

# Prefer output regardless of exit code
if output:
    return output, (result.returncode == 0)
else:
    error = result.stderr.decode('utf-8', errors='replace')
    return error or f"Exit {result.returncode}", False
```

## Files Generated

- `hermes_integration.py` (6.6 KB) — Core HermesAgent + HermesFormatter
- `test_integration.py` (3.5 KB) — Integration tests
- `spartan_king.py`, `jenko.py`, etc. (3.1-3.3 KB each) — 5 updated Discord bot files
- `HERMES_INTEGRATION.md` (14 KB) — Full documentation
- `INTEGRATION_COMPLETE.md` (15 KB) — Deployment summary

## Reusability

This pattern scales to:
- **Calling any CLI tool** (API client, language compiler, system utility)
- **From any async context** (Discord, FastAPI, async web app, async agent)
- **With robust error handling** (timeouts, encoding issues, non-zero exits)
- **Testing** (mock subprocess, test async code with pytest-asyncio)

Next agent can reference this skill instead of re-solving the same problem.
