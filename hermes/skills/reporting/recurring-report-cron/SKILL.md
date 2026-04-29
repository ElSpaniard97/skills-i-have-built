---
name: recurring-report-cron
description: Build a Hermes skill + cron job pair for recurring scheduled reports (cost reports, security audits, status digests, etc.). Use when the user asks for a recurring/periodic report delivered on a schedule. Pairs a stdlib-only Python script under a skill with a cron job that runs it and posts the output back to the requesting channel.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [Cron, Reporting, Skills, Automation]
    related_skills: [codex, hermes-agent]
---

# Recurring Report Cron

Pattern for "give me X report every N days/hours" requests. Two artifacts:

1. **A skill** containing the report-generating script (stdlib Python, no deps)
2. **A cron job** that loads the skill and invokes the script, delivering stdout back to the requesting channel

This pattern is reusable for cost reports, security audits, mailbox digests, GitHub activity summaries, weather rollups — anything that's "compute → markdown → post on a schedule".

## Skill Structure

```
~/.hermes/skills/<category>/<skill-name>/
├── SKILL.md              # Trigger conditions + invocation docs
└── scripts/
    ├── <name>.py         # Standalone Python (stdlib only)
    └── config.json       # Externalized config (pricing, thresholds, API keys not — use env)
```

**Why externalize config:** lets the user tweak prices, thresholds, or filter lists without editing code. Script reads via `--config <path>` with a sensible default sibling-file.

**Script requirements:**
- Stdlib only (`sqlite3`, `json`, `argparse`, `datetime`, `pathlib`, `collections`, `os`, `sys`)
- argparse with `--since-days N` (or equivalent time window) and `--config PATH`
- Output markdown to stdout. Stdout is the report — no stderr noise mixed in.
- Exit 0 on success, non-zero on hard failure (DB missing, etc.)
- Treat missing/NULL data gracefully (warn to stderr, don't crash)

## Cron Job Configuration

```python
cronjob(
    action="create",
    name="<Human-readable name>",
    schedule="0 10 */2 * *",          # every 2 days at 10am, system tz
    skills=["<skill-name>"],           # auto-loads SKILL.md into cron agent context
    enabled_toolsets=["terminal"],     # LEAN — usually just terminal, maybe file
    deliver="origin",                  # CRITICAL: posts back to requesting thread/channel
    prompt="""Run the report script for the last N days:

  python3 ~/.hermes/skills/<cat>/<skill>/scripts/<name>.py --since-days N

Post the script's stdout (the markdown report) verbatim as your final response — do not paraphrase, summarize, or add commentary. The final response is auto-delivered to the requesting channel."""
)
```

## Critical Patterns

### 1. `deliver="origin"` (or just omit `deliver`)
This makes the cron job's final response go back to the channel/thread the user requested it from — preserving topic context on Telegram, thread context on Discord. Don't hardcode `discord:#channel` unless the user explicitly asks for a different destination.

### 2. Verbatim-stdout prompt
Cron agents have a strong instinct to summarize/paraphrase. The phrase **"Post the script's stdout (the markdown report) verbatim as your final response — do not paraphrase, summarize, or add commentary"** prevents this. Without it the agent will compress your carefully-formatted tables into prose.

### 3. Lean `enabled_toolsets`
Cron agents bill for every loaded tool's schema in input tokens. For "run a script and print output" jobs, `["terminal"]` is enough. Add `"file"` only if the script reads/writes files the agent needs to inspect. **Do NOT** include `web`, `browser`, `delegation` unless required — they add 5–15K tokens per run.

### 4. Skill auto-loaded into cron context
Passing `skills=["<name>"]` makes the cron agent load `SKILL.md` before executing the prompt. So your SKILL.md should include the exact invocation command — the agent will read it and run it.

### 5. Schedule syntax
- `"0 10 */2 * *"` → every 2 days at 10:00 system local time
- `"30m"` / `"every 2h"` / ISO timestamp also accepted by Hermes scheduler
- System local time = whatever the host is set to (check `TZ` / `timedatectl`)

## Build Workflow

1. **Plan with the smart model first.** Define: data source, computation, sections, schedule, channel.
2. **Write a detailed spec to `/tmp/spec.md`.** Include: file paths, exact section structure, validation steps, "done criteria".
3. **Delegate the build to Codex** via the `codex` skill: `codex exec --yolo --skip-git-repo-check "$(cat /tmp/spec.md)"` with `workdir` pointing at the new skill directory. Run with `background=true, pty=true, notify_on_complete=true`.
4. **Verify before scheduling.** Run the script manually with the exact args the cron will use. Confirm output is non-empty and well-formed.
5. **Create the cron job.** Use `deliver="origin"`, lean toolsets, verbatim-output prompt.
6. **Note the `next_run_at` returned** so you can tell the user when to expect the first run.

## Pitfalls

- **Don't `mkdir` first then run codex with `--full-auto`** — the bwrap sandbox blocks writes outside the sandbox root in some configs. Use `--yolo` when building skills under `~/.hermes/skills/`.
- **Don't pipe codex output through `tail`/`head`** — buffers everything until exit, makes monitoring impossible. Run codex directly.
- **DB columns named `*_cost_usd` are often NULL** in `~/.hermes/state.db` — Hermes doesn't always backfill them. Compute from token counts × pricing, don't trust those columns.
- **Cron prompts run in a fresh session** with no chat memory. Everything the agent needs must be in the prompt or the loaded skill.
- **`started_at` in `state.db` is a Unix epoch float**, not ISO. Use `datetime.fromtimestamp(ts)` not `fromisoformat`.
- **Persona prompts can override `deliver=origin`** — if your top-level CLAUDE.md says "always post to channel X", the cron agent may ignore the thread. Check persona before scheduling cross-channel jobs.

## Update / Manage

```python
cronjob(action="list")                                    # find job_id
cronjob(action="update", job_id="...", schedule="0 9 * * *")
cronjob(action="run", job_id="...")                       # trigger manually
cronjob(action="pause", job_id="...")
cronjob(action="remove", job_id="...")
```

To change the report's content (add a section, fix a bug): edit the script in the skill dir. No cron change needed — the cron just invokes whatever the script does today.

To change the price/threshold list: edit the JSON config file. Same — no code change.

## Reference Implementation

`~/.hermes/skills/reporting/hermes-cost-report/` is a working example built with this pattern. Cron job `053897d149a4` invokes it every 2 days. Read its SKILL.md and `scripts/cost_report.py` for a concrete template.
