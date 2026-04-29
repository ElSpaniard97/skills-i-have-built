---
name: interactive-sudo-via-chat
description: Run sudo commands on behalf of the user when only the user knows the password and you're operating from chat (Discord, Telegram, etc.). Forward the password from the user through a PTY to sudo without triggering shell-cache or heredoc pitfalls.
version: 1.0.0
author: Hermes Agent
---

# Interactive Sudo via Chat

When the user approves running sudo commands but the host requires a password, and the user explicitly asks you to execute (Option B-style: "you run it, I'll provide password"), use this exact pattern. Naive approaches fail in non-obvious ways.

## When to use

- User says "run it for me" / "you do it" / explicitly approves password forwarding
- The agent has shell access but no passwordless sudo
- Single multi-command hardening/install/config block

## When NOT to use

- One-off command — just ask the user to run it themselves
- User hasn't explicitly consented to sending password through chat (always warn that the platform retains messages)
- Long-running interactive tools that need ongoing sudo prompts (use scoped NOPASSWD sudoers entry instead)

## The pattern that works

Write the entire sudo-block to a script file, then feed the password via a temp file with `sudo -S`:

```python
# 1. Write the work script (uses sudo -n inside; the outer sudo -S authenticates once)
write_file("/tmp/work.sh", """#!/bin/bash
set +e
sudo -n ufw enable
sudo -n systemctl enable --now fail2ban
# ... etc
""")

# 2. Ask user for password in chat (explicitly warn about retention)
# 3. When they reply, run:
terminal(command='''cat > /tmp/sp <<'PWEOF'
USER_PASSWORD_HERE
PWEOF
chmod 600 /tmp/sp
sudo -S -p '' bash /tmp/work.sh < /tmp/sp 2>&1
shred -u /tmp/sp 2>/dev/null || rm -f /tmp/sp
echo DONE''',
    background=True,
    notify_on_complete=True,
    timeout=600)
```

**Why this works:**
- `sudo -S` reads password from stdin (not the terminal)
- `-p ''` suppresses the `[sudo] password for user:` prompt so it doesn't appear in output
- The first `sudo -S` call inside the script authenticates and refreshes the timestamp; subsequent `sudo -n` calls in the same process tree use the cached credential
- Heredoc with `'PWEOF'` (quoted) prevents shell expansion of `$` in passwords
- `shred -u` overwrites + deletes the password file immediately after
- Background + `notify_on_complete` lets long apt installs run without blocking

## Pitfalls — patterns that DO NOT work

### ❌ `sudo -S bash <<EOF`
Sudo eats the entire heredoc as the password. You'll get "Sorry, try again" three times then sudo lockout.

### ❌ Separate `sudo -v` then `sudo <cmd>` in two `terminal()` calls
Sudo's credential cache is per-TTY (specifically per-tty pgrp). Each `terminal()` call gets a fresh shell with a fresh tty, so the cache from call 1 isn't visible in call 2.

```python
# THIS DOES NOT WORK:
terminal("sudo -v", pty=True)  # caches in shell A
# ... user submits password ...
terminal("sudo apt-get update")  # shell B — cache miss, "password required"
```

### ❌ `echo "$PW" | sudo -S cmd` without `-p ''`
The `[sudo] password for user:` prompt leaks into stdout, polluting parsing.

### ❌ Inlining the password in the command string
Shows up in process lists (`ps aux`), shell history, and log retention.

### ❌ Using PTY mode and `process.submit()` for multiple sudo calls
Works for one prompt but the cache still doesn't survive across separate `terminal()` invocations. Useful only if the entire sudo workflow runs in a single command.

## Password handling checklist

Before forwarding a password through chat, in this order:

1. **Warn the user** that the platform (Discord/Telegram/Slack) retains the message
2. **Suggest alternatives first:**
   - Run it themselves (one paste, 30 seconds)
   - Set up scoped `NOPASSWD` sudoers entry for specific binaries
3. **If they insist:** proceed with the pattern above
4. **After completion:** remind them to delete the password message from the chat history
5. **Never echo the password back** in any tool output, summary, or confirmation

## Scoped NOPASSWD sudoers (better long-term solution)

For agents that regularly need sudo, propose this instead of repeated password forwarding:

```
# /etc/sudoers.d/agent-tools (visudo this — DO NOT edit directly)
USERNAME ALL=(ALL) NOPASSWD: /usr/sbin/ufw, /usr/bin/systemctl, /usr/bin/apt-get, /usr/bin/tailscale, /usr/bin/install
```

Limits blast radius to just those binaries. Still risky if any of them have shell-out paths (`apt-get` can run package post-install scripts as root), but much better than full NOPASSWD or repeated chat password forwarding.

## Verification

After running the sudo block, always:
1. Check `exit_code` of the parent terminal call
2. Look for `sudo: a password is required` in output (means the cache broke mid-run)
3. Confirm the password file was deleted: `ls /tmp/sp` should fail
4. Re-run the relevant scan/check to verify changes took effect
