---
name: local-file-ops
description: Safely summarize, audit, and organize local files and folders. Produces folder summaries, duplicate reports, large-file inventories, and cleanup plans. No move, rename, or delete actions without explicit approval of exact paths.
version: 1.0.0
allowed-tools: Bash Read Write
---

# Local File Ops

## Trigger
Use this skill when the user asks to summarize a folder, find duplicate files, identify large files, propose a cleanup plan, organize a project directory, or audit workstation storage. Also use before archiving or deleting a project to ensure nothing valuable is lost.

## Required Inputs
- Target path(s): one or more directories to inspect (e.g. `~/Downloads`, `~/Documents`).
- Operation mode: `report-only` (default — no changes) or `propose-plan` (generates a specific move/delete proposal for approval).
- Max depth for traversal: default 3 levels.
- Size threshold for large-file flagging: default 100MB.
- Duplicate detection method: `name+size` (fast, default) or `content-hash` (thorough, requires approval due to read cost on large trees).

## Procedure
1. **Scope confirmation (always first)**
   - Echo the target path(s) and mode back to the user before any traversal.
   - If target path contains `~/.ssh`, `~/.gnupg`, `~/.config`, or `/etc`: require explicit confirmation before proceeding.
2. **Folder summary (read-only)**
   - Total size, file count, subdirectory count.
   - Top 10 largest files with sizes.
   - Top 5 largest subdirectories with sizes.
   - File type breakdown (by extension, top 10).
   - Commands: `du -sh`, `find`, `ls -lhS`.
3. **Large file report (read-only)**
   - List all files exceeding the size threshold with full path, size, and last-modified date.
   - Flag files not accessed in >180 days as archive candidates.
4. **Duplicate detection (read-only)**
   - `name+size` mode: group files by identical name + size; flag groups with 2+ members.
   - `content-hash` mode: run `md5sum` or `sha256sum` on candidates; requires explicit approval before running on trees >1GB.
   - Report: duplicate group, file count, wasted space, all paths.
5. **Stale and orphan detection (read-only)**
   - Flag: temp files (`*.tmp`, `*.bak`, `~*`, `*.swp`), empty directories, zero-byte files.
   - Flag: log files >50MB.
   - Flag: `node_modules` / `.venv` / `__pycache__` / build artifacts outside active projects.
6. **Cleanup plan (propose-plan mode only)**
   - Generate an explicit, line-by-line plan: action (`DELETE`, `MOVE`, `ARCHIVE`), exact source path, exact destination (if move/archive), reason.
   - Group by risk: `Safe to remove` vs `Review before removing`.
   - Do **not** execute any action — present the plan for approval.
7. **Await approval before any mutation**
   - If user approves the cleanup plan, execute actions one at a time, confirming each batch.
   - Log every completed action to `/home/zeke/claudeclaw/outputs/file-ops-YYYY-MM-DD.log`.

## Guardrails
- **Default mode is report-only.** No file is moved, renamed, or deleted unless the user explicitly approves a specific cleanup plan.
- Do **not** traverse or report on `~/.ssh`, `~/.gnupg`, or any path containing `secret`, `token`, `key`, `credential` in the name — skip and note.
- Do **not** delete any file modified in the last 7 days without a second explicit confirmation.
- Do **not** run content-hash deduplication on trees >1GB without approval (I/O cost).
- Do **not** empty a directory named after a project without confirming it is archived or committed.
- Always show exact paths in the cleanup plan — no wildcards in approval requests.
- Log all executed mutations; never silently skip a failed action.

## Output Format

```markdown
# Local File Ops Report
- Target Path(s):
- Mode: Report-Only | Propose-Plan
- Timestamp:
- Depth:

## 1) Folder Summary
- Total size:
- File count:
- Subdirectory count:
- Top 5 largest subdirs:
- Top 10 largest files:
- File type breakdown:

## 2) Large File Report (>threshold)
| File | Size | Last Modified | Flag |
|------|------|--------------|------|

## 3) Duplicate Report
| Group | Files | Wasted Space | Paths |
|-------|-------|-------------|-------|

## 4) Stale & Orphan Findings
- Temp files:
- Empty directories:
- Build artifacts:
- Large logs:

## 5) Cleanup Plan (propose-plan mode only)
| # | Action | Path | Destination | Reason | Risk |
|---|--------|------|-------------|--------|------|

## Verification
- Commands used:
- Paths skipped (sensitive):
- Confidence:
- Log file (if mutations executed):
```

## Verification
A run passes only if:
- Scope confirmation was echoed before traversal.
- Sections 1–4 are present (or explicitly marked not applicable).
- No file was modified without an approved cleanup plan.
- Every action in an executed plan is logged.
- Sensitive paths were skipped and noted.

## Sample Prompt
"Run Local File Ops in report-only mode on ~/Downloads and ~/Documents. Summarize folder sizes, flag files over 100MB, identify duplicates by name and size, and list stale temp files. Do not move or delete anything."

## Notes
- Always start in `report-only` mode — let the user decide if a cleanup plan is needed after seeing the report.
- `node_modules`, `.venv`, and `__pycache__` are often safe to delete from inactive projects but should be confirmed — they are regenerable, not unique.
