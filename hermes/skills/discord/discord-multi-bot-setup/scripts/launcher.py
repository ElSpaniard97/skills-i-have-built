#!/usr/bin/env python3
"""Discord Multi-Bot Launcher
Manages 5+ independent Discord bot processes with auto-restart on crash.
Logs all activity to launcher.log.
"""

import subprocess
import time
import signal
import sys
import os

VENV_PYTHON = "/home/zeke/.hermes/hermes-agent/venv/bin/python3"
BOT_DIR = "/home/zeke/.hermes/discord-bots"
LOG_FILE = f"{BOT_DIR}/launcher.log"

BOTS = [
    {"script": "spartan_king.py", "name": "Spartan King"},
    {"script": "jenko.py", "name": "Jenko"},
    {"script": "archer.py", "name": "Archer"},
    {"script": "achilles.py", "name": "Achilles"},
    {"script": "epsn.py", "name": "EPSN"},
]

processes = {}

def log(msg):
    with open(LOG_FILE, "a") as f:
        f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {msg}\n")
    print(msg)

def start_bot(bot_config):
    script_path = os.path.join(BOT_DIR, bot_config["script"])
    cmd = [VENV_PYTHON, script_path]
    try:
        process = subprocess.Popen(cmd, cwd=BOT_DIR)
        processes[bot_config["name"]] = process.pid
        log(f"✓ Started {bot_config['name']} (PID {process.pid})")
        return process
    except Exception as e:
        log(f"✗ Failed to start {bot_config['name']}: {e}")
        return None

def monitor_bots():
    while True:
        for bot_config in BOTS:
            bot_name = bot_config["name"]
            if bot_name not in processes:
                log(f"⚠ {bot_name} not running, restarting...")
                start_bot(bot_config)
            else:
                pid = processes[bot_name]
                try:
                    os.kill(pid, 0)  # Check if process exists
                except OSError:
                    log(f"⚠ {bot_name} (PID {pid}) crashed, restarting...")
                    del processes[bot_name]
                    start_bot(bot_config)
        time.sleep(5)

def signal_handler(sig, frame):
    log("Shutting down launcher...")
    for bot_name, pid in processes.items():
        try:
            os.kill(pid, signal.SIGTERM)
            log(f"Terminated {bot_name} (PID {pid})")
        except:
            pass
    sys.exit(0)

if __name__ == "__main__":
    log("=== Discord Bot Launcher Started ===")
    
    # Start all bots
    for bot_config in BOTS:
        start_bot(bot_config)
        time.sleep(1)
    
    # Monitor and restart
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)
    
    try:
        monitor_bots()
    except KeyboardInterrupt:
        signal_handler(None, None)
