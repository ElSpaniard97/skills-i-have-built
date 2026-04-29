#!/usr/bin/env bash
set -uo pipefail
python3 - <<'PY'
import json, os, re, shutil, socket, subprocess

findings = []
notes = []

def run(cmd, timeout=30, shell=True):
    try:
        return subprocess.run(cmd, shell=shell, text=True, capture_output=True, timeout=timeout)
    except Exception as exc:
        cp = subprocess.CompletedProcess(cmd, 124, "", str(exc))
        return cp

def add(sev, title, evidence, fix, cmd="", sudo=False, auto=False):
    findings.append({
        "id": None, "scope": "system", "severity": sev, "title": title,
        "evidence": str(evidence).strip()[:2000], "fix_description": fix,
        "fix_command": cmd, "requires_sudo": bool(sudo), "auto_applicable": bool(auto),
    })

def note(tool):
    add("Low", f"{tool} missing", f"{tool} is not installed or unavailable", f"Install {tool}", "", True, False)

if shutil.which("ss"):
    cp = run("ss -tulnp", timeout=20)
    # Allowlist: standard web/ssh + known-legitimate services on this host.
    # Tailscale (41641 UDP, 5353 mDNS), CUPS (631 localhost-only), systemd-resolved (53),
    # Next.js dev (3000 — bound to 0.0.0.0 for LAN dev access, accepted risk),
    # xrdp (3389 — service inactive but socket may persist; mitigated by firewall).
    allowed = {22, 80, 443, 3000, 3389, 5353, 41641, 49807, 36914}
    # Suppress findings for sockets bound only to Tailscale interface (100.64.0.0/10) or tailnet IPv6 (fd7a:115c:a1e0::/48)
    tailscale_re = re.compile(r"\s(100\.(?:6[4-9]|[7-9]\d|1[01]\d|12[0-7])\.\d+\.\d+|\[fd7a:115c:a1e0[:a-f0-9]*\]):\d+")
    for line in cp.stdout.splitlines():
        if tailscale_re.search(line):
            continue  # bound only to Tailscale — not public
        if not re.search(r"(\*|0\.0\.0\.0|\[::\]|::):", line):
            continue
        m = re.search(r"(?:(?:0\.0\.0\.0|\*|\[::\]|::):)(\d+)\b", line)
        if not m:
            continue
        port = int(m.group(1))
        if port not in allowed:
            add("High", f"Unexpected public listening port {port}", line, "Stop the service or bind it to localhost", "", True, False)
else:
    note("ss")

cp = run("apt list --upgradable 2>/dev/null | tail -n +2", timeout=60)
up = [l for l in cp.stdout.splitlines() if l.strip()]
if up:
    sev = "High" if any("security" in l.lower() for l in up) else "Med"
    add(sev, "APT packages are upgradable", f"{len(up)} packages\n" + "\n".join(up[:20]), "Review and install package updates", "sudo apt-get update && sudo apt-get upgrade", True, False)

if shutil.which("debsecan"):
    suite = run("lsb_release -cs", timeout=10).stdout.strip() or "stable"
    cp = run(f"debsecan --suite={suite} --only-fixed 2>/dev/null | head -50", timeout=90)
    if cp.stdout.strip():
        add("High", "Fixed Debian CVEs available", cp.stdout, "Install fixed packages reported by debsecan", "sudo apt-get update && sudo apt-get upgrade", True, False)
else:
    note("debsecan")

if shutil.which("journalctl"):
    cp = run("journalctl _COMM=sshd --since '24 hours ago' 2>/dev/null | grep -ic 'Failed password' || true", timeout=40)
    try:
        failed = int(cp.stdout.strip() or "0")
    except ValueError:
        failed = 0
    if failed > 50:
        add("High", "High SSH failed-password volume", f"{failed} failed password attempts in 24 hours", "Review SSH exposure and enable fail2ban", "sudo systemctl enable --now fail2ban", True, False)
else:
    note("journalctl")

sshd_out = ""
for cmd in ["/usr/sbin/sshd -T -f /etc/ssh/sshd_config 2>/dev/null", "sudo -n sshd -T 2>/dev/null"]:
    cp = run(cmd, timeout=20)
    if cp.returncode == 0 and cp.stdout.strip():
        sshd_out = cp.stdout.lower()
        break
if not sshd_out and os.path.exists("/etc/ssh/sshd_config"):
    cp = run("grep -Ei '^(PermitRootLogin|PasswordAuthentication)' /etc/ssh/sshd_config 2>/dev/null || true")
    sshd_out = cp.stdout.lower()
if re.search(r"permitrootlogin\s+yes", sshd_out):
    add("Critical", "SSH PermitRootLogin enabled", "sshd config -> permitrootlogin yes", "Disable root SSH login and reload sshd", "sudo sed -i 's/^PermitRootLogin.*/PermitRootLogin no/' /etc/ssh/sshd_config && sudo systemctl reload ssh", True, False)
if re.search(r"passwordauthentication\s+yes", sshd_out):
    add("Critical", "SSH password authentication enabled", "sshd config -> passwordauthentication yes", "Disable SSH password login and reload sshd", "sudo sed -i 's/^PasswordAuthentication.*/PasswordAuthentication no/' /etc/ssh/sshd_config && sudo systemctl reload ssh", True, False)

cp = run("find /etc /usr /var -xdev -type f -perm -0002 2>/dev/null | head -20", timeout=90)
if cp.stdout.strip():
    first = cp.stdout.splitlines()[0]
    add("Med", "World-writable system files found", cp.stdout, "Remove world-write permission after confirming ownership", f"sudo chmod o-w {first}", True, False)

cp = run("systemctl is-active unattended-upgrades 2>/dev/null", timeout=15)
if cp.stdout.strip() != "active":
    add("Med", "unattended-upgrades is not active", cp.stdout.strip() or "inactive/unknown", "Enable unattended upgrades", "sudo systemctl enable --now unattended-upgrades", True, False)

cp = run("sudo -n grep -r NOPASSWD /etc/sudoers /etc/sudoers.d/ 2>/dev/null || true", timeout=20)
for line in cp.stdout.splitlines():
    if line.strip() and not line.lstrip().startswith("#") and not re.search(r"\broot\b", line):
        add("High", "Non-root sudoers NOPASSWD entry", line, "Remove unnecessary NOPASSWD sudoers grants", "", True, False)

print(json.dumps({"findings": findings, "notes": notes}, ensure_ascii=False))
PY
