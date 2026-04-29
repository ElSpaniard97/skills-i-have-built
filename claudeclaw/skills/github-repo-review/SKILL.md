---
name: github-repo-review
description: Perform a standardized repository quality review for GitHub projects (README, docs, CI, hygiene, structure, and risk) with patch/PR recommendations only.
version: 1.0.0
allowed-tools: Bash Read
---

# GitHub Repo Review

## Trigger
Use this skill when the user asks to review a GitHub repository, audit repo quality, assess project readiness, check portfolio quality, or run periodic repository QA.

## Required Inputs
- Repository identifier (`owner/repo`) or local repo path.
- Review mode: single repo or batch sweep.
- Output target: chat summary, markdown report, or issue-ready checklist.

## Procedure
1. **Baseline repo metadata**
   - Default branch, last commit activity, open issues/PR counts (if available).
2. **Documentation quality**
   - Check README completeness (purpose, setup, usage, architecture, troubleshooting).
   - Verify LICENSE presence and contribution guidance.
3. **Project hygiene**
   - Check `.gitignore`, `.editorconfig` (if relevant), dependency lockfiles, and env template usage.
   - Scan for obvious secret exposure patterns and unsafe hardcoded credentials.
4. **Build/test/CI posture**
   - Detect test framework and whether tests are runnable/documented.
   - Validate CI workflows exist and align to project language/runtime.
5. **Repository structure & maintainability**
   - Assess folder structure clarity, onboarding friction, and dead/duplicate artifacts.
6. **Links and portfolio readiness**
   - Validate critical links in README/docs when possible.
   - Evaluate public-facing clarity for recruiter/stakeholder consumption.
7. **Recommendations**
   - Provide prioritized findings: Critical, High, Medium, Low.
   - Propose patches/PRs/issues instead of silent rewrites.

## Guardrails
- Do **not** push commits automatically.
- Do **not** force-edit default branches.
- Do **not** expose secrets found in scans; redact evidence.
- Do **not** claim CI/test status unless command/API evidence was collected.
- For changes, provide explicit proposed patch/PR plan and wait for approval.

## Output Format

```markdown
# GitHub Repository Review
- Repository:
- Timestamp:
- Scope:
- Overall Score: /100
- Readiness: Production | Portfolio-Ready | Needs Work

## 1) Documentation
- README Coverage:
- Missing Sections:
- LICENSE/CONTRIBUTING:

## 2) Hygiene & Security
- Secret Exposure Risk:
- Config Hygiene:
- Dependency/Lockfile Notes:

## 3) CI/Test Posture
- Test Framework Detected:
- CI Workflows:
- Confidence in Build Reproducibility:

## 4) Structure & Maintainability
- Structure Assessment:
- Technical Debt Signals:

## 5) Top Findings (Prioritized)
1. [Severity] ...
2. [Severity] ...
3. [Severity] ...

## 6) Recommended Actions
- Immediate (this week)
- Near-term (this month)
- Optional improvements

## Verification
- Evidence sources:
- Commands/API checks performed:
- Known blind spots:
```

## Verification
A run passes only if:
- At least one evidence-backed finding exists in each major section.
- Findings include severity and rationale.
- Recommendations are actionable and scoped.
- Any potential secret evidence is redacted.

## Sample Prompt
"Review `owner/repo` for documentation, CI, hygiene, and portfolio readiness. Return the standardized GitHub Repository Review with prioritized recommendations only."

## Notes
- Prefer reproducible checks over opinion.
- If API access is limited, perform local-structure review and clearly state limitations.
- Pair with `career-artifact-builder` to turn strong repo findings into portfolio content.
