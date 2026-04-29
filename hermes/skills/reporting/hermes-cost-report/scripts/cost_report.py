#!/usr/bin/env python3
import argparse
import json
import os
import sqlite3
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path


TOKEN_FIELDS = (
    "input_tokens",
    "output_tokens",
    "cache_read_tokens",
    "cache_write_tokens",
)


def parse_args():
    default_pricing = Path(__file__).resolve().with_name("pricing.json")
    parser = argparse.ArgumentParser(
        description="Generate a markdown Hermes cost report from session token usage."
    )
    parser.add_argument("--since-days", type=int, default=2, help="Days to include; 0 means all-time.")
    parser.add_argument("--db", default="~/.hermes/state.db", help="Path to Hermes state.db.")
    parser.add_argument("--pricing", default=str(default_pricing), help="Path to pricing JSON.")
    parser.add_argument("--top", type=int, default=5, help="Number of top sessions to show.")
    return parser.parse_args()


def expand_path(value):
    return Path(os.path.expanduser(value)).resolve()


def load_pricing(path):
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def utc_date(epoch):
    return datetime.fromtimestamp(float(epoch), tz=timezone.utc).date()


def money(value, digits=2):
    return f"${value:,.{digits}f}"


def fmt_tokens(value):
    value = int(value or 0)
    if value >= 1_000_000:
        return f"{value / 1_000_000:.1f}M"
    if value >= 10_000:
        return f"{value / 1_000:.1f}K"
    return f"{value:,}"


def pct(part, total):
    if total <= 0:
        return "0.0%"
    return f"{(part / total) * 100:.1f}%"


def pct_int(part, total):
    if total <= 0:
        return "0%"
    return f"{round((part / total) * 100):.0f}%"


def fetch_sessions(db_path, since_days):
    now = datetime.now(tz=timezone.utc).timestamp()
    where = ""
    params = []
    if since_days > 0:
        where = "WHERE started_at >= ?"
        params.append(now - since_days * 86400)

    query = f"""
        SELECT
            id, source, user_id, model, started_at, message_count, tool_call_count,
            input_tokens, output_tokens, cache_read_tokens, cache_write_tokens,
            reasoning_tokens, billing_provider, estimated_cost_usd, actual_cost_usd, title
        FROM sessions
        {where}
        ORDER BY started_at ASC
    """
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    try:
        return list(conn.execute(query, params))
    finally:
        conn.close()


def session_cost(row, pricing, unknown_models):
    model = row["model"] or "(unknown)"
    rates = pricing.get(model)
    if rates is None:
        if model not in unknown_models:
            print(f"unknown model: {model}", file=sys.stderr)
        unknown_models.add(model)
        return 0.0

    return (
        int(row["input_tokens"] or 0) * float(rates.get("input", 0.0))
        + int(row["output_tokens"] or 0) * float(rates.get("output", 0.0))
        + int(row["cache_read_tokens"] or 0) * float(rates.get("cache_read", 0.0))
        + int(row["cache_write_tokens"] or 0) * float(rates.get("cache_write", 0.0))
    ) / 1_000_000


def add_tokens(target, row):
    target["input"] += int(row["input_tokens"] or 0)
    target["output"] += int(row["output_tokens"] or 0)
    target["cache_read"] += int(row["cache_read_tokens"] or 0)
    target["cache_write"] += int(row["cache_write_tokens"] or 0)


def empty_bucket():
    return {
        "sessions": 0,
        "input": 0,
        "output": 0,
        "cache_read": 0,
        "cache_write": 0,
        "cost": 0.0,
    }


def aggregate(rows, pricing):
    unknown_models = set()
    by_model = defaultdict(empty_bucket)
    by_source = defaultdict(empty_bucket)
    by_day = defaultdict(lambda: {"sessions": 0, "cost": 0.0})
    sessions = []
    total = 0.0

    for row in rows:
        cost = session_cost(row, pricing, unknown_models)
        total += cost
        model = row["model"] or "(unknown)"
        source = row["source"] or "(unknown)"
        day = utc_date(row["started_at"]).isoformat()

        for bucket in (by_model[model], by_source[source]):
            bucket["sessions"] += 1
            bucket["cost"] += cost
            add_tokens(bucket, row)

        by_day[day]["sessions"] += 1
        by_day[day]["cost"] += cost
        sessions.append({"row": row, "cost": cost})

    sessions.sort(key=lambda item: item["cost"], reverse=True)
    return total, by_model, by_source, by_day, sessions, unknown_models


def render_recommendations(total, by_model, by_source, by_day, sessions, unknown_models, pricing):
    total_cost = total
    period_days = max(1, len(by_day))
    primary_model = "gpt-5.3-codex"
    model_cost_shares = {
        model: data["cost"] / total_cost if total_cost > 0 else 0.0
        for model, data in by_model.items()
    }
    source_cost_shares = {
        source: data["cost"] / total_cost if total_cost > 0 else 0.0
        for source, data in by_source.items()
    }
    primary = by_model.get(primary_model, empty_bucket())
    primary_cost = primary["cost"]
    primary_share = model_cost_shares.get(primary_model, 0.0)
    cron = by_source.get("cron", empty_bucket())
    cron_cost = cron["cost"]
    cron_share = source_cost_shares.get("cron", 0.0)
    discord = by_source.get("discord", empty_bucket())
    discord_cost = discord["cost"]
    discord_share = source_cost_shares.get("discord", 0.0)
    primary_rates = pricing.get(primary_model, {})
    total_cache_read_tokens = sum(data["cache_read"] for data in by_model.values())
    primary_cache_read_tokens = primary["cache_read"]
    cache_read_cost = (
        primary_cache_read_tokens * float(primary_rates.get("cache_read", 0.0))
    ) / 1_000_000

    lines = ["", "## 🔧 Recommendations"]

    if total_cost == 0:
        since_days = getattr(render_recommendations, "since_days", 0)
        if since_days > 0:
            lines.append(f"- ℹ️ No billable activity in the last {since_days} days.")
    else:
        daily_avg = total_cost / period_days
        monthly_proj = daily_avg * 30
        lines.append(
            f"- 📈 At current pace (**{money(daily_avg)}/day**), projected monthly spend is **{money(monthly_proj)}**."
        )

        if primary_share > 0.70:
            lines.append(
                f"- 🎯 GPT-5.3-Codex is **{pct_int(primary_cost, total_cost)}** of spend ({money(primary_cost)}). "
                "Route casual Discord chat & simple tool dispatch to **gpt-5.1-codex-mini** when quality permits. "
                "Keep GPT-5.3-Codex for hard reasoning, long planning, and coding-heavy tasks."
            )

        if primary_cost > 0 and cache_read_cost / primary_cost > 0.30:
            lines.append(
                f"- 💾 **{money(cache_read_cost)}** of GPT-5.3-Codex cost is cache reads "
                f"({pct_int(cache_read_cost, primary_cost)} of GPT-5.3-Codex). Trim the system prompt — every cached turn "
                "re-bills the full prompt. Lazy-load skill descriptions or prune unused skills."
            )

        cron_uses_primary = any(
            (item["row"]["source"] or "(unknown)") == "cron"
            and (item["row"]["model"] or "(unknown)") == primary_model
            for item in sessions
        )
        if cron_share > 0.15 and cron_uses_primary:
            lines.append(
                f"- ⏰ Cron jobs cost **{money(cron_cost)} ({pct_int(cron_cost, total_cost)})**. "
                "Consider gpt-5.1-codex-mini for low-risk scheduled jobs that mostly run scripts or summarize known files. "
                "Edit cron job model overrides via cronjob update."
            )

        whale = next((item for item in sessions if item["cost"] / total_cost > 0.10), None)
        if whale:
            row = whale["row"]
            title = row["title"] or "(untitled)"
            messages = int(row["message_count"] or 0)
            tools = int(row["tool_call_count"] or 0)
            lines.append(
                f"- 🐋 One session (\"{title}\") cost **{money(whale['cost'])}** "
                f"({pct_int(whale['cost'], total_cost)} of total) with {messages:,} messages and "
                f"{tools:,} tool calls. Long sessions compound cache costs — consider /clear or starting "
                "fresh sessions for unrelated tasks."
            )

        tool_heavy = None
        for item in sessions[:5]:
            row = item["row"]
            messages = int(row["message_count"] or 0)
            tools = int(row["tool_call_count"] or 0)
            tools_per_msg = tools / messages if messages > 0 else 0.0
            cost_per_msg = item["cost"] / messages if messages > 0 else 0.0
            if tools_per_msg > 0.6:
                tool_heavy = (item, messages, tools, tools_per_msg, cost_per_msg)
                break
        if tool_heavy:
            item, messages, tools, tools_per_msg, _cost_per_msg = tool_heavy
            title = item["row"]["title"] or "(untitled)"
            lines.append(
                f"- 🔧 \"{title}\" used {tools:,} tool calls across {messages:,} messages "
                f"({tools_per_msg:.1f} tools/msg). High tool density inflates cost — use execute_code "
                "to batch tool calls instead of issuing them one-by-one."
            )

        if discord_share > 0.70 and primary_share > 0.70:
            lines.append(
                f"- 💬 **{pct_int(discord_cost, total_cost)}** of spend is Discord. If most Discord chat "
                "is conversational (greetings, quick lookups), set a default cheaper model for Discord "
                "and reserve GPT-5.3-Codex for explicit complex tasks."
            )

    if total_cost > 0 and unknown_models:
        unknown_list = ", ".join(f"`{model}`" for model in sorted(unknown_models))
        lines.append(
            f"- ❓ Pricing missing for: {unknown_list}. These contributed $0 to estimates. "
            "Add entries to scripts/pricing.json."
        )

    lines.extend(
        [
            "",
            "### Quick Actions",
            "- Edit prices: `~/.hermes/skills/reporting/hermes-cost-report/scripts/pricing.json`",
            '- Change cron cadence: `cronjob update <id> schedule="0 10 * * *"` (daily)',
            "- All-time report: `python3 ~/.hermes/skills/reporting/hermes-cost-report/scripts/cost_report.py --since-days 0`",
        ]
    )
    return "\n".join(lines)


def period_label(rows, since_days):
    today = datetime.now(tz=timezone.utc).date()
    if rows:
        first = utc_date(rows[0]["started_at"])
        last = utc_date(rows[-1]["started_at"])
    elif since_days > 0:
        last = today
        first = datetime.fromtimestamp(
            datetime.now(tz=timezone.utc).timestamp() - since_days * 86400,
            tz=timezone.utc,
        ).date()
    else:
        first = today
        last = today

    if since_days > 0:
        day_count = since_days
    else:
        day_count = max((last - first).days + 1, 0)
    return first.isoformat(), last.isoformat(), day_count


def pricing_label(path):
    try:
        modified = datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc).date().isoformat()
    except OSError:
        modified = "unknown"

    default_path = Path(__file__).resolve().with_name("pricing.json")
    label = "scripts/pricing.json" if path == default_path else str(path)
    return label, modified


def render_report(rows, total, by_model, by_source, by_day, sessions, unknown_models, args, pricing_path, pricing):
    start, end, days = period_label(rows, args.since_days)
    pricing_name, pricing_modified = pricing_label(pricing_path)
    top_n = max(args.top, 0)

    lines = [
        "# 💰 Hermes Cost Report",
        "",
        f"**Period:** {start} → {end} ({days} days, {len(rows)} sessions)",
        f"**Total estimated cost: `{money(total)}`**",
        "",
        "> Costs computed from token counts × public list pricing (DB cost columns are NULL).",
        "",
        "## By Model",
        "| Model | Sessions | Input | Output | Cache Read | Cache Write | Cost |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]

    for model, data in sorted(by_model.items(), key=lambda item: item[1]["cost"], reverse=True):
        lines.append(
            f"| {model} | {data['sessions']:,} | {fmt_tokens(data['input'])} | "
            f"{fmt_tokens(data['output'])} | {fmt_tokens(data['cache_read'])} | "
            f"{fmt_tokens(data['cache_write'])} | {money(data['cost'], 4)} |"
        )

    if not by_model:
        lines.append("| _No sessions_ | 0 | 0 | 0 | 0 | 0 | $0.0000 |")

    lines.extend(["", "## By Source"])
    if by_source:
        for source, data in sorted(by_source.items(), key=lambda item: item[1]["cost"], reverse=True):
            lines.append(f"- **{source}:** {data['sessions']:,} sessions — {money(data['cost'])} ({pct(data['cost'], total)})")
    else:
        lines.append("- **(none):** 0 sessions — $0.00 (0.0%)")

    lines.extend(["", "## By Day", "| Date | Sessions | Cost |", "| --- | ---: | ---: |"])
    if by_day:
        for day, data in sorted(by_day.items()):
            lines.append(f"| {day} | {data['sessions']:,} | {money(data['cost'], 4)} |")
    else:
        lines.append("| _No sessions_ | 0 | $0.0000 |")

    lines.extend(["", f"## Top {top_n} Sessions by Cost"])
    if top_n and sessions:
        for index, item in enumerate(sessions[:top_n], start=1):
            row = item["row"]
            title = row["title"] or "(untitled)"
            messages = int(row["message_count"] or 0)
            tools = int(row["tool_call_count"] or 0)
            source = row["source"] or "(unknown)"
            model = row["model"] or "(unknown)"
            lines.append(
                f"{index}. **{money(item['cost'])}** — *{title}* "
                f"({messages:,} msgs, {tools:,} tools, {source}, {model})"
            )
    else:
        lines.append("No sessions found.")

    unknown_line = ", ".join(f"`{model}`" for model in sorted(unknown_models)) if unknown_models else "none"
    lines.extend(
        [
            "",
            "## Notes",
            f"- Models without pricing entries (if any): {unknown_line}",
            f"- Pricing source: {pricing_name} (last modified {pricing_modified})",
        ]
    )
    render_recommendations.since_days = args.since_days
    lines.append(render_recommendations(total, by_model, by_source, by_day, sessions, unknown_models, pricing))
    return "\n".join(lines) + "\n"


def main():
    args = parse_args()
    db_path = expand_path(args.db)
    pricing_path = expand_path(args.pricing)

    if not db_path.exists():
        print(f"database not found: {db_path}", file=sys.stderr)
        return 1

    pricing = load_pricing(pricing_path)
    rows = fetch_sessions(db_path, args.since_days)
    total, by_model, by_source, by_day, sessions, unknown_models = aggregate(rows, pricing)
    sys.stdout.write(render_report(rows, total, by_model, by_source, by_day, sessions, unknown_models, args, pricing_path, pricing))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
