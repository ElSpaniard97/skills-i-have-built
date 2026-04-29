#!/usr/bin/env python3
import argparse, json, os, re, shutil, subprocess, sys
import urllib.request
from datetime import datetime
from pathlib import Path

THREAD_ID = "1498647342142722198"
OUT = Path.home() / ".hermes" / "security-reports"

def discord(message):
    bot = os.environ.get("DISCORD_BOT_TOKEN")
    webhook = os.environ.get("DISCORD_WEBHOOK_URL")
    try:
        if bot:
            url = f"https://discord.com/api/v10/channels/{THREAD_ID}/messages"
            headers = {"Content-Type": "application/json", "Authorization": f"Bot {bot}"}
        elif webhook:
            url = webhook
            headers = {"Content-Type": "application/json"}
        else:
            return
        data = json.dumps({"content": message}).encode("utf-8")
        req = urllib.request.Request(url, data=data, headers=headers, method="POST")
        urllib.request.urlopen(req, timeout=30).read()
    except Exception:
        pass

def report_path(report_id):
    p = OUT / f"{report_id}.json"
    if not p.exists() and report_id == "latest":
        latest = OUT / "latest.md"
        if latest.exists():
            today = datetime.now().strftime("%Y-%m-%d")
            p = OUT / f"{today}.json"
    return p

def parse_file_from_command(cmd):
    matches = re.findall(r"(/(?:etc|home|var|usr)/[A-Za-z0-9._/@%+=:,~-]+)", cmd or "")
    for m in matches:
        p = Path(m)
        if p.exists() and p.is_file():
            return p
    return None

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("report_id")
    group = ap.add_mutually_exclusive_group(required=True)
    group.add_argument("--ids")
    group.add_argument("--all", action="store_true")
    group.add_argument("--all-auto", action="store_true")
    args = ap.parse_args()
    p = report_path(args.report_id)
    if not p.exists():
        print(f"Report not found: {p}")
        return 1
    data = json.loads(p.read_text())
    findings = data.get("findings", [])
    if args.all:
        selected = findings
    elif args.all_auto:
        selected = [f for f in findings if f.get("auto_applicable")]
    else:
        wanted = set()
        for part in args.ids.split(","):
            part = part.strip()
            if part:
                try:
                    wanted.add(int(part))
                except ValueError:
                    print(f"Invalid ID: {part}")
        selected = [f for f in findings if f.get("id") in wanted]
        missing = sorted(wanted - {f.get("id") for f in selected})
        if missing:
            print(f"No matching finding IDs: {','.join(map(str, missing))}")
    summary = []
    for f in selected:
        fid = f.get("id")
        if f.get("applied_at"):
            summary.append(f"[{fid}] skipped: already applied")
            continue
        cmd = f.get("fix_command") or ""
        if not cmd:
            summary.append(f"[{fid}] skipped: no fix_command")
            continue
        if f.get("requires_sudo"):
            queue = OUT / f"{fid}-pending-sudo.txt"
            queue.write_text(cmd + "\n")
            f["pending_sudo"] = True
            f["pending_sudo_at"] = datetime.now().isoformat()
            summary.append(f"[{fid}] pending sudo: {cmd}")
            discord(f"Security fix [{fid}] requires manual sudo approval/run:\n```bash\n{cmd}\n```")
            continue
        backup = None
        touched = parse_file_from_command(cmd)
        if touched:
            backup = OUT / f"{p.stem}-{fid}-{touched.name}.bak"
            shutil.copy2(touched, backup)
        try:
            cp = subprocess.run(cmd, shell=True, text=True, capture_output=True, timeout=120)
            f["applied_at"] = datetime.now().isoformat()
            f["result"] = {"returncode": cp.returncode, "stdout": cp.stdout[-4000:], "stderr": cp.stderr[-4000:], "backup": str(backup) if backup else None}
            summary.append(f"[{fid}] applied rc={cp.returncode}")
        except Exception as exc:
            f["result"] = {"error": str(exc), "backup": str(backup) if backup else None}
            summary.append(f"[{fid}] failed: {exc}")
    p.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
    msg = "Security fix application summary:\n" + "\n".join(summary or ["No selected fixes applied."])
    print(msg)
    discord(msg[:1900])
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
