#!/usr/bin/env python3
import argparse
import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path


def parse_args():
    parser = argparse.ArgumentParser(description="Generate a ClaudeClaw token cost report.")
    parser.add_argument("--since-days", type=int, default=2, help="Days to include; 0 means all-time.")
    parser.add_argument("--db", default=os.environ.get("CLAUDECLAW_DB", "/home/zeke/claudeclaw/store/claudeclaw.db"))
    return parser.parse_args()


def money(value):
    return f"${value:,.4f}"


def tokens(value):
    value = int(value or 0)
    if value >= 1_000_000:
        return f"{value / 1_000_000:.1f}M"
    if value >= 10_000:
        return f"{value / 1_000:.1f}K"
    return f"{value:,}"


def main():
    args = parse_args()
    db_path = Path(os.path.expanduser(args.db)).resolve()
    if not db_path.exists():
        raise SystemExit(f"Database not found: {db_path}")

    cutoff = 0 if args.since_days <= 0 else int((datetime.now(tz=timezone.utc).timestamp() - args.since_days * 86400) * 1000)
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    try:
        rows = conn.execute(
            """
            SELECT agent_id, model, input_tokens, output_tokens, estimated_cost, created_at
            FROM token_usage
            WHERE created_at >= ?
            ORDER BY created_at DESC
            """,
            (cutoff,),
        ).fetchall()
    finally:
        conn.close()

    total_in = sum(int(r["input_tokens"] or 0) for r in rows)
    total_out = sum(int(r["output_tokens"] or 0) for r in rows)
    total_cost = sum(float(r["estimated_cost"] or 0.0) for r in rows)

    by_agent = {}
    by_model = {}
    for row in rows:
        for bucket, key in ((by_agent, row["agent_id"] or "unknown"), (by_model, row["model"] or "unknown")):
            item = bucket.setdefault(key, {"runs": 0, "input": 0, "output": 0, "cost": 0.0})
            item["runs"] += 1
            item["input"] += int(row["input_tokens"] or 0)
            item["output"] += int(row["output_tokens"] or 0)
            item["cost"] += float(row["estimated_cost"] or 0.0)

    window = "all time" if args.since_days <= 0 else f"last {args.since_days} days"
    print(f"# ClaudeClaw Cost Report")
    print(f"- Window: {window}")
    print(f"- Generated: {datetime.now().strftime('%Y-%m-%d %I:%M %p')}")
    print(f"- Records: {len(rows):,}")
    print(f"- Input tokens: {tokens(total_in)}")
    print(f"- Output tokens: {tokens(total_out)}")
    print(f"- Estimated cost: {money(total_cost)}")
    print()
    print("## By Agent")
    if by_agent:
        for agent, data in sorted(by_agent.items(), key=lambda item: item[1]["cost"], reverse=True):
            print(f"- {agent}: {data['runs']} records, {tokens(data['input'])} in, {tokens(data['output'])} out, {money(data['cost'])}")
    else:
        print("- No token usage records found.")
    print()
    print("## By Model")
    if by_model:
        for model, data in sorted(by_model.items(), key=lambda item: item[1]["cost"], reverse=True):
            print(f"- {model}: {data['runs']} records, {tokens(data['input'])} in, {tokens(data['output'])} out, {money(data['cost'])}")
    else:
        print("- No model usage records found.")


if __name__ == "__main__":
    main()
