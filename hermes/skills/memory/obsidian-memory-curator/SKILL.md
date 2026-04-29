---
name: obsidian-memory-curator
description: Curate durable memory from sessions into reviewable Obsidian-ready updates by separating long-term facts from temporary noise.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [memory, obsidian, curation, knowledge-management, review]
---

# Obsidian Memory Curator

## Trigger
Use this skill when the user asks to clean memory, summarize durable context, prepare Obsidian updates, reduce memory noise, or review what should/should not be saved long-term.

## Required Inputs
- Source material: recent sessions, notes, or raw project updates.
- Target scope: person/profile facts, project conventions, environment facts, and open loops.
- Output mode: proposal-only (default) or approved-write mode.

## Procedure
1. **Collect candidate facts**
   - Extract potential memory items from session summaries, notes, and logs.
2. **Classify each item**
   - Durable fact (save candidate)
   - Temporary state (do not save)
   - Action/TODO (track elsewhere, not memory)
3. **Apply durability filter**
   - Keep only facts likely useful across future sessions.
   - Remove one-off outcomes, transient statuses, and noisy detail.
4. **Normalize and deduplicate**
   - Rewrite as concise declarative statements.
   - Merge duplicates/near-duplicates.
5. **Risk and sensitivity check**
   - Redact secrets, tokens, private identifiers not needed for future work.
6. **Prepare review proposal**
   - Present `Add`, `Replace`, `Remove`, and `Skip` sections with rationale.
7. **Await approval for writes**
   - Only apply durable memory updates after explicit approval.

## Guardrails
- Do **not** auto-write durable memory by default.
- Do **not** store secrets, passwords, tokens, or sensitive personal data unless explicitly requested and justified.
- Do **not** store temporary task progress or completed-task logs as long-term memory.
- Do **not** present imperative self-instructions as memory facts.

## Output Format
Return markdown with this exact structure:

```markdown
# Obsidian Memory Curation Review
- Scope:
- Timestamp:
- Mode: Proposal-Only | Approved-Write

## 1) Candidate Summary
- Total candidates:
- Durable candidates:
- Rejected as temporary:

## 2) Proposed Adds
- [target: user|memory] statement
- Rationale:

## 3) Proposed Replacements
- Old:
- New:
- Rationale:

## 4) Proposed Removals
- Statement:
- Rationale:

## 5) Skipped Items (Not Durable)
- Item:
- Reason skipped:

## 6) Open Loops (Non-memory)
- Item:
- Suggested tracker location:

## Verification
- Sources reviewed:
- Dedup applied:
- Sensitive-data check:
- Ready for approval:
```

## Verification
A run passes only if:
- Add/Replace/Remove proposals are clearly separated from skipped temporary items.
- Every proposed durable item is declarative and future-useful.
- Sensitive content is redacted or excluded.
- No memory write occurs without explicit user approval.

## Sample Prompt
"Curate the last week of Hermes activity into durable memory proposals for Obsidian. Proposal-only mode with Add/Replace/Remove/Skip sections."

## Notes
- Prefer fewer, high-value memory items over large noisy dumps.
- Keep language compact and factual for long-term retrieval quality.
