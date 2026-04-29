# skills-i-have-built

Backup of all skills built and installed across **ClaudeClaw**, **Hermes**, and **OpenClaw**. Purpose: if any system needs to be rebuilt from scratch, all skills are documented and restorable from this repo.

---

## Contents

| Folder | System | Skills |
|---|---|---|
| `claudeclaw/skills/` | ClaudeClaw | 18 |
| `hermes/skills/` | Hermes Agent | 89 |
| `openclaw/workspace-skills/` | OpenClaw (user-created) | 1 |
| `openclaw/project-skills/` | OpenClaw (project) | 1 |
| `openclaw/sandbox-skills/` | OpenClaw (agent sandbox library) | 60 |

---

## ClaudeClaw Skills

| Skill | Description |
|---|---|
| ai-model-research | Produce a source-backed AI model research briefing from recent vendor posts, papers, model cards, community signals, and selected video transcripts. |
| career-artifact-builder | Convert real project work into recruiter-ready artifacts — resume bullets, LinkedIn posts, portfolio case studies, and STAR stories. |
| daily-security-report | Run local defensive checks and return a markdown security report for ClaudeClaw Reports. |
| github-repo-review | Perform a standardized repository quality review for GitHub projects with patch/PR recommendations only. |
| gmail | Gmail integration for ClaudeClaw. |
| google-calendar | Google Calendar integration for ClaudeClaw. |
| helpdesk-triage | Structured IT support triage workflow across identity, network, device, and application layers. |
| hermes-cost-report | Generate a local ClaudeClaw cost report from claudeclaw.db token_usage records. |
| linux-system-health | Monitor Linux host health and produce an operations report with failed services, disk, memory, network, and update posture. |
| local-file-ops | Safely summarize, audit, and organize local files and folders. No destructive actions without explicit approval. |
| mission-control-report | Generate a local ClaudeClaw operations summary from ClaudeClaw dashboard state. |
| model-routing | Select the right model (Opus, Sonnet, Haiku, or specialist) before executing complex tasks. |
| obsidian-claudeclaw-memory | Set up Obsidian + ClaudeClaw as a living AI memory system with curated MEMORY.md and overnight distillation. |
| obsidian-memory-curator | Curate durable memory from sessions into reviewable Obsidian-ready updates. |
| pikastream-video-meeting | Join Google Meet or Zoom calls with a Pika video avatar. |
| security-triage | Defensive security triage for Linux host and project repos. Severity-ranked report with remediation checklists. |
| skill-quality-auditor | Audit the ClaudeClaw skills catalog for quality, clarity, safety, and overlap. |
| troubleshoot-debug-repair | Troubleshoot, debug, and repair broken ClaudeClaw features, services, dashboards, agents, APIs, and local integrations. |

---

## Hermes Skills

### apple
| Skill | Description |
|---|---|
| apple-notes | Manage Apple Notes via the memo CLI on macOS. |
| apple-reminders | Manage Apple Reminders via remindctl CLI. |
| findmy | Track Apple devices and AirTags via FindMy.app on macOS. |
| imessage | Send and receive iMessages/SMS via the imsg CLI on macOS. |

### autonomous-ai-agents
| Skill | Description |
|---|---|
| claude-code | Delegate coding tasks to Claude Code (Anthropic's CLI agent). |
| codex | Delegate coding tasks to OpenAI Codex CLI agent. |
| hermes-agent | Complete guide to using and extending Hermes Agent. |
| opencode | Delegate coding tasks to OpenCode CLI agent. |

### career
| Skill | Description |
|---|---|
| career-artifact-builder | Convert real project work into recruiter-ready artifacts. |

### creative
| Skill | Description |
|---|---|
| architecture-diagram | Generate dark-themed SVG diagrams of software systems and cloud infrastructure. |
| ascii-art | Generate ASCII art using pyfiglet, cowsay, boxes, toilet, and LLM fallback. |
| ascii-video | Production pipeline for ASCII art video — any format. |
| baoyu-comic | Knowledge comic creator supporting multiple art styles and tones. |
| baoyu-infographic | Generate professional infographics with 21 layout types and 21 visual styles. |
| creative-ideation | Generate project ideas through creative constraints. |
| design-md | Author, validate, diff, and export DESIGN.md files. |
| excalidraw | Create hand-drawn style diagrams using Excalidraw JSON format. |
| manim-video | Production pipeline for mathematical and technical animations using Manim. |
| p5js | Production pipeline for interactive and generative visual art using p5.js. |
| pixel-art | Convert images into retro pixel art with hardware-accurate palettes. |
| popular-web-designs | Popular web design patterns and layouts. |
| songwriting-and-ai-music | AI-assisted songwriting and music generation. |

### data-science
| Skill | Description |
|---|---|
| jupyter-live-kernel | Live Jupyter kernel integration for interactive data science. |

### development
| Skill | Description |
|---|---|
| github-repo-review | Perform a standardized repository quality review for GitHub projects. |
| skill-quality-auditor | Audit the Hermes skills catalog for quality, clarity, safety, and overlap. |

### devops
| Skill | Description |
|---|---|
| interactive-sudo-via-chat | Run sudo commands when only the user knows the password and you're operating from chat. |
| webhook-subscriptions | Create and manage webhook subscriptions for event-driven agent activation. |

### discord
| Skill | Description |
|---|---|
| discord-server-management | Create, edit, and delete Discord channels, categories, and threads. |
| mission-control-report | Generate and deliver a daily Mission Control status report to Discord. |

### discord-channel-management
| Skill | Description |
|---|---|
| discord-channel-management | Discord channel management operations. |

### email
| Skill | Description |
|---|---|
| himalaya | CLI to manage emails via IMAP/SMTP. |

### gaming
| Skill | Description |
|---|---|
| minecraft-modpack-server | Set up a modded Minecraft server from a CurseForge/Modrinth server pack zip. |
| pokemon-player | Play Pokemon games autonomously via headless emulation. |

### github
| Skill | Description |
|---|---|
| codebase-inspection | Inspect and analyze codebases using pygount for LOC counting and language breakdown. |
| github-auth | Set up GitHub authentication for the agent. |
| github-code-review | Review code changes by analyzing git diffs and leaving inline PR comments. |
| github-issues | Create, manage, triage, and close GitHub issues. |
| github-pages-portfolio-site | Bootstrap a recruiter-facing static portfolio site on GitHub Pages. |
| github-pr-workflow | Full pull request lifecycle — create branches, commit, open PRs, monitor CI, merge. |
| github-repo-management | Clone, create, fork, configure, and manage GitHub repositories. |

### images
| Skill | Description |
|---|---|
| dalle-image-gen | Generate images using FAL AI nano-banana-pro (Gemini 3 Pro) and post to Discord. |

### mcp
| Skill | Description |
|---|---|
| native-mcp | Built-in MCP client that connects to external MCP servers and registers tools natively. |

### media
| Skill | Description |
|---|---|
| gif-search | Search and download GIFs from Tenor using curl. |
| heartmula | Set up and run HeartMuLa, the open-source music generation model. |
| songsee | Generate spectrograms and audio feature visualizations from audio files. |
| spotify | Control Spotify — play music, search catalog, manage playlists. |
| video-gen | Generate short videos from text prompts using FAL AI (Kling v2). |
| youtube-content | YouTube content creation and management. |
| youtube-transcript | Transcribe any YouTube video using built-in captions or OpenAI Whisper fallback. |

### memory
| Skill | Description |
|---|---|
| obsidian-memory-curator | Curate durable memory from sessions into reviewable Obsidian-ready updates. |

### mlops
| Skill | Description |
|---|---|
| huggingface-hub | Hugging Face Hub CLI — search, download, upload models and datasets. |
| evaluation/lm-evaluation-harness | LM Evaluation Harness for benchmarking language models. |
| evaluation/weights-and-biases | Weights & Biases experiment tracking and visualization. |
| inference/llama-cpp | Run inference with llama.cpp — local quantized LLM serving. |
| inference/obliteratus | Obliteratus inference tooling. |
| inference/outlines | Structured generation with Outlines. |
| inference/vllm | High-throughput LLM serving with vLLM. |
| models/audiocraft | AudioCraft — Meta's audio generation models. |
| models/segment-anything | Segment Anything Model (SAM) — image segmentation. |
| research/dspy | DSPy — programmatic LLM pipeline optimization. |
| training/axolotl | Fine-tuning with Axolotl. |
| training/trl-fine-tuning | Fine-tuning with TRL (Transformer Reinforcement Learning). |
| training/unsloth | Fast fine-tuning with Unsloth. |

### note-taking
| Skill | Description |
|---|---|
| obsidian | Read, search, and create notes in the Obsidian vault. |
| obsidian-hermes-memory | Set up Obsidian + Hermes Agent as a living AI memory system. |

### operations
| Skill | Description |
|---|---|
| mission-control-report | Generate a structured JSON + Markdown operations summary for Mission Control. |
| model-routing | Select the right model (Codex, Claude, or both) before executing complex tasks. |

### productivity
| Skill | Description |
|---|---|
| google-workspace | Gmail, Calendar, Drive, Contacts, Sheets, and Docs integration for Hermes. |
| job-search-automation | Automated job search pipeline with curated board scanning and tailored recommendations. |
| linear | Manage Linear issues, projects, and teams via the GraphQL API. |
| maps | Maps and location lookup integration. |
| nano-pdf | Edit PDFs with natural-language instructions using the nano-pdf CLI. |
| notion | Notion API for creating and managing pages, databases, and blocks. |
| ocr-and-documents | Extract text from PDFs and scanned documents. |
| powerpoint | Full .pptx lifecycle — create, read, edit, and export PowerPoint presentations. |

### red-teaming
| Skill | Description |
|---|---|
| godmode | Jailbreak API-served LLMs using G0DM0D3 techniques for red-team model robustness testing. |

### reporting
| Skill | Description |
|---|---|
| hermes-cost-report | Generate a markdown report of Hermes session costs from ~/.hermes/state.db. |
| llm-cost-optimization | Systematic workflow for analyzing and reducing LLM API costs in production. |
| recurring-report-cron | Build a Hermes skill + cron job pair for recurring scheduled reports. |

### research
| Skill | Description |
|---|---|
| ai-model-research | Deep AI model research, weekly briefing, frontier labs, and Discord reporting. |
| arxiv | Search and retrieve academic papers from arXiv. |
| blogwatcher | Monitor blogs and RSS/Atom feeds for updates. |
| llm-wiki | Build and maintain a persistent, interlinked markdown knowledge base. |
| polymarket | Query Polymarket prediction market data. |
| research-paper-writing | End-to-end pipeline for writing ML/AI research papers. |

### security
| Skill | Description |
|---|---|
| daily-security-report | Daily automated security audit (system + repos + infra) posted to Discord at 2:00 AM CST. |

### smart-home
| Skill | Description |
|---|---|
| openhue | Control Philips Hue lights, rooms, and scenes via the OpenHue CLI. |

### social-media
| Skill | Description |
|---|---|
| xurl | Interact with X/Twitter via xurl — post, reply, search, DMs, media upload. |

### software-development
| Skill | Description |
|---|---|
| mission-control-dashboard-variant-rollout | Safely roll out a Mission Control dashboard redesign as an optional view mode. |
| plan | Plan mode for Hermes — inspect context and write a markdown plan without executing. |
| requesting-code-review | Workflow for requesting structured code reviews. |
| subagent-driven-development | Execute implementation plans by dispatching fresh subagents per task. |
| systematic-debugging | 4-phase root cause investigation — no fixes without understanding the problem first. |
| test-driven-development | Enforce RED-GREEN-REFACTOR cycle with test-first approach. |
| writing-plans | Create comprehensive implementation plans with bite-sized tasks and exact file paths. |

### support
| Skill | Description |
|---|---|
| helpdesk-triage | Structured IT support triage workflow across identity, network, device, and application layers. |

### system
| Skill | Description |
|---|---|
| linux-system-health | Monitor Linux host health and produce a daily operations report. |
| local-file-ops | Safely summarize, audit, and organize local files and folders. |
| security-triage | Defensive security triage for Linux host and project repos. |

---

## OpenClaw Skills

### Workspace Skills (user-created)
| Skill | Description |
|---|---|
| openclaw-image-skill | Generate images via OpenAI DALL-E 3 API. |

### Project Skills
| Skill | Description |
|---|---|
| mission-control | Interact with Mission Control — AI agent orchestration dashboard. |

### Sandbox Skills (agent library — 60 skills)
| Skill | Description |
|---|---|
| 1password | Set up and use 1Password CLI for sign-in, desktop integration, and secrets. |
| acp-router | Route plain-language requests to coding agents (Codex, Claude Code, OpenCode, Gemini, etc.). |
| apple-notes | Create, view, edit, delete, search, move, or export Apple Notes via memo CLI. |
| apple-reminders | List, add, edit, complete, or delete Apple Reminders via remindctl. |
| bear-notes | Create, search, and manage Bear notes via grizzly CLI. |
| blogwatcher | Monitor blogs and RSS/Atom feeds for updates. |
| blucli | BluOS CLI for discovery, playback, grouping, and volume. |
| bluebubbles | Send and manage iMessages via BlueBubbles. |
| browser-automation | Control web pages with the OpenClaw browser tool for multi-step flows. |
| camsnap | Capture frames or clips from RTSP/ONVIF cameras. |
| clawhub | Search, install, update, sync, or publish agent skills with the ClawHub CLI. |
| coding-agent | Delegate coding tasks to Codex, Claude Code, OpenCode, or Pi agents. |
| discord | Discord ops via the message tool. |
| eightctl | Control Eight Sleep pods (status, temperature, alarms, schedules). |
| gemini | Gemini CLI for one-shot Q&A, summaries, and generation. |
| gh-issues | Fetch GitHub issues, delegate fixes to subagents, open PRs. |
| gifgrep | Search GIF providers with CLI/TUI, download results, and extract stills. |
| github | Use gh for GitHub issues, PR status, CI/logs, comments, reviews, releases. |
| gog | Google Workspace CLI for Gmail, Calendar, Drive, Contacts, Sheets, and Docs. |
| goplaces | Query Google Places for text search, place details, and reviews. |
| healthcheck | Audit and harden hosts running OpenClaw. |
| himalaya | List, read, search, compose, reply, and organize IMAP/SMTP email. |
| imsg | iMessage/SMS CLI for listing chats, history, and sending messages. |
| mcporter | List, configure, authenticate, call, and inspect MCP servers/tools. |
| model-usage | Summarize CodexBar local cost logs by model. |
| nano-pdf | Edit PDFs with natural-language instructions. |
| node-connect | Diagnose OpenClaw Android, iOS, or macOS node pairing and connection failures. |
| notion | Notion API for creating and managing pages, databases, and blocks. |
| obsidian | Work with Obsidian vaults (plain Markdown notes). |
| obsidian-vault-maintainer | Maintain an Obsidian-friendly memory wiki vault. |
| openai-whisper | Local speech-to-text with the Whisper CLI (no API key). |
| openai-whisper-api | Transcribe audio via OpenAI Audio Transcriptions API. |
| openclaw-image-skill | Generate images via OpenAI DALL-E 3 API. |
| openhue | Control Philips Hue lights and scenes via the OpenHue CLI. |
| oracle | Bundle prompts and files for second-model debugging, refactor, or review. |
| ordercli | Foodora CLI for checking past orders and active order status. |
| peekaboo | Capture and automate macOS UI with the Peekaboo CLI. |
| qqbot-channel | QQ 频道管理 — channel list, sub-channels, members, posts, announcements. |
| qqbot-media | QQBot rich media send/receive with automatic type detection. |
| qqbot-remind | QQBot scheduled reminders — one-time and recurring. |
| sag | ElevenLabs text-to-speech with mac-style say UX. |
| session-logs | Search and analyze your own session logs using jq. |
| sherpa-onnx-tts | Local text-to-speech via sherpa-onnx (offline, no cloud). |
| skill-creator | Create, edit, improve, tidy, review, audit, or restructure SKILL.md files. |
| slack | React, pin/unpin, send, edit, delete Slack messages. |
| songsee | Generate spectrograms and feature-panel visualizations from audio. |
| sonoscli | Control Sonos speakers (discover/status/play/volume/group). |
| spotify-player | Terminal Spotify playback/search via spogo or spotify_player. |
| summarize | Summarize or transcribe URLs, YouTube/videos, podcasts, articles, PDFs, and local files. |
| taskflow | Coordinate multi-step detached tasks as one durable TaskFlow job. |
| taskflow-inbox-triage | TaskFlow pattern for inbox triage, intent routing, and waiting on replies. |
| things-mac | Add, update, list, search, or inspect Things 3 todos, projects, areas, and tags. |
| tmux | Remote-control tmux sessions for interactive CLIs. |
| trello | Manage Trello boards, lists, and cards via the Trello REST API. |
| video-frames | Extract frames or short clips from videos using ffmpeg. |
| voice-call | Start voice calls via the OpenClaw voice-call plugin. |
| wacli | Send WhatsApp messages or sync/search WhatsApp history via wacli. |
| weather | Get current weather, rain, temperature, and forecasts. |
| wiki-maintainer | Maintain the OpenClaw memory wiki vault with deterministic pages. |
| xurl | Authenticated X API posts, replies, search, DMs, media upload, and raw v2 calls. |

---

*Last updated: 2026-04-29*
