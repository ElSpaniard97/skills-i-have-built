#!/usr/bin/env bash
set -euo pipefail

# Usage: generate.sh "<prompt>" [channel_id] [duration] [aspect_ratio]
# duration: 5 | 10 | 20 | 30  (default: 10)
# aspect_ratio: 9:16 | 16:9 | 1:1  (default: 9:16 — TikTok portrait)
PROMPT="${1:-}"
CHANNEL_ID="${2:-1498055202257768448}"
DURATION="${3:-10}"
ASPECT="${4:-9:16}"

if [ -z "$PROMPT" ]; then
  echo "Usage: generate.sh \"<prompt>\" [channel_id] [duration] [aspect_ratio]"
  exit 1
fi

FAL_KEY=$(grep "^FAL_KEY=" ~/.hermes/.env | cut -d= -f2 | tr -d '\n\r')
DISCORD_BOT_TOKEN=$(grep "^DISCORD_BOT_TOKEN=" ~/.hermes/.env | cut -d= -f2 | tr -d '\n\r')
TIKTOK_ACCESS_TOKEN=$(grep "^TIKTOK_ACCESS_TOKEN=" ~/.hermes/.env | cut -d= -f2 | tr -d '\n\r' 2>/dev/null || echo "")

FFMPEG="${HOME}/.local/bin/ffmpeg"
[ ! -x "$FFMPEG" ] && FFMPEG=$(which ffmpeg 2>/dev/null || echo "")

send_discord_msg() {
  local msg="$1"
  curl -s -X POST \
    -H "Authorization: Bot $DISCORD_BOT_TOKEN" \
    -H "Content-Type: application/json" \
    "https://discord.com/api/v10/channels/$CHANNEL_ID/messages" \
    -d "{\"content\": $(python3 -c "import sys,json; print(json.dumps(sys.argv[1]))" "$msg")}" > /dev/null
}

PROMPT_JSON=$(python3 -c "import sys, json; print(json.dumps(sys.argv[1]))" "$PROMPT")

# Determine number of clips needed (Kling max = 10s per clip)
if [ "$DURATION" -le 10 ]; then
  CLIP_DURATION="$DURATION"
  NUM_CLIPS=1
elif [ "$DURATION" -le 20 ]; then
  CLIP_DURATION="10"
  NUM_CLIPS=2
else
  CLIP_DURATION="10"
  NUM_CLIPS=3
fi

echo "Generating ${DURATION}s video (${NUM_CLIPS} x ${CLIP_DURATION}s clips)..."
send_discord_msg "🎬 Generating **${DURATION}s video**: $PROMPT — hang tight, this takes 2-4 minutes..."

# Submit all clips to FAL queue in parallel
declare -a REQUEST_IDS=()
for i in $(seq 1 $NUM_CLIPS); do
  RESP=$(curl -s -X POST "https://queue.fal.run/fal-ai/kling-video/v2/master/text-to-video" \
    -H "Authorization: Key $FAL_KEY" \
    -H "Content-Type: application/json" \
    -d "{\"prompt\": $PROMPT_JSON, \"duration\": \"$CLIP_DURATION\", \"aspect_ratio\": \"$ASPECT\"}")
  REQ_ID=$(echo "$RESP" | python3 -c "import sys,json; print(json.load(sys.stdin).get('request_id',''))" 2>/dev/null || echo "")
  if [ -z "$REQ_ID" ]; then
    ERR=$(echo "$RESP" | python3 -c "import sys,json; d=json.load(sys.stdin); print(str(d.get('detail',d))[:200])" 2>/dev/null || echo "unknown")
    send_discord_msg "❌ Failed to queue clip $i: $ERR"
    exit 1
  fi
  REQUEST_IDS+=("$REQ_ID")
  echo "Clip $i queued: $REQ_ID"
done

# Poll all clips until complete
declare -a CLIP_FILES=()
TMPDIR_LOCAL=$(mktemp -d /tmp/fal_video_XXXXXX)
trap "rm -rf $TMPDIR_LOCAL" EXIT

for i in $(seq 1 $NUM_CLIPS); do
  REQ_ID="${REQUEST_IDS[$((i-1))]}"
  echo "Polling clip $i ($REQ_ID)..."
  MAX_POLLS=40
  POLL=0
  while [ $POLL -lt $MAX_POLLS ]; do
    sleep 15
    POLL=$((POLL + 1))
    STATUS_RESP=$(curl -s \
      -H "Authorization: Key $FAL_KEY" \
      "https://queue.fal.run/fal-ai/kling-video/v2/master/text-to-video/requests/$REQ_ID/status")
    STATUS=$(echo "$STATUS_RESP" | python3 -c "import sys,json; print(json.load(sys.stdin).get('status',''))" 2>/dev/null || echo "")
    echo "  Clip $i poll $POLL: $STATUS"
    if [ "$STATUS" = "COMPLETED" ]; then break; fi
    if [ "$STATUS" = "FAILED" ]; then
      send_discord_msg "❌ Clip $i generation failed."
      exit 1
    fi
  done
  if [ $POLL -ge $MAX_POLLS ]; then
    send_discord_msg "❌ Clip $i timed out after 10 minutes."
    exit 1
  fi

  RESULT=$(curl -s \
    -H "Authorization: Key $FAL_KEY" \
    "https://queue.fal.run/fal-ai/kling-video/v2/master/text-to-video/requests/$REQ_ID")
  VIDEO_URL=$(echo "$RESULT" | python3 -c "
import sys, json
d = json.load(sys.stdin)
v = d.get('video', {})
if isinstance(v, dict): print(v.get('url', ''))
elif isinstance(v, str): print(v)
else:
    vids = d.get('videos', [])
    print(vids[0].get('url', '') if vids else '')
" 2>/dev/null || echo "")

  if [ -z "$VIDEO_URL" ]; then
    send_discord_msg "❌ Could not extract URL for clip $i."
    exit 1
  fi

  CLIP_FILE="$TMPDIR_LOCAL/clip_${i}.mp4"
  curl -sf "$VIDEO_URL" -o "$CLIP_FILE"
  CLIP_FILES+=("$CLIP_FILE")
  echo "Clip $i downloaded: $CLIP_FILE"
done

# Concatenate clips if more than one
if [ ${#CLIP_FILES[@]} -eq 1 ]; then
  FINAL_VIDEO="${CLIP_FILES[0]}"
else
  echo "Concatenating ${NUM_CLIPS} clips..."
  CONCAT_LIST="$TMPDIR_LOCAL/concat.txt"
  for f in "${CLIP_FILES[@]}"; do
    echo "file '$f'" >> "$CONCAT_LIST"
  done
  FINAL_VIDEO="$TMPDIR_LOCAL/final.mp4"
  "$FFMPEG" -f concat -safe 0 -i "$CONCAT_LIST" -c copy "$FINAL_VIDEO" -y -loglevel error
  echo "Concatenation complete: $FINAL_VIDEO"
fi

FILE_SIZE=$(stat -c%s "$FINAL_VIDEO")
echo "Final video: $FINAL_VIDEO ($FILE_SIZE bytes)"

# Post to Discord
CAPTION_JSON=$(python3 -c "import sys, json; print(json.dumps('🎬 **' + sys.argv[1] + '**'))" "$PROMPT")
curl -s -X POST \
  -H "Authorization: Bot $DISCORD_BOT_TOKEN" \
  "https://discord.com/api/v10/channels/$CHANNEL_ID/messages" \
  -F "payload_json={\"content\": $CAPTION_JSON}" \
  -F "files[0]=@$FINAL_VIDEO;type=video/mp4" > /dev/null
echo "Video posted to Discord channel $CHANNEL_ID"

# Upload to TikTok if credentials are set
if [ -n "$TIKTOK_ACCESS_TOKEN" ]; then
  echo "Uploading to TikTok..."
  bash "$(dirname "$0")/upload-tiktok.sh" "$FINAL_VIDEO" "$PROMPT" && \
    send_discord_msg "✅ Video also uploaded to TikTok!" || \
    send_discord_msg "⚠️ TikTok upload failed — check logs."
fi
