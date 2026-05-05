#!/usr/bin/env python3
"""
Hermes AI Integration Module
Provides async interface for Discord bots to communicate with Hermes AI
Copy this file to your discord-bots directory and import as:
  from hermes_integration import HermesAgent, HermesFormatter
"""

import subprocess
import logging
import asyncio
from typing import Optional, Tuple

logger = logging.getLogger("HermesIntegration")


class HermesAgent:
    """Interface to Hermes AI agent via CLI subprocess"""
    
    def __init__(self, model: str = "claude-haiku-4-5-20251001", timeout: int = 30):
        """
        Initialize Hermes agent
        
        Args:
            model: Hermes model to use (default: claude-haiku-4-5-20251001 for speed)
            timeout: Response timeout in seconds
        """
        self.model = model
        self.timeout = timeout
        self.hermes_bin = "/home/zeke/.hermes/hermes-agent/venv/bin/hermes"
    
    async def chat(
        self, 
        message: str, 
        context: Optional[str] = None
    ) -> Tuple[str, bool]:
        """
        Send a message to Hermes AI and get a response
        
        Args:
            message: User message content
            context: Optional context/system prompt
            
        Returns:
            Tuple of (response_text, success_bool)
            - response_text: AI response (truncated to 1800 chars for Discord)
            - success_bool: True if request succeeded, False on error
        """
        try:
            # Combine context and message
            if context:
                full_message = f"{context}\n\n{message}"
            else:
                full_message = message
            
            logger.debug(f"Sending to Hermes: {full_message[:100]}...")
            
            # Run hermes in subprocess via executor
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
            
            if success:
                # Truncate to Discord message limit (2000 chars)
                if len(response_text) > 1800:
                    response_text = response_text[:1800] + "\n... (truncated)"
                
                logger.info(f"Hermes response: {len(response_text)} chars")
                return response_text, True
            else:
                logger.warning(f"Hermes error: {response_text}")
                return "❌ Error getting response from AI", False
                
        except asyncio.TimeoutError:
            logger.error(f"Hermes timeout after {self.timeout}s")
            return f"⏱️ AI took too long to respond (>{self.timeout}s timeout)", False
        except Exception as e:
            logger.error(f"Hermes integration error: {e}")
            return f"❌ Error: {str(e)[:100]}", False
    
    def _run_hermes_cli(self, message: str) -> Tuple[str, bool]:
        """
        Synchronous wrapper to execute hermes command (runs in executor)
        
        Args:
            message: Message content to pass to hermes
            
        Returns:
            Tuple of (response, success)
        """
        try:
            # Use hermes CLI with -z for direct prompt/response
            cmd = [
                self.hermes_bin,
                "-z", message,
                "-m", self.model,
                "--yolo",  # Skip confirmations for non-interactive use
            ]
            
            logger.debug(f"Running: {cmd[0]} -z ... -m {self.model}")
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                timeout=25,  # Leave 5s buffer for executor overhead
                check=False,
                text=False  # Get bytes, decode with error handling
            )
            
            # Always check stdout first, regardless of exit code
            response = result.stdout.decode('utf-8', errors='replace').strip()
            
            if result.returncode == 0 and response:
                return response, True
            elif response:
                # Even if exit code wasn't 0, if we got output use it
                logger.warning(f"Hermes returned non-zero exit code {result.returncode}")
                return response, True
            else:
                # No output, use stderr or generic error
                error = result.stderr.decode('utf-8', errors='replace').strip()
                if not error:
                    error = f"No response (exit code {result.returncode})"
                return error, False
                
        except subprocess.TimeoutExpired:
            logger.error(f"Hermes command timed out")
            return "Hermes timed out", False
        except FileNotFoundError:
            logger.error(f"Hermes binary not found at {self.hermes_bin}")
            return "Hermes binary not found", False
        except Exception as e:
            logger.error(f"Error running Hermes: {e}")
            return str(e), False


class HermesFormatter:
    """Format Hermes responses for Discord"""
    
    @staticmethod
    def format_response(
        bot_name: str,
        response: str,
        success: bool
    ) -> str:
        """
        Format a Hermes response for Discord display
        
        Args:
            bot_name: Name of the responding bot
            response: Response text from Hermes
            success: Whether the request was successful
            
        Returns:
            Formatted Discord message
        """
        if success:
            return f"**{bot_name}:**\n{response}"
        else:
            return f"**{bot_name}:** ⚠️ {response}"
    
    @staticmethod
    def chunk_response(response: str, max_chunk: int = 1900) -> list:
        """
        Split long responses into Discord message chunks
        
        Args:
            response: Response text
            max_chunk: Max chars per chunk (default 1900 leaves room for formatting)
            
        Returns:
            List of message chunks
        """
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


# Export public API
__all__ = ['HermesAgent', 'HermesFormatter']
