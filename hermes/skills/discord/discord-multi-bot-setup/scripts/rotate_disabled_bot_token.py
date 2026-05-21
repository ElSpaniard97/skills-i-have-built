#!/usr/bin/env python3
"""
Rotate a fresh token for one disabled Discord bot in the Hermes multi-bot stack.

Security model:
- Do not pass tokens as positional CLI arguments.
- Prefer --token-stdin or DISCORD_NEW_TOKEN so the token is not printed by this script.
- The script never prints the token value.

Default paths match the user's Hermes Discord multi-bot deployment.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path

DEFAULT_BOTS_DIR = Path.home() / ".hermes" / "discord-bots"
DEFAULT_PYTHON = Path.home() / ".hermes" / "hermes-agent" / "venv" / "bin" / "python3"


def load_token(args: argparse.Namespace) -> str:
    if args.token_stdin:
        token = sys.stdin.read().strip()
    else:
        token = os.environ.get("DISCORD_NEW_TOKEN", "").strip()
    if not token:
        raise SystemExit("No token supplied. Use --token-stdin or DISCORD_NEW_TOKEN.")
    return token


def verify_token(token: str) -> dict:
    req = urllib.request.Request(
        "https://discord.com/api/v10/users/@me",
        headers={
            "Authorization": f"Bot {token}",
            "User-Agent": "DiscordBot (https://hermes-agent.local, 1.0)",
            "Accept": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as response:
            data = json.loads(response.read().decode())
            if not data.get("bot"):
                raise SystemExit("Verified token, but account is not marked as bot=true.")
            return {
                "id": data.get("id"),
                "username": data.get("username"),
                "discriminator": data.get("discriminator"),
                "bot": data.get("bot"),
            }
    except urllib.error.HTTPError as exc:
        body = exc.read().decode(errors="replace") if hasattr(exc, "read") else ""
        raise SystemExit(f"Discord token verification failed: HTTP {exc.code} {body[:180]}") from exc
    except Exception as exc:
        raise SystemExit(f"Discord token verification failed: {exc}") from exc


def update_bot_script(path: Path, bot: str, token: str) -> None:
    env_name = f"{bot.upper().replace('-', '_')}_TOKEN"
    text = path.read_text()
    if env_name not in text:
        raise SystemExit(f"{env_name} marker not found in {path}")
    updated = re.sub(
        rf'os\.getenv\("{re.escape(env_name)}"\s*,\s*"[^"]*"\)',
        lambda _m: 'os.getenv(' + repr(env_name) + ', ' + repr(token) + ')',
        text,
        count=1,
    )
    if updated == text:
        updated = re.sub(
            rf'DISCORD_TOKEN\s*=\s*os\.getenv\("{re.escape(env_name)}"\)',
            lambda _m: 'DISCORD_TOKEN = os.getenv(' + repr(env_name) + ', ' + repr(token) + ')',
            text,
            count=1,
        )
    if updated == text:
        raise SystemExit(f"Could not update token source pattern in {path}")
    path.write_text(updated)


def enable_launcher_bot(path: Path, bot: str) -> None:
    text = path.read_text()
    pattern = re.compile(rf'("{re.escape(bot)}"\s*:\s*\{{.*?"enabled"\s*:\s*)False(.*?\n\s*\}},)', re.S)
    updated, count = pattern.subn(r"\1True\2", text, count=1)
    if count != 1:
        raise SystemExit(f"Could not find disabled launcher block for {bot} in {path}")
    path.write_text(updated)


def remove_disabled_status(path: Path, bot: str) -> None:
    text = path.read_text()
    match = re.search(r'DISABLED_BOTS\s*=\s*\{([^}]*)\}', text)
    if not match:
        raise SystemExit(f"DISABLED_BOTS set not found in {path}")
    names = [x.strip().strip("\"'") for x in match.group(1).split(',') if x.strip()]
    names = [x for x in names if x != bot]
    replacement = "DISABLED_BOTS = {" + ", ".join(f'"{x}"' for x in names) + "}"
    updated = text[: match.start()] + replacement + text[match.end() :]
    path.write_text(updated)


def compile_bots(python_bin: Path, bots_dir: Path) -> None:
    subprocess.run([str(python_bin), "-m", "py_compile", *map(str, bots_dir.glob("*.py"))], check=True)


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify and enable one disabled Hermes Discord bot token.")
    parser.add_argument("bot", help="Bot slug, e.g. troy, togi, harvey")
    parser.add_argument("--bots-dir", type=Path, default=DEFAULT_BOTS_DIR)
    parser.add_argument("--python", type=Path, default=DEFAULT_PYTHON)
    parser.add_argument("--token-stdin", action="store_true", help="Read the new token from stdin")
    parser.add_argument("--apply", action="store_true", help="Write file changes after verification")
    parser.add_argument("--restart", action="store_true", help="Restart hermes-discord-bots.service after applying")
    args = parser.parse_args()

    bot = args.bot.lower().replace("_", "-")
    script_name = bot.replace("-", "_") + ".py"
    bot_script = args.bots_dir / script_name
    launcher = args.bots_dir / "launcher.py"
    status = args.bots_dir / "status.py"

    for path in (bot_script, launcher, status):
        if not path.exists():
            raise SystemExit(f"Required file missing: {path}")

    token = load_token(args)
    info = verify_token(token)
    print(f"Verified {bot}: {info['username']}#{info['discriminator']} id={info['id']} bot={info['bot']}")

    if not args.apply:
        print("Dry run only. Re-run with --apply to update files.")
        return 0

    update_bot_script(bot_script, bot, token)
    enable_launcher_bot(launcher, bot)
    remove_disabled_status(status, bot)
    compile_bots(args.python, args.bots_dir)
    print(f"Updated {bot_script}, launcher.py, status.py; compile passed.")

    if args.restart:
        subprocess.run(["systemctl", "--user", "restart", "hermes-discord-bots.service"], check=True)
        print("Restarted hermes-discord-bots.service. Verify with status.py and journalctl.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
