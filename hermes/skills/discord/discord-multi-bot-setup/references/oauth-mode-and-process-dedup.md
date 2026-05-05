# OAuth mode + duplicate-process remediation (May 2026)

Problem pattern:
- Bots reply with generic AI error despite service showing "running".
- Bots seem to require mention unexpectedly after a code change.

Root causes seen:
1) Provider API keys removed after switching Claude/Codex to OAuth, breaking direct SDK calls.
2) Multiple launcher/bot process sets running simultaneously, so old logic still responds.

Operational fixes:
1. Use OAuth-compatible path for AI calls (Hermes CLI fallback) or restore provider API keys.
2. Force single-process ownership before logic debugging:
   - stop service
   - kill all bot/launcher PIDs
   - start service cleanly
   - verify one PID per bot script

Verification commands:
- `systemctl --user status hermes-discord-bots.service --no-pager -l`
- `pgrep -af '/home/zeke/.hermes/discord-bots/(launcher.py|spartan_king.py|jenko.py|archer.py|achilles.py|epsn.py)'`
- `journalctl --user -u hermes-discord-bots.service -n 120 --no-pager`
