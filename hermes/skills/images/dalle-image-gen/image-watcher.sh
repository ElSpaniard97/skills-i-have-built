#!/usr/bin/env bash
# Watches #images channel for image generation requests and fires generate.sh directly.
# Runs as a background service — bypasses Achilles tool-call entirely.

CHANNEL_ID="1497631859058806906"
STATE_FILE="$HOME/.hermes/skills/images/dalle-image-gen/.last_message_id"
SKILL_DIR="$HOME/.hermes/skills/images/dalle-image-gen"
DISCORD_BOT_TOKEN=$(grep "^DISCORD_BOT_TOKEN=" ~/.hermes/.env | cut -d= -f2 | tr -d '\n\r')

# Keywords that trigger image generation
IMAGE_KEYWORDS="generate|create|draw|make|show|paint|sketch|render|imagine|produce"

# Phrases that indicate an image request (require "image" OR "picture" OR "photo" near a keyword)
# OR starts with generate/draw/create/make/show me/paint/sketch directly

is_image_request() {
  local msg="$1"
  local lower
  lower=$(echo "$msg" | tr '[:upper:]' '[:lower:]')

  # Explicit image words
  echo "$lower" | grep -qE "(generate|create|draw|make|paint|sketch|render|imagine).*(image|picture|photo|pic|art|illustration|portrait|scene)" && return 0
  echo "$lower" | grep -qE "(image|picture|photo|pic|art|illustration) of" && return 0
  # Starts with "generate" or "draw" etc. as a command
  echo "$lower" | grep -qE "^(generate|draw|create|make|paint|sketch|render|show me|give me).{5,}" && return 0

  return 1
}

extract_prompt() {
  local msg="$1"
  # Strip common prefixes
  echo "$msg" | sed -E \
    's/^[Gg]enerate (an? )?(image|picture|photo|pic|art|illustration|portrait|scene)? ?(of )?//i;
     s/^[Dd]raw (an? )?(image|picture|photo|pic|art|illustration|portrait|scene)? ?(of )?//i;
     s/^[Cc]reate (an? )?(image|picture|photo|pic|art|illustration|portrait|scene)? ?(of )?//i;
     s/^[Mm]ake (an? )?(image|picture|photo|pic|art|illustration|portrait|scene)? ?(of )?//i;
     s/^[Pp]aint (an? )?(image|picture|photo|pic|art|illustration|portrait|scene)? ?(of )?//i;
     s/^[Ss]ketch (an? )?(image|picture|photo|pic|art|illustration|portrait|scene)? ?(of )?//i;
     s/^[Ss]how me (an? )?(image|picture|photo|pic|art|illustration|portrait|scene)? ?(of )?//i' \
  | sed 's/^[[:space:]]*//'
}

# Load last seen message ID
LAST_ID=""
[ -f "$STATE_FILE" ] && LAST_ID=$(cat "$STATE_FILE")

echo "[image-watcher] Started. Watching channel $CHANNEL_ID. Last ID: ${LAST_ID:-none}"

while true; do
  # Fetch latest messages
  AFTER_PARAM=""
  [ -n "$LAST_ID" ] && AFTER_PARAM="&after=$LAST_ID"

  MESSAGES=$(curl -sf \
    -H "Authorization: Bot $DISCORD_BOT_TOKEN" \
    "https://discord.com/api/v10/channels/$CHANNEL_ID/messages?limit=10${AFTER_PARAM}" 2>/dev/null || echo "[]")

  # Parse and process (messages come newest-first, reverse to process in order)
  echo "$MESSAGES" | python3 -c "
import sys, json
msgs = json.load(sys.stdin)
# Reverse to process oldest first
for m in reversed(msgs):
    is_bot = m.get('author', {}).get('bot', False)
    content = m.get('content', '')
    msg_id = m.get('id', '')
    username = m.get('author', {}).get('username', '')
    print(f'{msg_id}|{\"bot\" if is_bot else \"user\"}|{username}|{content}')
" 2>/dev/null | while IFS='|' read -r msg_id author_type username content; do
    [ -z "$msg_id" ] && continue

    # Update last seen ID
    LAST_ID="$msg_id"
    echo "$LAST_ID" > "$STATE_FILE"

    # Skip bot messages
    [ "$author_type" = "bot" ] && continue

    # Check if this is an image request
    if is_image_request "$content"; then
      PROMPT=$(extract_prompt "$content")
      echo "[image-watcher] Image request from $username: $PROMPT"
      # Run generate.sh in background
      export PATH="$HOME/.local/bin:$PATH"
      bash "$SKILL_DIR/generate.sh" "$PROMPT" "$CHANNEL_ID" &
    fi
  done

  # Update LAST_ID from state file (updated inside subshell above)
  [ -f "$STATE_FILE" ] && LAST_ID=$(cat "$STATE_FILE")

  sleep 8
done
