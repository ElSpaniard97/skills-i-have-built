---
name: github-pages-portfolio-site
description: Bootstrap a recruiter-facing static portfolio/showcase site on GitHub Pages with strict secret hygiene. Use when the user wants a public site that documents their personal/private systems (AI agents, homelab, bots) without leaking credentials or proprietary code.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [github, github-pages, portfolio, showcase, security, gitleaks, static-site]
    related_skills: [github-repo-management, github-pr-workflow, codex, writing-plans]
---

# GitHub Pages Portfolio / Showcase Site

Bootstrap a recruiter-facing static site on GitHub Pages that showcases a user's personal infrastructure (AI agents, bots, homelab, second brain, etc.) **without leaking secrets or proprietary code**. Pairs well with delegating the actual UI build to a coding-agent CLI (Codex / Claude Code).

## When to use

- User wants a portfolio site about their *running* systems, not just code repos.
- The systems contain real credentials (`~/.hermes/config.yaml`, `auth.json`, bot tokens, vault notes) that **must not** be exposed.
- User wants polished UX (dark mode toggle, animations, etc.) — delegate the build to Codex with a tight spec.
- Default deploy target is GitHub Pages (free, no build step needed).

## End-to-end recipe

### 1. Confirm GitHub auth

```bash
gh auth status
```

Required scopes: `repo`, `workflow`. If missing, run `gh auth refresh -s workflow,repo`.

### 2. Create the repo + clone

```bash
cd ~/Documents/code  # or wherever the user keeps code
gh repo create <owner>/<repo-name> --public \
  --description "<one-line pitch>" \
  --clone --license mit --gitignore Node
cd <repo-name>
```

### 3. Set git identity LOCALLY (critical pitfall)

A fresh Ubuntu install often has no global git identity, so the first commit fails with:

```
fatal: unable to auto-detect email address (got 'user@hostname.(none)')
```

Set per-repo identity (avoids polluting global config):

```bash
git config user.email "<user-public-email>"
git config user.name "<user-full-name>"
```

### 4. Harden `.gitignore` and add `.nojekyll`

Append to the auto-generated `.gitignore`:

```
.env
.env.*
*.key
*.pem
auth.json
state.db*
secrets/
.idea/
.vscode/
*.swp
.DS_Store
```

Create `.nojekyll` so Pages serves files starting with `_` literally:

```bash
touch .nojekyll
```

### 5. Push placeholder, then enable Pages via API

```bash
echo '<!doctype html><meta charset=utf-8><title>Coming soon</title><h1>Coming soon</h1>' > index.html
git add -A && git commit -m "chore: scaffold repo (placeholder)"
git push -u origin main

# Enable Pages from main / root
gh api -X POST /repos/<owner>/<repo-name>/pages \
  -f 'source[branch]=main' -f 'source[path]=/'
```

Public URL: `https://<owner-lowercase>.github.io/<repo-name>/` (lowercase the owner!).

Verify after ~60s: `curl -sI https://<owner>.github.io/<repo>/ | head -1` → `HTTP/2 200`.

### 6. Write a tight spec for the coding-agent (Codex / Claude Code)

The user's vision usually includes UX requirements (dark mode toggle, animations, mobile responsive). Capture them all in a spec file, **plus security hard-rules**, before delegating.

Key spec sections (copy-pasteable structure):

- **Owner / contact info** — name, email, LinkedIn, GitHub (use real values once confirmed).
- **🚨 SECURITY HARD RULES** — bullet list of paths the agent must NEVER read or copy from. Include:
  - `~/.hermes/config.yaml`, `~/.hermes/auth.json`, `~/.hermes/state.db*`, `~/.hermes/sessions/`, `~/.hermes/hermes-agent/`
  - `~/Hermes-Vault/` or any private vault
  - any `.env`, `*.key`, `*.pem`
  - "All code shown on the site MUST be illustrative pseudocode written fresh — do NOT copy real proprietary source."
- **Architecture** — pure static (no build step), Tailwind via CDN, inline SVG diagrams, vanilla JS.
- **Visual direction** — color palette with hex codes, typography, vibe references (Linear/Vercel/Resend).
- **Required UX features** — explicit checklist (dark mode toggle with localStorage + `prefers-color-scheme`, mobile responsive, sticky nav with scroll-spy, smooth scroll, hamburger menu, IntersectionObserver fade-ins, copy-to-clipboard on code, 404 page, OG/Twitter Card meta, skip-to-content, keyboard nav, Lighthouse targets ≥ 90/95/95/95).
- **Site map** — exact file paths.
- **Section list** — ordered, with copy guidance.
- **CI workflow** — full YAML (see step 8).
- **Implementation order** — numbered.
- **Output expectations** — "no TODO, no lorem ipsum, every word ships."

Save spec to `/tmp/<project>-spec.md` (avoids shell-escaping pain).

### 7. Delegate to Codex (background + notify)

```bash
# Inside the cloned repo dir
codex exec --yolo --skip-git-repo-check "$(cat /tmp/<project>-spec.md)"
```

Run via Hermes terminal as `background=true`, `pty=true`, `notify_on_complete=true`. Typical build time for a multi-page site: 8-20 minutes.

While Codex runs, you (the orchestrator) can write the README and any auxiliary docs in parallel — Codex's working files don't conflict with the README.

### 8. CI workflow — secrets gate + link check

Create `.github/workflows/ci.yml`:

```yaml
name: ci
on:
  push:
    branches: [main]
  pull_request:
permissions:
  contents: read
jobs:
  gitleaks:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with: { fetch-depth: 0 }
      - uses: gitleaks/gitleaks-action@v2
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
  linkcheck:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: lycheeverse/lychee-action@v2
        with:
          args: --no-progress --exclude-mail --exclude 'linkedin\.com' './**/*.html' './**/*.md'
          fail: true
```

**Pitfall:** LinkedIn returns HTTP 999 to bots — **always exclude `linkedin\.com`** from lychee or the link check will fail spuriously on every push.

### 9. Optional local pre-commit guard

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/gitleaks/gitleaks
    rev: v8.21.2
    hooks:
      - id: gitleaks
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v5.0.0
    hooks:
      - id: detect-private-key
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
        args: ['--maxkb=2048']
```

```bash
pipx install pre-commit  # or pip install --user
pre-commit install
pre-commit run --all-files
```

### 10. Final scrub before announcing

```bash
gitleaks detect --source . --no-banner          # 0 leaks expected
grep -riE "sk-|ghp_|xoxb-|AIza|hf_" . --exclude-dir=.git
grep -riE "(\\b\\d{10,}\\b)" . --exclude-dir=.git  # catches stray phone/chat IDs
```

Manually open the site in incognito, click every link, toggle theme, check mobile width in dev tools, paste URL into https://www.opengraph.xyz/ to verify the social card.

Then: `git tag v1.0.0 && git push --tags`.

## Pitfalls

1. **Missing git identity** → first commit fails with `unable to auto-detect email`. Always run `git config user.email/name` after cloning a fresh repo on a fresh box.
2. **Forgetting `.nojekyll`** → Pages may strip files starting with `_` (e.g., `_assets/`).
3. **Owner casing in Pages URL** → GitHub lowercases the username in the URL even if the repo owner is mixed-case (`ElSpaniard97` → `elspaniard97.github.io`).
4. **LinkedIn link check** → always exclude `linkedin.com` from lychee.
5. **Codex copying real source** → without explicit security rules in the spec, Codex may decide to read `~/.hermes/hermes-agent/` for "accuracy." The spec MUST forbid this in plain language and list exact paths.
6. **`pipe-to-interpreter` security prompts** in Hermes when shelling `gh api ... | python3 -c ...` — prefer `--jq` flag on `gh api` instead.
7. **Codex needs a git repo** → if running outside one, use `--skip-git-repo-check`. We already have a repo here, but the flag is harmless.
8. **`gh repo create --gitignore Node`** is the cheapest way to get a sane base `.gitignore` even for a static site (covers IDE files, OS junk).
9. **Codex emits minified HTML** — Codex frequently writes `index.html` and detail pages as one giant single line. `wc -l` will show alarmingly low numbers (e.g. 14 lines for a 700-word case study). This is normal — verify with `wc -c` or by opening the file in the browser, not by line count.
10. **Vision-tool false positives on sticky nav** — when QA-ing with `browser_vision`, the tool will sometimes flag the intentional translucent backdrop-blur sticky nav as a "z-index bug" because nav text overlaps with diagram content beneath. This is the Linear/Vercel-style design, not a bug. Verify with a manual scrolled screenshot before "fixing" anything.
11. **Sections start at `opacity: 0`** when using IntersectionObserver fade-ins — the vision tool only sees the top viewport and may report "huge empty area below hero." Check `document.querySelectorAll('section').length` and `document.body.scrollHeight` via `browser_console` to confirm content is actually present before assuming a render failure.

## Verification checklist

- [ ] `gh auth status` shows `repo, workflow` scopes
- [ ] Repo created, `.nojekyll` present, hardened `.gitignore`
- [ ] Local `git config user.email/name` set
- [ ] Pages enabled, public URL returns 200
- [ ] Spec includes explicit security hard-rules with paths
- [ ] CI workflow excludes `linkedin.com` from link check
- [ ] `gitleaks detect` returns 0 leaks
- [ ] Site renders correctly at mobile (375px) and desktop widths
- [ ] Dark/light toggle persists and respects `prefers-color-scheme`
- [ ] All "Read more" / project links resolve

## Post-launch security audit + hardening pass

After the site is live, run a structured audit before declaring it recruiter-ready. The grep-based audit below catches the issues `gitleaks` alone misses: PII, hardcoded demo creds, missing CSP, missing SRI, unsandboxed iframes, `target="_blank"` without `noopener`, mixed content, etc.

### Audit script (run from repo root)

```bash
echo "---GITLEAKS---" && gitleaks detect --source . --no-banner -v 2>&1 | tail -5
echo "---SECRET PATTERNS---" && grep -riE "sk-[a-zA-Z0-9]{20,}|ghp_[a-zA-Z0-9]{20,}|gho_[a-zA-Z0-9]{20,}|xoxb-|AIza[a-zA-Z0-9]{20,}|hf_[a-zA-Z0-9]{20,}|AKIA[0-9A-Z]{16}|fal_[a-zA-Z0-9]" --include='*.html' --include='*.js' --include='*.css' --include='*.md' --include='*.yml' --include='*.json' . 2>/dev/null | head -5
echo "---PII (phone)---" && grep -rE "\\b\\(?[0-9]{3}\\)?[-. ][0-9]{3}[-. ][0-9]{4}\\b" --include='*.html' --include='*.md' .
echo "---HARDCODED DEMO CREDS---" && grep -rinE "login\\s*info|password|admin|guest" --include='*.html' --include='*.md' . | grep -iE "admin|guest|1234|password"
echo "---INLINE EVENT HANDLERS---" && grep -rE 'onclick=|onerror=|onload=|onmouseover=|javascript:' --include='*.html' --include='*.js' .
echo "---innerHTML/eval/document.write---" && grep -rnE "innerHTML|document\\.write|eval\\(|new Function\\(" --include='*.js' --include='*.html' .
echo "---target=_blank w/o noopener---" && grep -rEn 'target="_blank"' --include='*.html' . | grep -v noopener
echo "---External scripts (audit each)---" && grep -rhE '<(script|iframe)[^>]*src=' --include='*.html' . | grep -oE 'src="[^"]+"' | sort -u
echo "---Mixed content---" && grep -rE 'http://[^"]+' --include='*.html' --include='*.js' --include='*.css' . | grep -v "w3.org\\|xmlns"
echo "---CSP / Permissions-Policy / Referrer-Policy---" && grep -nE "Content-Security-Policy|Permissions-Policy|Referrer-Policy|name=.referrer." index.html
echo "---Iframe sandbox?---" && grep -nB1 -A3 "<iframe" index.html
echo "---HTTPS enforced on Pages?---" && gh api /repos/<owner>/<repo>/pages --jq '.https_enforced'
```

### Severity rubric

| Severity | Examples | Fix |
|---|---|---|
| 🔴 HIGH | Phone number in plaintext, real API key, real chat ID | Remove immediately, force-push if already public, rotate any exposed credential |
| 🟠 MEDIUM | Hardcoded demo `Guest/1234` credentials shown publicly, missing `.gitignore`, missing CSP | Replace with on-request note, add `.gitignore`, add CSP meta tag |
| 🟡 LOW | No SRI on CDN scripts, missing `Permissions-Policy`/`Referrer-Policy`, `target="_blank"` with only `noreferrer`, unsandboxed `<iframe>` | Pin SRI where possible, add policy meta tags, use `noopener noreferrer`, add `sandbox=""` |

### Hardening recipes

**CSP for a Tailwind+Fonts+Simple-Icons static site:**

```html
<meta http-equiv="Content-Security-Policy"
  content="default-src 'self';
           img-src 'self' https://cdn.simpleicons.org data:;
           style-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://cdn.tailwindcss.com;
           script-src 'self' 'unsafe-inline' https://cdn.tailwindcss.com;
           font-src 'self' https://fonts.gstatic.com;
           connect-src 'self';
           object-src 'none';
           base-uri 'self';
           form-action 'self';
           frame-ancestors 'none';
           upgrade-insecure-requests;">
<meta http-equiv="Permissions-Policy" content="camera=(), microphone=(), geolocation=(), payment=(), usb=(), interest-cohort=()">
<meta name="referrer" content="strict-origin-when-cross-origin">
```

`'unsafe-inline'` is required for the inline FOUC-prevention theme script and the inline `tailwind.config`. Acceptable trade-off for a static site with no user input.

**SRI limitations to know:**

- ❌ **Tailwind Play CDN (`cdn.tailwindcss.com`)** — NOT SRI-able (dynamic content). Restrict via CSP `script-src` instead and add a comment explaining the limitation.
- ❌ **FontAwesome Kits (`kit.fontawesome.com`)** — NOT SRI-able. Replace with the pinned cdnjs version + SRI hash:
  ```html
  <link rel="stylesheet"
        href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.2/css/all.min.css"
        integrity="sha512-SnH5WK+bZxgPHs44uWIX+LLJAJ9/2PkPKZ5QiAj6Ta86w+fsb2TkcmfRyVX3pBnMFcV7oQPJkl9QevSCWr3W6A=="
        crossorigin="anonymous"
        referrerpolicy="no-referrer">
  ```
- ❌ **Google Fonts CSS** — Google rotates the file; skip SRI, just add `crossorigin="anonymous" referrerpolicy="no-referrer"`.

**Iframe sandbox for trusted local PDFs:**

```html
<iframe src="assets/cert.pdf"
        title="Certificate"
        loading="lazy"
        sandbox=""
        referrerpolicy="no-referrer"></iframe>
```

Empty `sandbox=""` = max restriction. PDFs render fine without any sandbox flags.

**External link hardening:** always pair `noopener` and `noreferrer`:

```html
<a href="https://example.com" target="_blank" rel="noopener noreferrer">link</a>
```

### Delegating the hardening pass to Codex

The audit + fixes are tedious and pattern-heavy — perfect for Codex. Spec template:

```
# Security Hardening Spec — <repo>

cd ~/path/to/repo for all changes. Use conventional commits, one per logical fix.

### Fix 1 — <issue>: <one-sentence fix>
[exact before/after snippets]
Commit: chore(security): <message>

### Fix 2 — ...

### VERIFICATION
[grep commands that should return zero matches]
```

Then: `codex exec --yolo "$(cat /tmp/security-spec.md)"` in background with `notify_on_complete=true`.

## Reusable spec template

For complex sites, put the spec in `/tmp/<project>-spec.md` and feed via `"$(cat /tmp/...)"` to avoid shell escaping issues. Keep these top-level sections:

```
1. Owner / contact info
2. 🚨 SECURITY HARD RULES
3. Architecture (no build step, Tailwind CDN, inline SVG)
4. Visual / UX direction (palette + required UX features list)
5. Site map (exact paths)
6. Sections of index.html (ordered)
7. Detail pages (projects/*.html)
8. CI workflow (full YAML)
9. 404 page
10. Implementation order (numbered)
11. Output expectations (no TODO, no lorem ipsum)
```
