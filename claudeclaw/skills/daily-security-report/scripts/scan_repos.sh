#!/usr/bin/env bash
set -uo pipefail
export PATH="$HOME/.local/bin:/usr/local/bin:$PATH"
SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export SKILL_DIR
python3 - <<'PY'
import json, os, re, shutil, subprocess
from pathlib import Path

skill = Path(os.environ["SKILL_DIR"])
repos_file = skill / "references" / "repos.txt"
findings = []

def run(cmd, cwd=None, timeout=120):
    try:
        return subprocess.run(cmd, shell=True, cwd=cwd, text=True, capture_output=True, timeout=timeout)
    except Exception as exc:
        return subprocess.CompletedProcess(cmd, 124, "", str(exc))

def add(repo, sev, title, evidence, fix, cmd="", sudo=False, auto=False):
    findings.append({
        "id": None, "scope": "repo", "repo": str(repo), "severity": sev, "title": title,
        "evidence": str(evidence).strip()[:2000], "fix_description": fix,
        "fix_command": cmd, "requires_sudo": bool(sudo), "auto_applicable": bool(auto),
    })

def discover():
    found = []
    hermes = Path.home() / "hermes"
    if (hermes / ".git").exists():
        found.append(hermes)
    cp = run("find /home/zeke -maxdepth 5 -type d -name .git 2>/dev/null", timeout=120)
    for line in cp.stdout.splitlines():
        p = Path(line).parent
        try:
            if p.exists() and p not in found:
                found.append(p)
        except OSError:
            pass
    return found

existing = [Path(l.strip()).expanduser() for l in repos_file.read_text(errors="ignore").splitlines() if l.strip()] if repos_file.exists() else []
if not existing:
    existing = discover()
    repos_file.write_text("\n".join(str(p) for p in existing) + ("\n" if existing else ""))

repos = [p for p in existing if (p / ".git").exists()]
if not repos:
    print(json.dumps({"findings": [{"id": None, "scope": "repo", "severity": "Low", "title": "No repositories found", "evidence": str(repos_file), "fix_description": "Add repository paths to references/repos.txt", "fix_command": "", "requires_sudo": False, "auto_applicable": False}]}))
    raise SystemExit(0)

missing = []
for tool in ["gitleaks", "osv-scanner", "semgrep"]:
    if not shutil.which(tool):
        missing.append(tool)
        findings.append({"id": None, "scope": "repo", "severity": "Low", "title": f"{tool} missing", "evidence": f"{tool} is not installed", "fix_description": f"Run install_tools.sh to install {tool}", "fix_command": "", "requires_sudo": True, "auto_applicable": False})

for repo in repos:
    before = len(findings)
    if shutil.which("gitleaks"):
        cp = run(f"gitleaks detect --source={repo} --no-git -f json", timeout=120)
        data = []
        try:
            data = json.loads(cp.stdout or "[]")
        except json.JSONDecodeError:
            data = []
        for leak in data[:30]:
            add(repo, "Critical", "Secret detected by gitleaks", json.dumps(leak, ensure_ascii=False)[:2000], "Rotate the secret and remove it from repository history", "", False, False)

    if shutil.which("osv-scanner"):
        cp = run(f"osv-scanner -r --json {repo}", timeout=180)
        try:
            data = json.loads(cp.stdout or "{}")
        except json.JSONDecodeError:
            data = {}
        vulns = []
        def walk(obj):
            if isinstance(obj, dict):
                if "vulnerabilities" in obj and isinstance(obj["vulnerabilities"], list):
                    vulns.extend(obj["vulnerabilities"])
                for v in obj.values():
                    walk(v)
            elif isinstance(obj, list):
                for v in obj:
                    walk(v)
        walk(data)
        for vuln in vulns[:30]:
            sev = "High"
            text = json.dumps(vuln, ensure_ascii=False)
            if re.search(r"critical", text, re.I):
                sev = "Critical"
            elif re.search(r"moderate|medium", text, re.I):
                sev = "Med"
            elif re.search(r"low", text, re.I):
                sev = "Low"
            add(repo, sev, "Dependency vulnerability detected by osv-scanner", text[:2000], "Upgrade the affected dependency to a fixed version", "", False, False)

    if shutil.which("semgrep") or os.path.exists(os.path.expanduser("~/.local/bin/semgrep")):
        cp = run(f"semgrep --config=auto --json --quiet {repo}", timeout=120)
        try:
            data = json.loads(cp.stdout or "{}")
        except json.JSONDecodeError:
            data = {}
        for item in data.get("results", [])[:30]:
            extra = item.get("extra", {})
            s = str(extra.get("severity", "")).upper()
            sev = "High" if s == "ERROR" else "Med" if s == "WARNING" else "Low"
            add(repo, sev, "SAST finding from semgrep", json.dumps(item, ensure_ascii=False)[:2000], "Review and fix the reported code path", "", False, False)

    cp = run("git ls-files | grep -E '^\\.env$|/\\.env$' || true", cwd=repo, timeout=30)
    if cp.stdout.strip():
        add(repo, "High", ".env file tracked in git", cp.stdout, "Remove .env from git and rotate any contained secrets", "git rm --cached .env && echo .env >> .gitignore", False, True)

    repo_findings = findings[before:]
    if len(repo_findings) > 30:
        del findings[before + 30:]
        add(repo, "Low", "Repository findings capped", "More than 30 findings were detected for this repo", "Inspect raw scanner output manually", "", False, False)

print(json.dumps({"findings": findings}, ensure_ascii=False))
PY
