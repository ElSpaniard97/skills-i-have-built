# File Structure Reference

Annotated file tree for the Obsidian + Hermes Agent memory workspace.

```
$OBSIDIAN_VAULT_PATH/          (e.g. ~/Hermes-Vault)
│
│  ── CORE IDENTITY FILES ──────────────────────────────────────────
│
├── SOUL.md        ──symlink──► ~/.hermes/SOUL.md
│                               AI persona, tone, and values
│                               Who Hermes is, how it speaks
│                               Guides every response
│
├── USER.md        ──symlink──► ~/.hermes/memories/USER.md
│                               Context about the human
│                               Name, timezone, goals, preferences
│                               What to call them, what they care about
│
│  ── MEMORY FILES ─────────────────────────────────────────────────
│
├── MEMORY.md      ──symlink──► ~/.hermes/memories/MEMORY.md
│                               ★ LONG-TERM MEMORY ★
│                               Curated, distilled insights from daily logs
│                               Like a human's long-term memory
│                               Updated by heartbeat cron or on demand
│                               Injected into every Hermes session
│
├── memory/        ──symlink──► ~/.hermes/memories/
│   ├── 2026-04-25.md           Raw daily session log
│   ├── 2026-04-24.md           One file per day
│   └── ...
│
│  ── PROACTIVE BEHAVIOR ────────────────────────────────────────────
│
├── HEARTBEAT.md                Checklist for proactive Hermes cron behavior
│                               Checked on schedule (e.g. 3 AM daily)
│                               Example: "review memory, distill insights"
│                               Keep small — burns tokens on every cron run
│
│  ── KNOWLEDGE BASE ────────────────────────────────────────────────
│
├── second-brain/
│   ├── README.md               Index / navigation for the knowledge base
│   ├── journal/
│   │   └── 2026-04-25.md       Daily summaries of important discussions
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
- **Written:** By Hermes during heartbeat cron or when you say "save this to memory"
- **Read:** Every Hermes session (injected into system prompt automatically)
- **Content:** Key decisions, important context, lessons learned
- **Keep:** Short and high-signal. Remove outdated entries.

### memory/YYYY-MM-DD.md (Daily Logs)
- **Written:** During each session — raw notes Hermes saves automatically
- **Read:** Hermes reads recent logs for short-term context; searchable via session_search
- **Content:** Unformatted notes, session summaries, quick captures
- **Keep:** All logs (cheap storage, useful for distillation)

### second-brain/journal/YYYY-MM-DD.md (Daily Summaries)
- **Written:** End of significant conversations
- **Read:** When researching past work or context
- **Content:** Structured summary — discussion topics, decisions, open questions
- **Keep:** Permanent record

### HEARTBEAT.md (Proactive Checklist)
- **Written:** When you want Hermes to do something proactively on a schedule
- **Read:** By Hermes cron job at configured interval
- **Content:** Short checklist of tasks, checks, reminders
- **Keep:** Small — it burns tokens on every cron run

### directives/ (SOPs)
- **Written:** When a workflow is established and should be repeatable
- **Read:** When Hermes executes that specific workflow
- **Content:** Step-by-step instructions, inputs, outputs, edge cases
- **Keep:** Update as workflows evolve; add lessons learned

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
- The symlinked files (SOUL.md, MEMORY.md, USER.md, memory/) appear as normal files in Obsidian — edits sync instantly to Hermes
