# Hermes Update: Autostash and Gateway Verification

Use this reference after `hermes update`, especially when the updater reports local changes or the gateway briefly errors after update.

## Verification sequence

```bash
hermes --version
hermes status --all || true
hermes doctor --fix || true
systemctl --user is-active hermes-gateway || true
systemctl --user status hermes-gateway --no-pager -n 40 || true
journalctl --user -u hermes-gateway --since '2 minutes ago' --no-pager | tail -80
```

## Local source changes

The updater may complete by resetting the working tree and preserving local source edits in a git stash.

Check:

```bash
cd /home/zeke/.hermes/hermes-agent
git status --short
git stash list | head -10
```

Report the stash ref. Do not apply the stash automatically unless the user explicitly asks; applying it can reintroduce old code or conflicts.

## Transient DB/schema errors

A transient gateway startup error can occur immediately after update if schema migration races with startup, for example a missing kanban column. Before changing code, verify whether the schema is already migrated and whether errors are still occurring.

Use the Hermes venv Python on this host because `/usr/bin/python` may be absent:

```bash
/home/zeke/.hermes/hermes-agent/venv/bin/python3 - <<'PY'
import sqlite3
from pathlib import Path
p = Path('/home/zeke/.hermes/kanban.db')
print(p, p.exists())
if p.exists():
    con = sqlite3.connect(p)
    for row in con.execute("PRAGMA table_info(tasks)"):
        print(row)
PY
```

Then check fresh journal output. If no new errors are present and the gateway is active, treat the error as transient.

## Restart approvals

If `systemctl --user restart hermes-gateway` is blocked or denied by the user's approval system, do not retry the same restart. Continue with non-restart diagnostics (`doctor`, status, journal, schema checks) and report the verified state.

## Example outcome

A successful update verified as:

```text
Hermes Agent v0.12.0 (2026.4.30)
hermes-gateway active/running
working tree clean
stash preserved: stash@{0}: On main: hermes-update-autostash-20260506-143956
```
