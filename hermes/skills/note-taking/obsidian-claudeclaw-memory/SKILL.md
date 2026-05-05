---
name: obsidian-claudeclaw-memory
description: Set up Obsidian + ClaudeClaw as a living AI memory system. Wires the Obsidian vault to ClaudeClaw's context injection, maintains curated MEMORY.md and USER.md in the vault, and schedules overnight memory distillation via ClaudeClaw's built-in scheduler. Covers vault file structure, CLAUDE.md persona sync, MEMORY.md distillation, and heartbeat-based maintenance.
version: 1.0.0
author: ClaudeClaw
license: MIT
allowed-tools: Bash Read Write
---

# Obsidian + ClaudeClaw Memory System

## Overview

ClaudeClaw doesn't *have* memory — it *reads* memory. At every session start, ClaudeClaw searches `OBSIDIAN_VAULT_PATH` for notes relevant to the current query. Obsidian visualises the knowledge graph. ClaudeClaw's built-in scheduler drives proactive memory distillation between sessions.

**Three components:**
- **ClaudeClaw** — searches vault via keyword-match on every message (`buildObsidianContext`), and stores conversation facts automatically in `claudeclaw.db` using Gemini embeddings
- **Obsidian** — vault pointed at `OBSIDIAN_VAULT_PATH`; Graph View shows connections between memory files
- **ClaudeClaw Scheduler** — runs memory maintenance overnight via cron-based scheduled tasks

## Prerequisites

- `OBSIDIAN_VAULT_PATH` set in `/home/zeke/claudeclaw/.env` (e.g. `/home/zeke/Hermes-Vault`)
- Obsidian desktop app installed and vault opened at that path
- ClaudeClaw running (confirms vault path is active)

Verify:
```bash
grep OBSIDIAN_VAULT_PATH /home/zeke/claudeclaw/.env
```

## File Structure

See `references/file-structure.md` for the full annotated file tree.

Core files the vault should contain:

| File/Folder | Purpose |
|---|---|
| `SOUL.md` | Symlink → `CLAUDE.md` — ClaudeClaw's persona, tone, and operating rules |
| `USER.md` | Context about the human — maintained in vault, read by ClaudeClaw |
| `MEMORY.md` | Curated long-term memory distilled from daily session logs |
| `memory/YYYY-MM-DD.md` | Raw daily session logs |
| `second-brain/` | Structured knowledge base (concepts, journal, documents) |
| `directives/` | SOPs and repeatable workflows |
| `HEARTBEAT.md` | Checklist for ClaudeClaw's scheduled maintenance tasks |

## Setting Up the Vault

### 1. Confirm vault path

```bash
VAULT=$(grep OBSIDIAN_VAULT_PATH /home/zeke/claudeclaw/.env | cut -d= -f2)
echo "Vault: $VAULT"
```

### 2. Symlink CLAUDE.md as SOUL.md

ClaudeClaw's persona lives in `CLAUDE.md`. Expose it in the vault so Obsidian can visualise it and edits flow back:

```bash
ln -sf /home/zeke/claudeclaw/CLAUDE.md "$VAULT/SOUL.md"
```

### 3. Create MEMORY.md (if not present)

ClaudeClaw's embedding-based memory in `claudeclaw.db` is automatic, but a curated `MEMORY.md` in the vault gives ClaudeClaw searchable, human-readable long-term context that surfaces on every relevant query:

```bash
[ -f "$VAULT/MEMORY.md" ] || cat > "$VAULT/MEMORY.md" << 'EOF'
# Memory

Curated long-term context for ClaudeClaw. Updated by scheduled maintenance or on demand ("save this to memory").

## Key Facts

## Open Loops

## Preferences & Conventions
EOF
```

### 4. Create USER.md (if not present)

```bash
[ -f "$VAULT/USER.md" ] || cat > "$VAULT/USER.md" << 'EOF'
# User

## Identity
- Name:
- Timezone:
- Primary OS: Ubuntu Linux

## Goals & Focus Areas

## Communication Preferences
- Concise replies preferred
- Telegram as primary chat interface

## Known Expertise
EOF
```

### 5. Create memory/ folder for daily logs

```bash
mkdir -p "$VAULT/memory"
```

### 6. Create HEARTBEAT.md

```bash
cat > "$VAULT/HEARTBEAT.md" << 'EOF'
## Memory Maintenance
- [ ] Review memory/ logs from the last 3 days
- [ ] Distill key insights into MEMORY.md
- [ ] Remove outdated entries from MEMORY.md
- [ ] Update USER.md if anything new was learned about the user
EOF
```

### 7. Schedule overnight memory maintenance

Tell ClaudeClaw to schedule the heartbeat task. Ask it in chat:

> "Schedule a daily memory maintenance task at 3 AM: read HEARTBEAT.md in the Obsidian vault and complete all unchecked tasks — distill recent memory/ logs into MEMORY.md and update USER.md."

ClaudeClaw will create a scheduled task via its built-in cron scheduler (stored in `claudeclaw.db`). Verify with:

> "List my scheduled tasks"

## How ClaudeClaw Reads the Vault

ClaudeClaw's `buildObsidianContext()` runs on every incoming message. It:
1. Extracts keywords from the query
2. Walks the vault (up to depth 4) for `.md` files containing those keywords
3. Injects the first 20 lines of up to 3 matching notes into the agent's context

This means `MEMORY.md`, `USER.md`, and daily logs in `memory/` will surface automatically when the query is relevant. No configuration needed — only `OBSIDIAN_VAULT_PATH` must be set.

**Key principle: write important things to the vault, not just say them in chat.** Tell ClaudeClaw "save this to memory" and it will update `MEMORY.md` directly.

## Obsidian Setup

1. **Open vault** — File → Open Vault → Open Folder as Vault → select `OBSIDIAN_VAULT_PATH`
2. **Enable Graph View** (Ctrl+G) — visualise how memory files link to each other
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
6. **Set daily notes folder** — Settings → Core Plugins → Daily Notes → folder: `memory`

## Heartbeat-Based Memory Maintenance

`HEARTBEAT.md` drives proactive ClaudeClaw behavior on a schedule. ClaudeClaw's scheduler reads the vault on the configured cron interval, works through the checklist, and updates `MEMORY.md` and `USER.md` — like a human reviewing their journal overnight.

The scheduled task prompt should be:
```
Read HEARTBEAT.md at $OBSIDIAN_VAULT_PATH/HEARTBEAT.md.
Complete all unchecked tasks:
- Review memory/ logs from the last 3 days
- Distill key insights into MEMORY.md (append under ## Key Facts, deduplicate)
- Remove entries from MEMORY.md that are no longer relevant
- Update USER.md if anything new was learned about the user
Check off each completed item in HEARTBEAT.md.
```

## Architecture

```
Obsidian Graph View
       │
       ▼
$OBSIDIAN_VAULT_PATH/          ← Obsidian vault root
├── SOUL.md   ──symlink──►  /home/zeke/claudeclaw/CLAUDE.md
├── USER.md                  ← maintained in vault
├── MEMORY.md                ← curated long-term memory
├── memory/
│   └── YYYY-MM-DD.md        ← raw daily session logs
├── HEARTBEAT.md             ← read by ClaudeClaw scheduler
├── second-brain/
├── directives/
└── ...
         │
         ▼
   ClaudeClaw (buildObsidianContext)
   keyword search → injects matching notes
   into every agent message
         │
         ▼
   claudeclaw.db (automatic)
   Gemini-extracted facts → embeddings
   → cosine-similarity retrieval
         │
         ▼
   ClaudeClaw Scheduler (3 AM)
   "act on HEARTBEAT.md"
```

## Guardrails
- Do **not** overwrite existing `MEMORY.md` or `USER.md` without showing the proposed changes and getting approval.
- Do **not** delete `memory/YYYY-MM-DD.md` log files — they are the source of truth for distillation.
- Do **not** symlink any file containing secrets (`.env`, auth tokens) into the vault — vault content surfaces in ClaudeClaw's context.
- Do **not** set `OBSIDIAN_VAULT_PATH` to a path inside `/home/zeke/claudeclaw/` — the vault should be separate from the project root.

## Best Practices

1. **Write it down** — tell ClaudeClaw "save this to memory" to update `MEMORY.md` directly
2. **Keep MEMORY.md curated** — distilled essence, not a dump; short, high-signal entries
3. **Daily logs are raw** — `memory/YYYY-MM-DD.md` is for unformatted session notes
4. **Use directives/ for SOPs** — repeatable workflows go here so ClaudeClaw can follow them consistently
5. **Link files in Obsidian** — use `[[MEMORY]]` wiki-links to build the graph view
6. **Keep HEARTBEAT.md small** — it is read on every scheduled run and burns tokens

## Verification

A setup run passes only if:
- `OBSIDIAN_VAULT_PATH` is set and the path exists.
- `SOUL.md` symlink resolves to `CLAUDE.md`.
- `MEMORY.md` and `USER.md` exist in the vault.
- `memory/` directory exists.
- `HEARTBEAT.md` exists with the maintenance checklist.
- A scheduled task for memory maintenance exists in ClaudeClaw (confirm via "list scheduled tasks").

## Sample Prompt

"Set up Obsidian + ClaudeClaw memory. My vault is at ~/Hermes-Vault. Create the symlink, MEMORY.md, USER.md, memory/ folder, and HEARTBEAT.md, then schedule nightly maintenance at 3 AM."
