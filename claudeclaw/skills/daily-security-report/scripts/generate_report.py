#!/usr/bin/env python3
import json, os
from datetime import datetime
from pathlib import Path

SEV_ORDER = {"Critical": 0, "High": 1, "Med": 2, "Low": 3}
SEV_ICON = {"Critical": "🔴", "High": "🟠", "Med": "🟡", "Low": "🟢"}
OUT = Path(os.environ.get("SECURITY_REPORT_DIR", "/home/zeke/claudeclaw/store/security-reports"))

def load(path):
    try:
        return json.loads(Path(path).read_text())
    except Exception as exc:
        return {"findings": [{"scope": "meta", "severity": "Low", "title": f"Could not read {path}", "evidence": str(exc), "fix_description": "Review scanner stderr", "fix_command": "", "requires_sudo": False, "auto_applicable": False}]}

def split_parts(text, limit=1900):
    parts, buf = [], ""
    for block in text.split("\n\n"):
        candidate = block if not buf else buf + "\n\n" + block
        if len(candidate) <= limit:
            buf = candidate
        else:
            if buf:
                parts.append(buf)
            while len(block) > limit:
                parts.append(block[:limit])
                block = block[limit:]
            buf = block
    if buf:
        parts.append(buf)
    return parts or [text[:limit]]

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    date_id = datetime.now().strftime("%Y-%m-%d")
    display = datetime.now().strftime("%b %d, %Y (2:00 AM CST)")
    docs = [load("/tmp/sec_system.json"), load("/tmp/sec_repos.json"), load("/tmp/sec_infra.json")]
    findings = []
    for doc in docs:
        findings.extend(doc.get("findings", []))
        if doc.get("error"):
            findings.append({"scope": "meta", "severity": "Low", "title": "Scanner exited with error", "evidence": "run_all.sh wrote fallback JSON; inspect /tmp/sec_*.err", "fix_description": "Review scanner stderr", "fix_command": "", "requires_sudo": False, "auto_applicable": False})
    findings.sort(key=lambda f: (SEV_ORDER.get(f.get("severity", "Low"), 9), f.get("title", "")))
    for i, f in enumerate(findings, 1):
        f["id"] = i
    counts = {s: sum(1 for f in findings if f.get("severity") == s) for s in ["Critical", "High", "Med", "Low"]}
    report = {"date": date_id, "generated_at": datetime.now().isoformat(), "findings": findings, "counts": counts}
    json_path = OUT / f"{date_id}.json"
    md_path = OUT / f"{date_id}.md"
    parts_path = OUT / f"{date_id}.parts.json"
    latest = OUT / "latest.md"
    json_path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n")
    lines = [
        f"🔐 **Daily Security Report — {display}**",
        "",
        f"🔴 Critical: {counts['Critical']} │ 🟠 High: {counts['High']} │ 🟡 Med: {counts['Med']} │ 🟢 Low: {counts['Low']}",
        "",
    ]
    if not findings:
        lines.append("No findings detected.")
        lines.append("")
    for f in findings:
        sev = f.get("severity", "Low")
        icon = SEV_ICON.get(sev, "🟢")
        scope = f.get("scope", "unknown")
        lines.append(f"{icon} **[{f['id']}] {f.get('title','Untitled')}** _({scope})_")
        ev = str(f.get("evidence", "")).replace("`", "'").strip()
        if len(ev) > 450:
            ev = ev[:447] + "..."
        lines.append(f"   • Evidence: `{ev or 'n/a'}`")
        lines.append(f"   • Fix: {f.get('fix_description','Review finding')}")
        auto = "⚠️ requires sudo" if f.get("requires_sudo") else ("yes" if f.get("auto_applicable") else "manual")
        lines.append(f"   • Auto-apply: {auto}")
        if f.get("fix_command"):
            lines.append(f"   • Command: `{f.get('fix_command')}`")
        lines.append("")
    lines.extend([
        "---",
        "**To approve fixes:** Reply `approve <ids>` (e.g. `approve 1,3,5`) or `approve all`.",
        "For sudo fixes, run the printed command manually after approving.",
        f"Full data: `{json_path}`",
        "",
    ])
    md = "\n".join(lines)
    md_path.write_text(md)
    latest.write_text(md)
    parts_path.write_text(json.dumps(split_parts(md), ensure_ascii=False, indent=2) + "\n")
    (OUT / "latest.parts.json").write_text(parts_path.read_text())

if __name__ == "__main__":
    main()
