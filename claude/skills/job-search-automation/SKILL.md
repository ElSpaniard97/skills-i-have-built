---
name: job-search-automation
description: "Find and rank job openings that fit the user's actual background: read their resume, GitHub, or LinkedIn summary, search job connectors (Indeed, Dice) and curated boards, filter by skills, level, location and work authorization, and return a prioritized shortlist with why-it-fits notes and an application plan. Use when the user asks to find jobs, wants roles matching their resume, says they are job hunting or looking for work, or asks which openings to apply to first."
---

# Job Search Automation

Turn the user's real profile into a short, ranked list of roles worth applying to.

## Inputs
- Profile source: resume file, resume/portfolio repo, LinkedIn text, or a plain summary. Never guess profile details.
- Targets: role titles or fields, seniority, location or remote, salary floor (optional), work authorization or sponsorship needs.
- Freshness window: default last 14 days.

If targets are missing, infer them from the profile, state the assumption in one line, and proceed.

## Procedure
1. **Profile analysis.** Extract current role, years of experience, core skills, certifications, domains, and two or three standout projects. If the user has a resume or portfolio repo, read it (for example `gh repo list USER --json name,description` then read the README and resume files).
2. **Search, best sources first:**
   - Job connectors when available in this session (Indeed, Dice, or similar): run several searches that combine the target titles with the strongest skills and the location.
   - Curated GitHub boards for early-career roles, such as `SimplifyJobs/New-Grad-Positions` (Markdown/HTML table, updated by the community). In those tables 🛂 means no sponsorship and 🇺🇸 means U.S. citizenship required.
   - Web search of company career pages for named target companies.
   - Do not scrape LinkedIn or Indeed pages directly; use connectors or public listings.
3. **Filter.** Drop roles outside the seniority band, location, or authorization constraints, and anything older than the freshness window. Deduplicate the same role across sources. Strip tracking parameters from links.
4. **Rank.** Score each role on skill overlap (with the specific matching skills named), seniority fit, recency, and constraint fit. Keep the top 10–20, grouped into two to four categories (for example IT Operations, Cloud/DevOps, AI/ML, Security).
5. **Plan.** Assign Priority 1 (strong fit, posted recently) and Priority 2, then add the user's competitive advantages and resume talking points tailored to the top roles.

## Guardrails
- Never apply, message recruiters, or submit anything on the user's behalf.
- Never invent salary, requirements, or posting dates. If a listing doesn't say, write "not listed".
- Keep personal details (phone, address) out of the output.
- Say plainly when a source could not be searched.

## Output Format
```markdown
## Job Search Results for (name)
Profile summary: (3–5 bullets from their materials)
Search scope: (titles, location, window, sources searched)

### (Category)
**1. Company — Role** · Location · Posted (age) · [link]
   Why it fits: (specific skills/experience that match)
   Watch-outs: (missing requirement, sponsorship flag, etc.)

## Application Strategy
- Priority 1:
- Priority 2:
- Talking points:

## Gaps
- Sources not searched or filters relaxed:
```

## Verification
Every listed role has a working link and a source, every "why it fits" names at least one skill from the profile, and no role violates a stated constraint.

## Follow-ups to offer
Tailored cover letters for the Priority 1 roles, an ATS review of the resume against one posting (pairs with `career-artifact-builder`), or an application tracker spreadsheet.
