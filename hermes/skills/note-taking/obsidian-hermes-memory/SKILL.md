---
name: obsidian-hermes-memory
description: Set up Obsidian + Hermes Agent as a living AI memory system. Use when helping users configure their workspace so Hermes remembers context across sessions, builds a knowledge graph in Obsidian, and proactively maintains memory via Hermes cron. Covers vault file structure, SOUL.md persona, MEMORY.md distillation, session search, and heartbeat-based memory maintenance.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [Obsidian, Memory, Knowledge Graph, SOUL, Cron, Vault]
    related_skills: [obsidian]
---

# Obsidian + Hermes Memory System

## Overview

Hermes doesn't *have* memory — it *reads* memory. At every session start, Hermes injects `SOUL.md`, `MEMORY.md`, and `USER.md` into the system prompt, giving it persistent context. Obsidian points at the same folder and visualises the knowledge graph. Hermes cron drives proactive memory maintenance between sessions.

**Three components:**
- **Hermes Agent** — reads vault files at session start (injected into system prompt via `memory_enabled: true` in `config.yaml`)
- **Obsidian** — vault pointed at `$OBSIDIAN_VAULT_PATH`; Graph View shows connections between memory files
- **Hermes session_search** — semantic search over past sessions without loading every file into context

## Prerequisites

- `OBSIDIAN_VAULT_PATH` set in `~/.hermes/.env` (e.g. `/home/user/Hermes-Vault`)
- Obsidian desktop app installed and vault opened at that path
- Hermes Agent v0.8+ with `memory_enabled: true` in `~/.hermes/config.yaml`

## File Structure

See `references/file-structure.md` for the full annotated file tree.

Core files the vault should contain:

| File/Folder | Purpose |
|---|---|
| `SOUL.md` | AI persona, tone, and values — mirrors `~/.hermes/SOUL.md` |
| `USER.md` | Context about the human — mirrors `~/.hermes/memories/USER.md` |
| `MEMORY.md` | Curated long-term memory distilled from daily session logs |
| `memory/YYYY-MM-DD.md` | Raw daily session logs |
| `second-brain/` | Structured knowledge base (concepts, journal, documents) |
| `directives/` | SOPs and repeatable workflows |
| `HEARTBEAT.md` | Drives proactive Hermes cron behavior |

## How Hermes Reads Files

Hermes injects `SOUL.md`, `MEMORY.md`, and `USER.md` at the start of every session via its built-in memory system. Configure in `~/.hermes/config.yaml`:

```yaml
memory:
  memory_enabled: true
  user_profile_enabled: true
  memory_char_limit: 2200
  user_char_limit: 1375
```

Hermes manages `~/.hermes/SOUL.md` and `~/.hermes/memories/` internally. To keep your Obsidian vault in sync, symlink them:

```bash
VAULT="$OBSIDIAN_VAULT_PATH"

# Symlink Hermes memory files into the vault
ln -sf ~/.hermes/SOUL.md "$VAULT/SOUL.md"
ln -sf ~/.hermes/memories/MEMORY.md "$VAULT/MEMORY.md"
ln -sf ~/.hermes/memories/USER.md "$VAULT/USER.md"

# Symlink the full memories folder for daily logs
ln -sf ~/.hermes/memories "$VAULT/memory"
```

Now edits in Obsidian update Hermes's live memory files, and vice versa.

Key principle: **write important things to memory files, not just say them in chat.** Tell Hermes "save this to memory" and it will update `MEMORY.md` directly.

## Obsidian Setup

1. **Open vault** — File → Open Vault → Open Folder as Vault → select `$OBSIDIAN_VAULT_PATH`
2. **Enable Graph View** (Ctrl/Cmd+G) — visualise how memory files link to each other
3. **Install plugins** (Settings → Community Plugins):
   - **Dataview** — query memory files like a database
   - **Templater** — daily note templates for `memory/YYYY-MM-DD.md`
4. **Daily note template** (via Templater, save to `templates/daily.md`):
   ```markdown
   # <% tp.date.now("YYYY-MM-DD") %>

   ## Session Log

   ## Decisions Made

   ## Things to Remember
   ```
5. **Dataview query** to surface recent memories (paste into any note):
   ```dataview
   LIST FROM "memory" SORT file.name DESC LIMIT 7
   ```
6. **Set daily notes folder** — Settings → Core Plugins → Daily Notes → set folder to `memory`

## Session Search (replaces QMD)

Hermes has built-in semantic session search. Enable it in `~/.hermes/config.yaml`:

```yaml
platform_toolsets:
  cli: [hermes-cli, session_search]
  telegram: [hermes-telegram, session_search]
  discord: [hermes-discord, session_search]
```

Then ask Hermes to recall past context naturally:
> "What did we decide about X last week?"
> "Find sessions where we discussed Y"

Hermes will search its session history and surface relevant context without loading every file.

## Heartbeat-Based Memory Maintenance

`HEARTBEAT.md` in your vault drives proactive Hermes behavior on a schedule. Create it:

```bash
cat > "$OBSIDIAN_VAULT_PATH/HEARTBEAT.md" << 'EOF'
## Memory Maintenance
- [ ] Review memory/ logs from the last 3 days
- [ ] Distill key insights into MEMORY.md
- [ ] Remove outdated entries from MEMORY.md
- [ ] Update USER.md if anything new was learned about the user
EOF
```

Schedule Hermes to act on it with cron:

```bash
# Run memory maintenance every day at 3 AM
hermes cron add "memory-heartbeat" "0 3 * * *" \
  "Read $OBSIDIAN_VAULT_PATH/HEARTBEAT.md and complete all unchecked tasks"
```

Hermes will wake up, review recent session logs, distill key insights into `MEMORY.md`, and clear the checklist — like a human reviewing their journal overnight.

**Verify the cron was added:**
```bash
hermes cron list
```

## Best Practices

1. **Write it down** — tell Hermes "save this to memory" or update `memory/YYYY-MM-DD.md` directly
2. **Keep MEMORY.md curated** — distilled essence, not a dump; short, high-signal entries
3. **Daily logs are raw** — `memory/YYYY-MM-DD.md` is for unformatted session notes; don't worry about formatting
4. **Use directives/ for SOPs** — repeatable workflows go here so Hermes can follow them consistently
5. **Link files in Obsidian** — use `[[MEMORY]]` wiki-links to build the graph view
6. **Sync SOUL.md** — personalise `~/.hermes/SOUL.md` to shape how Hermes speaks and behaves; it reflects in Obsidian automatically via the symlink

## Architecture

```
Obsidian Graph View
       │
       ▼
$OBSIDIAN_VAULT_PATH/          ← Obsidian vault root
├── SOUL.md   ──symlink──►  ~/.hermes/SOUL.md
├── MEMORY.md ──symlink──►  ~/.hermes/memories/MEMORY.md
├── USER.md   ──symlink──►  ~/.hermes/memories/USER.md
├── memory/   ──symlink──►  ~/.hermes/memories/
│   └── YYYY-MM-DD.md
├── HEARTBEAT.md             ← read by Hermes cron
├── second-brain/
├── directives/
└── ...
         │
         ▼
   Hermes Agent
   (injects SOUL + MEMORY + USER
    into system prompt each session)
         │
         ▼
   hermes cron (3 AM)
   "act on HEARTBEAT.md"
```
