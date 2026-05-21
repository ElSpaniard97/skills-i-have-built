# Repo Rename + Static Site Rebrand Checklist

Use this reference when a user asks to rename a GitHub repository and rebrand a GitHub Pages/static website in the same session.

## Safe sequence

1. Inspect current repo metadata first:

```bash
gh repo view OWNER/OLD_REPO --json nameWithOwner,description,defaultBranchRef,homepageUrl,visibility,updatedAt
```

2. Avoid destructive cleanup in `/tmp` or working folders. Prefer a fresh timestamped clone directory:

```bash
workdir="/tmp/${OLD_REPO}-review-$(date +%Y%m%d%H%M%S)"
git clone "https://github.com/${OWNER}/${OLD_REPO}.git" "$workdir"
cd "$workdir"
```

3. Check target availability before rename:

```bash
if gh repo view "$OWNER/$NEW_REPO" >/dev/null 2>&1; then
  echo "Target repo already exists: $OWNER/$NEW_REPO" >&2
  exit 1
fi
```

4. Update static-site content before or immediately after rename:

- Page titles, meta descriptions, OG title/description/image/url
- Logo asset and favicon references
- Header/footer/company name text
- Contact form hidden `_subject` and `_next` URL
- README clone URL, live URL, project tree, and deployment notes
- Any CSP `connect-src` entries needed by chat/API widgets
- Chat widget welcome text and support label
- Backend worker prompts/URLs if under your control

5. Commit and rename:

```bash
git add .
git diff --check
git commit -m "Rebrand website as NEW_BRAND"
gh repo rename "$NEW_REPO" -R "$OWNER/$OLD_REPO" --yes
git remote set-url origin "https://github.com/${OWNER}/${NEW_REPO}.git"
git push origin main
```

## Verification checklist

Run local static smoke checks:

```bash
python3 - <<'PY'
from html.parser import HTMLParser
from pathlib import Path
class P(HTMLParser): pass
for path in sorted(Path('.').glob('*.html')):
    parser = P(); parser.feed(path.read_text()); parser.close()
    print('OK', path)
PY
node --check main.js 2>/dev/null || true
git diff --check
```

Verify GitHub and Pages:

```bash
gh repo view "$OWNER/$NEW_REPO" --json nameWithOwner,url,homepageUrl,defaultBranchRef,visibility
for i in 1 2 3 4 5 6; do
  gh run list -R "$OWNER/$NEW_REPO" --limit 1
  sleep 10
done
```

Open the live Pages URL in a browser and confirm:

- The page title uses the new brand.
- The visible H1 and nav load.
- The logo loads from the new asset.
- Browser console has no JavaScript errors.
- GitHub Pages deployment finished with `success`.

## Pitfalls

- `gh repo rename` changes the remote URL; update `git remote set-url origin` before pushing.
- GitHub Pages may temporarily show a cancelled deployment followed by a queued/in-progress deployment after rename or push; wait for the latest run to complete.
- If the frontend references a Cloudflare Worker or other backend named after the old repo, note it explicitly as a follow-up unless credentials/API access are available to update it.
- GitHub Pages homepage URL may update automatically after the rename; verify with `gh repo view --json homepageUrl` rather than assuming.
- For custom domains, adding a `CNAME` file and pushing it can set the Pages `cname` automatically. HTTPS enforcement may fail with `The certificate does not exist yet` until DNS points at GitHub Pages and the certificate provisions; report the required DNS records and re-check later instead of treating this as a repo failure.
- Before claiming a custom domain is live, check DNS (`dig A apex`, `dig CNAME www`) and Pages status. If the domain still resolves to a registrar/site-builder such as Squarespace, the repo side can be complete while DNS remains a user-side follow-up.
- When the user provides a local brand image, use it as the asset source and verify the final file type/dimensions with `file` if image libraries are unavailable.
