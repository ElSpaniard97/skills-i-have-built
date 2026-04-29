---
name: "discord-channel-management"
description: "Manage Discord channels via the Discord API, including creating, editing, and deleting channels."
category: "discord"
---

## Overview
This skill enables the creation and management of Discord channels using the Discord API. It requires a valid Discord Bot Token and Discord Guild (Server) ID.

## Prerequisites
- A bot must be added to the server and have the necessary permissions to manage channels.
- Environment variables `DISCORD_BOT_TOKEN` and `DISCORD_GUILD_ID` must be set.

## Steps
1. **Setup Environment**:
   Ensure environment variables `DISCORD_BOT_TOKEN` and `DISCORD_GUILD_ID` are set.

2. **Create a Channel**:
   ```bash
   curl -X POST "https://discord.com/api/v8/guilds/$DISCORD_GUILD_ID/channels" \
   -H "Authorization: Bot $DISCORD_BOT_TOKEN" \
   -H "Content-Type: application/json" \
   -d '{"name":"{channel_name}", "type":0}'
   ```
   Replace `{channel_name}` with the desired name.

3. **Edit a Channel**:
   ```bash
   curl -X PATCH "https://discord.com/api/v8/channels/{channel_id}" \
   -H "Authorization: Bot $DISCORD_BOT_TOKEN" \
   -H "Content-Type: application/json" \
   -d '{"name":"{new_name}"}'
   ```
   Replace `{channel_id}` and `{new_name}` accordingly.

4. **Delete a Channel**:
   ```bash
   curl -X DELETE "https://discord.com/api/v8/channels/{channel_id}" \
   -H "Authorization: Bot $DISCORD_BOT_TOKEN"
   ```
   Replace `{channel_id}` with the desired channel ID to delete.

## Pitfalls
- Ensure the bot has the appropriate permissions to manage channels (e.g., `MANAGE_CHANNELS`).
- Double-check that the environment is set up with correct token values to avoid authentication errors.

## Verification
By following the steps above, commands can be issued through the terminal or an environment supporting CURL commands to manage Discord channels efficiently.