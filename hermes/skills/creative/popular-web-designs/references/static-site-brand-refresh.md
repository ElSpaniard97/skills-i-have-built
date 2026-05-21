# Static site brand refresh pattern

Use when an existing static website/app needs to be rebranded from a logo, screenshot, or business-name image and pushed to GitHub Pages.

## Workflow

1. Preserve the deployment surface unless the user explicitly asks for a rename:
   - Keep the existing repository name, Pages URL, and localStorage keys if changing them would break links or saved browser data.
   - Rebrand visible copy, metadata, README, and assets instead.
2. Convert visual identity into repo-friendly assets:
   - Prefer clean SVG logo/icon assets over embedding a large base64 image in HTML.
   - Create both a horizontal logo/wordmark and a square icon/favicon when the app has both header/dashboard and browser-tab needs.
   - Add accessible `<title>` and `<desc>` elements to SVGs.
3. Update the app surface:
   - `<title>`, meta description, favicon link.
   - Header/hero/dashboard brand panel.
   - Export filenames or user-facing labels where appropriate.
4. Update project documentation and metadata:
   - README title, description, contents, brand section, asset list, and setup commands.
   - GitHub repo description/homepage via `gh repo edit` when authenticated and the user asked to update GitHub.
5. Update CI/smoke tests:
   - Replace old brand/title grep strings with new title strings.
   - Add a check for the new logo/icon references.
6. Verify before and after pushing:
   - Local `curl`/grep for title, logo ref, favicon ref, and unchanged persistence keys if relevant.
   - Browser check for visual layout and console errors.
   - SVG XML parse check for generated assets.
   - After push, watch both custom CI and GitHub Pages deployment, then `curl -L` the live URL and fetch the live SVG assets.

## Pitfalls

- Do not paste or preserve huge inline base64 uploads in repo files or session summaries; treat them as transient input unless the user asks to store the exact asset.
- Do not rename repo or Pages URL as part of a branding change unless explicitly requested.
- Do not change localStorage keys during rebrand unless migration code is added; old keys preserve users' saved browser data.
- CI often contains old brand strings; update smoke tests in the same commit or the push will fail despite the app working.
