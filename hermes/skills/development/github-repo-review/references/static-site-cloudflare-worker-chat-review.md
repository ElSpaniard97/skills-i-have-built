# Static Site + Cloudflare Worker Chat Review Notes

Use this reference when reviewing a static marketing site that includes a JavaScript chat widget backed by a Cloudflare Worker or similar API proxy.

## Cross-file consistency checks

Check the endpoint and brand values in all places, not just the main app file:

- `main.js` or frontend config: chat/API URL used by `fetch()`.
- HTML CSP meta tags: `connect-src` must allow the same worker origin.
- Worker CORS allowlist: production GitHub Pages origin and any intended custom domain.
- Worker config (`wrangler.jsonc`): worker `name` should match the intended brand/deployment if a rename/rebrand occurred.
- README/docs: endpoint examples should include the exact path used by the frontend, such as `/api/chat`.

## Fallback-response regression checks

For simple keyword-based fallback bots, test the exact quick-reply labels shown in the UI. Do not only test semantically related words.

Example: if the quick reply button says `Pricing`, but worker code checks only `price`, `plan`, or `cost`, the pricing branch may not fire. Patch keyword sets to include visible UI labels and current pricing/user-limit facts.

Suggested probes:

```bash
curl -sS \
  -H 'Origin: https://OWNER.github.io' \
  -H 'Content-Type: application/json' \
  -d '{"messages":[{"role":"user","content":"Pricing"}]}' \
  https://example-worker.workers.dev/api/chat
```

Also probe each quick reply: `Services`, `Service Area`, `Contact`, and any custom labels.

## Local-vs-production CORS

A local static server origin such as `http://localhost:4180` may not be in the Worker CORS allowlist, while the production GitHub Pages origin works. Capture this as a testing-context note, not as a broken-chat finding, unless production fails too.

When local browser chat fails but curl with the production `Origin` succeeds:

- State that local chat testing is blocked by CORS.
- Recommend either temporary localhost origins for development or documented production-origin testing.
- Do not claim the live chat endpoint is down without production-origin evidence.

## Static link checker pitfall

When checking local internal links/assets, strip both query strings and fragments before testing filesystem existence.

Examples:

- `contact.html?plan=Premium+Support` -> `contact.html`
- `pricing.html#web-design-management` -> `pricing.html`

Failing to strip fragments can create false broken-link findings for valid in-page anchors.

## Minimum verification set

- JavaScript syntax check: `node --check main.js` and `node --check worker.js` where applicable.
- Local static HTTP 200 checks for all pages and key assets.
- Browser load with console-error check.
- UI smoke tests for theme toggles, menus, and chat open/close.
- Production GitHub Pages HTTP check if the site is deployed.
- Worker probe with the production Origin header for each visible quick reply.