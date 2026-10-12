---
name: github-repo-review
description: "Run a standardized, evidence-based quality review of a GitHub repository or local repo (README and docs, license, hygiene, secret exposure, CI and tests, structure, portfolio readiness) and return a scored report with prioritized findings and proposed patches. Use when the user asks to review, audit, or grade a repo, check whether a project is portfolio- or production-ready, find what a repo is missing, or run periodic QA across several repos. Recommends changes only; never pushes."
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
   - Useful commands: `gh repo view OWNER/REPO --json defaultBranchRef,pushedAt,licenseInfo,description`, `gh pr list --state open`, `gh issue list --state open`, or for a local clone `git log -1 --format=%cd` and `git ls-files | head -200`.
2. **Documentation quality**
   - Check README completeness (purpose, setup, usage, architecture, troubleshooting).
   - Verify LICENSE presence and contribution guidance.
3. **Project hygiene**
   - Check `.gitignore`, `.editorconfig` (if relevant), dependency lockfiles, and env template usage.
   - Scan for obvious secret exposure patterns and unsafe hardcoded credentials (use `gitleaks detect --no-banner` or `trufflehog git file://.` if installed; otherwise `git grep -nIE '(api[_-]?key|secret|token|password)\s*[:=]'` and review hits by hand).
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

## Scoring
Score each area, then sum to /100: Documentation 25, Hygiene & Security 25, CI/Test 20, Structure & Maintainability 15, Links & Portfolio Readiness 15. Any confirmed exposed secret caps the overall score at 49 and readiness at "Needs Work".
Readiness: 85+ Production, 70–84 Portfolio-Ready, below 70 Needs Work.

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
"Review `owner/repo` for documentation, CI, hygiene, and portfolio readiness. Return the GitHub Repository Review with prioritized recommendations only."

## Notes
- Prefer reproducible checks over opinion.
- If API access is limited, perform local-structure review and clearly state limitations.
- Pair with `career-artifact-builder` to turn strong repo findings into portfolio content.
