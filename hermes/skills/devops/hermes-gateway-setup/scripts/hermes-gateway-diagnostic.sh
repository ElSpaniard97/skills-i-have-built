#!/bin/bash
# hermes-gateway-diagnostic.sh
# Quick diagnostic tool to check gateway status and config issues
# Usage: bash scripts/hermes-gateway-diagnostic.sh

set -e

echo "╔════════════════════════════════════════════════════════════╗"
echo "║   Hermes Gateway Diagnostic Tool                           ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# 1. Check if hermes is installed
echo "▸ Checking Hermes installation..."
if ! command -v hermes &> /dev/null; then
  echo "  ✗ hermes CLI not found in PATH"
  exit 1
fi
echo "  ✓ hermes CLI found"
echo ""

# 2. Check gateway service status
echo "▸ Gateway service status..."
if systemctl --user is-active --quiet hermes-gateway.service 2>/dev/null; then
  echo "  ✓ Service is running"
  systemctl --user status hermes-gateway.service --no-pager | head -8
else
  echo "  ✗ Service is NOT running"
  echo "    To install: hermes gateway install"
  echo "    To start: hermes gateway start"
fi
echo ""

# 3. Check .env file
echo "▸ Checking ~/.hermes/.env configuration..."
if [ ! -f ~/.hermes/.env ]; then
  echo "  ✗ ~/.hermes/.env not found"
  exit 1
fi

# Count configured platforms
DISCORD_COUNT=$(grep -c "^DISCORD_BOT_TOKEN=" ~/.hermes/.env || echo 0)
TELEGRAM_COUNT=$(grep -c "^TELEGRAM_BOT_TOKEN=" ~/.hermes/.env || echo 0)
SLACK_COUNT=$(grep -c "^SLACK_BOT_TOKEN=" ~/.hermes/.env || echo 0)

if [ "$DISCORD_COUNT" -gt 0 ]; then
  echo "  ✓ Discord bot token configured"
  DISCORD_TOKEN=$(grep "^DISCORD_BOT_TOKEN=" ~/.hermes/.env | cut -d= -f2)
  TOKEN_LEN=${#DISCORD_TOKEN}
  echo "    Token length: $TOKEN_LEN chars (should be ~80+)"
  if [[ $DISCORD_TOKEN == *"."* ]]; then
    echo "    ✓ Token has dot separator (correct format)"
  else
    echo "    ✗ Token missing dot separator (may be invalid)"
  fi
else
  echo "  ✗ No Discord bot token configured"
fi

if [ "$TELEGRAM_COUNT" -gt 0 ]; then
  echo "  ✓ Telegram bot token configured"
else
  echo "  ○ Telegram bot token not configured"
fi

if [ "$SLACK_COUNT" -gt 0 ]; then
  echo "  ✓ Slack bot token configured"
else
  echo "  ○ Slack bot token not configured"
fi
echo ""

# 4. Check allowlist
echo "▸ Checking user allowlist..."
ALLOW_ALL=$(grep "^GATEWAY_ALLOW_ALL_USERS=" ~/.hermes/.env | cut -d= -f2)
DISCORD_USERS=$(grep "^DISCORD_ALLOWED_USERS=" ~/.hermes/.env | cut -d= -f2)

if [ "$ALLOW_ALL" = "true" ]; then
  echo "  ✓ Gateway allows all users (GATEWAY_ALLOW_ALL_USERS=true)"
elif [ -n "$DISCORD_USERS" ]; then
  echo "  ✓ Discord allowlist configured: $DISCORD_USERS"
else
  echo "  ⚠ No user allowlist configured — bots may reject all messages"
  echo "    Set DISCORD_ALLOWED_USERS or GATEWAY_ALLOW_ALL_USERS=true"
fi
echo ""

# 5. Check recent logs
echo "▸ Recent gateway logs (last 10 lines)..."
if journalctl --user -u hermes-gateway -n 10 --no-pager 2>/dev/null | grep -q "ERROR\|LoginFailure"; then
  echo "  ✗ Errors detected:"
  journalctl --user -u hermes-gateway -n 10 --no-pager | grep "ERROR\|LoginFailure\|Unauthorized"
else
  echo "  ✓ No recent errors"
fi
echo ""

echo "╔════════════════════════════════════════════════════════════╗"
echo "║   Next Steps                                               ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo "If service is not running:"
echo "  hermes gateway install"
echo "  hermes gateway start"
echo ""
echo "If token errors appear:"
echo "  1. Go to Discord Developer Portal: https://discord.com/developers/applications"
echo "  2. Select your bot application"
echo "  3. Go to Bot → TOKEN → Reset Token"
echo "  4. Copy new token to ~/.hermes/.env (DISCORD_BOT_TOKEN=...)"
echo "  5. hermes gateway restart"
echo ""
echo "To view live logs:"
echo "  journalctl --user -u hermes-gateway -f"
echo ""
