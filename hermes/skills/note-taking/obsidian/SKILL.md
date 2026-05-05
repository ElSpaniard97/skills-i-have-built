---
name: obsidian
description: Read, search, and create notes in the Obsidian vault.
---

# Obsidian Vault

**Location:** `OBSIDIAN_VAULT_PATH=/home/zeke/claudeclaw` (set in `~/.hermes/.env`).

## Vault Structure

```
/home/zeke/claudeclaw/          ← Obsidian vault root
├── SOUL.md                     ← Agent persona (symlink → CLAUDE.md)
├── USER.md                     ← Context about the human (name, goals, prefs)
├── MEMORY.md                   ← ★ Curated long-term memory ★
├── HEARTBEAT.md                ← Checklist for scheduled maintenance
├── memory/
│   └── YYYY-MM-DD.md           ← Raw daily session logs
├── second-brain/
│   ├── journal/                ← Daily summaries
│   ├── concepts/               ← Deep dives on ideas/frameworks
│   └── documents/              ← Working docs, strategies, plans
├── directives/                 ← SOPs and repeatable workflows
└── projects/                   ← Per-project folders
```

## Read a note

```bash
VAULT="${OBSIDIAN_VAULT_PATH:-/home/zeke/claudeclaw}"
cat "$VAULT/Note Name.md"
```

## List notes

```bash
VAULT="${OBSIDIAN_VAULT_PATH:-/home/zeke/claudeclaw}"

# All notes
find "$VAULT" -name "*.md" -type f -not -path '*/.git/*' -not -path '*/.obsidian/*' -not -path '*/node_modules/*'

# In a specific folder
ls "$VAULT/memory/"
```

## Search

```bash
VAULT="${OBSIDIAN_VAULT_PATH:-/home/zeke/claudeclaw}"

# By filename
find "$VAULT" -name "*.md" -iname "*keyword*" -not -path '*/.git/*'

# By content
grep -rli "keyword" "$VAULT" --include="*.md" --exclude-dir=.git --exclude-dir=.obsidian --exclude-dir=node_modules
```

## Create a note

```bash
VAULT="${OBSIDIAN_VAULT_PATH:-/home/zeke/claudeclaw}"
cat > "$VAULT/New Note.md" << 'ENDNOTE'
# Title

Content here.
ENDNOTE
```

## Append to a note

```bash
VAULT="${OBSIDIAN_VAULT_PATH:-/home/zeke/claudeclaw}"
echo "
New content here." >> "$VAULT/Existing Note.md"
```

## Key Files

| File | Purpose |
|------|---------|
| `MEMORY.md` | Curated long-term memory — key facts, open loops, preferences |
| `USER.md` | Identity, goals, communication preferences, expertise |
| `HEARTBEAT.md` | Checklist for scheduled maintenance tasks |
| `memory/YYYY-MM-DD.md` | Raw daily session logs (source for distillation) |
| `directives/*.md` | SOPs and repeatable workflows |

## Saving to Memory

When the user says "save this to memory" or "remember this":
1. Read current `MEMORY.md`
2. Append the new fact under the appropriate section (Key Facts, Open Loops, or Preferences & Conventions)
3. Deduplicate — don't add what's already there

## Writing Daily Logs

After significant sessions, write a summary to `memory/YYYY-MM-DD.md`:
```bash
VAULT="${OBSIDIAN_VAULT_PATH:-/home/zeke/claudeclaw}"
cat > "$VAULT/memory/$(date +%Y-%m-%d).md" << 'EOF'
# Session Log - $(date +%Y-%m-%d)

## Topics Discussed

## Decisions Made

## Things to Remember
EOF
```

## Wikilinks

Obsidian links notes with `[[Note Name]]` syntax. When creating notes, use these to link related content. This builds the Graph View.

## Guardrails

- Do NOT overwrite MEMORY.md or USER.md without showing proposed changes first
- Do NOT delete memory/YYYY-MM-DD.md logs — they are source of truth
- Do NOT symlink files containing secrets into the vault
- Keep MEMORY.md curated and short — distilled essence, not a dump
