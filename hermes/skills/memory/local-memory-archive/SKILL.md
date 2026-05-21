---
name: local-memory-archive
description: Archive overgrown Hermes durable memory entries to local SSD files instead of keeping them in injected memory. Use when memory is full, memory writes fail due to capacity, old durable facts should be retained for future reference but removed or compacted from active memory, or the user asks to store memory/archive knowledge locally without using persistent memory budget.
---

# Local Memory Archive

Use this skill to move low-priority or verbose durable memory out of Hermes injected memory and into a searchable local archive on disk.

## Storage location

Default archive root:

`/home/zeke/.hermes/local-memory-archive/`

Files:
- `archives/YYYY-MM-DD.md` — human-readable snapshots.
- `archives/YYYY-MM-DD.jsonl` — one JSON object per archived memory entry.
- `index.md` — brief index of archive snapshots and search commands.

This archive lives on local SSD and is not injected into every session. Load it only when needed with `read_file` or search it with `search_files`.

## Procedure

1. Read active memory files:
   - `/home/zeke/.hermes/memories/MEMORY.md`
   - `/home/zeke/.hermes/memories/USER.md` only if user-profile memory is also full.
2. Split entries on the separator line `§`.
3. Classify entries:
   - Keep in active memory: facts needed frequently, safety-critical quirks, current service paths, current credentials-location hints without secret values.
   - Archive locally: verbose historical setup notes, old status details, repeated troubleshooting procedures already covered by skills, completed-work logs, stale project details, raw IDs that are easily searchable elsewhere.
   - Move to skills: reusable procedures, troubleshooting checklists, command sequences, and pitfalls.
4. Append archived entries to the local archive in both Markdown and JSONL formats.
5. Add or update `index.md` with snapshot date, source file, count, and search examples.
6. Only after verifying the archive, remove or compact selected entries from active memory using the `memory` tool. Do not delete facts that are not archived unless the user explicitly asks.
7. Verify memory headroom by retrying a small memory add/replace or by checking the next memory-tool output.

## Commands / script

Use the bundled script for deterministic archiving. On this host `/usr/bin/python` may be absent, so prefer the Hermes venv Python:

`/home/zeke/.hermes/hermes-agent/venv/bin/python3 /home/zeke/.hermes/skills/memory/local-memory-archive/scripts/archive_hermes_memory.py --source /home/zeke/.hermes/memories/MEMORY.md --archive-root /home/zeke/.hermes/local-memory-archive --tag manual-memory-capacity-fix`

The script is read-only with respect to active memory. It writes archive files only. Active memory deletion/compaction must be done separately via the `memory` tool after verification.

For the detailed capacity triage/verification pattern from the first archive run, read `references/memory-capacity-triage.md`.

## Search archived memory

Use file search instead of active memory:

`search_files(pattern="Codex OAuth|discord-homes|Mission Control", path="/home/zeke/.hermes/local-memory-archive", target="content")`

Or from shell:

`rg -n "Codex OAuth|discord-homes|Mission Control" /home/zeke/.hermes/local-memory-archive`

## Guardrails

- Never print archived secrets in final responses. If an entry contains a token or API key, archive it locally but summarize it in final output as `[secret archived locally]`.
- Do not remove active memory before the archive file exists and has non-zero size.
- Prefer compacting active memory over deleting everything. Keep a small pointer like: `Archived historical Hermes memory lives at /home/zeke/.hermes/local-memory-archive; search it before asking the user to repeat old setup details.`
- Procedures belong in skills, not active memory. If an archived item is a workflow, create or patch the relevant skill.
