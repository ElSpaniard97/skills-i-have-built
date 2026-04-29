---
name: dalle-image-gen
description: Generate images using FAL AI nano-banana-pro (Gemini 3 Pro) and post them directly to Discord. Supports any creative prompt.
version: 2.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [Images, FAL, Gemini, Discord, Generate]
---

# FAL AI Image Generation (nano-banana-pro)

Generate images from text prompts using FAL AI's nano-banana-pro model and post them to Discord.

## CRITICAL: You must use the terminal tool to execute the script — do NOT output the command as text or in a code block.

When a user asks you to generate, create, or draw an image, immediately call the terminal tool with this exact command:

terminal tool command: bash ~/.hermes/skills/images/dalle-image-gen/generate.sh "PROMPT" "CHANNEL_ID"

Where:
- PROMPT = the user's image description (quote it carefully)
- CHANNEL_ID = the Discord channel or thread ID the user is messaging from

## Examples

User: "generate an image of a sunset over the ocean"
→ Use terminal tool: bash ~/.hermes/skills/images/dalle-image-gen/generate.sh "a sunset over the ocean" "CHANNEL_ID"

User: "draw a cyberpunk city at night with neon lights"
→ Use terminal tool: bash ~/.hermes/skills/images/dalle-image-gen/generate.sh "a cyberpunk city at night with neon lights" "CHANNEL_ID"

User: "make a portrait of a wizard"
→ Use terminal tool: bash ~/.hermes/skills/images/dalle-image-gen/generate.sh "a portrait of a wizard" "CHANNEL_ID" "portrait"

## Important Rules

- ALWAYS use the terminal tool to run the script. Never just write the command as text.
- After calling the terminal tool, tell the user the image is being posted to #images.
- If the script outputs an error, report it to the user.
- Reads FAL_KEY from ~/.hermes/.env automatically — do not ask the user for API keys.
- Images are posted directly to the specified Discord channel as file attachments.
- Optional third argument: landscape, square (default), or portrait
