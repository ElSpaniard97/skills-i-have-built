# File Structure Reference

Annotated file tree for the Obsidian + ClaudeClaw memory workspace.

```
$OBSIDIAN_VAULT_PATH/          (e.g. ~/Hermes-Vault)
│
│  ── CORE IDENTITY FILES ──────────────────────────────────────────
│
├── SOUL.md        ──symlink──► /home/zeke/claudeclaw/CLAUDE.md
│                               ClaudeClaw's persona, operating rules, and agent roster
│                               Edits in Obsidian update CLAUDE.md live
│
├── USER.md                     Context about the human
│                               Name, timezone, goals, preferences
│                               Maintained manually or by scheduled maintenance
│                               Surfaces in ClaudeClaw context when query matches
│
│  ── MEMORY FILES ─────────────────────────────────────────────────
│
├── MEMORY.md                   ★ LONG-TERM MEMORY ★
│                               Curated, distilled insights from daily logs
│                               Updated by heartbeat scheduler or on demand
│                               Surfaces in ClaudeClaw context via keyword search
│                               Keep short and high-signal
│
├── memory/
│   ├── 2026-04-28.md           Raw daily session log
│   ├── 2026-04-27.md           One file per day
│   └── ...                     Source material for MEMORY.md distillation
│
│  ── AUTOMATIC MEMORY (claudeclaw.db) ──────────────────────────────
│
│   NOTE: ClaudeClaw also maintains a parallel SQLite memory system
│   at /home/zeke/claudeclaw/store/claudeclaw.db. Every conversation
│   turn is automatically extracted by Gemini, embedded, and stored.
│   This complements the vault — vault provides human-readable,
│   long-term curated context; the DB provides fast semantic recall.
│
│  ── PROACTIVE BEHAVIOR ────────────────────────────────────────────
│
├── HEARTBEAT.md                Checklist for ClaudeClaw's scheduled maintenance
│                               Read by the cron scheduled task at 3 AM
│                               Keep small — burns tokens on every run
│                               Example tasks: distill logs, update USER.md
│
│  ── KNOWLEDGE BASE ────────────────────────────────────────────────
│
├── second-brain/
│   ├── README.md               Index / navigation for the knowledge base
│   ├── journal/
│   │   └── 2026-04-28.md       Daily summaries of important discussions
│   ├── concepts/
│   │   └── example.md          Deep dives on important ideas / frameworks
│   └── documents/              Working documents, strategies, plans
│
│  ── DIRECTIVES / SOPs ─────────────────────────────────────────────
│
├── directives/
│   ├── example-sop.md          Step-by-step workflow for repeatable tasks
│   └── ...                     One file per workflow/SOP
│
│  ── PROJECTS ──────────────────────────────────────────────────────
│
└── projects/
    └── my-project/             One folder per project
        └── ...                 Project-specific files, notes, assets
```

---

## File Lifecycle

### MEMORY.md (Long-Term Memory)
- **Written:** By ClaudeClaw during heartbeat maintenance or when you say "save this to memory"
- **Read:** Via `buildObsidianContext()` — injected when query keywords match
- **Content:** Key decisions, important context, lessons learned, preferences
- **Keep:** Short and high-signal. Remove outdated entries regularly.

### memory/YYYY-MM-DD.md (Daily Logs)
- **Written:** Manually during each session, or by ClaudeClaw on request
- **Read:** By heartbeat maintenance task for distillation into MEMORY.md
- **Content:** Unformatted notes, session summaries, quick captures
- **Keep:** All logs — they are the source for distillation

### claudeclaw.db memories table (Automatic)
- **Written:** Automatically — every conversation turn is processed by Gemini, embedded, and stored
- **Read:** Via cosine-similarity search at each session turn
- **Content:** Gemini-extracted summaries with entities, topics, importance score
- **Keep:** Managed automatically; consolidation runs periodically

### second-brain/journal/YYYY-MM-DD.md (Daily Summaries)
- **Written:** End of significant conversations
- **Read:** When researching past work or context
- **Content:** Structured summary — discussion topics, decisions, open questions
- **Keep:** Permanent record

### HEARTBEAT.md (Proactive Checklist)
- **Written:** When you want ClaudeClaw to do something proactively on a schedule
- **Read:** By ClaudeClaw's scheduled task at configured cron interval
- **Content:** Short checklist of tasks, checks, reminders
- **Keep:** Small — it burns tokens on every scheduled run

### SOUL.md → CLAUDE.md (Persona)
- **Written:** When you update ClaudeClaw's persona or operating rules
- **Read:** Surfaces in ClaudeClaw context whenever "soul", "persona", or "rules" match
- **Content:** ClaudeClaw's identity, tone, capabilities, specialist agents
- **Keep:** In sync with `/home/zeke/claudeclaw/CLAUDE.md` (they are the same file via symlink)

### directives/ (SOPs)
- **Written:** When a workflow is established and should be repeatable
- **Read:** When ClaudeClaw executes that specific workflow
- **Content:** Step-by-step instructions, inputs, outputs, edge cases
- **Keep:** Update as workflows evolve

---

## ClaudeClaw vs Hermes Memory: Key Differences

| Aspect | Hermes Agent | ClaudeClaw |
|--------|-------------|-----------|
| Automatic memory | `state.db` sessions | `claudeclaw.db` with Gemini extraction + embeddings |
| Persona file | `~/.hermes/SOUL.md` | `/home/zeke/claudeclaw/CLAUDE.md` |
| Memory config | `memory_enabled: true` in `config.yaml` | Always on — `memory-ingest.ts` runs automatically |
| Scheduled tasks | `hermes cron add` | Ask ClaudeClaw to schedule; uses `scheduler.ts` + SQLite |
| Session search | `session_search` toolset | Cosine-similarity search over `claudeclaw.db` embeddings |
| Vault read | Memory injection at session start | `buildObsidianContext()` keyword search on every message |

---

## Obsidian-Specific Tips

- Use `[[filename]]` wiki-links to create edges in the Graph View
- Tag files with `#memory`, `#concept`, `#directive` for filtering
- Dataview plugin queries across all files:
  ```
  TABLE file.mtime FROM "memory" SORT file.mtime DESC
  ```
- Set `memory/` as the daily notes folder in Obsidian settings
- Use Canvas for visual planning that links back to notes
- The symlinked SOUL.md appears as a normal file in Obsidian — edits sync instantly to `CLAUDE.md`
