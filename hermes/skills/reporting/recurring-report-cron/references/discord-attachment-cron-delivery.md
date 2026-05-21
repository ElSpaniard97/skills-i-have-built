# Discord attachment delivery from Hermes cron

Session learning from the Achilles security-report cron setup.

## Problem class

Recurring reports can exceed Discord's message length limits, so the user may want a short header plus a full Markdown attachment.

## Observed pitfalls

- `cronjob(script=...)` paths must be relative to `~/.hermes/scripts/`; absolute or `~`-relative paths are rejected.
- `no_agent=True` script jobs are convenient for fixed stdout watchdogs, but the scheduler's script execution timeout may be shorter than a slow report's required runtime. If the report needs several minutes, prefer an agent-mode cron prompt that runs the wrapper via `terminal(timeout=...)`.
- Returning `MEDIA:/path/to/file` from an agent-mode cron final response may not reliably become a Discord attachment. Verify the actual Discord message after a manual run before declaring success.

## Reliable pattern for large Discord reports

1. Create a wrapper in `~/.hermes/scripts/<job>.py`.
2. Wrapper runs the report generator with its own timeout and freshness checks.
3. Wrapper writes/archive-copies the report to a stable path.
4. Wrapper posts directly to the resolved Discord channel/thread using a multipart upload when an attachment is required.
5. Configure the Hermes cron job with `deliver="local"` to avoid duplicate cron response messages when the wrapper already posts to Discord.
6. Run `cronjob(action="run", job_id=...)`, then verify the Discord message has both the expected header and the attachment.

## Security-report-specific hardening

For security reports, scan generated output for token-like strings before enabling scheduled delivery. If a report command includes tool status output such as `gh auth status`, redact `Token:`, `Token=`, `api_key`, `secret`, `password`, GitHub token patterns, and OpenAI-style `sk-...` patterns before archiving or posting.

## Example final shape

- Hermes cron schedule: local-time cron expression such as `0 10 * * 1,5`.
- Prompt: run `python3 /home/<user>/.hermes/scripts/<job>.py --post-discord` with a terminal timeout longer than the wrapper's internal timeout.
- Delivery: `local` when wrapper posts directly.
- Manual trigger: `hermes cron run <job_id>`.
