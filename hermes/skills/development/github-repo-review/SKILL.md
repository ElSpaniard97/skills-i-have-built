---
name: github-repo-review
description: Perform a standardized repository quality review for GitHub projects (README, docs, CI, hygiene, structure, and risk) with patch/PR recommendations only.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [github, repository, qa, review, ci, documentation]
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
   - If the repo is a static browser app and the user asks for UI suggestions or localStorage/page persistence, also read `references/static-react-localstorage-review.md` and follow its browser-verification pattern.
   - If the user asks to rename/rebrand a static GitHub Pages site from a supplied logo/reference image, also read `references/static-site-rebrand-rename.md` for the review-to-implementation workflow and verification checklist.
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
7. **Static UI/app review when applicable**
   - For single-page/static apps, run locally with a simple server and inspect the UI in a browser instead of relying only on source review.
   - If the static site has a Cloudflare Worker/API-backed chat widget, also read `references/static-site-cloudflare-worker-chat-review.md` and verify endpoint/CSP/CORS/docs consistency plus the exact visible quick-reply labels.
   - If the user supplies a brand image or reference design, analyze it with vision first, then verify the implemented/static page visually in the browser against that palette, logo treatment, typography feel, spacing, and obvious layout issues.
   - Check persistence behavior explicitly: click a tab/control, reload, and inspect `localStorage`/state restoration if the app claims to remember progress or pages.
   - When running local internal link checks, strip query strings and fragments before filesystem checks so valid links like `pricing.html#section` and `contact.html?plan=...` are not false positives.
   - Recommend practical UX hardening for local-only apps: visible backup warning, export/import validation, stronger reset confirmation, mobile tab/table behavior, and action-oriented dashboard cards.
8. **Recommendations**
   - Provide prioritized findings: Critical, High, Medium, Low.
   - Propose patches/PRs/issues instead of silent rewrites unless the user explicitly asked for implementation.
   - When making local changes, do not push automatically unless the user explicitly asked for the repository to be changed/deployed; provide changed paths and verification either way.

## Guardrails
- Do **not** push commits automatically for review-only requests.
- If the user explicitly asks to change, rename, deploy, or update a repo, implementation and push are allowed after verifying authentication, target repo, and working tree state.
- Do **not** force-edit default branches unless the user clearly requested direct changes and you have verified the scope.
- Do **not** expose secrets found in scans; redact evidence.
- Do **not** claim CI/test status unless command/API evidence was collected.
- When replacing emoji/icon-only UI controls with text labels, also check CSS sizing; circular fixed-width buttons often need pill/min-width styles.
- For review-only changes, provide explicit proposed patch/PR plan and wait for approval.

## Output Format
Return markdown with this exact structure:

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
