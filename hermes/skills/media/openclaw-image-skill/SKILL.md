---
name: openclaw-image-skill
description: "Generate images via OpenAI DALL-E 3 API. Use when a user asks to create, generate, or visualize an image from a text prompt."
---

# OpenClaw Image Skill

Generate images from text prompts using OpenAI's DALL-E 3 model.

## Requirements

- `OPENAI_API_KEY` environment variable set, **or** pass the key inline
- `curl` available in PATH

## Usage

```bash
# Using env var (recommended)
export OPENAI_API_KEY=sk-proj-...
./scripts/generate.sh "a glowing robot holding a paintbrush" output.png

# Inline key
OPENAI_API_KEY=sk-proj-... ./scripts/generate.sh "a cat on a laptop" cat.png
```

The script downloads the generated image to the specified output path.

## How It Works

1. Sends a POST to `https://api.openai.com/v1/images/generations` with model `dall-e-3`
2. Parses the returned image URL from the JSON response
3. Downloads the image to disk (URLs expire after ~2 hours)
4. Prints the output path on success

## Parameters

| Param | Default | Notes |
|---|---|---|
| Model | `dall-e-3` | Hardcoded; swap to `dall-e-2` for cheaper/smaller |
| Size | `1024x1024` | DALL-E 3 supports `1024x1024`, `1792x1024`, `1024x1792` |
| Quality | `standard` | Use `hd` for higher detail (costs more) |

## Sample Images

- `images/skill-concept.png` — AI-generated visualization of "what a skill is": a glowing modular puzzle piece slotting into a robot brain
- `images/cat.png` — AI-generated orange tabby cat on a desk next to a laptop

## Agent Instructions

When a user asks to generate an image:

1. Confirm you have `OPENAI_API_KEY` available
2. Craft a detailed, descriptive prompt from the user's request
3. Choose a filename slug from the prompt (e.g. `donkey-jet-ski`) and save to the workspace images dir:
   `/home/zeke/.openclaw/workspace/images/<slug>.png`
4. Run `./scripts/generate.sh "<prompt>" /home/zeke/.openclaw/workspace/images/<slug>.png`
5. Post the image back to the originating channel using the `message` tool:
   - Discord: `action: send`, `channel: discord`, `to: channel:<channelId>`, `media: file:///home/zeke/.openclaw/workspace/images/<slug>.png`
   - Do NOT skip this step — always post the file, never just report the path
   - Do NOT save to /tmp — files there are cleaned up before posting can occur
6. Do not remind the user about URL expiry (the file is local; there is no expiring URL)

## Security Note

Never log, echo, or commit the API key. Always use env vars or a secrets manager.
