# Isolated Hermes Home OAuth Pitfall

Use this reference when a Discord fleet bot is online but replies with a generic Hermes CLI failure, especially after adding new bot homes.

## Symptom

Discord reply or logs show:

```text
<Bot>: hermes exit code 1
No Codex credentials stored. Run `hermes auth` to authenticate.
```

The standalone bot process may be healthy. The failure occurs inside the per-message Hermes subprocess.

## Root cause

The bot integration runs Hermes with an isolated home such as:

```bash
HERMES_HOME=/home/zeke/.hermes/discord-homes/<bot>
```

That isolated home has its own config/memory/skills, but Codex OAuth credentials live in the main Hermes home:

```text
/home/zeke/.hermes/auth.json
```

If the isolated home lacks `auth.json`, Hermes CLI OAuth fallback cannot authenticate even though the main CLI works.

## Reproduce

Run the exact provider/model smoke test with the bot's isolated home:

```bash
HERMES_HOME=/home/zeke/.hermes/discord-homes/<bot> \
  hermes chat -Q -q 'Reply with exactly OK' \
  --provider openai-codex -m gpt-5.5
```

A missing-credentials failure confirms the issue.

## Fix

Prefer a symlink to avoid token drift:

```bash
ln -s /home/zeke/.hermes/auth.json /home/zeke/.hermes/discord-homes/<bot>/auth.json
```

If a non-symlink `auth.json` already exists, move it to a timestamped backup before replacing it. Never print the contents.

## Verification

1. Re-run the isolated-home Hermes smoke test for each affected bot; expect exactly `OK`.
2. Run fleet status:
   ```bash
   /home/zeke/.hermes/hermes-agent/venv/bin/python3 /home/zeke/.hermes/discord-bots/status.py
   ```
3. No Discord bot service restart is required for this specific credential-file fix because each Discord message spawns a fresh Hermes subprocess that sees the file immediately.

## Session note

This fixed newly added `hector`, `troy`, `hellen`, `togi`, and `harvey` bot homes by linking each home's `auth.json` to the main Hermes auth file. Credential contents are secrets and must remain redacted.
