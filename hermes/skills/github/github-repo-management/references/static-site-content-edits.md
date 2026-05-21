# Static Site Content Edits in GitHub Repos

Use this reference when the user asks for small content/price/copy changes in a GitHub-hosted static site, especially GitHub Pages sites with custom domains.

## Repo identity guardrail

When multiple similar repos or brands exist, verify the target repository from the user's URL before editing or pushing:

```bash
REQUESTED="OWNER/REPO"   # parse from the user's GitHub URL
pwd
git remote get-url origin
gh repo view "$REQUESTED" --json nameWithOwner,url,homepageUrl,defaultBranchRef
```

Do not rely on memory of a similarly branded repo. Before commit/push, re-check:

```bash
git remote get-url origin | grep -i "github.com[:/]${REQUESTED//\//\/}" || {
  echo "Wrong origin for requested repo" >&2
  exit 1
}
```

## Content consistency workflow

1. Search for every old value and nearby wording across source and docs.

```bash
python3 - <<'PY'
from pathlib import Path
terms = ['old price', '$OLD', 'On-site', 'onsite', 'visit']
for p in Path('.').rglob('*'):
    if p.is_dir() or '.git' in p.parts:
        continue
    try:
        text = p.read_text(errors='ignore')
    except Exception:
        continue
    hits = [t for t in terms if t.lower() in text.lower()]
    if hits:
        print(p, hits)
PY
```

2. Update all public-facing copies, not just the HTML page:

- HTML pages and partials
- README pricing tables and deployment notes
- JSON data/config files that hydrate the page
- Worker/server prompts or hard-coded fallback copy, if present
- SEO metadata if the changed value appears there

3. Run syntax and whitespace checks appropriate to the repo:

```bash
git diff --check
node --check main.js 2>/dev/null || true
node --check worker.js 2>/dev/null || true
```

4. Verify locally by serving the static site and checking the visible text, not just grepping files.

```bash
python3 -m http.server 8000
# open http://127.0.0.1:8000/path.html and confirm rendered text
```

5. Commit with a narrow message and push only after the diff shows the requested scope.

## Logo and brand asset refresh workflow

When the user provides a new logo for an existing static site, treat it as an asset refresh plus rendered-brand verification, not only a binary copy.

1. Inspect the supplied image and current repo assets.

```bash
file '/path/to/new-logo.png'
identify -format '%f %w %h %m %[colorspace]\n' '/path/to/new-logo.png' logo.png logo-mark.png 2>/dev/null || true
sha256sum logo.png logo-mark.png '/path/to/new-logo.png'
```

2. Search for logo usage across HTML, metadata, CSS, README, and worker/config files.

```bash
python3 - <<'PY'
from pathlib import Path
for p in sorted(Path('.').glob('*.html')):
    txt = p.read_text(errors='ignore')
    print(p.name, 'logo.png', txt.count('logo.png'), 'logo-mark.png', txt.count('logo-mark.png'))
PY
```

3. Replace the full-size display/social image and regenerate any mark/favicon image from the same source. If ImageMagick or Pillow is unavailable, ffmpeg can crop/resize PNGs reliably:

```bash
cp '/path/to/new-logo.png' logo.png
ffmpeg -y -i '/path/to/new-logo.png' -vf 'crop=700:700:277:90,scale=512:512' logo-mark.png
```

Adjust crop dimensions for the actual logo. Visually inspect the generated mark so it contains only the intended emblem and does not clip important details or include stray text.

4. Verify all image references resolve locally before committing.

```bash
python3 - <<'PY'
from pathlib import Path
from html.parser import HTMLParser
class Parser(HTMLParser):
    def __init__(self): super().__init__(); self.refs=[]
    def handle_starttag(self, tag, attrs):
        d=dict(attrs)
        for key in ('src','href','content'):
            val=d.get(key)
            if val and '.png' in val:
                self.refs.append((tag,key,val))
missing=[]
for html in sorted(Path('.').glob('*.html')):
    p=Parser(); p.feed(html.read_text(errors='ignore'))
    for tag,key,val in p.refs:
        if val.startswith('https://example.com/'):
            local=Path(val.replace('https://example.com/',''))
        elif val.startswith(('http://','https://','data:')):
            continue
        else:
            local=Path(val)
        if not local.exists(): missing.append((html.name, tag, key, val))
print('PNG references missing:', len(missing))
for item in missing: print(item)
PY
```

5. Serve the site and do a visual smoke test of the header, favicon/mark usage, and hero/social logo locations. Confirm the logo is not distorted, cropped, or overlapping navigation before reporting completion.

## GitHub Pages verification

After pushing, verify both source and deployment:

```bash
git status --short
git log -1 --oneline
gh run list -R "$REQUESTED" --limit 3
# If there is a Pages/deploy run, wait for its conclusion before reporting done.
```

For public repos, raw GitHub is a good propagation check for the committed content:

```bash
curl -fsSL "https://raw.githubusercontent.com/${REQUESTED}/main/path/to/file" | grep -F 'expected new text'
```

## Custom domain caveat

If the Pages site uses a custom domain, distinguish repo completion from DNS/hosting state. Check response headers and DNS before claiming the public domain reflects the push:

```bash
curl -I https://example.com/path.html
# also check dig A example.com and dig CNAME www.example.com when diagnosing routing
```

If headers indicate another host/site builder such as Squarespace, report that GitHub is updated and deployed, but the custom domain is still routed outside GitHub Pages. Treat that as a DNS/domain follow-up, not a failed repo edit.
