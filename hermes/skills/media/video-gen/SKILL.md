---
name: video-gen
description: Generate short videos (5-30s) from text prompts using FAL AI (Kling v2), post to Discord, and optionally auto-upload to TikTok.
version: 2.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [Video, FAL, Kling, Discord, TikTok, Generate]
---

# FAL AI Video Generation (Kling v2)

Generate videos from text prompts using FAL AI's Kling v2 model. Supports 5, 10, 20, or 30 second videos. Posts to Discord and auto-uploads to TikTok if credentials are configured.

## CRITICAL: You must use the terminal tool to execute the script — do NOT output the command as text or in a code block.

When a user asks you to generate, create, or make a video, immediately call the terminal tool with this exact command:

terminal tool command: bash ~/.hermes/skills/media/video-gen/generate.sh "PROMPT" "CHANNEL_ID" "DURATION" "ASPECT"

Where:
- PROMPT = detailed video description (be descriptive — Kling responds well to rich prompts)
- CHANNEL_ID = Discord channel ID (default: 1498055202257768448 for #videos)
- DURATION = 5, 10, 20, or 30 (seconds, default: 10)
- ASPECT = 9:16 (TikTok portrait), 16:9 (landscape), or 1:1 (square) — default: 9:16

## How durations work
- 5s or 10s = single Kling v2 clip
- 20s = 2 clips concatenated with ffmpeg
- 30s = 3 clips concatenated with ffmpeg

## TikTok auto-upload
If TIKTOK_ACCESS_TOKEN is set in ~/.hermes/.env, the video is automatically uploaded to TikTok after posting to Discord.

## Examples

User: "make a 30 second video of a city timelapse"
→ terminal tool: bash ~/.hermes/skills/media/video-gen/generate.sh "cinematic city timelapse, busy streets, day to night transition, golden hour, wide angle" "1498055202257768448" "30" "9:16"

User: "generate a 20 second beach video"
→ terminal tool: bash ~/.hermes/skills/media/video-gen/generate.sh "tropical beach with crystal clear water, gentle waves, palm trees swaying, golden sunset, peaceful atmosphere" "1498055202257768448" "20" "9:16"

User: "make a 10 second video of a dog surfing"
→ terminal tool: bash ~/.hermes/skills/media/video-gen/generate.sh "golden retriever surfing on ocean waves, sunny day, playful, slow motion" "1498055202257768448" "10" "9:16"

## Important Notes
- Videos take 2-5 minutes to generate (longer for 20-30s). Script posts progress to Discord immediately.
- Always run with terminal(background=true) so the user gets a response while it generates.
- Default aspect ratio is 9:16 (portrait) — ideal for TikTok, Instagram Reels, YouTube Shorts.
- For landscape (YouTube, presentations): use "16:9"
