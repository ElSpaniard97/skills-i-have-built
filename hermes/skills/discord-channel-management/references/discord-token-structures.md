# Discord Credential Formats & Structures

## Bot Token Formats

Discord bot tokens vary by encoding/origin. Know the format to spot errors quickly.

### Standard Discord Bot Token (from Developer Portal)

Format: `ODk4MjI0NzQ5MzI3MTc4Nzg0.GabCdE.7z1X2Y3Z4aBcDeF...` (base64 + separator + base64)

Pattern:
- **User ID** (base64) — up to ~12 chars
- `.` (literal dot)
- **Timestamp** (base64) — up to ~6 chars
- `.` (literal dot)
- **HMAC-SHA256 hash** (base64) — 27+ chars

**Source:** Discord Developer Portal → Applications → {Your Bot} → TOKEN

### Hermes-Wrapped Bot Token

Format: `MTA0OTc4NDc2NzEzNzI1MTQ5LkczaWI0bi5IaXdhY0VvMndjaDZSakw2ZW9kWnByTDkwOUhOYlBEMUlOeEhTaVdCTkJ0YUNrVFEtbkpL`

Pattern: Single continuous base64 string (no dots in visible part; encryption/encoding applied by Hermes or external system)

**Note:** When extracted from Hermes screenshots or dashboards, tokens may be encrypted or re-encoded. Use as-is.

---

## Guild (Server) ID Format

Simple numeric string, typically 18 digits.

Example: `149978476713725149`

**Source:** Discord Server Settings → Server Details → Copy Server ID (or right-click server name if dev mode on)

---

## Discord User ID Format

Numeric string, typically 18 digits.

Example: `132133748533415534`

**Source:** Right-click username → Copy User ID (requires Developer Mode in Discord)

---

## How to Extract Credentials from Screenshots

When given a screenshot or table with Discord credentials:

1. **Identify the column headers** — look for "Token", "Bot Token", "Server ID", "Guild ID", "User ID"
2. **Copy the EXACT value** — do not trim, sanitize, or guess at formatting
3. **Validate format** before using:
   - Bot token: should be long (50+ chars), alphanumeric, may contain dots or base64
   - Server/Guild ID: numeric, usually 18 digits
   - User ID: numeric, usually 18 digits
4. **Apply via Hermes** using `hermes config set channels.discord.*`

---

## Example: Credential Extraction from Data Table

```
| Name         | Type              | Value                                     |
|--------------|-------------------|-------------------------------------------|
| Archer       | Discord Bot Token | MTA0OTc4NDc2NzEzNzI1MTQ5LkczaWI0bi...    |
| Hermes Srv   | Server ID         | 149978476713725149                        |
| User         | Discord User ID   | 132133748533415534                        |
```

**Extraction:**
- Bot token → `channels.discord.token`
- Server ID → `channels.discord.server_id`
- User ID → `channels.discord.user_id`

**Command:**
```bash
hermes config set channels.discord.token "MTA0OTc4NDc2NzEzNzI1MTQ5LkczaWI0bi..."
hermes config set channels.discord.server_id "149978476713725149"
hermes config set channels.discord.user_id "132133748533415534"
```

---

## Troubleshooting

### Token Validation

```bash
curl -H "Authorization: Bot <TOKEN>" \
  https://discord.com/api/v10/users/@me
```

- **200 OK** with user JSON → token is valid
- **401 Unauthorized** → token is invalid, malformed, or expired
- **403 Forbidden** → token is valid but bot lacks permissions for the request

### Server ID Verification

```bash
curl -H "Authorization: Bot <TOKEN>" \
  https://discord.com/api/v10/users/@me/guilds | jq '.[] | select(.id == "149978476713725149")'
```

- **Non-empty result** → server ID is correct and bot is in that server
- **Empty/no match** → bot is not in this server, or ID is wrong

---

## References

- Discord Developer Portal: https://discord.com/developers/applications
- Discord API Docs (v10): https://discord.com/developers/docs/intro
- Token Security: Never commit tokens to git; use .env or Hermes config
