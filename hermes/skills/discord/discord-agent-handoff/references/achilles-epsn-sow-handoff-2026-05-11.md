# Achilles to EPSN SOW Handoff Failure/Fix

Session-specific reference for the Discord agent handoff class.

## Failure observed

A user asked Achilles in `#achilles-security`:

```text
Send this feedback to Espn and have them update the SOW using this feedback
```

Evidence from Discord/audit showed Achilles did send an `AGENT TASK` to EPSN:

- Source user message in `#achilles-security`: `1503451324602253332`
- Achilles confirmation: `1503451331648815366`
- `AGENT TASK` in `#espn-operations`: `1503451330520547525`
- Audit event: `agent_handoff` from `achilles` to `epsn`, `ok=true`

However EPSN immediately posted the canned `epsn_operations_ideas.pdf` instead of processing the SOW update. Later, when asked if the task was completed, EPSN said it could not find a formal Achilles task. EPSN's false status was then forwarded back to Achilles as a security escalation, causing Achilles to agree incorrectly that no clean task had been sent.

## Root causes

1. The running bot processes were stale. `fleet_runtime.py` had already been patched and compiled, but live bot PIDs started before the file mtime, so they were still using old broad PDF-trigger behavior.
2. The old PDF trigger interpreted routed task wording such as "PDF" / "create/update PDF" as the canned ideas-PDF workflow.
3. Human task-status questions were sent to the LLM without recent Discord channel context, so the bot could claim it checked task history even though it had no reliable task-history retrieval.

## Correct class-level fix

- Keep the stricter `is_pdf_ideas_request(...)` behavior: only generate the canned ideas PDF for explicit ideas/designated-channel PDF requests. Document review/update tasks for SOW/MSA/PDF feedback must pass through to the LLM.
- Keep routed task allowlisting via `is_bot_task_message(...)` for `**AGENT TASK**`, `**SK DISPATCH**`, `**SECURITY ESCALATION**`, and `**LEGAL ESCALATION**`.
- For human questions containing task/status terms such as `task`, `assigned`, `sent`, `complete`, `completed`, `handoff`, or `dispatch`, append recent Discord channel context before calling the LLM. This prevents a bot from falsely saying no task exists when the task is visible in recent channel history.

## Urgent delivery workaround used

Because service restart was blocked/denied, Discord REST was used to repost a clean task from Achilles to EPSN without PDF-trigger language:

- Corrected `AGENT TASK` in `#espn-operations`: `1503458517363855482`
- EPSN completion response: `1503458677376680157`
- No attachment/canned ideas PDF was posted for the corrected task.

## Verification

- `python3 -m py_compile /home/zeke/.hermes/discord-bots/*.py` passed after patching.
- Running processes still predated modified files, so runtime activation requires service restart by the user/approved context.
- Do not retry restart automatically after `BLOCKED: User denied. Do NOT retry.`
