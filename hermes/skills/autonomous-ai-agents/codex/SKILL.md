---
name: codex
description: Delegate coding tasks to OpenAI Codex CLI agent. Use for building features, refactoring, PR reviews, and batch issue fixing. Requires the codex CLI and a git repository.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [Coding-Agent, Codex, OpenAI, Code-Review, Refactoring]
    related_skills: [claude-code, hermes-agent]
---

# Codex CLI

Delegate coding tasks to [Codex](https://github.com/openai/codex) via the Hermes terminal. Codex is OpenAI's autonomous coding agent CLI.

## Prerequisites

- Codex installed: `npm install -g @openai/codex`
- OpenAI API key configured
- **Must run inside a git repository** — Codex refuses to run outside one
- Use `pty=true` in terminal calls — Codex is an interactive terminal app

## One-Shot Tasks

```
terminal(command="codex exec 'Add dark mode toggle to settings'", workdir="~/project", pty=true)
```

For scratch work (Codex needs a git repo):
```
terminal(command="cd $(mktemp -d) && git init && codex exec 'Build a snake game in Python'", pty=true)
```

**Or use `--skip-git-repo-check` to bypass the requirement entirely** (useful when building a skill in a non-git directory like `~/.hermes/skills/...`):
```
codex exec --yolo --skip-git-repo-check "your prompt"
```

## Long Specs via File (recommended for multi-step builds)

For complex builds (multi-file skills, refactors with detailed requirements), write the spec to a file and pass via command substitution. Avoids shell-escape hell:

```
write_file("/tmp/spec.md", "# Detailed spec...\n...")
terminal(command='codex exec --yolo --skip-git-repo-check "$(cat /tmp/spec.md)"',
         workdir="~/path/to/project", background=true, pty=true, notify_on_complete=true)
```

**Or skip the git check entirely** with `--skip-git-repo-check` — useful when you've created a fresh target dir (e.g. a new skill directory) and don't need version control:
```
terminal(command="codex exec --yolo --skip-git-repo-check 'your prompt'", workdir="~/path/to/dir", pty=true)
```

## Background Mode (Long Tasks)

```
# Start in background with PTY
terminal(command="codex exec --full-auto 'Refactor the auth module'", workdir="~/project", background=true, pty=true)
# Returns session_id

# Monitor progress
process(action="poll", session_id="<id>")
process(action="log", session_id="<id>")
```

**⚠️ Output buffering caveat:** If you wrap the codex command with shell pipes like `| tail -200` or `| head`, the entire stdout buffers until codex exits — `process(action='log')` will show empty output mid-run even though codex is working. **Workarounds:**
1. Don't pipe — run codex directly so PTY output streams to the process buffer
2. Check the workdir directly (`ls`, `search_files`) to see files being created in real time
3. Use `notify_on_complete=true` and just wait for the completion notification

# Send input if Codex asks a question
process(action="submit", session_id="<id>", data="yes")

# Kill if needed
process(action="kill", session_id="<id>")
```

## Key Flags

| Flag | Effect |
|------|--------|
| `exec "prompt"` | One-shot execution, exits when done |
| `--full-auto` | Sandboxed but auto-approves file changes in workspace |
| `--yolo` | No sandbox, no approvals (fastest, most dangerous) |

## PR Reviews

Clone to a temp directory for safe review:

```
terminal(command="REVIEW=$(mktemp -d) && git clone https://github.com/user/repo.git $REVIEW && cd $REVIEW && gh pr checkout 42 && codex review --base origin/main", pty=true)
```

## Parallel Issue Fixing with Worktrees

```
# Create worktrees
terminal(command="git worktree add -b fix/issue-78 /tmp/issue-78 main", workdir="~/project")
terminal(command="git worktree add -b fix/issue-99 /tmp/issue-99 main", workdir="~/project")

# Launch Codex in each
terminal(command="codex --yolo exec 'Fix issue #78: <description>. Commit when done.'", workdir="/tmp/issue-78", background=true, pty=true)
terminal(command="codex --yolo exec 'Fix issue #99: <description>. Commit when done.'", workdir="/tmp/issue-99", background=true, pty=true)

# Monitor
process(action="list")

# After completion, push and create PRs
terminal(command="cd /tmp/issue-78 && git push -u origin fix/issue-78")
terminal(command="gh pr create --repo user/repo --head fix/issue-78 --title 'fix: ...' --body '...'")

# Cleanup
terminal(command="git worktree remove /tmp/issue-78", workdir="~/project")
```

## Batch PR Reviews

```
# Fetch all PR refs
terminal(command="git fetch origin '+refs/pull/*/head:refs/remotes/origin/pr/*'", workdir="~/project")

# Review multiple PRs in parallel
terminal(command="codex exec 'Review PR #86. git diff origin/main...origin/pr/86'", workdir="~/project", background=true, pty=true)
terminal(command="codex exec 'Review PR #87. git diff origin/main...origin/pr/87'", workdir="~/project", background=true, pty=true)

# Post results
terminal(command="gh pr comment 86 --body '<review>'", workdir="~/project")
```

## Sandbox Failures → Use `--yolo`

`--full-auto` uses bubblewrap (`bwrap`) for sandboxing. On some hosts (containers, restricted Linux environments) bwrap fails with errors like:

```
bwrap: loopback: Failed RTM_NEWADDR: Operation not permitted
```

When this happens Codex cannot write any files — even `apply_patch` to `/tmp` fails — and the run exits "successfully" having done nothing. **Symptom:** the Codex output ends with messages about being "blocked by the execution environment" and probe writes failing.

**Fix:** retry the same command with `--yolo` instead of `--full-auto`. `--yolo` skips the sandbox entirely.

```
# If --full-auto fails with bwrap errors:
codex exec --yolo "your prompt"
```

Trade-off: `--yolo` has no sandbox, so only use it on hosts you trust and on tasks scoped to a known directory.

## Rules

1. **Always use `pty=true`** — Codex is an interactive terminal app and hangs without a PTY
2. **Git repo required** — Codex won't run outside a git directory. Use `mktemp -d && git init` for scratch
3. **Use `exec` for one-shots** — `codex exec "prompt"` runs and exits cleanly
4. **`--full-auto` for building** — auto-approves changes within the sandbox; fall back to `--yolo` if sandbox is unavailable (see above)
5. **Background for long tasks** — use `background=true` and monitor with `process` tool
6. **Don't interfere** — monitor with `poll`/`log`, be patient with long-running tasks
7. **Parallel is fine** — run multiple Codex processes at once for batch work
8. **Pass long specs via file** — for complex prompts, write the spec to `/tmp/spec.md` and invoke as `codex exec --yolo "$(cat /tmp/spec.md)"` to avoid shell-escaping issues
