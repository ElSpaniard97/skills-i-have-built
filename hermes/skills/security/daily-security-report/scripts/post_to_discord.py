#!/usr/bin/env python3
import json, os, sys
import urllib.request
from pathlib import Path

THREAD_ID = "1498647342142722198"
OUT = Path.home() / ".hermes" / "security-reports"

def post_json(url, payload, headers):
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json", **headers}, method="POST")
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read()

def main():
    parts_file = OUT / "latest.parts.json"
    md_file = OUT / "latest.md"
    if parts_file.exists():
        parts = json.loads(parts_file.read_text())
    elif md_file.exists():
        parts = [md_file.read_text()]
    else:
        return 0
    bot = os.environ.get("DISCORD_BOT_TOKEN")
    webhook = os.environ.get("DISCORD_WEBHOOK_URL")
    if bot:
        url = f"https://discord.com/api/v10/channels/{THREAD_ID}/messages"
        for part in parts:
            post_json(url, {"content": part}, {"Authorization": f"Bot {bot}"})
    elif webhook:
        for part in parts:
            post_json(webhook, {"content": part}, {})
    return 0

if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"Discord post failed: {exc}", file=sys.stderr)
        raise SystemExit(0)
