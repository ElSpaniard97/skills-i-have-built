---
name: skill-quality-auditor
description: "Audit a skills catalog (or a single skill) for trigger-ready descriptions, input clarity, safety guardrails, verification steps, output format, maintainability, and overlap between skills, and return a scored report with prioritized, concrete edit recommendations. Use when the user asks to audit or grade their skills, find overlapping, stale, or broken skills, check a new SKILL.md before publishing, or clean up the catalog after adding several skills. Read-only: never edits skill files."
version: 1.1.0
allowed-tools: Bash Read
---

# Skill Quality Auditor

## Trigger
Use this skill when the user asks to audit the skills catalog, review skill quality, find overlapping or stale skills, score a single skill, or prepare the catalog for a new phase of expansion.

## Required Inputs
- Scope: `full` (all installed skills), `skill/<name>` (one skill).
- Skills root: `${CLAUDECLAW_HOME:-$HOME/claudeclaw}/skills/` (default), or any folder of `*/SKILL.md` the user names.
- Output target: chat reply or file (`${CLAUDECLAW_HOME:-$HOME/claudeclaw}/outputs/skill-audit-YYYY-MM-DD.md`).

## Scoring Rubric

Each skill is scored out of **100** across six dimensions (max points shown):

| Dimension | Max | What earns full marks |
|-----------|-----|-----------------------|
| **Trigger clarity** | 20 | The frontmatter `description` says both what the skill does and when to use it (the description is what decides whether the skill loads), with concrete user phrasings, and distinguishes it from similar skills |
| **Input clarity** | 15 | All required inputs are listed; none are implicit or assumed |
| **Safety / guardrails** | 20 | At least three explicit guardrails; destructive actions require approval; no silent mutations |
| **Verification** | 20 | Concrete pass/fail criteria; at least one evidence requirement per major step |
| **Output format** | 15 | Exact output structure defined; consumer (chat/dashboard/cron) is named |
| **Maintainability** | 10 | Valid frontmatter (`name` matches the folder, lowercase-hyphenated; `description` under 1024 characters); version field present; no hardcoded home-directory paths; every referenced script/reference file exists; SKILL.md under ~500 lines with detail moved to `references/` |

**Score bands:**
- 90–100: Publish-ready
- 75–89: Minor edits needed
- 50–74: Needs rework
- <50: Rewrite or deprecate

## Procedure
1. **Enumerate skills (read-only)**
   - `find "$SKILLS_ROOT" -name SKILL.md | sort` to collect all skill paths (`SKILLS_ROOT` is the skills root above).
   - Filter by scope if not `full`.
2. **Parse each skill**
   - Extract: `name`, `description`, `version`, presence of Trigger / Required Inputs / Procedure / Guardrails / Output Format / Verification / Sample Prompt sections.
3. **Score each skill**
   - Apply the rubric above per dimension.
   - Note specific missing or weak elements per score deduction.
4. **Detect overlaps**
   - Flag any two skills whose `description` or `Trigger` covers the same use case.
   - Recommend: merge, differentiate trigger, or deprecate weaker one.
5. **Detect staleness**
   - Flag skills with no `version` field, placeholder content, or references to non-existent paths.
6. **Rank findings**
   - Sort skills by score ascending (worst first).
   - Assign change priority: `Critical` (<50), `High` (50–74), `Medium` (75–89), `Pass` (90+).
7. **Generate recommendations**
   - For each `Critical` or `High` skill: one concrete edit recommendation.
   - For overlaps: one merge or differentiation recommendation.
8. **Summarize catalog health**
   - Overall pass rate, average score, top risks.

## Guardrails
- Do **not** edit or delete any skill file during the audit.
- Do **not** claim a skill is safe unless its guardrails section was explicitly checked.
- Do **not** mark a skill as stale solely because it is simple — brevity is not a defect.
- Recommendations must be actionable edits, not vague complaints.
- If a skill file cannot be parsed, flag it as `Unreadable` and continue.

## Output Format

```markdown
# Skill Quality Audit Report
- Timestamp:
- Scope:
- Skills evaluated:
- Overall pass rate (≥75):
- Average score:

## Catalog Health Summary
- Publish-ready (90–100):
- Minor edits (75–89):
- Needs rework (50–74):
- Rewrite/deprecate (<50):
- Overlaps detected:
- Stale skills detected:

## Skill Scores (sorted by score ascending)

| Skill | Score | Trigger | Inputs | Safety | Verification | Output | Maint. | Priority |
|-------|-------|---------|--------|--------|--------------|--------|--------|----------|

## Overlap Findings
- Skills A + B: <overlap description> — Recommendation: <merge|differentiate|deprecate>

## Staleness Findings
- Skill: <path> — Issue: <description>

## Change Recommendations (Critical and High only)
1. [Critical] `<skill-path>`: <specific edit needed>
2. [High] `<skill-path>`: <specific edit needed>

## Verification
- Skills enumerated via:
- Parse errors:
- Confidence:
```

## Verification
A run passes only if:
- Every skill in scope has a row in the scores table.
- Every `Critical` or `High` skill has at least one concrete recommendation.
- Overlaps are identified by comparing trigger text, not just names.
- No skill file was modified during the audit.

## Sample Prompt
"Run a full skill quality audit across all installed skills. Score each skill, flag overlaps and stale entries, and return the standard audit report with change recommendations for anything below 75."

## Notes
- Run this skill after any major expansion of the catalog (e.g. after adding 5+ new skills).
- The rubric is intentionally strict on guardrails and verification — these are the dimensions most likely to cause unsafe behavior at runtime.
