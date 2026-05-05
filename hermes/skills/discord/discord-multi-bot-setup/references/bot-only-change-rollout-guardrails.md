# Bot-only change rollout guardrails (multi-bot discord.py)

Use this when modifying only one bot (for example `jenko.py`) in a shared launcher service.

## Why
A single service (`hermes-discord-bots.service`) supervises all bots. A one-bot change can accidentally break only that bot while others stay healthy, which is easy to miss if you only check service-level `active (running)`.

## Safe rollout sequence
1. Patch only the target bot file.
2. Restart shared service.
3. Verify all:
   - target bot PID exists (`pgrep -af '/home/zeke/.hermes/discord-bots/jenko.py'`)
   - target bot has a recent online log line (`✓ Jenko is online as ...`)
   - no crash loop messages (`crashed`, `Failed`, `exit code`)
4. Re-test command paths changed by patch (example: `!cron create`).

## High-risk edits checklist
- Token handling changes (hardcoded fallback -> env-only)
  - confirm env var exists before restart
  - if not, rollout will fail immediately for that bot
- CLI syntax changes
  - validate against live CLI expectations
  - `hermes cron create` uses positional prompt, not `--prompt`
- Prompt policy injections
  - ensure policy is appended to existing system prompt, not replacing channel/security gates

## Fast rollback pattern
If target bot does not come back online after restart:
1. Revert last bot-only edit.
2. Restart service.
3. Confirm `✓ <bot> is online`.
4. Re-apply change in smaller steps.
