# Thread-only stock trading cron routing (Jenko pattern)

Use this when a user wants a recurring stock report delivered only to a Discord thread.

## Preconditions
- Per-bot isolation enabled (`HERMES_HOME=/home/zeke/.hermes/discord-homes/<bot>`).
- Existing cron job already producing valid report content.
- Thread ID available (from user-provided URL or copied ID).

## Delivery target rule
- Channel-only: `discord:<channel_id>`
- Thread-only: `discord:<channel_id>:<thread_id>`

In practice, thread IDs may not appear in `send_message list`; ask for URL/ID if missing.

## Reliable update sequence
1. Edit schedule and prompt in one pass.
2. Edit delivery target to explicit numeric channel/thread IDs (`discord:<channel_id>:<thread_id>`).
3. Trigger manual run + tick.
4. Confirm `cron list` shows updated schedule and deliver target.
5. Validate last run is `ok` and inspect latest `session_cron_<id>_*.json` for required format.
6. Send explicit test message to the exact thread target.

## Scheduler reliability in per-bot homes
If jobs are stored under isolated homes (example: `~/.hermes/discord-homes/jenko`) they can miss scheduled runs unless that home is being ticked continuously.

Diagnostic:
- `HERMES_HOME=... hermes cron list` shows jobs and a past-due next run
- `last_run_at` does not advance until manual `hermes cron tick`

Fix (systemd user timer):
- Create `~/.config/systemd/user/hermes-cron-<bot>.service`:
  - `Environment="HERMES_HOME=/home/zeke/.hermes/discord-homes/<bot>"`
  - `ExecStart=/home/zeke/.hermes/hermes-agent/venv/bin/hermes cron tick`
- Create `~/.config/systemd/user/hermes-cron-<bot>.timer`:
  - `OnBootSec=1min`
  - `OnUnitActiveSec=1min`
  - `Persistent=true`
- Enable it:
  - `systemctl --user daemon-reload`
  - `systemctl --user enable --now hermes-cron-<bot>.timer`

Verification:
- `systemctl --user status hermes-cron-<bot>.timer`
- Trigger one run: `HERMES_HOME=... hermes cron run <job_id>`
- Tick once: `HERMES_HOME=... hermes cron tick`
- Confirm `last_run_at` updates and `last_delivery_error` remains null

## Prompt hardening notes
- Prefer plain currency constraints (`below 50 USD`) to avoid shell interpolation glitches.
- Keep strict quality gates in prompt:
  - exact stock count
  - sub-price threshold
  - required color tags
  - source reliability flags

## Example schedule
- Monday and Wednesday at 10:00: `0 10 * * 1,3`
