---
name: discord-agent-handoff
description: Route work between the Hermes Discord agent fleet so bots can assign tasks, process AGENT TASK messages, complete deliverables in their private channels, and confirm completion.
status: stable
---

# Discord Agent Handoff

Use this skill when Discord bots/agents need to send work to each other instead of merely advising the user to copy/paste a task.

## Protocol

1. If a user says to send, tell, forward, route, dispatch, assign, delegate, or escalate work to another agent, create an `AGENT TASK` in the target agent's private channel. Do not answer with "I can't send it" unless the Discord API/token/channel is actually unavailable after verification.
2. Include:
   - target agent
   - source agent
   - requesting user
   - source channel
   - the exact task
   - recent source-channel context when the task says "this review", "that PDF", or otherwise depends on prior messages
3. Target bots must process `AGENT TASK`, `SK DISPATCH`, `SECURITY ESCALATION`, and `LEGAL ESCALATION` posts in their own channel even when the message author is another bot. A blanket `if message.author.bot: return` breaks inter-agent workflows; replace it with a self-message guard plus an allowlist for routed task headers.
4. Multi-target handoffs such as "send this to Harvey and Achilles" must fan out to every named target, not only the first alias match.
5. Target bots complete the task in their own channel, post any file/PDF deliverable there, and confirm what was done.
6. If service restart is denied or blocked, do not retry destructive/service actions. Instead, verify compile/runtime state, complete urgent delivery via Discord REST if safe, and clearly state that the new runtime code will not be active until the user restarts the service. When using REST fallback against old live code, avoid wording like "send/post PDF" in corrective `AGENT TASK` messages unless the task truly is the canned ideas-PDF workflow; old code may misroute those phrases to generic PDF generation instead of document review.
5. If a bot's model response assigns another agent, use this routable block exactly:

```text
DISPATCH: <agent_slug_or_name>
PRIORITY: low|normal|high|critical
TASK: <specific requested outcome>
NOTE: <context or deliverable location>
```
6. Handoff confirmations and target-agent deliverable posts should follow the fleet Discord response style: short title, status/date/prepared-by/source when useful, concise summary, short bullets, open items, important note, and Recommended Next Step. Avoid raw diffs, huge legal blocks, local metadata, or long file paths unless explicitly requested.

## Implementation files

Shared runtime:
- /home/zeke/.hermes/discord-bots/fleet_runtime.py

Bot scripts importing the shared handlers:
- /home/zeke/.hermes/discord-bots/spartan_king.py
- /home/zeke/.hermes/discord-bots/jenko.py
- /home/zeke/.hermes/discord-bots/archer.py
- /home/zeke/.hermes/discord-bots/achilles.py
- /home/zeke/.hermes/discord-bots/epsn.py
- /home/zeke/.hermes/discord-bots/hector.py
- /home/zeke/.hermes/discord-bots/troy.py
- /home/zeke/.hermes/discord-bots/hellen.py
- /home/zeke/.hermes/discord-bots/togi.py
- /home/zeke/.hermes/discord-bots/harvey.py

Prompt policy:
- /home/zeke/.hermes/discord-bots/bot_config.py `RESPONSE_RULES`

Session-specific references:
- `references/harvey-epsn-msa-handoff-2026-05-11.md` records the Harvey→EPSN MSA handoff failure, root cause, REST fallback, verification IDs, and pitfalls.
- `references/achilles-epsn-sow-handoff-2026-05-11.md` records the Achilles→EPSN SOW handoff failure where the task was sent but old live code treated it as a canned ideas-PDF request and later status checks lacked recent channel context.

## Verification

Run:

```bash
python3 -m py_compile /home/zeke/.hermes/discord-bots/*.py
systemctl --user restart hermes-discord-bots.service
journalctl --user -u hermes-discord-bots.service --since 'now' --no-pager
```

Then send a message like:

```text
Send this review to ESPN and tell her to update the MSA. ESPN should provide the updated PDF in her private channel.
```

Expected behavior:
- Source bot posts `AGENT TASK` to `#espn-operations`.
- EPSN processes the bot-authored task message instead of ignoring it.
- EPSN completes the task or asks one precise follow-up if context is missing.

## References

- `references/harvey-epsn-msa-handoff-2026-05-11.md` — concrete Harvey→EPSN MSA handoff failure, shared-runtime fix pattern, urgent REST delivery workaround, and response-style correction.
- `references/achilles-epsn-sow-handoff-2026-05-11.md` — concrete Achilles→EPSN SOW handoff failure where the task existed but old live code generated the canned ideas PDF and later status checks lacked recent context.
