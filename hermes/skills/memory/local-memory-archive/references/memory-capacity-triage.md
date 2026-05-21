# Memory Capacity Triage Pattern

Use this reference when Hermes durable memory is near capacity or `memory` tool writes fail.

## Proven sequence

1. Read active memory files before changing anything:
   - `/home/zeke/.hermes/memories/MEMORY.md`
   - `/home/zeke/.hermes/memories/USER.md` if user-profile memory is relevant.
2. Archive both to local SSD first using the skill script.
3. Verify archive files are non-zero and searchable:
   - `du -h /home/zeke/.hermes/local-memory-archive/archives/YYYY-MM-DD.*`
   - `rg -n "<known old detail>" /home/zeke/.hermes/local-memory-archive`
4. Compact active memory with the `memory` tool:
   - Replace verbose facts with shorter current-state summaries.
   - Remove entries that are now covered by a class-level skill or the local archive.
   - Keep one pointer to the archive path in active memory.
5. Retry a small memory add/replace only after compaction if needed.

## What to archive instead of keeping active

- Raw setup history and completed-work logs.
- API keys or secret-like values. Active memory should keep only where the credential lives, not the value.
- One-off repo backup notes that can be found by searching the archive.
- Long procedural notes already captured in skills.

## What to keep active

- Current service paths and service names.
- Current high-impact environment quirks.
- Short troubleshooting pivots the user repeatedly needs.
- A pointer: `Archived local memory snapshots live at /home/zeke/.hermes/local-memory-archive`.

## Verification checklist

- Archive Markdown exists and is non-zero.
- Archive JSONL exists and is non-zero.
- `index.md` includes the snapshot.
- Search can recover at least one archived fact.
- Active memory usage drops materially, ideally under 80%.

## Session example

A memory write failed at 2,190/2,200 characters. The fix was:
- Create local archive skill and script.
- Archive 9 MEMORY.md entries and 2 USER.md entries to `/home/zeke/.hermes/local-memory-archive/archives/2026-05-06.*`.
- Remove one low-priority active entry.
- Compact several verbose active entries.
- Preserve a short archive pointer in active memory.
- Result: active MEMORY.md dropped to roughly 1.6 KB / 72% usage.
