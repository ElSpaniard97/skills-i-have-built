# Discord thread routing for Hermes cron (session note)

Scenario
- Cron job posted to parent channel (#jenko) instead of intended thread ("Stock Trading").

Reliable fix
1. Pause job to stop further wrong posts.
2. Obtain thread URL from user.
3. Parse thread target ID from URL (last numeric segment where applicable).
4. Set deliver explicitly with Hermes cron edit:
   - `discord:<thread_id>` OR `discord:<channel_id>:<thread_id>`
5. Resume job.
6. Send immediate test post and capture message_id for proof.

Observed working target
- `discord:1499967305969565696`

Verification commands
```bash
HERMES_HOME=/home/zeke/.hermes/discord-homes/jenko hermes cron list
HERMES_HOME=/home/zeke/.hermes/discord-homes/jenko hermes cron run 7ffa05e79e8c
HERMES_HOME=/home/zeke/.hermes/discord-homes/jenko hermes cron tick
```

Operational note
- `send_message(action='list')` may not enumerate thread targets; explicit ID-based targeting is the reliable path.
