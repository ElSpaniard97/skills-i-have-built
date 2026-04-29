#!/usr/bin/env bash
set -euo pipefail

# Upload a video file to TikTok via Content Posting API v2.
# Requires TIKTOK_ACCESS_TOKEN in ~/.hermes/.env
#
# Usage: upload-tiktok.sh <video_file> <caption>

VIDEO_FILE="${1:-}"
CAPTION="${2:-}"

if [ -z "$VIDEO_FILE" ] || [ ! -f "$VIDEO_FILE" ]; then
  echo "Usage: upload-tiktok.sh <video_file> <caption>"
  exit 1
fi

TIKTOK_ACCESS_TOKEN=$(grep "^TIKTOK_ACCESS_TOKEN=" ~/.hermes/.env | cut -d= -f2 | tr -d '\n\r')
if [ -z "$TIKTOK_ACCESS_TOKEN" ]; then
  echo "Error: TIKTOK_ACCESS_TOKEN not found in ~/.hermes/.env"
  exit 1
fi

FILE_SIZE=$(stat -c%s "$VIDEO_FILE")
CAPTION_SAFE=$(echo "$CAPTION" | cut -c1-150)

echo "Initializing TikTok upload ($FILE_SIZE bytes)..."

INIT_RESP=$(curl -s -X POST \
  "https://open.tiktokapis.com/v2/post/publish/video/init/" \
  -H "Authorization: Bearer $TIKTOK_ACCESS_TOKEN" \
  -H "Content-Type: application/json; charset=UTF-8" \
  -d "{
    \"post_info\": {
      \"title\": $(python3 -c "import sys,json; print(json.dumps(sys.argv[1]))" "$CAPTION_SAFE"),
      \"privacy_level\": \"PUBLIC_TO_EVERYONE\",
      \"disable_duet\": false,
      \"disable_comment\": false,
      \"disable_stitch\": false,
      \"video_cover_timestamp_ms\": 1000
    },
    \"source_info\": {
      \"source\": \"FILE_UPLOAD\",
      \"video_size\": $FILE_SIZE,
      \"chunk_size\": $FILE_SIZE,
      \"total_chunk_count\": 1
    }
  }")

PUBLISH_ID=$(echo "$INIT_RESP" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('data',{}).get('publish_id',''))" 2>/dev/null || echo "")
UPLOAD_URL=$(echo "$INIT_RESP" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('data',{}).get('upload_url',''))" 2>/dev/null || echo "")

if [ -z "$UPLOAD_URL" ] || [ -z "$PUBLISH_ID" ]; then
  ERR=$(echo "$INIT_RESP" | python3 -c "import sys,json; d=json.load(sys.stdin); print(str(d.get('error', d))[:300])" 2>/dev/null || echo "Unknown error")
  echo "TikTok init failed: $ERR"
  exit 1
fi

echo "Upload URL obtained. Uploading video..."
LAST_BYTE=$((FILE_SIZE - 1))

HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" -X PUT "$UPLOAD_URL" \
  -H "Content-Range: bytes 0-${LAST_BYTE}/${FILE_SIZE}" \
  -H "Content-Length: $FILE_SIZE" \
  -H "Content-Type: video/mp4" \
  --data-binary "@$VIDEO_FILE")

if [ "$HTTP_STATUS" != "201" ] && [ "$HTTP_STATUS" != "200" ]; then
  echo "TikTok upload failed with HTTP $HTTP_STATUS"
  exit 1
fi

echo "Video uploaded to TikTok (publish_id: $PUBLISH_ID)"

# Poll publish status
echo "Waiting for TikTok to process video..."
for i in $(seq 1 12); do
  sleep 10
  STATUS_RESP=$(curl -s -X POST \
    "https://open.tiktokapis.com/v2/post/publish/status/fetch/" \
    -H "Authorization: Bearer $TIKTOK_ACCESS_TOKEN" \
    -H "Content-Type: application/json; charset=UTF-8" \
    -d "{\"publish_id\": \"$PUBLISH_ID\"}")
  STATUS=$(echo "$STATUS_RESP" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('data',{}).get('status',''))" 2>/dev/null || echo "")
  echo "  TikTok status: $STATUS"
  if [ "$STATUS" = "PUBLISH_COMPLETE" ]; then
    echo "TikTok upload complete!"
    exit 0
  fi
  if [ "$STATUS" = "FAILED" ]; then
    FAIL_CODE=$(echo "$STATUS_RESP" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('data',{}).get('fail_reason','unknown'))" 2>/dev/null || echo "unknown")
    echo "TikTok processing failed: $FAIL_CODE"
    exit 1
  fi
done

echo "TikTok upload submitted (processing may still be in progress)"
