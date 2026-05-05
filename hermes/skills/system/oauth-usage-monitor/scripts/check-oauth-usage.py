#!/usr/bin/env python3
"""
OAuth usage monitor for Claude Code and Codex CLI.
Checks auth status and rate limits, outputs a report.
Deployed at ~/.hermes/scripts/check-oauth-usage.py
Cron job: oauth-usage-check (every 2h)
"""

import json
import subprocess
import sys
from datetime import datetime, timezone


def check_claude_code():
    """Check Claude Code auth and rate limits."""
    result = {"tool": "Claude Code", "auth_ok": False, "rate_limited": False}

    try:
        auth = subprocess.run(
            ["claude", "auth", "status"],
            capture_output=True, text=True, timeout=10
        )
        auth_data = json.loads(auth.stdout)
        result["auth_ok"] = auth_data.get("loggedIn", False)
        result["auth_method"] = auth_data.get("authMethod", "unknown")
        result["subscription"] = auth_data.get("subscriptionType", "unknown")
        result["email"] = auth_data.get("email", "unknown")
    except Exception as e:
        result["auth_error"] = str(e)
        return result

    if not result["auth_ok"]:
        result["action_needed"] = "Run: claude auth login"
        return result

    try:
        rate_check = subprocess.run(
            ["claude", "-p", "hi", "--output-format", "stream-json",
             "--verbose", "--max-turns", "1"],
            capture_output=True, text=True, timeout=30
        )
        for line in rate_check.stdout.strip().split("\n"):
            try:
                event = json.loads(line)
                if event.get("type") == "rate_limit_event":
                    info = event.get("rate_limit_info", {})
                    result["status"] = info.get("status", "unknown")
                    result["rate_limited"] = (info.get("status") == "rate_limited")
                    result["rate_type"] = info.get("rateLimitType", "unknown")
                    result["overage"] = info.get("overageStatus", "unknown")

                    resets_at = info.get("resetsAt", 0)
                    if resets_at:
                        reset_dt = datetime.fromtimestamp(resets_at, tz=timezone.utc)
                        now = datetime.now(timezone.utc)
                        hours_left = (reset_dt - now).total_seconds() / 3600
                        result["resets_at"] = reset_dt.strftime("%Y-%m-%d %H:%M UTC")
                        result["hours_until_reset"] = round(hours_left, 1)
                    break
            except json.JSONDecodeError:
                continue
    except Exception as e:
        result["rate_check_error"] = str(e)

    return result


def check_codex():
    """Check Codex CLI auth status."""
    result = {"tool": "Codex CLI", "auth_ok": False}

    try:
        auth = subprocess.run(
            ["codex", "login", "status"],
            capture_output=True, text=True, timeout=10
        )
        # PITFALL: codex login status outputs to STDERR, not stdout
        output = (auth.stdout.strip() or auth.stderr.strip())
        result["auth_ok"] = "logged in" in output.lower()
        result["status_message"] = output
    except Exception as e:
        result["auth_error"] = str(e)
        return result

    if not result["auth_ok"]:
        result["action_needed"] = "Run: codex login --device-auth"

    return result


def format_report(claude_result, codex_result):
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    lines = [
        f"OAuth Usage Report — {now}",
        "=" * 50, "",
        "--- Claude Code ---",
    ]

    if claude_result.get("auth_error"):
        lines.append(f"  Auth check failed: {claude_result['auth_error']}")
    elif not claude_result["auth_ok"]:
        lines.append("  Auth: EXPIRED")
        lines.append(f"  Action: {claude_result.get('action_needed', 'Re-authenticate')}")
    else:
        lines.append(f"  Auth: OK ({claude_result.get('subscription', '?')} plan)")
        lines.append(f"  Email: {claude_result.get('email', '?')}")
        status = claude_result.get("status", "unknown")
        lines.append(f"  Rate limit status: {status.upper()}")
        if claude_result.get("resets_at"):
            lines.append(f"  Resets at: {claude_result['resets_at']} ({claude_result['hours_until_reset']}h from now)")
        if claude_result["rate_limited"]:
            lines.append("  >>> WARNING: RATE LIMITED — wait for reset!")

    lines.extend(["", "--- Codex CLI ---"])

    if codex_result.get("auth_error"):
        lines.append(f"  Auth check failed: {codex_result['auth_error']}")
    elif not codex_result["auth_ok"]:
        lines.append("  Auth: EXPIRED")
        lines.append(f"  Action: {codex_result.get('action_needed', 'Re-authenticate')}")
    else:
        lines.append(f"  Auth: OK ({codex_result.get('status_message', 'logged in')})")
        lines.append("  Note: Codex does not expose remaining quota or reset times.")

    issues = []
    if not claude_result["auth_ok"]:
        issues.append("Claude Code auth expired")
    if claude_result.get("rate_limited"):
        issues.append(f"Claude Code rate limited (resets {claude_result.get('resets_at', '?')})")
    if not codex_result["auth_ok"]:
        issues.append("Codex auth expired")

    lines.extend(["", "--- Summary ---"])
    if issues:
        lines.append("ISSUES FOUND:")
        for issue in issues:
            lines.append(f"  - {issue}")
    else:
        lines.append("All systems OK.")
    lines.append("")
    return "\n".join(lines)


if __name__ == "__main__":
    claude_result = check_claude_code()
    codex_result = check_codex()
    report = format_report(claude_result, codex_result)
    print(report)
    has_issues = (
        not claude_result["auth_ok"]
        or claude_result.get("rate_limited")
        or not codex_result["auth_ok"]
    )
    sys.exit(1 if has_issues else 0)
