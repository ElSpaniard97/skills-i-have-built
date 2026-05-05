---
name: async-subprocess-integration
title: Async Subprocess Integration Pattern
description: Call external CLI tools from async Python code reliably with timeouts, error handling, and output formatting.
summary: |
  Call external CLI tools from async Python code reliably. Covers subprocess
  communication in asyncio, error handling, timeouts, output formatting, and
  testing patterns for agent-to-tool workflows.
trigger: |
  • Need to invoke an external CLI (API client, language tool, system utility)
    from async Python code
  • Building a stateless agent that delegates work to subprocess commands
  • Integrating non-async tools into an async application
  • Handling subprocess timeouts, error codes, and stderr gracefully
  • Testing subprocess communication in async context
prerequisites:
  - Python 3.8+ with asyncio
  - subprocess module familiarity (sync version)
  - Understanding of asyncio event loop and executor pattern
difficulty: intermediate
time_estimate: 30-45 min to implement
---

## Quick Start

```python
import subprocess
import asyncio
from typing import Tuple

class ExternalTool:
    def __init__(self, binary_path: str, timeout: int = 30):
        self.binary_path = binary_path
        self.timeout = timeout
    
    async def call(self, args: list, input_text: str = "") -> Tuple[str, bool]:
        """Call external tool asynchronously.
        
        Returns: (output, success)
        """
        try:
            loop = asyncio.get_event_loop()
            result = await asyncio.wait_for(
                loop.run_in_executor(
                    None,
                    self._run_sync,
                    args,
                    input_text
                ),
                timeout=self.timeout
            )
            return result
        except asyncio.TimeoutError:
            return f"Timeout after {self.timeout}s", False
        except Exception as e:
            return str(e), False
    
    @staticmethod
    def _run_sync(args: list, input_text: str) -> Tuple[str, bool]:
        try:
            result = subprocess.run(
                args,
                input=input_text.encode('utf-8') if input_text else None,
                capture_output=True,
                timeout=25,  # Leave buffer for overall timeout
                check=False,
                text=False
            )
            output = result.stdout.decode('utf-8', errors='replace').strip()
            if result.returncode == 0 and output:
                return output, True
            elif output:
                return output, True  # Use output even if non-zero exit
            else:
                error = result.stderr.decode('utf-8', errors='replace')
                return error or f"Exit code {result.returncode}", False
        except subprocess.TimeoutExpired:
            return "Subprocess timed out", False
        except Exception as e:
            return str(e), False
```

## Pattern Explanation

### 1. **Async Wrapper + Executor Pattern**

```python
loop = asyncio.get_event_loop()
result = await asyncio.wait_for(
    loop.run_in_executor(
        None,  # Use default ThreadPoolExecutor
        self._run_sync,  # Sync function to run in thread
        args,
        input_text
    ),
    timeout=self.timeout  # Total timeout includes execution
)
```

**Why this works:**
- `run_in_executor()` runs the sync subprocess call in a thread pool, preventing event loop blocking
- `wait_for()` enforces a hard timeout on the entire operation
- Separation of `_run_sync()` (sync/subprocess) from `async call()` (async wrapper) keeps concerns clean

**Key insight:** Never call `subprocess.run()` directly in async context—it blocks the event loop. Always use executor.

### 2. **Timeout Layering**

```python
loop.run_in_executor(None, self._run_sync, ...)  # Will take up to timeout
timeout=self.timeout  # Hard deadline for the whole operation
```

Inside `_run_sync()`:
```python
subprocess.run(..., timeout=25)  # Leave 5s buffer for overhead
```

**Why three timeouts:**
- Subprocess timeout: Kills the tool if it hangs
- Executor timeout: Kills the thread if executor is slow
- Overall timeout: Cancels the whole call if deadline is reached
- Buffer (25s vs 30s): Room for thread scheduling, encoding

### 3. **Output Handling (No Assumptions)**

```python
output = result.stdout.decode('utf-8', errors='replace').strip()

if result.returncode == 0 and output:
    return output, True  # Normal success
elif output:
    return output, True  # Non-zero exit but we have output—use it
else:
    error = result.stderr.decode('utf-8', errors='replace')
    return error or f"Exit code {result.returncode}", False  # No output, use stderr
```

**Principle:** Never throw away output just because the exit code was non-zero. External tools often return error info in stdout (e.g., some CLIs return helpful messages with exit 1). Fallback hierarchy is: stdout > stderr > synthetic error message.

### 4. **Error Resilience**

All exceptions caught and returned as `(error_message, False)`. No crashes, no unhandled exceptions propagating up. Caller always gets `(str, bool)` tuple.

```python
except asyncio.TimeoutError:
    return f"Timeout after {self.timeout}s", False
except FileNotFoundError:
    return f"Binary not found at {self.binary_path}", False
except Exception as e:
    return str(e), False
```

---

## Real-World Example: Hermes AI Integration

See `references/hermes-integration-case-study.md` for the full session's integration pattern.

**Core pattern (from the Discord bot integration):**

```python
class HermesAgent:
    """Interface to external Hermes CLI tool."""
    
    def __init__(self, model: str = "claude-haiku-4-5-20251001", timeout: int = 30):
        self.model = model
        self.timeout = timeout
        self.hermes_bin = "/home/zeke/.hermes/hermes-agent/venv/bin/hermes"
    
    async def chat(self, message: str, context: Optional[str] = None) 
                   -> Tuple[str, bool]:
        """Send message to Hermes CLI, get AI response."""
        try:
            if context:
                full_message = f"{context}\n\n{message}"
            else:
                full_message = message
            
            loop = asyncio.get_event_loop()
            result = await asyncio.wait_for(
                loop.run_in_executor(
                    None,
                    self._run_hermes_cli,
                    full_message
                ),
                timeout=self.timeout
            )
            
            response_text, success = result
            
            if success and len(response_text) > 1800:
                response_text = response_text[:1800] + "\n... (truncated)"
            
            return response_text, success
                
        except asyncio.TimeoutError:
            return f"Timeout after {self.timeout}s", False
        except Exception as e:
            return f"Error: {str(e)[:100]}", False
    
    def _run_hermes_cli(self, message: str) -> Tuple[str, bool]:
        """Sync wrapper: actual subprocess call."""
        try:
            cmd = [
                self.hermes_bin,
                "-z", message,
                "-m", self.model,
                "--yolo"  # Skip confirmations for non-interactive use
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                timeout=25,
                check=False,
                text=False
            )
            
            response = result.stdout.decode('utf-8', errors='replace').strip()
            
            if result.returncode == 0 and response:
                return response, True
            elif response:
                return response, True
            else:
                error = result.stderr.decode('utf-8', errors='replace').strip()
                return error or f"Exit {result.returncode}", False
                
        except subprocess.TimeoutExpired:
            return "Subprocess timed out", False
        except FileNotFoundError:
            return f"Binary not found at {self.hermes_bin}", False
        except Exception as e:
            return str(e), False
```

---

## Testing Pattern

### Unit Test (Sync, Mocked)

```python
import unittest
from unittest.mock import patch

class TestExternalTool(unittest.TestCase):
    def test_successful_call(self):
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = subprocess.CompletedProcess(
                args=['echo', 'hello'],
                returncode=0,
                stdout=b'hello',
                stderr=b''
            )
            
            tool = ExternalTool('/bin/echo')
            output, success = tool._run_sync(['echo', 'hello'], '')
            
            assert success
            assert output == 'hello'
    
    def test_nonzero_exit_with_output(self):
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = subprocess.CompletedProcess(
                args=['tool'],
                returncode=1,
                stdout=b'helpful error message',
                stderr=b''
            )
            
            tool = ExternalTool('/bin/tool')
            output, success = tool._run_sync(['tool'], '')
            
            # Non-zero but has output -> use output, mark success
            assert success
            assert output == 'helpful error message'
```

---

## Pitfalls

### 1. **Calling subprocess.run() directly in async context**

❌ **WRONG:**
```python
async def bad_call(self, msg):
    result = subprocess.run(...)  # BLOCKS EVENT LOOP!
    return result
```

✅ **RIGHT:**
```python
async def good_call(self, msg):
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(None, self._run_sync, ...)
```

### 2. **Ignoring output when exit code is non-zero**

❌ **WRONG:**
```python
if result.returncode == 0:
    return result.stdout  # Throw away error messages!
else:
    return "Failed"
```

✅ **RIGHT:**
```python
output = result.stdout.decode(...)
if result.returncode == 0 and output:
    return output, True
elif output:
    return output, True  # Use it even if non-zero
else:
    error = result.stderr.decode(...)
    return error or f"Exit {result.returncode}", False
```

### 3. **Single timeout value**

❌ **WRONG:** Set only subprocess timeout without executor timeout wrapper.

✅ **RIGHT:** Use both subprocess timeout (25s) and executor timeout (30s) with buffer.

### 4. **Forgetting error handling on decode**

❌ **WRONG:** `output = result.stdout.decode('utf-8')` crashes on bad encoding.

✅ **RIGHT:** `output = result.stdout.decode('utf-8', errors='replace')`

---

## Configuration & Customization

### Dynamic Binary Path

```python
if binary_path is None:
    binary_path = shutil.which("mytool")
if not binary_path:
    raise FileNotFoundError("Binary 'mytool' not found in PATH")
```

### Retry Logic

```python
async def call_with_retry(self, message: str, retries: int = 3):
    for attempt in range(retries):
        output, success = await self.call(message)
        if success:
            return output, True
        await asyncio.sleep(2 ** attempt)  # Exponential backoff
    return output, False
```

---

## Related Skills

- **debugging-hermes-tui-commands**: Debugging subprocess-based tools
- **systematic-debugging**: Root cause analysis for subprocess failures
- **local-file-ops**: File I/O patterns paired with subprocess workflows

## References

- `references/hermes-integration-case-study.md` — Real-world Hermes AI + Discord bot example
- Python asyncio: https://docs.python.org/3/library/asyncio.html#executor
- subprocess: https://docs.python.org/3/library/subprocess.html
