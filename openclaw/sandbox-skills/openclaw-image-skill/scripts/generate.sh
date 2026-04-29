#!/usr/bin/env bash
# generate.sh — Generate an image via DALL-E 3 and download it to disk
# Usage: ./generate.sh "<prompt>" <output_path> [size] [quality]
# Requires: OPENAI_API_KEY env var, curl, jq (optional — uses python fallback if jq absent)

set -euo pipefail

PROMPT="${1:?Usage: $0 '<prompt>' <output_path> [size] [quality]}"
OUTPUT="${2:?Usage: $0 '<prompt>' <output_path>}"
SIZE="${3:-1024x1024}"
QUALITY="${4:-standard}"

if [[ -z "${OPENAI_API_KEY:-}" ]]; then
  echo "Error: OPENAI_API_KEY is not set" >&2
  exit 1
fi

echo "Generating image..." >&2

RESPONSE=$(curl -sf https://api.openai.com/v1/images/generations \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${OPENAI_API_KEY}" \
  -d "{
    \"model\": \"dall-e-3\",
    \"prompt\": $(printf '%s' "$PROMPT" | python3 -c 'import json,sys; print(json.dumps(sys.stdin.read()))'),
    \"n\": 1,
    \"size\": \"${SIZE}\",
    \"quality\": \"${QUALITY}\"
  }")

# Extract URL — try jq first, fall back to python
if command -v jq &>/dev/null; then
  IMAGE_URL=$(echo "$RESPONSE" | jq -r '.data[0].url')
else
  IMAGE_URL=$(echo "$RESPONSE" | python3 -c "import sys,json; print(json.load(sys.stdin)['data'][0]['url'])")
fi

if [[ -z "$IMAGE_URL" || "$IMAGE_URL" == "null" ]]; then
  echo "Error: Failed to get image URL from response:" >&2
  echo "$RESPONSE" >&2
  exit 1
fi

echo "Downloading image to ${OUTPUT}..." >&2
curl -sf "$IMAGE_URL" -o "$OUTPUT"

echo "$OUTPUT"
