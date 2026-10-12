---
name: github-pages-portfolio-site
description: "Build and publish a recruiter-facing static portfolio or showcase site on GitHub Pages with strict secret hygiene: repo setup, hardened .gitignore, Pages enablement, a build spec, gitleaks and link-check CI, and a post-launch security audit (CSP, SRI, PII, noopener). Use when the user wants a portfolio site, a public page about their homelab, AI agents, bots, or other private systems, or wants an existing GitHub Pages site audited and hardened before sharing it with recruiters."
---

# GitHub Pages Portfolio / Showcase Site

Ship a polished static site that shows off the user's work, especially private systems, without leaking credentials, PII, or proprietary code.

## Inputs
- Owner details for the site: name, public email, LinkedIn, GitHub (confirm before publishing).
- What to showcase: projects, systems, certifications, resume.
- Visual direction: palette, vibe references, required UX features.
- Repo name and whether it already exists.

## Security hard rules (put these in any build spec, verbatim)
- Never read or copy from credential or private locations: agent config and auth files, `.env`, `*.key`, `*.pem`, databases, session logs, private notes vaults. List the exact paths for this user.
- Code shown on the site is illustrative pseudocode written fresh, never copied proprietary source.
- No phone numbers, home address, chat or bot IDs, internal hostnames, or demo credentials.

## Procedure
1. **Auth:** `gh auth status` (needs `repo` and `workflow` scopes; `gh auth refresh -s repo,workflow` if not).
2. **Create the repo:** `gh repo create OWNER/REPO --public --description "..." --clone --license mit --gitignore Node`. On a fresh machine, set `git config user.email` and `user.name` locally in the repo first, or the first commit fails.
3. **Harden:** append `.env`, `.env.*`, `*.key`, `*.pem`, `auth.json`, `*.db*`, `secrets/`, `.DS_Store` to `.gitignore`; add an empty `.nojekyll` so files starting with `_` are served.
4. **Enable Pages:** push a placeholder `index.html`, then `gh api -X POST /repos/OWNER/REPO/pages -f 'source[branch]=main' -f 'source[path]=/'`. The URL is `https://owner-lowercased.github.io/REPO/`; confirm with `curl -sI` returning 200.
5. **Write the build spec** (save it to a file, not a shell string): owner info, the security hard rules, architecture (pure static, no build step, Tailwind via CDN, inline SVG, vanilla JS), palette and typography, required UX checklist (dark mode with `prefers-color-scheme` and saved choice, mobile layout, sticky nav with scroll-spy, accessible keyboard nav and skip link, fade-ins, copy buttons on code, 404 page, Open Graph tags, Lighthouse 90+), site map, ordered sections, and "no TODOs or lorem ipsum".
6. **Build:** build it directly, or hand the spec to a coding agent. Review the result against the spec before pushing.
7. **CI** in `.github/workflows/ci.yml`: a `gitleaks/gitleaks-action` job (checkout with `fetch-depth: 0`) and a `lycheeverse/lychee-action` link check with `--exclude 'linkedin\.com'` (LinkedIn answers bots with HTTP 999 and breaks every run).
8. **Pre-launch scrub:** `gitleaks detect --source . --no-banner` returns 0 leaks; grep for key prefixes (`sk-`, `ghp_`, `xoxb-`, `AIza`, `hf_`, `AKIA`) and long digit runs; click every link; check 375px and desktop widths; check the social card.

## Post-launch security audit
Run from the repo root and fix by severity:
- **High:** real keys, phone numbers, chat IDs. Remove, rotate the credential, and treat git history as exposed.
- **Medium:** demo credentials shown publicly, missing `.gitignore`, no Content-Security-Policy.
- **Low:** CDN scripts without SRI, no `Permissions-Policy` or referrer policy, `target="_blank"` without `rel="noopener noreferrer"`, iframes without `sandbox=""`.

Useful checks: `grep -rEn 'target="_blank"' --include='*.html' . | grep -v noopener`, `grep -rnE 'innerHTML|document\.write|eval\(' --include='*.js' --include='*.html' .`, `grep -rE 'http://' --include='*.html' .` (mixed content), and `gh api /repos/OWNER/REPO/pages --jq .https_enforced`.

A workable CSP for a Tailwind CDN + Google Fonts site allows `'self'` plus `cdn.tailwindcss.com` for scripts and styles, `fonts.googleapis.com` / `fonts.gstatic.com` for fonts, and sets `object-src 'none'; base-uri 'self'; frame-ancestors 'none'`. `'unsafe-inline'` is needed for the inline theme script and Tailwind config. The Tailwind Play CDN and Font Awesome Kits cannot take SRI hashes; use pinned cdnjs builds with `integrity` where possible.

## Guardrails
- Never push secrets or PII; if one slips into a public commit, tell the user immediately and help rotate it.
- Confirm owner contact details before they go public.
- Don't force-push or rewrite history without the user's explicit OK.

## Verification
- Pages URL returns 200 and HTTPS is enforced.
- CI is green: gitleaks finds 0 leaks and the link check passes.
- The audit's High and Medium items are all fixed; Low items are fixed or explained.
- Site checked at mobile and desktop widths with theme toggle working.

## Pitfalls
- Coding agents often write minified single-line HTML; check size with `wc -c`, not line counts.
- Fade-in sections start at `opacity: 0`, so a screenshot of the top of the page can look empty; check the DOM before "fixing" it.
- A translucent sticky nav overlapping content is the intended style, not a z-index bug.
