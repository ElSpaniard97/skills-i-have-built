# skills-i-have-built

Backup of all skills built and installed across ClaudeClaw, Hermes, MyClaw, and OpenClaw. Purpose: if any system needs to be rebuilt from scratch, all skills are documented and restorable from this repo.

This index is generated from discovered `SKILL.md` files in the repository.

## Contents

Total skills indexed: 262

| Folder | System | Skills |
|---|---|---|
| `claudeclaw/skills/` | ClaudeClaw | 16 |
| `hermes/skills/` | Hermes | 183 |
| `myclaw/skills/` | MyClaw | 1 |
| `openclaw/workspace-skills/` | OpenClaw Workspace | 1 |
| `openclaw/project-skills/` | OpenClaw Project | 1 |
| `openclaw/sandbox-skills/` | OpenClaw Sandbox | 60 |

---
## ClaudeClaw Skills

### (root)

| Skill | Path | Description |
|---|---|---|
| ai-model-research | `claudeclaw/skills/ai-model-research` | Produce a source-backed AI model research briefing from recent vendor posts, papers, model cards, community signals, and selected video transcripts. Output is saved locally through the ClaudeClaw Reports tab. |
| career-artifact-builder | `claudeclaw/skills/career-artifact-builder` | Convert real project work into recruiter-ready artifacts — resume bullets, LinkedIn posts, portfolio case studies, and STAR stories. Claims are grounded in actual evidence, never fabricated. |
| daily-security-report | `claudeclaw/skills/daily-security-report` | Run local defensive checks and return a markdown security report for ClaudeClaw Reports. No external delivery. |
| github-repo-review | `claudeclaw/skills/github-repo-review` | Perform a standardized repository quality review for GitHub projects (README, docs, CI, hygiene, structure, and risk) with patch/PR recommendations only. |
| helpdesk-triage | `claudeclaw/skills/helpdesk-triage` | Structured IT support triage workflow across identity, network, device, and application layers with evidence-based diagnosis and safe remediation proposals. |
| hermes-cost-report | `claudeclaw/skills/hermes-cost-report` | Generate a local ClaudeClaw cost report from claudeclaw.db token_usage records. Despite the historical name, this version reads ClaudeClaw state, not Hermes state. |
| linux-system-health | `claudeclaw/skills/linux-system-health` | Monitor Linux host health and produce an operations report with failed services, disk, memory, network, and update posture. Report-first, no service changes. |
| local-file-ops | `claudeclaw/skills/local-file-ops` | Safely summarize, audit, and organize local files and folders. Produces folder summaries, duplicate reports, large-file inventories, and cleanup plans. No move, rename, or delete actions without explicit approval of exact paths. |
| mission-control-report | `claudeclaw/skills/mission-control-report` | Generate a local ClaudeClaw operations summary from ClaudeClaw dashboard state. This port does not query Hermes gateway state. |
| model-routing | `claudeclaw/skills/model-routing` | Select the right model (Opus, Sonnet, Haiku, or a specialist agent) before executing complex tasks. Produces a consistent routing decision with rationale before work begins. |
| obsidian-claudeclaw-memory | `claudeclaw/skills/obsidian-claudeclaw-memory` | Set up Obsidian + ClaudeClaw as a living AI memory system. Wires the Obsidian vault to ClaudeClaw's context injection, maintains curated MEMORY.md and USER.md in the vault, and schedules overnight memory distillation via ClaudeClaw's built-in scheduler. Covers vault file structure, CLAUDE.md persona sync, MEMORY.md distillation, and heartbeat-based maintenance. |
| obsidian-memory-curator | `claudeclaw/skills/obsidian-memory-curator` | Curate durable memory from sessions into reviewable Obsidian-ready updates by separating long-term facts from temporary noise. |
| pikastream-video-meeting | `claudeclaw/skills/pikastream-video-meeting` | Join Google Meet or Zoom calls with a Pika video avatar. Handles meeting join/leave and pre-flight briefing. |
| security-triage | `claudeclaw/skills/security-triage` | Defensive security triage for the Linux host and project repos. Inspects logs, open ports, firewall state, failed logins, and package posture. Produces a severity-ranked report with evidence and remediation checklists. Defensive use only — no offensive guidance. |
| skill-quality-auditor | `claudeclaw/skills/skill-quality-auditor` | Audit the ClaudeClaw skills catalog for trigger clarity, input clarity, safety guardrails, verification steps, output format completeness, and inter-skill overlap. Produces a scored report with prioritized change recommendations. |
| troubleshoot-debug-repair | `claudeclaw/skills/troubleshoot-debug-repair` | Troubleshoot, debug, diagnose, and repair broken ClaudeClaw features, services, dashboards, agents, chat flows, cron jobs, reports, APIs, databases, and local integrations. Use when something is failing, regressed, misconfigured, unavailable, throwing errors, returning empty data, or needs root-cause analysis and a verified fix. |

---
## Hermes Skills

### (root)

| Skill | Path | Description |
|---|---|---|
| discord-channel-management | `hermes/skills/discord-channel-management` | Manage Discord channels via the Discord API, including creating, editing, and deleting channels. |
| dogfood | `hermes/skills/dogfood` | Exploratory QA of web apps: find bugs, evidence, reports. |
| yuanbao | `hermes/skills/yuanbao` | Yuanbao (元宝) groups: @mention users, query info/members. |

### apple

| Skill | Path | Description |
|---|---|---|
| apple-notes | `hermes/skills/apple/apple-notes` | Manage Apple Notes via memo CLI: create, search, edit. |
| apple-reminders | `hermes/skills/apple/apple-reminders` | Apple Reminders via remindctl: add, list, complete. |
| findmy | `hermes/skills/apple/findmy` | Track Apple devices/AirTags via FindMy.app on macOS. |
| imessage | `hermes/skills/apple/imessage` | Send and receive iMessages/SMS via the imsg CLI on macOS. |
| macos-computer-use | `hermes/skills/apple/macos-computer-use` | \| Drive the macOS desktop in the background — screenshots, mouse, keyboard, scroll, drag — without stealing the user's cursor, keyboard focus, or Space. Works with any tool-capable model. Load this skill whenever the `computer_use` tool is available. |

### autonomous-ai-agents

| Skill | Path | Description |
|---|---|---|
| claude-code | `hermes/skills/autonomous-ai-agents/claude-code` | Delegate coding to Claude Code CLI (features, PRs). |
| codex | `hermes/skills/autonomous-ai-agents/codex` | Delegate coding to OpenAI Codex CLI (features, PRs). |
| hermes-agent | `hermes/skills/autonomous-ai-agents/hermes-agent` | Configure, extend, or contribute to Hermes Agent. |
| kanban-codex-lane | `hermes/skills/autonomous-ai-agents/kanban-codex-lane` | Use when a Hermes Kanban worker wants to run Codex CLI as an isolated implementation lane while Hermes keeps ownership of task lifecycle, reconciliation, testing, and handoff. |
| opencode | `hermes/skills/autonomous-ai-agents/opencode` | Delegate coding to OpenCode CLI (features, PR review). |

### career

| Skill | Path | Description |
|---|---|---|
| career-artifact-builder | `hermes/skills/career/career-artifact-builder` | Convert real project work into recruiter-ready artifacts — resume bullets, LinkedIn posts, portfolio case studies, and STAR stories. Claims are grounded in actual evidence, never fabricated. |

### creative

| Skill | Path | Description |
|---|---|---|
| architecture-diagram | `hermes/skills/creative/architecture-diagram` | Dark-themed SVG architecture/cloud/infra diagrams as HTML. |
| ascii-art | `hermes/skills/creative/ascii-art` | ASCII art: pyfiglet, cowsay, boxes, image-to-ascii. |
| ascii-video | `hermes/skills/creative/ascii-video` | ASCII video: convert video/audio to colored ASCII MP4/GIF. |
| baoyu-article-illustrator | `hermes/skills/creative/baoyu-article-illustrator` | Article illustrations: type × style × palette consistency. |
| baoyu-comic | `hermes/skills/creative/baoyu-comic` | Knowledge comics (知识漫画): educational, biography, tutorial. |
| baoyu-infographic | `hermes/skills/creative/baoyu-infographic` | Infographics: 21 layouts x 21 styles (信息图, 可视化). |
| claude-design | `hermes/skills/creative/claude-design` | Design one-off HTML artifacts (landing, deck, prototype). |
| comfyui | `hermes/skills/creative/comfyui` | Generate images, video, and audio with ComfyUI — install, launch, manage nodes/models, run workflows with parameter injection. Uses the official comfy-cli for lifecycle and direct REST/WebSocket API for execution. |
| ideation | `hermes/skills/creative/creative-ideation` | Generate project ideas via creative constraints. |
| design-md | `hermes/skills/creative/design-md` | Author/validate/export Google's DESIGN.md token spec files. |
| excalidraw | `hermes/skills/creative/excalidraw` | Hand-drawn Excalidraw JSON diagrams (arch, flow, seq). |
| humanizer | `hermes/skills/creative/humanizer` | Humanize text: strip AI-isms and add real voice. |
| manim-video | `hermes/skills/creative/manim-video` | Manim CE animations: 3Blue1Brown math/algo videos. |
| p5js | `hermes/skills/creative/p5js` | p5.js sketches: gen art, shaders, interactive, 3D. |
| pixel-art | `hermes/skills/creative/pixel-art` | Pixel art w/ era palettes (NES, Game Boy, PICO-8). |
| popular-web-designs | `hermes/skills/creative/popular-web-designs` | 54 real design systems (Stripe, Linear, Vercel) as HTML/CSS. |
| pretext | `hermes/skills/creative/pretext` | Use when building creative browser demos with @chenglou/pretext — DOM-free text layout for ASCII art, typographic flow around obstacles, text-as-geometry games, kinetic typography, and text-powered generative art. Produces single-file HTML demos by default. |
| sketch | `hermes/skills/creative/sketch` | Throwaway HTML mockups: 2-3 design variants to compare. |
| songwriting-and-ai-music | `hermes/skills/creative/songwriting-and-ai-music` | Songwriting craft and Suno AI music prompts. |
| touchdesigner-mcp | `hermes/skills/creative/touchdesigner-mcp` | Control a running TouchDesigner instance via twozero MCP — create operators, set parameters, wire connections, execute Python, build real-time visuals. 36 native tools. |

### data-science

| Skill | Path | Description |
|---|---|---|
| jupyter-live-kernel | `hermes/skills/data-science/jupyter-live-kernel` | Iterative Python via live Jupyter kernel (hamelnb). |

### development

| Skill | Path | Description |
|---|---|---|
| github-repo-review | `hermes/skills/development/github-repo-review` | Perform a standardized repository quality review for GitHub projects (README, docs, CI, hygiene, structure, and risk) with patch/PR recommendations only. |
| skill-quality-auditor | `hermes/skills/development/skill-quality-auditor` | Audit the Hermes skills catalog for trigger clarity, input clarity, safety guardrails, verification steps, output format completeness, and inter-skill overlap. Produces a scored report with prioritized change recommendations. |

### devops

| Skill | Path | Description |
|---|---|---|
| hermes-gateway-setup | `hermes/skills/devops/hermes-gateway-setup` | Install, configure, and troubleshoot the Hermes messaging gateway for Discord, Telegram, Slack, WhatsApp, and other platforms. Covers bot token validation, systemd service management, and platform allowlisting. |
| interactive-sudo-via-chat | `hermes/skills/devops/interactive-sudo-via-chat` | Run sudo commands on behalf of the user when only the user knows the password and you're operating from chat (Discord, Telegram, etc.). Forward the password from the user through a PTY to sudo without triggering shell-cache or heredoc pitfalls. |
| kanban-orchestrator | `hermes/skills/devops/kanban-orchestrator` | Decomposition playbook + anti-temptation rules for an orchestrator profile routing work through Kanban. The "don't do the work yourself" rule and the basic lifecycle are auto-injected into every kanban worker's system prompt; this skill is the deeper playbook when you're specifically playing the orchestrator role. |
| kanban-worker | `hermes/skills/devops/kanban-worker` | Pitfalls, examples, and edge cases for Hermes Kanban workers. The lifecycle itself is auto-injected into every worker's system prompt as KANBAN_GUIDANCE (from agent/prompt_builder.py); this skill is what you load when you want deeper detail on specific scenarios. |
| webhook-subscriptions | `hermes/skills/devops/webhook-subscriptions` | Webhook subscriptions: event-driven agent runs. |

### discord

| Skill | Path | Description |
|---|---|---|
| discord-agent-handoff | `hermes/skills/discord/discord-agent-handoff` | Route work between the Hermes Discord agent fleet so bots can assign tasks, process AGENT TASK messages, complete deliverables in their private channels, and confirm completion. |
| discord-bot-cost-optimization | `hermes/skills/discord/discord-bot-cost-optimization` | \| All Discord bot response behavior is controlled from a single config file: ~/.hermes/discord-bots/bot_config.py This is the ONLY file you need to edit to change how bots respond. Changes apply to ALL bots after a service restart. Works with any AI model/provider — the config is model-agnostic. |
| discord-bot-hermes-integration | `hermes/skills/discord/discord-bot-hermes-integration` | \| Provides a reusable HermesAgent class that calls the Anthropic API directly with a proper system prompt for reliable character identity. Includes response formatting, message chunking (Discord 2000-char limit), timeout management, and graceful error handling. Works for both single-bot and multi-bot (independent process) architectures. IMPORTANT: Uses direct Anthropic SDK, NOT Hermes CLI subprocess. The CLI approach was abandoned because Hermes injects its own identity (Claude Code persona, memory, SOUL.md, AGENTS.md) which overrides bot character even with --ignore-rules. Direct API with system= parameter is the only reliable way to maintain bot identity. |
| discord-bot-model-switching | `hermes/skills/discord/discord-bot-model-switching` | \| All 5 Discord bots support runtime model switching via the !model command. Supports Anthropic (Claude) and OpenAI (GPT/Codex) providers. Models are defined in bot_config.py — add new ones there. Each bot maintains its own model state independently. |
| discord-multi-bot-setup | `hermes/skills/discord/discord-multi-bot-setup` | \| Set up and deploy multiple independent Discord bots using standalone discord.py scripts. Manage bot lifecycle with a launcher process and systemd service for auto-restart and boot persistence. Supports mixed response modes: respond-all (primary bot) + mention-only (auxiliary bots). Supports channel-aware routing: bots auto-respond in their dedicated channel + war-room (+ threads), mention-only elsewhere. |
| discord-server-management | `hermes/skills/discord/discord-server-management` | Create, edit, and delete Discord channels, categories, and threads using the Discord REST API. Use this skill whenever the user asks to create or manage Discord channels, categories, or server structure. |
| mission-control-report | `hermes/skills/discord/mission-control-report` | Generate and deliver a daily Mission Control status report to the Discord #setup > mission-control thread. Covers dashboard status, active tasks, agents, skills, cron jobs, sessions, memory, and Obsidian vault activity. All times in 12-hour format (e.g. 2:00 AM). |

### email

| Skill | Path | Description |
|---|---|---|
| himalaya | `hermes/skills/email/himalaya` | Himalaya CLI: IMAP/SMTP email from terminal. |

### gaming

| Skill | Path | Description |
|---|---|---|
| minecraft-modpack-server | `hermes/skills/gaming/minecraft-modpack-server` | Host modded Minecraft servers (CurseForge, Modrinth). |
| pokemon-player | `hermes/skills/gaming/pokemon-player` | Play Pokemon via headless emulator + RAM reads. |

### github

| Skill | Path | Description |
|---|---|---|
| codebase-inspection | `hermes/skills/github/codebase-inspection` | Inspect codebases w/ pygount: LOC, languages, ratios. |
| github-auth | `hermes/skills/github/github-auth` | GitHub auth setup: HTTPS tokens, SSH keys, gh CLI login. |
| github-code-review | `hermes/skills/github/github-code-review` | Review PRs: diffs, inline comments via gh or REST. |
| github-issues | `hermes/skills/github/github-issues` | Create, triage, label, assign GitHub issues via gh or REST. |
| github-pages-portfolio-site | `hermes/skills/github/github-pages-portfolio-site` | Bootstrap a recruiter-facing static portfolio/showcase site on GitHub Pages with strict secret hygiene. Use when the user wants a public site that documents their personal/private systems (AI agents, homelab, bots) without leaking credentials or proprietary code. |
| github-pr-workflow | `hermes/skills/github/github-pr-workflow` | GitHub PR lifecycle: branch, commit, open, CI, merge. |
| github-repo-management | `hermes/skills/github/github-repo-management` | Clone/create/fork repos; manage remotes, releases. |

### images

| Skill | Path | Description |
|---|---|---|
| dalle-image-gen | `hermes/skills/images/dalle-image-gen` | Generate images using FAL AI nano-banana-pro (Gemini 3 Pro) and post them directly to Discord. Supports any creative prompt. |

### mcp

| Skill | Path | Description |
|---|---|---|
| native-mcp | `hermes/skills/mcp/native-mcp` | MCP client: connect servers, register tools (stdio/HTTP). |

### media

| Skill | Path | Description |
|---|---|---|
| camsnap | `hermes/skills/media/camsnap` | Capture frames or clips from RTSP/ONVIF cameras. |
| gif-search | `hermes/skills/media/gif-search` | Search/download GIFs from Tenor via curl + jq. |
| gifgrep | `hermes/skills/media/gifgrep` | Search GIF providers with CLI/TUI, download results, and extract stills/sheets. |
| heartmula | `hermes/skills/media/heartmula` | HeartMuLa: Suno-like song generation from lyrics + tags. |
| openai-whisper | `hermes/skills/media/openai-whisper` | Local speech-to-text with the Whisper CLI (no API key). |
| openai-whisper-api | `hermes/skills/media/openai-whisper-api` | Transcribe audio via OpenAI Audio Transcriptions API (Whisper). |
| openclaw-image-skill | `hermes/skills/media/openclaw-image-skill` | Generate images via OpenAI DALL-E 3 API. Use when a user asks to create, generate, or visualize an image from a text prompt. |
| peekaboo | `hermes/skills/media/peekaboo` | Capture and automate macOS UI with the Peekaboo CLI. |
| pikastream-video-meeting | `hermes/skills/media/pikastream-video-meeting` | Join Google Meet or Zoom calls with a Pika video avatar. Handles meeting join/leave and pre-flight briefing. |
| sherpa-onnx-tts | `hermes/skills/media/sherpa-onnx-tts` | Local text-to-speech via sherpa-onnx (offline, no cloud) |
| songsee | `hermes/skills/media/songsee` | Audio spectrograms/features (mel, chroma, MFCC) via CLI. |
| sonoscli | `hermes/skills/media/sonoscli` | Control Sonos speakers (discover/status/play/volume/group). |
| spotify | `hermes/skills/media/spotify` | Spotify: play, search, queue, manage playlists and devices. |
| spotify-player | `hermes/skills/media/spotify-player` | Terminal Spotify playback/search via spogo (preferred) or spotify_player. |
| video-frames | `hermes/skills/media/video-frames` | Extract frames or short clips from videos using ffmpeg. |
| video-gen | `hermes/skills/media/video-gen` | Generate short videos (5-30s) from text prompts using FAL AI (Kling v2), post to Discord, and optionally auto-upload to TikTok. |
| voice-call | `hermes/skills/media/voice-call` | Start voice calls via the OpenClaw voice-call plugin. |
| youtube-content | `hermes/skills/media/youtube-content` | YouTube transcripts to summaries, threads, blogs. |
| youtube-transcript | `hermes/skills/media/youtube-transcript` | Transcribe any YouTube video posted in the #youtube-transcripts Discord channel. Uses YouTube's built-in captions first; falls back to OpenAI Whisper if none are available. Transcripts are saved to ~/hermes-transcripts/. |

### memory

| Skill | Path | Description |
|---|---|---|
| local-memory-archive | `hermes/skills/memory/local-memory-archive` | Archive overgrown Hermes durable memory entries to local SSD files instead of keeping them in injected memory. Use when memory is full, memory writes fail due to capacity, old durable facts should be retained for future reference but removed or compacted from active memory, or the user asks to store memory/archive knowledge locally without using persistent memory budget. |
| obsidian-memory-curator | `hermes/skills/memory/obsidian-memory-curator` | Curate durable memory from sessions into reviewable Obsidian-ready updates by separating long-term facts from temporary noise. |

### mlops

| Skill | Path | Description |
|---|---|---|
| gemini | `hermes/skills/mlops/gemini` | Gemini CLI for one-shot Q&A, summaries, and generation. |
| huggingface-hub | `hermes/skills/mlops/huggingface-hub` | HuggingFace hf CLI: search/download/upload models, datasets. |
| model-usage | `hermes/skills/mlops/model-usage` | Summarize CodexBar local cost logs by model for Codex or Claude, including current or full breakdowns. |
| oracle | `hermes/skills/mlops/oracle` | Use oracle CLI to bundle prompts and files for second-model debugging, refactor, design, or review checks. |
| sag | `hermes/skills/mlops/sag` | ElevenLabs text-to-speech with mac-style say UX. |

### mlops/evaluation

| Skill | Path | Description |
|---|---|---|
| evaluating-llms-harness | `hermes/skills/mlops/evaluation/lm-evaluation-harness` | lm-eval-harness: benchmark LLMs (MMLU, GSM8K, etc.). |
| weights-and-biases | `hermes/skills/mlops/evaluation/weights-and-biases` | W&B: log ML experiments, sweeps, model registry, dashboards. |

### mlops/inference

| Skill | Path | Description |
|---|---|---|
| llama-cpp | `hermes/skills/mlops/inference/llama-cpp` | llama.cpp local GGUF inference + HF Hub model discovery. |
| obliteratus | `hermes/skills/mlops/inference/obliteratus` | OBLITERATUS: abliterate LLM refusals (diff-in-means). |
| outlines | `hermes/skills/mlops/inference/outlines` | Outlines: structured JSON/regex/Pydantic LLM generation. |
| serving-llms-vllm | `hermes/skills/mlops/inference/vllm` | vLLM: high-throughput LLM serving, OpenAI API, quantization. |

### mlops/models

| Skill | Path | Description |
|---|---|---|
| audiocraft-audio-generation | `hermes/skills/mlops/models/audiocraft` | AudioCraft: MusicGen text-to-music, AudioGen text-to-sound. |
| segment-anything-model | `hermes/skills/mlops/models/segment-anything` | SAM: zero-shot image segmentation via points, boxes, masks. |

### mlops/research

| Skill | Path | Description |
|---|---|---|
| dspy | `hermes/skills/mlops/research/dspy` | DSPy: declarative LM programs, auto-optimize prompts, RAG. |

### mlops/training

| Skill | Path | Description |
|---|---|---|
| axolotl | `hermes/skills/mlops/training/axolotl` | Axolotl: YAML LLM fine-tuning (LoRA, DPO, GRPO). |
| fine-tuning-with-trl | `hermes/skills/mlops/training/trl-fine-tuning` | TRL: SFT, DPO, PPO, GRPO, reward modeling for LLM RLHF. |
| unsloth | `hermes/skills/mlops/training/unsloth` | Unsloth: 2-5x faster LoRA/QLoRA fine-tuning, less VRAM. |

### note-taking

| Skill | Path | Description |
|---|---|---|
| bear-notes | `hermes/skills/note-taking/bear-notes` | Create, search, and manage Bear notes via grizzly CLI. |
| obsidian | `hermes/skills/note-taking/obsidian` | Read, search, and create notes in the Obsidian vault. |
| obsidian-claudeclaw-memory | `hermes/skills/note-taking/obsidian-claudeclaw-memory` | Set up Obsidian + ClaudeClaw as a living AI memory system. Wires the Obsidian vault to ClaudeClaw's context injection, maintains curated MEMORY.md and USER.md in the vault, and schedules overnight memory distillation via ClaudeClaw's built-in scheduler. Covers vault file structure, CLAUDE.md persona sync, MEMORY.md distillation, and heartbeat-based maintenance. |
| obsidian-hermes-memory | `hermes/skills/note-taking/obsidian-hermes-memory` | Set up Obsidian + Hermes Agent as a living AI memory system. Use when helping users configure their workspace so Hermes remembers context across sessions, builds a knowledge graph in Obsidian, and proactively maintains memory via Hermes cron. Covers vault file structure, SOUL.md persona, MEMORY.md distillation, session search, and heartbeat-based memory maintenance. |
| obsidian-vault-maintainer | `hermes/skills/note-taking/obsidian-vault-maintainer` | Maintain an Obsidian-friendly memory wiki vault with wikilinks, frontmatter, and official Obsidian CLI awareness. |
| wiki-maintainer | `hermes/skills/note-taking/wiki-maintainer` | Maintain the OpenClaw memory wiki vault with deterministic pages, managed blocks, and source-backed updates. |

### operations

| Skill | Path | Description |
|---|---|---|
| mission-control-report | `hermes/skills/operations/mission-control-report` | Generate a structured JSON + Markdown operations summary covering system status, active projects, agent runs, warnings, and open loops. Feeds the Mission Control GUI dashboard and Discord/Telegram delivery targets. |
| model-routing | `hermes/skills/operations/model-routing` | Select the right model (Codex, Claude, or both) before executing complex tasks. Produces a consistent routing decision with rationale before work begins. |

### productivity

| Skill | Path | Description |
|---|---|---|
| airtable | `hermes/skills/productivity/airtable` | Airtable REST API via curl. Records CRUD, filters, upserts. |
| clawhub | `hermes/skills/productivity/clawhub` | Search, install, update, sync, or publish agent skills with the ClawHub CLI and registry. |
| discord-pdf-workflow | `hermes/skills/productivity/discord-pdf-workflow` | Create, edit, improve, review, extract, revise, and post PDFs from Discord bot tasks. Use for any Discord fleet agent asked to make a PDF, update an existing PDF/SOW/MSA/proposal/report, improve formatting/content, convert markdown/text to PDF, revise from feedback, or avoid accidentally sending canned ideas PDFs. |
| google-workspace | `hermes/skills/productivity/google-workspace` | Gmail, Calendar, Drive, Docs, Sheets via gws CLI or Python. |
| job-search-automation | `hermes/skills/productivity/job-search-automation` | Automated job search pipeline — analyze candidate profile, search curated job boards, filter by skills/keywords, and generate tailored recommendations with application strategy. |
| linear | `hermes/skills/productivity/linear` | Linear: manage issues, projects, teams via GraphQL + curl. |
| maps | `hermes/skills/productivity/maps` | Geocode, POIs, routes, timezones via OpenStreetMap/OSRM. |
| nano-pdf | `hermes/skills/productivity/nano-pdf` | Edit PDF text/typos/titles via nano-pdf CLI (NL prompts). |
| notion | `hermes/skills/productivity/notion` | Notion API + ntn CLI: pages, databases, markdown, Workers. |
| ocr-and-documents | `hermes/skills/productivity/ocr-and-documents` | Extract text from PDFs/scans (pymupdf, marker-pdf). |
| ordercli | `hermes/skills/productivity/ordercli` | Foodora-only CLI for checking past orders and active order status (Deliveroo WIP). |
| powerpoint | `hermes/skills/productivity/powerpoint` | Create, read, edit .pptx decks, slides, notes, templates. |
| summarize | `hermes/skills/productivity/summarize` | Summarize or transcribe URLs, YouTube/videos, podcasts, articles, transcripts, PDFs, and local files. |
| taskflow | `hermes/skills/productivity/taskflow` | Coordinate multi-step detached tasks as one durable TaskFlow job with owner context, state, waits, and child tasks. |
| taskflow-inbox-triage | `hermes/skills/productivity/taskflow-inbox-triage` | Example TaskFlow pattern for inbox triage, intent routing, waiting on replies, and later summaries. |
| teams-meeting-pipeline | `hermes/skills/productivity/teams-meeting-pipeline` | Operate the Teams meeting summary pipeline via Hermes CLI — summarize meetings, inspect pipeline status, replay jobs, manage Microsoft Graph subscriptions. |
| things-mac | `hermes/skills/productivity/things-mac` | Add, update, list, search, or inspect Things 3 todos, inbox, today, projects, areas, and tags on macOS. |
| trello | `hermes/skills/productivity/trello` | Manage Trello boards, lists, and cards via the Trello REST API. |

### red-teaming

| Skill | Path | Description |
|---|---|---|
| godmode | `hermes/skills/red-teaming/godmode` | Jailbreak LLMs: Parseltongue, GODMODE, ULTRAPLINIAN. |

### reporting

| Skill | Path | Description |
|---|---|---|
| hermes-cost-report | `hermes/skills/reporting/hermes-cost-report` | Generate a markdown report of Hermes session costs from ~/.hermes/state.db. Computes per-token cost from a configurable pricing JSON. Use when the user asks for a cost report, usage summary, or spend analysis. |
| llm-cost-optimization | `hermes/skills/reporting/llm-cost-optimization` | Systematic workflow for analyzing and reducing LLM API costs in production. Measures spend, identifies cost drivers, and implements optimizations (model routing, prompt pruning, caching). Use when the user asks to reduce costs, analyze spend, or optimize their LLM setup. |
| recurring-report-cron | `hermes/skills/reporting/recurring-report-cron` | Build a Hermes skill + cron job pair for recurring scheduled reports (cost reports, security audits, status digests, etc.). Use when the user asks for a recurring/periodic report delivered on a schedule. Pairs a stdlib-only Python script under a skill with a cron job that runs it and posts the output back to the requesting channel. |

### research

| Skill | Path | Description |
|---|---|---|
| ai-model-research | `hermes/skills/research/ai-model-research` | Performs deep AI model research, weekly briefing, frontier labs, YouTube discovery, benchmark tracking, paper triage, community signal checks, and Discord reporting. |
| arxiv | `hermes/skills/research/arxiv` | Search arXiv papers by keyword, author, category, or ID. |
| blogwatcher | `hermes/skills/research/blogwatcher` | Monitor blogs and RSS/Atom feeds via blogwatcher-cli tool. |
| gog | `hermes/skills/research/gog` | Google Workspace CLI for Gmail, Calendar, Drive, Contacts, Sheets, and Docs. |
| goplaces | `hermes/skills/research/goplaces` | Query Google Places for text search, place details, resolve, reviews, or scriptable JSON via goplaces. |
| llm-wiki | `hermes/skills/research/llm-wiki` | Karpathy's LLM Wiki: build/query interlinked markdown KB. |
| polymarket | `hermes/skills/research/polymarket` | Query Polymarket: markets, prices, orderbooks, history. |
| research-paper-writing | `hermes/skills/research/research-paper-writing` | Write ML papers for NeurIPS/ICML/ICLR: design→submit. |
| weather | `hermes/skills/research/weather` | Get current weather, rain, temperature, and forecasts for locations or travel planning. |

### security

| Skill | Path | Description |
|---|---|---|
| daily-security-report | `hermes/skills/security/daily-security-report` | Daily automated security audit (system + repos + infra) with approval-gated fix application. Posts to Discord at 2:00 AM CST. |

### smart-home

| Skill | Path | Description |
|---|---|---|
| blucli | `hermes/skills/smart-home/blucli` | BluOS CLI (blu) for discovery, playback, grouping, and volume. |
| eightctl | `hermes/skills/smart-home/eightctl` | Control Eight Sleep pods (status, temperature, alarms, schedules). |
| openhue | `hermes/skills/smart-home/openhue` | Control Philips Hue lights, scenes, rooms via OpenHue CLI. |

### social-media

| Skill | Path | Description |
|---|---|---|
| bluebubbles | `hermes/skills/social-media/bluebubbles` | Send and manage iMessages via BlueBubbles, including attachments, tapbacks, edits, replies, and groups. |
| discord | `hermes/skills/social-media/discord` | Discord ops via the message tool (channel=discord). |
| imsg | `hermes/skills/social-media/imsg` | iMessage/SMS CLI for listing chats, history, and sending messages via Messages.app. |
| qqbot-channel | `hermes/skills/social-media/qqbot-channel` | QQ 频道管理技能。查询频道列表、子频道、成员、发帖、公告、日程等操作。使用 qqbot_channel_api 工具代理 QQ 开放平台 HTTP 接口，自动处理 Token 鉴权。当用户需要查看频道、管理子频道、查询成员、发布帖子/公告/日程时使用。 |
| qqbot-media | `hermes/skills/social-media/qqbot-media` | QQBot 富媒体收发能力。使用 <qqmedia> 标签，系统根据文件扩展名自动识别类型（图片/语音/视频/文件）。 |
| qqbot-remind | `hermes/skills/social-media/qqbot-remind` | QQBot 定时提醒。支持一次性和周期性提醒的创建、查询、取消。当通过 QQ 通道通信且涉及提醒/定时任务时使用。 |
| slack | `hermes/skills/social-media/slack` | Use the Slack tool to react, pin/unpin, send, edit, delete messages, or fetch Slack member info. |
| wacli | `hermes/skills/social-media/wacli` | Send third-party WhatsApp messages or sync/search WhatsApp history via wacli, not normal active chats. |
| xurl | `hermes/skills/social-media/xurl` | X/Twitter via xurl CLI: post, search, DM, media, v2 API. |

### software-development

| Skill | Path | Description |
|---|---|---|
| acp-router | `hermes/skills/software-development/acp-router` | Route plain-language requests for Pi, Claude Code, Cursor, Copilot, OpenClaw ACP, OpenCode, Gemini CLI, Qwen, Kiro, Kimi, iFlow, Factory Droid, Kilocode, or explicit ACP harness work into either OpenClaw ACP runtime sessions or direct acpx-driven sessions ("telephone game" flow). For coding-agent thread requests, read this skill first, then use only `sessions_spawn` for thread creation. Codex chat binding defaults to the native Codex app-server plugin unless ACP is explicit or background spawn needs ACP. |
| async-subprocess-integration | `hermes/skills/software-development/async-subprocess-integration` | Call external CLI tools from async Python code reliably with timeouts, error handling, and output formatting. |
| browser-automation | `hermes/skills/software-development/browser-automation` | Use when controlling web pages with the OpenClaw browser tool, especially multi-step flows, login checks, tab management, or recovery from stale refs/timeouts. |
| coding-agent | `hermes/skills/software-development/coding-agent` | Delegate coding tasks to Codex, Claude Code, OpenCode, or Pi agents via immediate background processes. Use when: (1) building or creating features/apps, (2) reviewing PRs in a temp clone/worktree, (3) refactoring large codebases, (4) iterative coding that needs file exploration. NOT for: simple one-line fixes (just edit), reading code (use read tool), thread-bound ACP harness requests in chat (use sessions_spawn with runtime:"acp"), or any work in ~/clawd workspace (never spawn agents here). All coding-agent runs start with background:true immediately. Claude Code: use --print --permission-mode bypassPermissions (no PTY). Codex/Pi/OpenCode: pty:true required. Completion notification must use openclaw message send, not system event/heartbeat. |
| debugging-hermes-tui-commands | `hermes/skills/software-development/debugging-hermes-tui-commands` | Debug Hermes TUI slash commands: Python, gateway, Ink UI. |
| gh-issues | `hermes/skills/software-development/gh-issues` | Fetch GitHub issues, delegate fixes to subagents, open PRs, watch reviews, or run /gh-issues workflows. |
| github | `hermes/skills/software-development/github` | Use gh for GitHub issues, PR status, CI/logs, comments, reviews, releases, and API queries. |
| hermes-agent-skill-authoring | `hermes/skills/software-development/hermes-agent-skill-authoring` | Author in-repo SKILL.md: frontmatter, validator, structure. |
| mcporter | `hermes/skills/software-development/mcporter` | List, configure, authenticate, call, and inspect MCP servers/tools with mcporter over HTTP or stdio. |
| mission-control-dashboard-variant-rollout | `hermes/skills/software-development/mission-control-dashboard-variant-rollout` | Safely roll out a major Mission Control dashboard redesign as an optional view mode (modern/classic) without breaking existing data flow or APIs. |
| node-connect | `hermes/skills/software-development/node-connect` | Diagnose OpenClaw Android, iOS, or macOS node pairing, QR/setup code, route, auth, and connection failures. |
| node-inspect-debugger | `hermes/skills/software-development/node-inspect-debugger` | Debug Node.js via --inspect + Chrome DevTools Protocol CLI. |
| plan | `hermes/skills/software-development/plan` | Plan mode: write markdown plan to .hermes/plans/, no exec. |
| python-debugpy | `hermes/skills/software-development/python-debugpy` | Debug Python: pdb REPL + debugpy remote (DAP). |
| requesting-code-review | `hermes/skills/software-development/requesting-code-review` | Pre-commit review: security scan, quality gates, auto-fix. |
| skill-creator | `hermes/skills/software-development/skill-creator` | Create, edit, improve, tidy, review, audit, or restructure AgentSkills and SKILL.md files. |
| spike | `hermes/skills/software-development/spike` | Throwaway experiments to validate an idea before build. |
| subagent-driven-development | `hermes/skills/software-development/subagent-driven-development` | Execute plans via delegate_task subagents (2-stage review). |
| systematic-debugging | `hermes/skills/software-development/systematic-debugging` | 4-phase root cause debugging: understand bugs before fixing. |
| test-driven-development | `hermes/skills/software-development/test-driven-development` | TDD: enforce RED-GREEN-REFACTOR, tests before code. |
| tmux | `hermes/skills/software-development/tmux` | Remote-control tmux sessions for interactive CLIs by sending keystrokes and scraping pane output. |
| troubleshoot-debug-repair | `hermes/skills/software-development/troubleshoot-debug-repair` | Troubleshoot, debug, diagnose, and repair broken ClaudeClaw features, services, dashboards, agents, chat flows, cron jobs, reports, APIs, databases, and local integrations. Use when something is failing, regressed, misconfigured, unavailable, throwing errors, returning empty data, or needs root-cause analysis and a verified fix. |
| writing-plans | `hermes/skills/software-development/writing-plans` | Write implementation plans: bite-sized tasks, paths, code. |

### support

| Skill | Path | Description |
|---|---|---|
| helpdesk-triage | `hermes/skills/support/helpdesk-triage` | Structured IT support triage workflow across identity, network, device, and application layers with evidence-based diagnosis and safe remediation proposals. |

### system

| Skill | Path | Description |
|---|---|---|
| 1password | `hermes/skills/system/1password` | Set up and use 1Password CLI for sign-in, desktop integration, and reading or injecting secrets. |
| healthcheck | `hermes/skills/system/healthcheck` | Audit and harden hosts running OpenClaw for SSH, firewall, updates, exposure, cron checks, and risk posture. |
| linux-system-health | `hermes/skills/system/linux-system-health` | Monitor Linux host health and produce a daily operations report with failed services, disk, memory, network, and update posture. Report-first, no service changes. |
| local-file-ops | `hermes/skills/system/local-file-ops` | Safely summarize, audit, and organize local files and folders. Produces folder summaries, duplicate reports, large-file inventories, and cleanup plans. No move, rename, or delete actions without explicit approval of exact paths. |
| oauth-reauth | `hermes/skills/system/oauth-reauth` | Detect expired OAuth sessions for Claude Code and Codex CLI, and prompt the user to re-authenticate. |
| oauth-usage-monitor | `hermes/skills/system/oauth-usage-monitor` | Check Claude Code and Codex CLI OAuth usage levels, warn when running low, and show when limits reset. |
| security-triage | `hermes/skills/system/security-triage` | Defensive security triage for the Linux host and project repos. Inspects logs, open ports, firewall state, failed logins, and package posture. Produces a weekly severity-ranked report with evidence and remediation checklists. Defensive use only — no offensive guidance. |
| session-logs | `hermes/skills/system/session-logs` | Search and analyze your own session logs (older/parent conversations) using jq. |

---
## MyClaw Skills

### (root)

| Skill | Path | Description |
|---|---|---|
| myclaw-context | `myclaw/skills/myclaw-context` | Core context about the MyClaw harness — layout, operating principles, and what the operator expects when you receive a chat request |

---
## OpenClaw Workspace Skills

### (root)

| Skill | Path | Description |
|---|---|---|
| openclaw-image-skill | `openclaw/workspace-skills/openclaw-image-skill` | Generate images via OpenAI DALL-E 3 API. Use when a user asks to create, generate, or visualize an image from a text prompt. |

---
## OpenClaw Project Skills

### (root)

| Skill | Path | Description |
|---|---|---|
| mission-control | `openclaw/project-skills/mission-control` | Interact with Mission Control — AI agent orchestration dashboard. Use when registering agents, managing tasks, syncing skills, or querying agent/task status via MC APIs. |

---
## OpenClaw Sandbox Skills

### (root)

| Skill | Path | Description |
|---|---|---|
| 1password | `openclaw/sandbox-skills/1password` | Set up and use 1Password CLI for sign-in, desktop integration, and reading or injecting secrets. |
| acp-router | `openclaw/sandbox-skills/acp-router` | Route plain-language requests for Pi, Claude Code, Cursor, Copilot, OpenClaw ACP, OpenCode, Gemini CLI, Qwen, Kiro, Kimi, iFlow, Factory Droid, Kilocode, or explicit ACP harness work into either OpenClaw ACP runtime sessions or direct acpx-driven sessions ("telephone game" flow). For coding-agent thread requests, read this skill first, then use only `sessions_spawn` for thread creation. Codex chat binding defaults to the native Codex app-server plugin unless ACP is explicit or background spawn needs ACP. |
| apple-notes | `openclaw/sandbox-skills/apple-notes` | Create, view, edit, delete, search, move, or export Apple Notes via the memo CLI on macOS. |
| apple-reminders | `openclaw/sandbox-skills/apple-reminders` | List, add, edit, complete, or delete Apple Reminders and reminder lists via remindctl. |
| bear-notes | `openclaw/sandbox-skills/bear-notes` | Create, search, and manage Bear notes via grizzly CLI. |
| blogwatcher | `openclaw/sandbox-skills/blogwatcher` | Monitor blogs and RSS/Atom feeds for updates using the blogwatcher CLI. |
| blucli | `openclaw/sandbox-skills/blucli` | BluOS CLI (blu) for discovery, playback, grouping, and volume. |
| bluebubbles | `openclaw/sandbox-skills/bluebubbles` | Send and manage iMessages via BlueBubbles, including attachments, tapbacks, edits, replies, and groups. |
| browser-automation | `openclaw/sandbox-skills/browser-automation` | Use when controlling web pages with the OpenClaw browser tool, especially multi-step flows, login checks, tab management, or recovery from stale refs/timeouts. |
| camsnap | `openclaw/sandbox-skills/camsnap` | Capture frames or clips from RTSP/ONVIF cameras. |
| clawhub | `openclaw/sandbox-skills/clawhub` | Search, install, update, sync, or publish agent skills with the ClawHub CLI and registry. |
| coding-agent | `openclaw/sandbox-skills/coding-agent` | Delegate coding tasks to Codex, Claude Code, OpenCode, or Pi agents via immediate background processes. Use when: (1) building or creating features/apps, (2) reviewing PRs in a temp clone/worktree, (3) refactoring large codebases, (4) iterative coding that needs file exploration. NOT for: simple one-line fixes (just edit), reading code (use read tool), thread-bound ACP harness requests in chat (use sessions_spawn with runtime:"acp"), or any work in ~/clawd workspace (never spawn agents here). All coding-agent runs start with background:true immediately. Claude Code: use --print --permission-mode bypassPermissions (no PTY). Codex/Pi/OpenCode: pty:true required. Completion notification must use openclaw message send, not system event/heartbeat. |
| discord | `openclaw/sandbox-skills/discord` | Discord ops via the message tool (channel=discord). |
| eightctl | `openclaw/sandbox-skills/eightctl` | Control Eight Sleep pods (status, temperature, alarms, schedules). |
| gemini | `openclaw/sandbox-skills/gemini` | Gemini CLI for one-shot Q&A, summaries, and generation. |
| gh-issues | `openclaw/sandbox-skills/gh-issues` | Fetch GitHub issues, delegate fixes to subagents, open PRs, watch reviews, or run /gh-issues workflows. |
| gifgrep | `openclaw/sandbox-skills/gifgrep` | Search GIF providers with CLI/TUI, download results, and extract stills/sheets. |
| github | `openclaw/sandbox-skills/github` | Use gh for GitHub issues, PR status, CI/logs, comments, reviews, releases, and API queries. |
| gog | `openclaw/sandbox-skills/gog` | Google Workspace CLI for Gmail, Calendar, Drive, Contacts, Sheets, and Docs. |
| goplaces | `openclaw/sandbox-skills/goplaces` | Query Google Places for text search, place details, resolve, reviews, or scriptable JSON via goplaces. |
| healthcheck | `openclaw/sandbox-skills/healthcheck` | Audit and harden hosts running OpenClaw for SSH, firewall, updates, exposure, cron checks, and risk posture. |
| himalaya | `openclaw/sandbox-skills/himalaya` | Use himalaya to list, read, search, compose, reply, forward, and organize IMAP/SMTP email. |
| imsg | `openclaw/sandbox-skills/imsg` | iMessage/SMS CLI for listing chats, history, and sending messages via Messages.app. |
| mcporter | `openclaw/sandbox-skills/mcporter` | List, configure, authenticate, call, and inspect MCP servers/tools with mcporter over HTTP or stdio. |
| model-usage | `openclaw/sandbox-skills/model-usage` | Summarize CodexBar local cost logs by model for Codex or Claude, including current or full breakdowns. |
| nano-pdf | `openclaw/sandbox-skills/nano-pdf` | Edit PDFs with natural-language instructions using the nano-pdf CLI. |
| node-connect | `openclaw/sandbox-skills/node-connect` | Diagnose OpenClaw Android, iOS, or macOS node pairing, QR/setup code, route, auth, and connection failures. |
| notion | `openclaw/sandbox-skills/notion` | Notion API for creating and managing pages, databases, and blocks. |
| obsidian | `openclaw/sandbox-skills/obsidian` | Work with Obsidian vaults (plain Markdown notes) and automate via obsidian-cli. |
| obsidian-vault-maintainer | `openclaw/sandbox-skills/obsidian-vault-maintainer` | Maintain an Obsidian-friendly memory wiki vault with wikilinks, frontmatter, and official Obsidian CLI awareness. |
| openai-whisper | `openclaw/sandbox-skills/openai-whisper` | Local speech-to-text with the Whisper CLI (no API key). |
| openai-whisper-api | `openclaw/sandbox-skills/openai-whisper-api` | Transcribe audio via OpenAI Audio Transcriptions API (Whisper). |
| openclaw-image-skill | `openclaw/sandbox-skills/openclaw-image-skill` | Generate images via OpenAI DALL-E 3 API. Use when a user asks to create, generate, or visualize an image from a text prompt. |
| openhue | `openclaw/sandbox-skills/openhue` | Control Philips Hue lights and scenes via the OpenHue CLI. |
| oracle | `openclaw/sandbox-skills/oracle` | Use oracle CLI to bundle prompts and files for second-model debugging, refactor, design, or review checks. |
| ordercli | `openclaw/sandbox-skills/ordercli` | Foodora-only CLI for checking past orders and active order status (Deliveroo WIP). |
| peekaboo | `openclaw/sandbox-skills/peekaboo` | Capture and automate macOS UI with the Peekaboo CLI. |
| qqbot-channel | `openclaw/sandbox-skills/qqbot-channel` | QQ 频道管理技能。查询频道列表、子频道、成员、发帖、公告、日程等操作。使用 qqbot_channel_api 工具代理 QQ 开放平台 HTTP 接口，自动处理 Token 鉴权。当用户需要查看频道、管理子频道、查询成员、发布帖子/公告/日程时使用。 |
| qqbot-media | `openclaw/sandbox-skills/qqbot-media` | QQBot 富媒体收发能力。使用 <qqmedia> 标签，系统根据文件扩展名自动识别类型（图片/语音/视频/文件）。 |
| qqbot-remind | `openclaw/sandbox-skills/qqbot-remind` | QQBot 定时提醒。支持一次性和周期性提醒的创建、查询、取消。当通过 QQ 通道通信且涉及提醒/定时任务时使用。 |
| sag | `openclaw/sandbox-skills/sag` | ElevenLabs text-to-speech with mac-style say UX. |
| session-logs | `openclaw/sandbox-skills/session-logs` | Search and analyze your own session logs (older/parent conversations) using jq. |
| sherpa-onnx-tts | `openclaw/sandbox-skills/sherpa-onnx-tts` | Local text-to-speech via sherpa-onnx (offline, no cloud) |
| skill-creator | `openclaw/sandbox-skills/skill-creator` | Create, edit, improve, tidy, review, audit, or restructure AgentSkills and SKILL.md files. |
| slack | `openclaw/sandbox-skills/slack` | Use the Slack tool to react, pin/unpin, send, edit, delete messages, or fetch Slack member info. |
| songsee | `openclaw/sandbox-skills/songsee` | Generate spectrograms and feature-panel visualizations from audio with the songsee CLI. |
| sonoscli | `openclaw/sandbox-skills/sonoscli` | Control Sonos speakers (discover/status/play/volume/group). |
| spotify-player | `openclaw/sandbox-skills/spotify-player` | Terminal Spotify playback/search via spogo (preferred) or spotify_player. |
| summarize | `openclaw/sandbox-skills/summarize` | Summarize or transcribe URLs, YouTube/videos, podcasts, articles, transcripts, PDFs, and local files. |
| taskflow | `openclaw/sandbox-skills/taskflow` | Coordinate multi-step detached tasks as one durable TaskFlow job with owner context, state, waits, and child tasks. |
| taskflow-inbox-triage | `openclaw/sandbox-skills/taskflow-inbox-triage` | Example TaskFlow pattern for inbox triage, intent routing, waiting on replies, and later summaries. |
| things-mac | `openclaw/sandbox-skills/things-mac` | Add, update, list, search, or inspect Things 3 todos, inbox, today, projects, areas, and tags on macOS. |
| tmux | `openclaw/sandbox-skills/tmux` | Remote-control tmux sessions for interactive CLIs by sending keystrokes and scraping pane output. |
| trello | `openclaw/sandbox-skills/trello` | Manage Trello boards, lists, and cards via the Trello REST API. |
| video-frames | `openclaw/sandbox-skills/video-frames` | Extract frames or short clips from videos using ffmpeg. |
| voice-call | `openclaw/sandbox-skills/voice-call` | Start voice calls via the OpenClaw voice-call plugin. |
| wacli | `openclaw/sandbox-skills/wacli` | Send third-party WhatsApp messages or sync/search WhatsApp history via wacli, not normal active chats. |
| weather | `openclaw/sandbox-skills/weather` | Get current weather, rain, temperature, and forecasts for locations or travel planning. |
| wiki-maintainer | `openclaw/sandbox-skills/wiki-maintainer` | Maintain the OpenClaw memory wiki vault with deterministic pages, managed blocks, and source-backed updates. |
| xurl | `openclaw/sandbox-skills/xurl` | Use xurl for authenticated X API posts, replies, search, DMs, media upload, followers, or raw v2 calls. |
