# Static GitHub Pages push verification

Use this reference when the repo is a static HTML/React/Vite/etc. site deployed by GitHub Pages and the user asks to apply UI changes and push.

## Recommended workflow

1. Work in a local clone and verify GitHub auth before editing:
   ```bash
   git status --short
   git remote -v
   gh auth status
   ```

2. For UI/localStorage changes, serve the static site locally and verify in a browser:
   ```bash
   python3 -m http.server 4173
   ```
   Then use browser automation to click the relevant tab/control, reload the page, and inspect `localStorage`:
   ```js
   localStorage.getItem('<active-tab-key>')
   document.body.innerText.includes('<new UI label>')
   ```

3. Add a lightweight GitHub Actions smoke test for static repos that otherwise have no CI. The minimal check should:
   - start `python3 -m http.server 4173`
   - `curl --fail` the root page
   - grep for the app title and one key string from the new feature

4. Push to `main` only when the user explicitly asked to update/push GitHub. Otherwise prefer a branch/PR.

5. After pushing, verify both CI and Pages deployment:
   ```bash
   gh run list --repo OWNER/REPO --limit 5
   gh run watch RUN_ID --repo OWNER/REPO --exit-status
   curl -L --fail --silent --show-error https://OWNER.github.io/REPO/ | grep '<new feature string>'
   ```

## UI/localStorage patterns from this session

- Persist the active UI tab/page separately from the main app state, e.g. `app-active-tab-v1`.
- Wrap localStorage reads/writes in try/catch so privacy-mode or blocked-storage failures do not crash the app.
- Validate/normalize imported JSON backups before replacing app state.
- Use a stronger destructive reset confirmation for local-only data, e.g. require typing `RESET`.
- Make mobile tab nav horizontally scrollable with non-shrinking tab buttons instead of wrapping into an awkward multi-row header.

## Pitfalls

- A successful push is not enough for GitHub Pages; wait for Pages deployment and verify the live URL contains the new code.
- GitHub Pages may run its own `pages-build-deployment` workflow separately from custom CI. Check both when available.
- If the repo has a `CNAME`, `https://OWNER.github.io/REPO/` may 301 to the custom domain. When DNS for that custom domain is not pointed at GitHub Pages yet, live curl verification can land on the old host. In that case verify the Pages run/build status and use `raw.githubusercontent.com/OWNER/REPO/main/...` to confirm pushed asset/reference contents; do not treat the stale custom-domain response as a failed deploy unless DNS is already correct.
- GitHub Actions may emit Node deprecation warnings for official actions; treat as warnings unless the run fails.
- Brand/title changes often break smoke tests that grep for old copy; update workflow grep strings and add a check for new logo/icon references in the same commit.
- For service-business sites that use a website chat widget but promise human service desk support, keep the distinction explicit everywhere: label the widget as a website assistant/general questions tool, update its greeting plus backend prompt/fallbacks, and avoid wording that implies AI replaces ticket/service-desk conversations.
- For Squarespace-connected domains, verify both apex and `www`: Squarespace may leave apex A records on Squarespace while `www` CNAME points to GitHub. GitHub Pages may then redirect `www` to apex, causing the live site to show Squarespace parking even though Pages built successfully. Report the exact DNS split and the needed apex A-record fix.
