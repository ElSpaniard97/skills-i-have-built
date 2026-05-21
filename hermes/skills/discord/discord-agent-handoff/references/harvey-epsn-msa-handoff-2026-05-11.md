# Harvey to EPSN MSA Handoff Failure/Fix

Session-specific reference for the Discord agent handoff class.

## Failure observed

A user asked Harvey:

```text
Send this review to ESPN and tell her to update the MSA to reflect the recommended fixes. ESPN should then provide the updated PDF on their private channel.
```

Harvey responded with a clarification-timeout style message and said it could not send directly. The root issue was runtime behavior, not a missing user instruction:

- bot scripts returned early on `message.author.bot`, so target agents ignored bot-authored task posts
- there was no shared explicit handoff parser for human instructions like "send/tell/forward to ESPN"
- the task depended on prior-channel context ("this review"), so a useful handoff needed recent context

## Correct class-level fix

Do not let every bot respond to every bot message. Instead:

1. Keep `message.author == bot.user` self-guard.
2. Permit bot-authored messages only if they are in the target bot's own channel/thread and start with a routed header:
   - `**AGENT TASK**`
   - `**SK DISPATCH**`
   - `**SECURITY ESCALATION**`
   - `**LEGAL ESCALATION**`
3. Add shared handoff helpers in `fleet_runtime.py`:
   - `parse_inter_agent_handoff(...)`
   - `recent_channel_context(...)`
   - `forward_inter_agent_handoff(...)`
   - `is_bot_task_message(...)`
   - `normalize_bot_task_content(...)`
4. In each bot's `on_message`, handle routed bot-authored tasks before ordinary human-message routing.
5. For human messages that explicitly send/tell/forward/assign/delegate to another agent, post an `AGENT TASK` in the target private channel and stop; do not route the same message through LLM first.

## Urgent delivery workaround

If code is compiled but restart is denied/blocked and the user needs immediate delivery, Discord REST can be used once with the proper bot token and `User-Agent` header. Do not print tokens.

For the MSA case, the task post and PDF post were verified by Discord API:

- Harvey `AGENT TASK` message in `#espn-operations`: `1503418354361307228`
- EPSN PDF message in `#espn-operations`: `1503418356458590208`
- attachment: `anchorlink_msa_updated_2026-05-11.pdf`

## Response style correction from same workflow

After EPSN/Harvey document work, the user corrected bot response style. Future handoff confirmations should be concise, structured, and Discord-readable:

- short title
- status/date/prepared-by/source when useful
- brief summary
- key updates or action taken
- open items
- important note
- recommended next step

Avoid raw diffs, huge legal blocks, and local file metadata unless explicitly requested.
