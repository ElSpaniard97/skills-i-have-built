---
name: career-artifact-builder
description: Convert real project work into recruiter-ready artifacts — resume bullets, LinkedIn posts, portfolio case studies, and STAR stories. Claims are grounded in actual evidence, never fabricated.
version: 1.0.0
allowed-tools: Read Bash
---

# Career Artifact Builder

## Trigger
Use this skill when the user asks to write resume bullets, draft a LinkedIn post about a project, build a portfolio case study, compose a STAR story, or turn project activity into career-facing content.

## Required Inputs
- Source material: one or more of — project notes, Git commit history, README, session logs, task records, or a plain description of what was built/done.
- Artifact type(s) requested: `resume-bullet`, `linkedin-post`, `portfolio-case-study`, `star-story`, or `all`.
- Target role or audience (optional but improves quality): e.g. "IT Operations Engineer", "AI/ML Engineer", "DevOps".
- Tone: `professional` (default), `conversational` (LinkedIn), or `technical`.

## Procedure
1. **Extract evidence (read-only)**
   - Pull concrete facts from source material: what was built, what problem it solved, what changed, what scale or impact can be stated.
   - Flag any claim that cannot be supported by evidence — do not invent metrics.
2. **Identify the core achievement**
   - Distill to one sentence: `[Action verb] + [what] + [result or scale]`.
   - Confirm the achievement is defensible in an interview.
3. **Draft requested artifact(s)**

   ### Resume Bullet
   - Format: `[Strong action verb] [what you built/did] [using what] [resulting in measurable outcome or clear value]`.
   - Max 2 lines. Quantify where evidence exists. No buzzword padding.

   ### LinkedIn Post
   - Opening hook (1 sentence, no "I'm excited to share").
   - 3–5 short paragraphs: problem → what you built → key insight or result → what you learned.
   - Closing call to action or reflection.
   - Hashtags (3–5, relevant, not spammy).
   - Tone: `conversational` unless overridden.

   ### Portfolio Case Study
   - Sections: Problem, Approach, What I Built, Key Decisions, Results/Impact, What I'd Do Differently.
   - 300–600 words. Link to repo or live demo if available.
   - Recruiter-readable: no unexplained jargon.

   ### STAR Story
   - **Situation:** context and stakes.
   - **Task:** your specific responsibility.
   - **Action:** concrete steps you took (emphasize your decisions, not the team's).
   - **Result:** outcome, impact, or lesson — quantified if possible.
   - Target length: 150–250 words for interview use.

4. **Accuracy check**
   - Re-read each artifact against the source evidence.
   - Remove or soften any claim not directly supported.
   - Flag any metric that is an estimate — label it as such.
5. **Present artifacts for review**
   - Always present as drafts. User approves before any posting or saving.

## Guardrails
- Do **not** fabricate metrics, impact claims, or outcomes not present in the source material.
- Do **not** post or publish to LinkedIn or any platform — output is drafts only.
- Do **not** include private project details, client names, or internal identifiers without explicit approval.
- Do **not** use filler phrases: "I'm excited to share", "passionate", "synergy", "leverage" (verb), "utilize".
- If source material is thin, say so and ask for more evidence rather than padding.

## Output Format

```markdown
# Career Artifact Draft
- Source:
- Artifact Type(s):
- Target Role/Audience:
- Timestamp:

## Resume Bullet
> [draft]
Evidence basis: [what from source supports this]

## LinkedIn Post
[draft]

## Portfolio Case Study
**Problem:**
**Approach:**
**What I Built:**
**Key Decisions:**
**Results/Impact:**
**What I'd Do Differently:**

## STAR Story
**Situation:**
**Task:**
**Action:**
**Result:**

## Accuracy Notes
- Claims fully supported:
- Claims estimated (flagged):
- Claims removed (unsupported):

## Next Steps
- [ ] Review and approve drafts
- [ ] Add any missing metrics or context
```

## Verification
A run passes only if:
- Every metric or impact claim traces back to source evidence.
- At least one artifact type is fully drafted.
- Accuracy notes section is present and honest.
- No artifact is posted or saved without explicit user approval.

## Sample Prompt
"Build career artifacts for [project]. Source: the README and commit history. Target role: AI/ML Operations Engineer. Give me a resume bullet, a STAR story, and a LinkedIn post draft."

## Notes
- STAR stories work best when the Action section uses first-person singular decisions, not team actions.
- For LinkedIn, shorter posts (150–250 words) consistently outperform long-form on engagement.
