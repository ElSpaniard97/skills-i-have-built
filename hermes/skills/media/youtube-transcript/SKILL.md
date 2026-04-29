---
name: youtube-transcript
description: Transcribe any YouTube video posted in the #youtube-transcripts Discord channel. Uses YouTube's built-in captions first; falls back to OpenAI Whisper if none are available. Transcripts are saved to ~/hermes-transcripts/.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [YouTube, Transcription, Media, Discord]
---

# YouTube Transcript Skill

When a YouTube URL is posted in the `#youtube-transcripts` Discord channel, immediately transcribe it.

## Instructions

When you see a YouTube URL (youtube.com or youtu.be), run:

```bash
bash ~/.hermes/skills/media/youtube-transcript/transcribe.sh "URL" "CHANNEL_ID"
```

Replace `URL` with the YouTube link and `CHANNEL_ID` with the current channel ID.

For the `#youtube-transcripts` channel the default channel ID is `1497941305710346291` — you can omit it:

```bash
bash ~/.hermes/skills/media/youtube-transcript/transcribe.sh "URL"
```

## How it works

1. **Extracts** the video ID and fetches the title
2. **Method 1 — YouTube captions**: Tries to pull the existing transcript directly (free, instant)
3. **Method 2 — Whisper fallback**: If no captions exist, downloads the audio with `yt-dlp` and transcribes via OpenAI Whisper
4. **Saves** the transcript to `~/hermes-transcripts/<title>_<video_id>.txt`
5. **Posts** a summary + the transcript file back to Discord

## Transcript storage

All transcripts are saved to: `~/hermes-transcripts/`

File format: `<video_title>_<video_id>.txt`

Each file contains the title, author, URL, date, transcription method, and full transcript text.
