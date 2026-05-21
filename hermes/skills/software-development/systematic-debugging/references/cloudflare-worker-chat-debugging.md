# Cloudflare Worker-backed static-site chat debugging

Use this reference when a static GitHub Pages/HTML site has a browser chat widget that calls a Cloudflare Worker or Pages Function proxy.

## Symptom pattern

- Browser console: `TypeError: Failed to fetch` from `fetch(WORKER_URL, { method: 'POST', ... })`.
- Direct `curl -X OPTIONS` to the Worker returns `405` or lacks `Access-Control-Allow-*` headers.
- Direct `curl -X POST` to the Worker root returns `405`, `404`, or static HTML instead of JSON.
- A Cloudflare Worker URL serves the static site on `GET /`, but does not handle `POST`/`OPTIONS` for chat.

## Root-cause workflow

1. Read the frontend chat code and identify the exact `WORKER_URL` path.
2. Reproduce in the browser and capture console output.
3. Probe the Worker directly before changing code:

```bash
curl -i -s -X OPTIONS "$WORKER_URL" \
  -H 'Origin: https://elspaniard97.github.io' \
  -H 'Access-Control-Request-Method: POST' \
  -H 'Access-Control-Request-Headers: content-type' | sed -n '1,80p'

curl -i -s "$WORKER_URL" \
  -H 'Origin: https://elspaniard97.github.io' \
  -H 'Content-Type: application/json' \
  --data '{"messages":[{"role":"user","content":"What services do you offer?"}]}' | sed -n '1,120p'
```

4. Inspect Worker deployment config. In a Cloudflare static asset Worker, `wrangler.jsonc` with only `assets.directory` can deploy assets but no API handler. To handle chat, it needs `main: "worker.js"` and an asset binding, for example:

```jsonc
{
  "name": "my-worker",
  "main": "worker.js",
  "compatibility_date": "2026-05-08",
  "assets": { "directory": ".", "binding": "ASSETS" }
}
```

5. Implement a Worker route such as `/api/chat` that handles:
   - `OPTIONS` with 204 and CORS headers.
   - `POST` with JSON parsing and validation.
   - `GET`/static assets by delegating to `env.ASSETS.fetch(request)`.
6. Update frontend `WORKER_URL` to the API path, not the static root.
7. Verify with both direct API probes and real browser chat interaction.

## Secret/config pitfall

If `wrangler secret list` or deployment commands fail with:

```text
In a non-interactive environment, it's necessary to set a CLOUDFLARE_API_TOKEN environment variable
```

then the local shell cannot inspect or set Cloudflare secrets. Do not claim the live LLM key is configured. Either ask the user for Cloudflare token scope or implement/verify a non-secret fallback if acceptable.

For Anthropic-backed Workers, accept common secret names (`ANTHROPIC_API_KEY`, `CLAUDE_API_TOKEN`, `CLAUDE_API_KEY`) but never print secret values. If no secret is configured, the Worker should return a clear 503 or a deterministic fallback response; the frontend should not silently fail.

## Verification checklist

- `node --check main.js`
- `node --check worker.js`
- Local module-level test of Worker `fetch()` for `OPTIONS` and `POST`.
- Live `OPTIONS` returns `204` and includes `Access-Control-Allow-Origin`, `Access-Control-Allow-Methods`, and `Access-Control-Allow-Headers`.
- Live `POST /api/chat` returns `200` JSON with a `reply`, or an intentional non-2xx JSON error that the UI handles.
- Live browser chat sends a message, appends a bot reply, and browser console has no JS errors.
- If a Cloudflare deployment branch differs from `main`, patch/push both the site branch and the Worker deployment branch as needed.
