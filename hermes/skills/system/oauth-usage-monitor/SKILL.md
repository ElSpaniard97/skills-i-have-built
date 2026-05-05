---
name: oauth-usage-monitor
description: Check Claude Code and Codex CLI OAuth usage levels, warn when running low, and show when limits reset.
version: "1.0"
platforms: [linux, macos]
metadata:
  hermes:
    tags: [oauth, usage, rate-limit, claude-code, codex, monitoring]
    category: system
---

# OAuth Usage Monitor — Claude Code & Codex CLI

## When to Use

- User asks about remaining usage, rate limits, or quota
- Before starting a large coding task, to verify capacity
- When Claude Code or Codex returns rate limit errors
- As a periodic check (cron job) to alert before hitting limits
- User asks "when does my usage reset?"

## How Usage Limits Work

### Claude Code (Pro Plan — $20/mo)

- **Rate limit window:** 5 hours (rolling)
- **Reset:** Every 5 hours from first use in the window
- **No hard token cap disclosed** — usage is metered internally
- **Overage:** Rejected (org_level_disabled by default on Pro)
- **Detection:** The `rate_limit_event` in stream-json output shows exact status

### Codex CLI (ChatGPT Plus/Pro)

- **Rate limit window:** Tied to ChatGPT subscription tier
- **No public API for checking remaining quota**
- **Detection:** Codex returns errors when rate limited; no preemptive check available
- **Usage data:** Only available per-request in `turn.completed` events (token counts)

## Checking Usage

### Claude Code — Full Usage Check

```bash
claude -p "hi" --output-format stream-json --verbose --max-turns 1 2>&1 | \
  grep '"rate_limit_event"' | \
  python3 -c "
import sys, json
from datetime import datetime, timezone
for line in sys.stdin:
    d = json.loads(line)
    info = d.get('rate_limit_info', {})
    status = info.get('status', 'unknown')
    resets_at = info.get('resetsAt', 0)
    rate_type = info.get('rateLimitType', 'unknown')
    overage = info.get('overageStatus', 'unknown')
    using_overage = info.get('isUsingOverage', False)
    
    reset_dt = datetime.fromtimestamp(resets_at, tz=timezone.utc)
    now = datetime.now(timezone.utc)
    remaining = reset_dt - now
    hours = remaining.total_seconds() / 3600
    
    print(f'Status:        {status}')
    print(f'Rate type:     {rate_type}')
    print(f'Resets at:     {reset_dt.strftime(\"%Y-%m-%d %H:%M UTC\")}')
    print(f'Time left:     {hours:.1f} hours')
    print(f'Overage:       {overage}')
    print(f'Using overage: {using_overage}')
    
    if status == 'rate_limited':
        print('')
        print('WARNING: RATE LIMITED — wait for reset or upgrade plan')
    elif status == 'allowed':
        print('')
        print('OK: Usage within limits')
"
```

**Key `rate_limit_info` fields:**
- `status`: "allowed" (good) or "rate_limited" (hit the wall)
- `resetsAt`: Unix epoch timestamp when the 5-hour window resets
- `rateLimitType`: "five_hour" for Pro plan
- `overageStatus`: "rejected" means no overage allowed
- `isUsingOverage`: false on Pro (overage is a Max plan feature)

### Codex CLI — Usage Check

Codex doesn't expose a rate limit endpoint. Check per-request usage:

```bash
cd /tmp/hermes-setup-guide && \
codex exec "say hi" --json 2>&1 | \
  grep '"turn.completed"' | \
  python3 -c "
import sys, json
for line in sys.stdin:
    d = json.loads(line)
    usage = d.get('usage', {})
    print(f'Input tokens:  {usage.get(\"input_tokens\", 0):,}')
    print(f'Cached input:  {usage.get(\"cached_input_tokens\", 0):,}')
    print(f'Output tokens: {usage.get(\"output_tokens\", 0):,}')
    print(f'Reasoning:     {usage.get(\"reasoning_output_tokens\", 0):,}')
    print('')
    print('Note: Codex does not expose remaining quota or reset time.')
    print('If rate limited, Codex will return an error on the next request.')
"
```

**When Codex is rate limited:**
- Exec commands fail with a rate limit error message
- The fix is to wait (usually resets within minutes to hours depending on tier)

## Combined Check Script

Save as `~/.hermes/scripts/check-oauth-usage.sh`:

```bash
#!/bin/bash
# Combined OAuth usage check for Claude Code and Codex CLI

echo "============================================"
echo "  OAuth Usage Report — $(date '+%Y-%m-%d %H:%M %Z')"
echo "============================================"
echo ""

# --- Claude Code ---
echo "--- Claude Code ---"
CLAUDE_AUTH=$(claude auth status 2>&1)
if echo "$CLAUDE_AUTH" | grep -q '"loggedIn": true'; then
    SUB_TYPE=$(echo "$CLAUDE_AUTH" | python3 -c "import sys,json; print(json.load(sys.stdin).get('subscriptionType','unknown'))" 2>/dev/null)
    echo "Auth: OK ($SUB_TYPE plan)"
    
    # Get rate limit info
    RATE_INFO=$(claude -p "hi" --output-format stream-json --verbose --max-turns 1 2>&1 | grep '"rate_limit_event"')
    if [ -n "$RATE_INFO" ]; then
        echo "$RATE_INFO" | python3 -c "
import sys, json
from datetime import datetime, timezone
for line in sys.stdin:
    d = json.loads(line)
    info = d.get('rate_limit_info', {})
    status = info.get('status', 'unknown')
    resets_at = info.get('resetsAt', 0)
    reset_dt = datetime.fromtimestamp(resets_at, tz=timezone.utc)
    now = datetime.now(timezone.utc)
    hours_left = (reset_dt - now).total_seconds() / 3600
    print(f'Status: {status.upper()}')
    print(f'Resets: {reset_dt.strftime(\"%Y-%m-%d %H:%M UTC\")} ({hours_left:.1f}h from now)')
    if status == 'rate_limited':
        print('>>> WARNING: RATE LIMITED — wait for reset!')
" 2>/dev/null
    else
        echo "Could not retrieve rate limit info"
    fi
else
    echo "Auth: EXPIRED — run: claude auth login"
fi

echo ""

# --- Codex CLI ---
echo "--- Codex CLI ---"
CODEX_AUTH=$(codex login status 2>&1)
if echo "$CODEX_AUTH" | grep -qi "logged in"; then
    echo "Auth: OK ($CODEX_AUTH)"
    echo "Note: Codex does not expose remaining quota. Will error if rate limited."
else
    echo "Auth: EXPIRED — run: codex login --device-auth"
fi

echo ""
echo "============================================"
```

## Interpreting Results

| Claude Code Status | Meaning | Action |
|-------------------|---------|--------|
| `allowed` | Usage within limits | All good |
| `rate_limited` | Hit the 5-hour window cap | Wait for `resetsAt` time |
| Auth expired | OAuth session no longer valid | Run `claude auth login` |

| Codex Status | Meaning | Action |
|-------------|---------|--------|
| Logged in | Auth valid, no known rate limit | All good |
| Rate limit error on exec | Hit usage cap | Wait (varies by tier) |
| Not logged in | OAuth expired | Run `codex login --device-auth` |

## Reset Schedule

- **Claude Code Pro:** 5-hour rolling window. `resetsAt` epoch in rate_limit_event tells you exactly when.
- **Claude Code Max:** Same 5-hour window but with higher limits and optional overage.
- **Codex (ChatGPT Plus):** Varies; OpenAI doesn't publish exact reset times. Generally resets within a few hours.
- **Codex (ChatGPT Pro):** Higher limits, same opacity on reset timing.

## Pitfalls

- The Claude Code usage check makes a real API call (`claude -p "hi"`) which itself costs ~$0.006-0.03 — don't check every minute
- Codex exec must run inside a git repo directory, otherwise it fails with "Not inside a trusted directory"
- The `resetsAt` field from Claude is a Unix epoch in seconds — convert with `datetime.fromtimestamp()`
- Claude Code `--bare` mode uses API key auth, not OAuth — its rate limits are separate from the Pro plan
- After hitting Claude rate limits, the `status` field changes to `rate_limited` but the API call still "succeeds" as a check — it just won't let you do real work
- `codex login status` outputs to STDERR, not stdout — when using subprocess, check both `stdout` and `stderr`
- The monitoring script lives at `~/.hermes/scripts/check-oauth-usage.py` — run it directly or via cron
- A copy is also stored in this skill at `scripts/check-oauth-usage.py` for reference
- Hermes cron job `oauth-usage-check` runs the script every 2 hours automatically
