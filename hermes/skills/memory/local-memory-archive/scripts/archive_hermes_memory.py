#!/usr/bin/env python3
"""Archive Hermes memory entries to local SSD files.

This script does not edit active Hermes memory. It reads a MEMORY.md/USER.md-style
file, splits entries on separator lines containing only '§', and writes a dated
Markdown snapshot plus JSONL records under the archive root.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path

SEP_RE = re.compile(r"^\s*§\s*$", re.M)
SECRET_RE = re.compile(
    r"(?i)(api[_ -]?key|token|secret|password|authorization|bearer)\s*[:=]\s*([^\s`]+)"
)


def split_entries(text: str) -> list[str]:
    return [chunk.strip() for chunk in SEP_RE.split(text) if chunk.strip()]


def redact_for_preview(text: str) -> str:
    return SECRET_RE.sub(lambda m: f"{m.group(1)}=[REDACTED]", text)


def sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def main() -> int:
    parser = argparse.ArgumentParser(description="Archive Hermes memory entries locally")
    parser.add_argument("--source", default=str(Path.home() / ".hermes" / "memories" / "MEMORY.md"))
    parser.add_argument("--archive-root", default=str(Path.home() / ".hermes" / "local-memory-archive"))
    parser.add_argument("--tag", default="manual")
    parser.add_argument("--date", default=datetime.now().strftime("%Y-%m-%d"))
    args = parser.parse_args()

    source = Path(args.source).expanduser().resolve()
    root = Path(args.archive_root).expanduser().resolve()
    archives = root / "archives"
    archives.mkdir(parents=True, exist_ok=True)

    text = source.read_text(encoding="utf-8")
    entries = split_entries(text)
    now = datetime.now(timezone.utc).isoformat()
    source_label = source.name

    md_path = archives / f"{args.date}.md"
    jsonl_path = archives / f"{args.date}.jsonl"

    records = []
    for i, entry in enumerate(entries, start=1):
        records.append({
            "archived_at": now,
            "source": str(source),
            "source_label": source_label,
            "tag": args.tag,
            "entry_index": i,
            "sha256_16": sha(entry),
            "contains_secret_like_text": bool(SECRET_RE.search(entry)),
            "text": entry,
        })

    with md_path.open("a", encoding="utf-8") as f:
        f.write(f"\n\n# Hermes memory archive snapshot — {args.date}\n")
        f.write(f"- Archived at: {now}\n")
        f.write(f"- Source: {source}\n")
        f.write(f"- Tag: {args.tag}\n")
        f.write(f"- Entries: {len(records)}\n\n")
        for r in records:
            f.write(f"## Entry {r['entry_index']} — {r['sha256_16']}\n")
            if r["contains_secret_like_text"]:
                f.write("Secret-like text detected; avoid printing this entry publicly.\n\n")
            f.write(r["text"].rstrip() + "\n\n")

    with jsonl_path.open("a", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    index = root / "index.md"
    summary_line = f"- {args.date}: {len(records)} entries from `{source}` tag `{args.tag}` -> `{md_path.name}`, `{jsonl_path.name}`\n"
    if index.exists():
        idx = index.read_text(encoding="utf-8")
        idx += summary_line
    else:
        idx = "# Local Hermes Memory Archive\n\n" + summary_line
        idx += "\nSearch examples:\n"
        idx += "- `rg -n \"discord-homes|Codex OAuth|Mission Control\" /home/zeke/.hermes/local-memory-archive`\n"
        idx += "- Use Hermes `search_files` with target=content and path=/home/zeke/.hermes/local-memory-archive.\n"
    index.write_text(idx, encoding="utf-8")

    print(json.dumps({
        "ok": True,
        "source": str(source),
        "entries": len(records),
        "markdown": str(md_path),
        "jsonl": str(jsonl_path),
        "index": str(index),
        "secret_like_entries": sum(1 for r in records if r["contains_secret_like_text"]),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
