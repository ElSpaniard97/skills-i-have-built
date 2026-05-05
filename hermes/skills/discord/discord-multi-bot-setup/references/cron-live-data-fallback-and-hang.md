# Cron live-data fallback and stuck-tick recovery (Jenko pattern)

Use this when a Discord cron report is expected but nothing posts, even though the job is active.

## Symptoms
- `hermes cron run <job_id>` reports "Triggered job... It will run on next scheduler tick".
- `hermes cron list` keeps old `last_run_at`.
- `systemctl --user status hermes-cron-<bot>.service` shows long-running `hermes cron tick` in `activating` state.
- Session files appear under `~/.hermes/discord-homes/<bot>/sessions/session_cron_<jobid>_*.json` but no delivered post.

## Fast diagnosis sequence
1) Confirm delivery target format (thread-safe):
   - `discord:<channel_id>:<thread_id>` for thread-only posts.
2) Check timer/service health:
   - `systemctl --user status hermes-cron-<bot>.timer --no-pager`
   - `systemctl --user status hermes-cron-<bot>.service --no-pager`
3) Inspect newest cron session JSON for tool failures:
   - Missing dependency (`ModuleNotFoundError: yfinance`)
   - Provider auth/rate limits (Yahoo `401/429`)
   - Stooq intraday endpoint requiring API key/captcha
4) Validate whether output files were created:
   - `~/.hermes/discord-homes/<bot>/cron/output/<job_id>/`

## Recovery actions
1) Keep route alive: send a direct thread test post (`send_message`) to prove Discord delivery path works.
2) Reduce failure surface in cron job:
   - remove optional skill hooks if they force brittle data dependencies.
3) Enforce fallback behavior in prompt:
   - If live market/news fetch fails, still post a short risk-first continuity bulletin.
   - Never return empty/no-post outcomes.
4) Re-run and wait for timer tick, then re-check `cron list` and session artifacts.

## Recommended prompt hardening snippet
Add to recurring finance/trading prompt:
- "If live data providers fail, post a fallback report with: regime read, conservative watchlist, explicit uncertainty note, and risk limits. Do not skip posting."

## Why this matters
A blocked tick in a oneshot systemd service can stall subsequent runs. Fallback posting preserves operational reliability in Discord threads even when data vendors degrade.
