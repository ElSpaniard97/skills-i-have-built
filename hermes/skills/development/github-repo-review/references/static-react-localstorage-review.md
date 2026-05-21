# Static React / GitHub Pages localStorage review pattern

Use when reviewing a single-file React/Tailwind GitHub Pages app or similar static dashboard and the user asks for UI suggestions or browser persistence.

## Checks

1. Serve locally instead of only reading files:
   - `python3 -m http.server <port>` from the repo root.
   - Open `http://127.0.0.1:<port>/` with browser tools.
2. Verify the visible UI:
   - Capture a browser snapshot for headings/buttons/forms.
   - Use visual review for hierarchy, spacing, responsive risks, accessibility, destructive controls, and empty-state clarity.
3. Inspect persistence:
   - Identify existing localStorage keys and state shape.
   - Confirm whether data persistence and view/page/tab persistence are separate concerns.
   - For “remember pages/tabs”, persist only the active navigation value under a dedicated key rather than mixing it into exported domain data unless the user explicitly wants export/import to carry UI location.
4. Implement conservatively when asked:
   - Add safe wrappers around `localStorage.getItem` / `setItem` so blocked storage or private-mode failures do not crash the app.
   - Validate restored tab/page names against the known nav list before using them.
   - Do not push unless explicitly asked; provide changed paths and/or a patch file.
5. Verify in browser:
   - Click a non-default tab/page.
   - Reload or navigate back to the app.
   - Check the page reopens on that tab.
   - Evaluate `localStorage.getItem(<key>)` and inspect console errors.

## Minimal pattern

```js
const ACTIVE_TAB_STORAGE_KEY = "app-active-tab-v1";
const NAV_TABS = ["Dashboard", "Timeline", "Budget"];

const safeLocalStorageGet = (key, fallback = null) => {
  try { return localStorage.getItem(key) ?? fallback; } catch { return fallback; }
};
const safeLocalStorageSet = (key, value) => {
  try { localStorage.setItem(key, value); } catch {}
};

const [tab, setTab] = useState(() => {
  const savedTab = safeLocalStorageGet(ACTIVE_TAB_STORAGE_KEY, "Dashboard");
  return NAV_TABS.includes(savedTab) ? savedTab : "Dashboard";
});
useEffect(() => safeLocalStorageSet(ACTIVE_TAB_STORAGE_KEY, tab), [tab]);
```

## UI review prompts

Prioritize actionable product improvements, not generic taste notes:

- Add next-action cards when dashboards show status but not what to do next.
- Make mobile nav scrollable or collapsible when tab count is high.
- Add stronger confirmation for destructive reset when localStorage is the only data store.
- Validate JSON import before replacing app state.
- Convert wide tables to mobile cards where spreadsheet-style horizontal scroll is awkward.
- Add screenshots/live demo to README for portfolio/public repos.
