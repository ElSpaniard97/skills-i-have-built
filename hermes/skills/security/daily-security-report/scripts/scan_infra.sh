#!/usr/bin/env bash
set -uo pipefail
python3 - <<'PY'
import json, os, re, shutil, stat, subprocess
from pathlib import Path

findings = []
home = Path.home()

def run(cmd, timeout=30):
    try:
        return subprocess.run(cmd, shell=True, text=True, capture_output=True, timeout=timeout)
    except Exception as exc:
        return subprocess.CompletedProcess(cmd, 124, "", str(exc))

def redact_evidence(value):
    text = str(value)
    # gh auth status may print an OAuth token line; reports must never persist or post it.
    text = re.sub(r"(?im)^(\s*-\s*Token\s*:\s*)\S+", r"\1<REDACTED>", text)
    text = re.sub(r"(?im)^(\s*-\s*Token\s*=\s*)\S+", r"\1<REDACTED>", text)
    text = re.sub(r"(?i)(api[_-]?key|token|secret|password)(\s*[:=]\s*)[^\s`]{12,}", r"\1\2<REDACTED>", text)
    text = re.sub(r"gh[pousr]_[A-Za-z0-9_]{20,}", "gh_token_<REDACTED>", text)
    text = re.sub(r"sk-[A-Za-z0-9_-]{20,}", "sk-<REDACTED>", text)
    return text

def add(sev, title, evidence, fix, cmd="", sudo=False, auto=False):
    findings.append({
        "id": None, "scope": "infra", "severity": sev, "title": title,
        "evidence": redact_evidence(evidence).strip()[:2000], "fix_description": fix,
        "fix_command": cmd, "requires_sudo": bool(sudo), "auto_applicable": bool(auto),
    })

ak = home / ".ssh" / "authorized_keys"
if ak.exists():
    lines = [l.strip() for l in ak.read_text(errors="ignore").splitlines() if l.strip() and not l.startswith("#")]
    weak = []
    for i, line in enumerate(lines, 1):
        parts = line.split()
        if not parts:
            continue
        if parts[0] == "ssh-dss":
            weak.append(f"line {i}: DSA key")
        if parts[0] == "ssh-rsa":
            cp = run(f"ssh-keygen -lf {ak} | sed -n '{i}p'", timeout=10)
            m = re.match(r"(\d+)\s+", cp.stdout.strip())
            if m and int(m.group(1)) < 3072:
                weak.append(f"line {i}: RSA {m.group(1)} bits")
    if weak:
        add("High", "Weak SSH authorized_keys entry", f"{len(lines)} keys total\n" + "\n".join(weak), "Replace weak authorized_keys entries", "", False, False)
else:
    add("Low", "No authorized_keys file found", str(ak), "No action unless SSH key login is expected", "", False, False)

if shutil.which("gh"):
    cp = run("gh auth status 2>&1", timeout=30)
    api = run("gh api user 2>&1", timeout=30)
    evidence = (cp.stdout + cp.stderr + "\n" + api.stdout + api.stderr).strip()
    if cp.returncode != 0:
        add("Med", "GitHub CLI is not authenticated", evidence, "Run gh auth login", "gh auth login", False, False)
    if re.search(r"admin:", evidence, re.I):
        add("High", "GitHub token has admin scopes", evidence, "Re-authenticate gh with narrower scopes", "gh auth refresh", False, True)
    if "expires" not in evidence.lower() and "expiration" not in evidence.lower():
        add("Low", "GitHub token expiry not visible", evidence or "No expiry shown by gh auth status", "Review GitHub token lifetime", "gh auth status", False, False)
else:
    add("Low", "gh missing", "gh CLI is not installed", "Install gh CLI", "", True, False)

ufw = run("sudo -n ufw status 2>/dev/null", timeout=20)
ipt = run("iptables -L -n 2>/dev/null", timeout=20)
fw_evidence = (ufw.stdout + "\n" + ipt.stdout).strip()
if "Status: inactive" in ufw.stdout or (re.search(r"Chain INPUT \(policy ACCEPT\)", ipt.stdout) and not re.search(r"\nACCEPT|\nDROP|\nREJECT", ipt.stdout)):
    add("Critical", "Firewall appears open or inactive", fw_evidence or "No firewall rules visible", "Enable firewall with explicit allow rules first", "sudo ufw allow 22/tcp && sudo ufw enable", True, False)

cp = run("systemctl is-active fail2ban 2>/dev/null", timeout=15)
if cp.stdout.strip() != "active":
    add("Med", "fail2ban is not active", cp.stdout.strip() or "inactive/unknown", "Enable fail2ban", "sudo systemctl enable --now fail2ban", True, False)

cp = run("last -n 10 2>/dev/null", timeout=20)
bad = [l for l in cp.stdout.splitlines() if l.strip() and not l.startswith(("zeke ", "reboot", "wtmp", "root "))]
if bad:
    add("Low", "Recent login by non-zeke user", "\n".join(bad[:10]), "Review recent logins", "last -n 20", False, False)

ssh_dir = home / ".ssh"
if ssh_dir.exists():
    for p in ssh_dir.glob("id_*"):
        if p.is_file() and not p.name.endswith(".pub"):
            mode = stat.S_IMODE(p.stat().st_mode)
            if mode != 0o600:
                add("Critical", "SSH private key permissions too open", f"{p}: {oct(mode)}", "Set private key permissions to 600", f"chmod 600 {p}", False, True)

print(json.dumps({"findings": findings}, ensure_ascii=False))
PY
