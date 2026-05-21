---
name: myclaw-context
description: Core context about the MyClaw harness — layout, operating principles, and what the operator expects when you receive a chat request
---

# MyClaw Context

You are running inside MyClaw, the operator's local-only AI control plane on Linux. This skill auto-loads on every chat turn and grounds you in where you are and what you can do.

## Project layout

- Backend: `/home/zeke/myclaw/backend/myclaw/` (FastAPI, Python, uv-managed)
- Frontend: `/home/zeke/myclaw/frontend/` (React + Vite, built into `frontend/dist/` and served by FastAPI)
- App data: `~/.myclaw/` (`config.toml`, `db.sqlite`, `missions/`, `chats/`, `logs/`)
- Listens on: `http://127.0.0.1:8765` (localhost-only, enforced by middleware)

## Related projects on this machine

- `/home/zeke/claudeclaw/` — older Node.js/TypeScript control plane (port 3141, runs as `claudeclaw.service`)
- `/home/zeke/claudeclaw-mission-control/` — separate Next.js dashboard for ClaudeClaw (different from MyClaw)
- `/home/zeke/skills-i-have-built/` — shared skill library; MyClaw auto-loads everything under `myclaw/`

## Operating principles

- **OAuth only.** Common model API-key env vars (`ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, etc.) are stripped before launching Claude or Codex. Never claim MyClaw uses API keys.
- **Localhost only.** HTTP middleware blocks any client other than `127.0.0.1` / `localhost`.
- **Full local tool access.** From chat, you have the same authority as the operator at the terminal — read/write any file, run any shell command, use `git` and `gh`, edit configs. The operator has authorized this; do not ask for permission to act.
- **Workspace defaults to `~`.** Configurable via `chat_workspace` in `~/.myclaw/config.toml`, or per-conversation via the `workspace` field on `POST /api/chats`.

## When the operator asks you to do something

1. Use your tools directly. Edit files, run commands, inspect state — don't describe what you would do.
2. Report what you actually did and the resulting state, briefly.
3. If something fails, say what failed and why; don't invent a workaround.

## Configuration files worth knowing

- `~/.myclaw/config.toml` — host, port, default agent, concurrency cap, log line limit, chat workspace
- `~/.myclaw/db.sqlite` — chats, messages, missions, mission events, tasks, memory notes, cron, webhooks, activities
- `/home/zeke/myclaw/backend/myclaw/chat.py` — chat invocation, prompt assembly, command construction
- `/home/zeke/myclaw/backend/myclaw/skills.py` — skill discovery (`SKILL.md` walk under `/home/zeke/skills-i-have-built/`)
