#!/usr/bin/env bash
set -euo pipefail

# Usage: generate.sh "<prompt>" [channel_id] [aspect_ratio]
# Default channel: #images (1497631859058806906)
# aspect_ratio: landscape | square | portrait  (default: square)
PROMPT="${1:-}"
CHANNEL_ID="${2:-1497631859058806906}"
ASPECT="${3:-square}"

if [ -z "$PROMPT" ]; then
  echo "Usage: generate.sh \"<prompt>\" [channel_id] [aspect_ratio]"
  exit 1
fi

FAL_KEY=$(grep "^FAL_KEY=" ~/.hermes/.env | cut -d= -f2 | tr -d '\n\r')
DISCORD_BOT_TOKEN=$(grep "^DISCORD_BOT_TOKEN=" ~/.hermes/.env | cut -d= -f2 | tr -d '\n\r')

if [ -z "$FAL_KEY" ]; then
  echo "Error: FAL_KEY not found in ~/.hermes/.env"
  exit 1
fi

# Map aspect_ratio name to FAL ratio string
case "$ASPECT" in
  landscape) FAL_ASPECT="16:9" ;;
  portrait)  FAL_ASPECT="9:16" ;;
  *)         FAL_ASPECT="1:1"  ;;
esac

echo "Generating image with FAL nano-banana-pro (Gemini 3 Pro)..."

PROMPT_JSON=$(python3 -c "import sys, json; print(json.dumps(sys.argv[1]))" "$PROMPT")

RESPONSE=$(curl -s -X POST "https://fal.run/fal-ai/nano-banana-pro" \
  -H "Authorization: Key $FAL_KEY" \
  -H "Content-Type: application/json" \
  -d "{
    \"prompt\": $PROMPT_JSON,
    \"aspect_ratio\": \"$FAL_ASPECT\",
    \"num_images\": 1,
    \"output_format\": \"png\",
    \"safety_tolerance\": \"5\",
    \"resolution\": \"1K\"
  }")

IMAGE_URL=$(echo "$RESPONSE" | python3 -c "import sys, json; d=json.load(sys.stdin); print(d['images'][0]['url'])" 2>/dev/null || echo "")

if [ -z "$IMAGE_URL" ]; then
  ERROR=$(echo "$RESPONSE" | python3 -c "import sys, json; d=json.load(sys.stdin); print(d.get('detail', d.get('error', str(d))))" 2>/dev/null || echo "Unknown error")
  echo "Error from FAL: $ERROR"
  curl -s -X POST \
    -H "Authorization: Bot $DISCORD_BOT_TOKEN" \
    -H "Content-Type: application/json" \
    "https://discord.com/api/v10/channels/$CHANNEL_ID/messages" \
    -d "{\"content\": \"❌ Image generation failed: $(echo "$ERROR" | head -c 200)\"}" > /dev/null
  exit 1
fi

TMP_FILE=$(mktemp /tmp/fal_XXXXXX.png)
curl -sf "$IMAGE_URL" -o "$TMP_FILE"

CAPTION_JSON=$(python3 -c "import sys, json; print(json.dumps('🎨 **' + sys.argv[1] + '**'))" "$PROMPT")

curl -s -X POST \
  -H "Authorization: Bot $DISCORD_BOT_TOKEN" \
  "https://discord.com/api/v10/channels/$CHANNEL_ID/messages" \
  -F "payload_json={\"content\": $CAPTION_JSON}" \
  -F "files[0]=@$TMP_FILE;type=image/png" > /dev/null

rm -f "$TMP_FILE"
echo "Image sent to Discord channel $CHANNEL_ID"
