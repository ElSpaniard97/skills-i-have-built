---
name: oauth-reauth
description: Detect expired OAuth sessions for Claude Code and Codex CLI, and prompt the user to re-authenticate.
version: "1.0"
platforms: [linux, macos]
metadata:
  hermes:
    tags: [oauth, auth, claude-code, codex, session, maintenance]
    category: system
---

# OAuth Re-Authentication — Claude Code & Codex CLI

## When to Use

- User reports "auth expired", "login failed", "unauthorized", or "session expired" for Claude Code or Codex
- A cron job or script detects an auth failure from either tool
- Before delegating work to Claude Code or Codex, to verify auth is valid
- When `claude auth status` shows not logged in or `codex login status` shows not logged in

## Detecting Expired Auth

### Claude Code

```bash
# Check auth status (JSON)
claude auth status
# Returns: {"loggedIn": true/false, "authMethod": "claude.ai", "subscriptionType": "pro", ...}

# Human-readable
claude auth status --text
# Returns: "Login method: Claude Pro account" or error if expired

# Quick test — if this fails with auth error, OAuth is expired
claude -p "test" --output-format json --max-turns 1 --bare 2>&1
# Look for: "api_error_status": 401 or "subtype": "error"
# Stream events show: "type": "system", "subtype": "api_retry" with "error": "billing_error"
```

**Signs of expired Claude Code OAuth:**
- `claude auth status` returns `{"loggedIn": false}`
- Any API call returns 401 Unauthorized
- Stream events show `api_retry` with auth-related errors
- Error message: "Your session has expired" or "Please log in again"

### Codex CLI

```bash
# Check login status
codex login status
# Returns: "Logged in using ChatGPT" or "Not logged in"

# Quick test — run in a git repo
cd /tmp/hermes-setup-guide && codex exec "say hi" --json 2>&1
# If auth expired, will show login prompt or error
```

**Signs of expired Codex OAuth:**
- `codex login status` shows "Not logged in"
- Any exec command prompts for login instead of running
- Error messages about invalid/expired tokens

## Re-Authentication Steps

### Claude Code — Browser OAuth (Claude Pro/Max)

```bash
# Step 1: Log out cleanly
claude auth logout

# Step 2: Log in via browser OAuth
claude auth login
# This opens a browser window — user must complete the OAuth flow
# If browser doesn't open, it prints a URL to visit manually

# Step 3: Verify
claude auth status --text
# Should show: "Login method: Claude Pro account"
```

**Alternative auth methods:**
```bash
# API key auth (for API billing instead of subscription)
claude auth login --console

# SSO auth (for Enterprise accounts)
claude auth login --sso
```

### Codex CLI — Browser OAuth (ChatGPT Plus/Pro)

```bash
# Step 1: Log out
codex logout

# Step 2: Log in via device auth (browser OAuth)
codex login --device-auth
# This prints a URL and code — user visits the URL and enters the code

# Step 3: Verify
codex login status
# Should show: "Logged in using ChatGPT"
```

**Alternative:**
```bash
# API key auth
printenv OPENAI_API_KEY | codex login --with-api-key
```

## Automated Check Script

Run this to check both tools at once:

```bash
#!/bin/bash
echo "=== Claude Code Auth ==="
CLAUDE_STATUS=$(claude auth status 2>&1)
if echo "$CLAUDE_STATUS" | grep -q '"loggedIn": true'; then
    echo "OK: Logged in"
    echo "$CLAUDE_STATUS" | python3 -c "import sys,json; d=json.load(sys.stdin); print(f'  Method: {d.get(\"authMethod\",\"unknown\")}'); print(f'  Type: {d.get(\"subscriptionType\",\"unknown\")}'); print(f'  Email: {d.get(\"email\",\"unknown\")}')"
else
    echo "EXPIRED: Not logged in — run: claude auth login"
fi

echo ""
echo "=== Codex CLI Auth ==="
CODEX_STATUS=$(codex login status 2>&1)
if echo "$CODEX_STATUS" | grep -qi "logged in"; then
    echo "OK: $CODEX_STATUS"
else
    echo "EXPIRED: Not logged in — run: codex login --device-auth"
fi
```

## Pitfalls

- Claude Code OAuth opens a browser — on headless servers, copy the printed URL manually
- Codex device auth requires visiting a URL and entering a code — it doesn't open a browser automatically
- After re-auth, restart any running Hermes services that depend on these tools (MCP server for Codex uses OPENAI_API_KEY from .env, not Codex OAuth)
- The Hermes MCP Codex server (`mcp_servers.codex` in config.yaml) uses the OPENAI_API_KEY env var, NOT Codex's OAuth. Re-authing Codex CLI doesn't fix MCP auth — update the API key in config.yaml if needed
- Claude Code `--bare` mode skips OAuth and requires ANTHROPIC_API_KEY env var
- `claude auth login` works in a terminal with browser access — it opens the browser automatically. If it can't, it prints an OAuth URL the user can visit manually and paste the code back
- On this system, Claude Code was originally on API key auth ("Claude API account"). After switching to OAuth, `claude auth status` shows "Claude Pro account" with `authMethod: "claude.ai"` and `subscriptionType: "pro"`
- Hermes itself (the agent) still uses ANTHROPIC_API_KEY from ~/.hermes/.env — OAuth is only for Claude Code and Codex CLI tools used directly
