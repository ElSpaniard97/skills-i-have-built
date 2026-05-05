# Discord Token Validation & LoginFailure Errors

## Error Signature

```
ERROR gateway.run: ✗ discord error: discord connect timed out after 30s
discord.errors.HTTPException: 401 Unauthorized (error code: 0): 401: Unauthorized
discord.errors.LoginFailure: Improper token has been passed.
```

This appears in `journalctl --user -u hermes-gateway` or when running `hermes gateway run` in foreground.

## Root Causes

1. **Token is invalid or malformed**
   - Characters missing or corrupted
   - Wrong token pasted (e.g., a user token instead of a bot token)
   - Token from a different platform

2. **Token is expired**
   - Bot token was regenerated in Developer Portal but .env not updated
   - Token was manually revoked

3. **Bot does not exist**
   - Application ID doesn't exist
   - Bot was deleted from the application

4. **Token has wrong format**
   - Should start with `MTAxNzA4...` (base64-like)
   - Should contain at least one `.` separator (ID.secret format)

## Correct Token Format

Discord bot tokens follow this pattern:
```
REDACTED_DISCORD_BOT_TOKEN
```

- **Part 1** (before first `.`): Application/Bot ID (base64)
- **Part 2** (between `.`): Timestamp or version marker
- **Part 3** (after second `.`): Secret token (base64)

All three parts must be present and non-empty.

## How to Regenerate

1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Select your application
3. Click **"Bot"** in the left sidebar
4. Under the bot name, find the **TOKEN** section
5. Click **"Reset Token"** (or **"Copy"** if generating for the first time)
6. A new token is generated and displayed once
7. Click **Copy** and immediately paste into `~/.hermes/.env` as `DISCORD_BOT_TOKEN=`

**⚠ Never commit tokens to git or share them publicly.**

## Multiple Discord Bots (Archer, Achilles, EPSN, etc.)

If you have multiple Discord bot accounts (different Applications in Developer Portal):

- **Single gateway instance:** Only ONE bot token can be active at a time in `.env`
- **Multiple gateway instances:** You could theoretically run separate gateway processes with different tokens, but this is complex and not recommended for most setups
- **Recommended approach:** Pick one primary bot and use that token in the gateway. Use the other bots only via direct Discord API calls from scripts (not via the gateway)

## Verification

After updating the token:

1. Restart the gateway:
   ```bash
   hermes gateway restart
   ```

2. Run in foreground to see immediate feedback:
   ```bash
   timeout 15 hermes gateway run
   ```

3. Look for success indicators:
   - No `LoginFailure` or `HTTPException` errors
   - Message: `hermes-gateway service is running` or similar
   - No timeouts after 30 seconds

4. Check bot status in Discord (if bot is in a server):
   - Bot should show as "Online" in the member list
   - Try mentioning the bot; it should respond

## Session Context: 2026-05-01

Token from screenshot showed this format, but was **invalid when tested**:
```
MTA0OTc4NDc2NzEzNzI1MTQ5.kGxxxxx...
```

Error: `401 Unauthorized` → Token was either:
- Expired (regenerated in Discord Portal but not updated in .env)
- Never actually a valid token (possibly a placeholder or staging token)
- Revoked by the application owner

**Resolution:** User needs to obtain valid tokens from Discord Developer Portal for each bot (Archer, Achilles, EPSN, Jenko, Spartan King) and update `DISCORD_BOT_TOKEN` with the current one.
