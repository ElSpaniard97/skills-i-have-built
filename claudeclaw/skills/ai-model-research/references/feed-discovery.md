# Feed Discovery — Lessons Learned

Notes on finding reliable RSS/Atom feeds and YouTube channel IDs for AI source aggregation. Captured from real failures so future maintainers don't repeat them.

## Frontier AI labs mostly DON'T publish RSS

Verified 404 (as of 2026-04):
- `https://www.anthropic.com/news/rss.xml`
- `https://www.anthropic.com/rss.xml`
- `https://ai.meta.com/blog/rss/`
- `https://ai.meta.com/feed/`
- `https://mistral.ai/news/rss.xml`
- `https://x.ai/news/rss.xml` (also blocks scraping with 403)
- `https://www.deepseek.com/blog/rss.xml`

The lab news pages exist as HTML but no machine-readable feed. **Don't waste time guessing more URL variants.**

### Workaround: HN Algolia API

Hacker News surfaces virtually every major lab announcement within hours. The Algolia search API is free, fast, and JSON-native:

```
https://hn.algolia.com/api/v1/search_by_date?query=KEYWORD&tags=story&numericFilters=points%3E15
```

Use one query per lab keyword. The `points>15` filter cuts noise effectively.

Tested coverage in a single 7-day window:
- "anthropic claude" → 7 hits
- "gpt openai" → 6 hits
- "mistral" → 4 hits
- "deepseek" → 4 hits
- "grok xai" → 1 hit (low traffic week)

Each hit gives you `title`, `url`, `points`, `num_comments`, `created_at`, `objectID` (for HN comment thread URL).

### Working official RSS feeds (verified)

| Source | URL |
|---|---|
| OpenAI Blog | `https://openai.com/blog/rss.xml` |
| Google DeepMind | `https://deepmind.google/blog/rss.xml` |
| Hugging Face Blog | `https://huggingface.co/blog/feed.xml` |
| Qwen | `https://qwenlm.github.io/blog/index.xml` |
| Simon Willison | `https://simonwillison.net/atom/everything/` |
| Latent Space | `https://www.latent.space/feed` |

## YouTube channel IDs from memory are unreliable

Five out of eleven channel IDs I "knew" from training were wrong (404 on the feed endpoint). **Always verify before adding to a config.**

### Reliable extraction technique

```bash
curl -sL --max-time 10 -A 'Mozilla/5.0' \
  'https://www.youtube.com/@HANDLE/about' \
  | grep -oE 'browseId":"UC[A-Za-z0-9_-]{22}' | head -1
```

The `/about` page returns server-rendered HTML containing `"browseId":"UC..."` which is the canonical channel ID. The 24-character format `UC` + 22 alphanumeric chars is reliable.

Once you have the ID, the feed URL is always:
```
https://www.youtube.com/feeds/videos.xml?channel_id=UCxxxxxxxxxxxxxxxxxxxxxx
```

### Verified IDs (2026-04)

| Channel | ID |
|---|---|
| AI Explained | `UCNJ1Ymd5yFuUPtn21xtRbbw` |
| Matthew Berman | `UCawZsQWqfGSbCI5yjkdVkTA` |
| Wes Roth | `UCqcbQf6yw5KzRoDDcZ_wBSw` |
| bycloud | `UC29ju8bIPH5as8OGnQzwJyA` |
| Yannic Kilcher | `UCZHmQk67mSJgfCCTn7xBfew` |
| Two Minute Papers | `UCbfYPyITQ-7l4upoX8nvctg` |
| Sam Witteveen | `UC55ODQSvARtgSyc8ThfiepQ` |
| 1littlecoder | `UCpV_X0VrL8-jg3t6wYGS-1g` |
| Dwarkesh Patel | `UCXl4i9dYBrFOabk0xGmbkRA` |
| AI Jason | `UCrXSVX9a1mj8l0CMLwKgMVw` |
| David Shapiro | `UCvKRFNawVcuz4b9ihUTApCg` |

## Reddit JSON endpoint quirks

Reddit's `*.json` endpoints are free and unauthenticated, but:

- **Default `python-urllib` UA gets 429'd or blocked.** Always send a custom UA like `Hermes ai-model-research/1.0`.
- Filter `data.stickied == true` (mod-pinned posts repeat across runs).
- Filter `data.over_18 == true` if you don't want NSFW.
- Filter on `data.score >= 50` to cut noise.
- `created_utc` is unix epoch — convert to ISO before storing.

URL pattern:
```
https://www.reddit.com/r/SUBREDDIT/top.json?t=week&limit=50
```

## Bluesky public API (no auth)

Free alternative to paid X/Twitter API:

```
https://public.api.bsky.app/xrpc/app.bsky.feed.searchPosts?q=QUERY&sort=top&limit=50
```

- No auth, no rate-limit headers documented (keep request count low).
- Posts have `record.text`, `record.createdAt`, `author.handle`, `uri`, `likeCount`, `repostCount`.
- `at://` URIs need conversion: `https://bsky.app/profile/{handle}/post/{rkey}` where `rkey` is the last `/`-segment of `uri`.
- Filter `likeCount + repostCount >= 10` to cut noise.

## X/Twitter is paid

The official X API requires a paid plan (min $5/mo) and `xurl` setup. Don't add it to default sources. If/when enabled, gate it on `xurl auth status` succeeding.

## General principle: verify URLs at config time

Cheap one-liner to batch-test feed URLs:

```bash
for url in URL1 URL2 URL3; do
  echo "$(curl -sLo /dev/null -w '%{http_code}' --max-time 8 "$url") $url"
done
```

A 200 + `application/xml` or `application/atom+xml` content-type means it's a real feed. 200 + `text/html` means the URL exists but isn't a feed (don't add it).
