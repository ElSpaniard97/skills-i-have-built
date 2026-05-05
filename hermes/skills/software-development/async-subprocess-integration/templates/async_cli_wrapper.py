"""
Template: Async CLI Tool Wrapper
Copy this and customize BINARY_PATH, ARGS_BUILDER, and OUTPUT_PARSER.
"""

import subprocess
import asyncio
import logging
from typing import Tuple, Optional

logger = logging.getLogger("CLIWrapper")


class AsyncCLIWrapper:
    """
    Async wrapper for any external CLI tool.
    
    Customize:
    1. __init__: Set BINARY_PATH, default arguments
    2. _build_args(): Create command-line arguments from parameters
    3. _parse_output(): Extract meaningful result from stdout
    """
    
    def __init__(self, binary_path: str, timeout: int = 30):
        """
        Initialize the CLI wrapper.
        
        Args:
            binary_path: Full path to the executable (e.g., /usr/bin/mytool)
            timeout: Max seconds to wait for the tool (includes all overhead)
        """
        self.binary_path = binary_path
        self.timeout = timeout
        
        # Verify binary exists
        try:
            subprocess.run(
                [self.binary_path, "--version"],
                capture_output=True,
                timeout=5
            )
        except (FileNotFoundError, subprocess.TimeoutExpired) as e:
            logger.warning(f"Binary may not be available: {e}")
    
    async def call(self, *args, **kwargs) -> Tuple[str, bool]:
        """
        Call the CLI tool asynchronously.
        
        Returns: (output_string, success_bool)
        """
        try:
            loop = asyncio.get_event_loop()
            result = await asyncio.wait_for(
                loop.run_in_executor(
                    None,
                    self._run_sync,
                    args,
                    kwargs
                ),
                timeout=self.timeout
            )
            return result
        except asyncio.TimeoutError:
            logger.error(f"Timeout after {self.timeout}s")
            return f"Timeout after {self.timeout}s", False
        except Exception as e:
            logger.error(f"Call failed: {e}")
            return str(e), False
    
    def _run_sync(self, args: tuple, kwargs: dict) -> Tuple[str, bool]:
        """
        Synchronous subprocess call (runs in thread pool).
        """
        try:
            # Build command line
            cmd = self._build_args(*args, **kwargs)
            
            logger.debug(f"Running: {' '.join(cmd[:3])}...")
            
            # Run subprocess with timeout (leave 5s buffer for wrapper)
            result = subprocess.run(
                cmd,
                capture_output=True,
                timeout=self.timeout - 5,
                check=False,
                text=False
            )
            
            # Decode output
            output = result.stdout.decode('utf-8', errors='replace').strip()
            
            # Parse and return
            if result.returncode == 0 and output:
                return output, True
            elif output:
                # Non-zero exit but has output—use it
                logger.warning(f"Non-zero exit ({result.returncode}) but has output")
                return output, True
            else:
                # No output, try stderr
                error = result.stderr.decode('utf-8', errors='replace').strip()
                return error or f"Exit code {result.returncode}", False
                
        except subprocess.TimeoutExpired:
            logger.error("Subprocess timed out")
            return "Subprocess timed out", False
        except FileNotFoundError:
            logger.error(f"Binary not found: {self.binary_path}")
            return f"Binary not found: {self.binary_path}", False
        except Exception as e:
            logger.error(f"Subprocess error: {e}")
            return str(e), False
    
    def _build_args(self, *args, **kwargs) -> list:
        """
        Build the command-line arguments.
        
        CUSTOMIZE THIS for your tool.
        
        Example:
            ["mytool", "--input", input_text, "--format", "json"]
        """
        raise NotImplementedError("Subclass must implement _build_args")


# Example: Hermes AI Implementation
class HermesAgent(AsyncCLIWrapper):
    """Async wrapper for Hermes CLI."""
    
    def __init__(self, hermes_bin: str = None, model: str = "claude-haiku-4-5-20251001", timeout: int = 30):
        if hermes_bin is None:
            hermes_bin = "/home/zeke/.hermes/hermes-agent/venv/bin/hermes"
        super().__init__(hermes_bin, timeout)
        self.model = model
    
    async def chat(self, message: str, context: str = None) -> Tuple[str, bool]:
        """
        Send a message to Hermes AI.
        
        Args:
            message: User message
            context: Optional system/context prompt
            
        Returns: (response, success)
        """
        if context:
            full_message = f"{context}\n\n{message}"
        else:
            full_message = message
        
        return await self.call(full_message)
    
    def _build_args(self, message: str = "", **kwargs) -> list:
        """Build hermes CLI command."""
        return [
            self.binary_path,
            "-z", message,
            "-m", self.model,
            "--yolo"  # Skip confirmations
        ]


# Example: Generic JSON API Tool
class JSONAPITool(AsyncCLIWrapper):
    """Async wrapper for a CLI that takes JSON input and outputs JSON."""
    
    async def call_json(self, request: dict) -> Tuple[dict, bool]:
        """Call tool with JSON, get JSON response."""
        import json
        response_str, success = await self.call(json.dumps(request))
        
        if not success:
            return {}, False
        
        try:
            data = json.loads(response_str)
            return data, True
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON response: {response_str[:100]}")
            return {}, False
    
    def _build_args(self, json_input: str = "", **kwargs) -> list:
        """Build command with JSON input."""
        return [self.binary_path, "--json"]  # Tool reads stdin for JSON


# Example: File Processing Tool
class FileProcessorTool(AsyncCLIWrapper):
    """Async wrapper for a tool that processes files."""
    
    async def process_file(self, input_file: str, output_format: str = "text") -> Tuple[str, bool]:
        """Process a file and return output."""
        return await self.call(input_file, output_format)
    
    def _build_args(self, input_file: str = "", output_format: str = "text", **kwargs) -> list:
        """Build command for file processing."""
        return [
            self.binary_path,
            "--input", input_file,
            "--format", output_format
        ]


if __name__ == "__main__":
    # Quick test
    import asyncio
    
    async def test():
        # Test with hermes (requires hermes installed)
        agent = HermesAgent()
        
        response, success = await agent.chat(
            "What is 2+2? Answer in one word."
        )
        
        print(f"Success: {success}")
        print(f"Response: {response}")
    
    asyncio.run(test())
