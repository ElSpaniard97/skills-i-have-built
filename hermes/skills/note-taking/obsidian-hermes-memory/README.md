# obsidian-hermes-memory

**Hermes Agent skill:** Use Obsidian + Hermes as a living AI memory system with a knowledge graph.

Adapted from [obsidian-openclaw-memory](https://github.com/Samin12/obsidian-openclaw-memory) by Samin12.

---

## What this does

This skill wires your Obsidian vault directly to Hermes Agent's memory system. Hermes reads `SOUL.md`, `MEMORY.md`, and `USER.md` at every session start. Obsidian visualises the knowledge graph. A Hermes cron job maintains memory overnight — distilling daily logs into long-term memory automatically.

## Install

```bash
hermes skills install ElSpaniard97/obsidian-hermes-memory
```

Or clone manually into your skills directory:

```bash
git clone https://github.com/ElSpaniard97/obsidian-hermes-memory \
  ~/.hermes/skills/note-taking/obsidian-hermes-memory
```

## Requirements

- Hermes Agent v0.8+
- `OBSIDIAN_VAULT_PATH` set in `~/.hermes/.env`
- Obsidian desktop app

## Quick start

1. Set your vault path in `~/.hermes/.env`:
   ```
   OBSIDIAN_VAULT_PATH=/home/youruser/Hermes-Vault
   ```
2. Symlink Hermes memory files into the vault:
   ```bash
   ln -sf ~/.hermes/SOUL.md "$OBSIDIAN_VAULT_PATH/SOUL.md"
   ln -sf ~/.hermes/memories/MEMORY.md "$OBSIDIAN_VAULT_PATH/MEMORY.md"
   ln -sf ~/.hermes/memories/USER.md "$OBSIDIAN_VAULT_PATH/USER.md"
   ln -sf ~/.hermes/memories "$OBSIDIAN_VAULT_PATH/memory"
   ```
3. Open the vault in Obsidian → File → Open Vault → Open Folder as Vault
4. Schedule nightly memory maintenance:
   ```bash
   hermes cron add "memory-heartbeat" "0 3 * * *" \
     "Read $OBSIDIAN_VAULT_PATH/HEARTBEAT.md and complete all unchecked tasks"
   ```

See `SKILL.md` for the full guide.

## License

MIT
