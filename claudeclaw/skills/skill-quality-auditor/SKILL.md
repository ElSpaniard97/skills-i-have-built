---
name: skill-quality-auditor
description: Audit the ClaudeClaw skills catalog for trigger clarity, input clarity, safety guardrails, verification steps, output format completeness, and inter-skill overlap. Produces a scored report with prioritized change recommendations.
version: 1.0.0
allowed-tools: Bash Read
---

# Skill Quality Auditor

## Trigger
Use this skill when the user asks to audit the skills catalog, review skill quality, find overlapping or stale skills, score a single skill, or prepare the catalog for a new phase of expansion.

## Required Inputs
- Scope: `full` (all installed skills), `skill/<name>` (one skill).
- Skills root: `/home/zeke/claudeclaw/skills/` (default).
- Output target: chat reply or file (`/home/zeke/claudeclaw/outputs/skill-audit-YYYY-MM-DD.md`).

## Scoring Rubric

Each skill is scored out of **100** across six dimensions (max points shown):

| Dimension | Max | What earns full marks |
|-----------|-----|-----------------------|
| **Trigger clarity** | 20 | Trigger is specific, unambiguous, and distinguishes this skill from similar ones |
| **Input clarity** | 15 | All required inputs are listed; none are implicit or assumed |
| **Safety / guardrails** | 20 | At least three explicit guardrails; destructive actions require approval; no silent mutations |
| **Verification** | 20 | Concrete pass/fail criteria; at least one evidence requirement per major step |
| **Output format** | 15 | Exact output structure defined; consumer (chat/dashboard/cron) is named |
| **Maintainability** | 10 | Version field present; no hardcoded paths that break profiles; no stale references |

**Score bands:**
- 90–100: Publish-ready
- 75–89: Minor edits needed
- 50–74: Needs rework
- <50: Rewrite or deprecate

## Procedure
1. **Enumerate skills (read-only)**
   - `find /home/zeke/claudeclaw/skills -name "SKILL.md" | sort` to collect all skill paths.
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
