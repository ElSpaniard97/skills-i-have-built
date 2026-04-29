#!/usr/bin/env bash
set -euo pipefail

# Usage: transcribe.sh "<youtube_url>" [channel_id]
URL="${1:-}"
CHANNEL_ID="${2:-1497941305710346291}"  # #youtube-transcripts

if [ -z "$URL" ]; then
  echo "Usage: transcribe.sh \"<youtube_url>\" [channel_id]"
  exit 1
fi

PYTHON="$HOME/.hermes/venv/bin/python3"
export PATH="$HOME/.local/bin:$PATH"
DISCORD_BOT_TOKEN=$(grep "^DISCORD_BOT_TOKEN=" ~/.hermes/.env | cut -d= -f2 | tr -d '\n\r')
OPENAI_API_KEY=$(grep "^OPENAI_API_KEY=" ~/.hermes/.env | cut -d= -f2 | tr -d '\n\r')
TRANSCRIPTS_DIR="$HOME/hermes-transcripts"
mkdir -p "$TRANSCRIPTS_DIR"

# Send a Discord message
send_discord() {
  local msg="$1"
  local escaped
  escaped=$($PYTHON -c "import sys, json; print(json.dumps(sys.argv[1]))" "$msg")
  curl -s -X POST \
    -H "Authorization: Bot $DISCORD_BOT_TOKEN" \
    -H "Content-Type: application/json" \
    "https://discord.com/api/v10/channels/$CHANNEL_ID/messages" \
    -d "{\"content\": $escaped}" > /dev/null
}

# Send a file to Discord
send_discord_file() {
  local file="$1"
  local caption="$2"
  local escaped_caption
  escaped_caption=$($PYTHON -c "import sys, json; print(json.dumps(sys.argv[1]))" "$caption")
  curl -s -X POST \
    -H "Authorization: Bot $DISCORD_BOT_TOKEN" \
    "https://discord.com/api/v10/channels/$CHANNEL_ID/messages" \
    -F "payload_json={\"content\": $escaped_caption}" \
    -F "files[0]=@$file;type=text/plain" > /dev/null
}

echo "Extracting video info..."

# Extract video ID and title
VIDEO_INFO=$($PYTHON -c "
import sys, re, json
import urllib.request

url = sys.argv[1]

# Extract video ID
patterns = [
    r'(?:v=|youtu\.be/|embed/|shorts/)([A-Za-z0-9_-]{11})',
]
video_id = None
for p in patterns:
    m = re.search(p, url)
    if m:
        video_id = m.group(1)
        break

if not video_id:
    print(json.dumps({'error': 'Could not extract video ID from URL'}))
    sys.exit(1)

# Get title via oembed
try:
    oembed_url = f'https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v={video_id}&format=json'
    req = urllib.request.urlopen(oembed_url, timeout=10)
    data = json.loads(req.read())
    title = data.get('title', video_id)
    author = data.get('author_name', 'Unknown')
except:
    title = video_id
    author = 'Unknown'

print(json.dumps({'video_id': video_id, 'title': title, 'author': author}))
" "$URL" 2>/dev/null)

VIDEO_ID=$($PYTHON -c "import sys,json; print(json.loads(sys.argv[1]).get('video_id',''))" "$VIDEO_INFO" 2>/dev/null || echo "")
TITLE=$($PYTHON -c "import sys,json; print(json.loads(sys.argv[1]).get('title','Unknown'))" "$VIDEO_INFO" 2>/dev/null || echo "Unknown")
AUTHOR=$($PYTHON -c "import sys,json; print(json.loads(sys.argv[1]).get('author','Unknown'))" "$VIDEO_INFO" 2>/dev/null || echo "Unknown")

if [ -z "$VIDEO_ID" ]; then
  send_discord "❌ Could not extract video ID from: $URL"
  exit 1
fi

# Safe filename
SAFE_TITLE=$($PYTHON -c "
import sys, re
t = sys.argv[1]
t = re.sub(r'[^\w\s-]', '', t).strip()
t = re.sub(r'[\s]+', '_', t)
print(t[:80])
" "$TITLE")

OUTPUT_FILE="$TRANSCRIPTS_DIR/${SAFE_TITLE}_${VIDEO_ID}.pdf"

# Check if already transcribed
if [ -f "$OUTPUT_FILE" ]; then
  send_discord "📄 Already transcribed: **$TITLE**
Saved at: \`$OUTPUT_FILE\`"
  exit 0
fi

send_discord "⏳ Transcribing: **$TITLE** by $AUTHOR..."

# METHOD 1: Try youtube-transcript-api (free, uses YouTube captions)
TRANSCRIPT=$($PYTHON -c "
import sys, json
from youtube_transcript_api import YouTubeTranscriptApi

video_id = sys.argv[1]
try:
    api = YouTubeTranscriptApi()
    try:
        fetched = api.fetch(video_id, languages=['en'])
    except Exception:
        fetched = api.fetch(video_id)
    text = '\n'.join(s.text for s in fetched.snippets)
    print(json.dumps({'success': True, 'text': text, 'method': 'youtube-captions'}))
except Exception as e:
    print(json.dumps({'success': False, 'error': str(e)}))
" "$VIDEO_ID" 2>/dev/null)

CAPTION_SUCCESS=$(printf '%s' "$TRANSCRIPT" | $PYTHON -c "import sys,json; print(json.loads(sys.stdin.read()).get('success',False))" 2>/dev/null || echo "False")

if [ "$CAPTION_SUCCESS" = "True" ]; then
  METHOD="YouTube captions"
  TRANSCRIPT_TEXT=$(printf '%s' "$TRANSCRIPT" | $PYTHON -c "import sys,json; print(json.loads(sys.stdin.read()).get('text',''))")
else
  # METHOD 2: Download audio and transcribe with OpenAI Whisper
  echo "No captions found, falling back to Whisper..."
  send_discord "💬 No captions found — downloading audio for Whisper transcription..."

  TMP_DIR=$(mktemp -d /tmp/yt_audio_XXXXXX)
  TMP_AUDIO="$TMP_DIR/audio.%(ext)s"

  $HOME/.hermes/venv/bin/yt-dlp \
    -x --audio-format mp3 \
    --audio-quality 5 \
    -o "$TMP_AUDIO" \
    --no-playlist \
    "$URL" 2>&1 | tail -3 || {
      send_discord "❌ Failed to download audio from: $URL"
      rm -rf "$TMP_DIR"
      exit 1
    }

  # Find the downloaded audio file
  ACTUAL_AUDIO=$(find "$TMP_DIR" -name "*.mp3" -o -name "*.m4a" -o -name "*.opus" 2>/dev/null | head -1)

  if [ -z "$ACTUAL_AUDIO" ]; then
    send_discord "❌ Audio download failed for: $URL"
    rm -rf "$TMP_DIR"
    exit 1
  fi

  export OPENAI_API_KEY
  TRANSCRIPT_TEXT=$($PYTHON -c "
import sys
from openai import OpenAI
import os

client = OpenAI(api_key=os.environ['OPENAI_API_KEY'])
with open(sys.argv[1], 'rb') as audio_file:
    result = client.audio.transcriptions.create(
        model='whisper-1',
        file=audio_file,
        response_format='text'
    )
print(result)
" "$ACTUAL_AUDIO")

  rm -rf "$TMP_DIR"

  rm -f "$TMP_AUDIO" "$ACTUAL_AUDIO" 2>/dev/null || true
  METHOD="OpenAI Whisper"
fi

# Build the PDF transcript
DATE=$(date +"%Y-%m-%d %H:%M")
WORD_COUNT=$(echo "$TRANSCRIPT_TEXT" | wc -w)

$PYTHON -c "
import sys
from fpdf import FPDF

title    = sys.argv[1]
author   = sys.argv[2]
url      = sys.argv[3]
video_id = sys.argv[4]
date     = sys.argv[5]
method   = sys.argv[6]
outfile  = sys.argv[7]
text     = sys.stdin.read()

pdf = FPDF()
pdf.set_auto_page_break(auto=True, margin=15)
pdf.add_page()

# Title
pdf.set_font('Helvetica', 'B', 16)
pdf.multi_cell(0, 10, title, align='L')
pdf.ln(2)

# Metadata
pdf.set_font('Helvetica', '', 10)
pdf.set_text_color(100, 100, 100)
for line in [f'Author: {author}', f'URL: {url}', f'Video ID: {video_id}', f'Transcribed: {date}  |  Method: {method}']:
    pdf.cell(0, 6, line, new_x='LMARGIN', new_y='NEXT')
pdf.ln(4)

# Divider
pdf.set_draw_color(180, 180, 180)
pdf.line(10, pdf.get_y(), 200, pdf.get_y())
pdf.ln(6)

# Transcript body
pdf.set_font('Helvetica', '', 11)
pdf.set_text_color(0, 0, 0)
pdf.multi_cell(0, 7, text)

pdf.output(outfile)
print('ok')
" "$TITLE" "$AUTHOR" "$URL" "$VIDEO_ID" "$DATE" "$METHOD" "$OUTPUT_FILE" <<< "$TRANSCRIPT_TEXT"

FILE_SIZE=$(du -h "$OUTPUT_FILE" | cut -f1)

# Send summary + file to Discord
SUMMARY="✅ **Transcript complete!**
📹 **$TITLE**
👤 $AUTHOR
🔗 $URL
📊 ~$WORD_COUNT words · $FILE_SIZE
💾 Saved to \`$OUTPUT_FILE\`
🔧 Method: $METHOD"

send_discord "$SUMMARY"

# Post the transcript file if under 8MB Discord limit
FILE_BYTES=$(stat -c%s "$OUTPUT_FILE")
if [ "$FILE_BYTES" -lt 8000000 ]; then
  send_discord_file "$OUTPUT_FILE" "📄 Full transcript (PDF):"
fi

echo "Transcript saved: $OUTPUT_FILE"
