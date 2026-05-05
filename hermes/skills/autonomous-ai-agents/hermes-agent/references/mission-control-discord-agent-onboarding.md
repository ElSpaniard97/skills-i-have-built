# Mission Control + Discord agent onboarding when channel telemetry is unavailable

Use this when Mission Control UI shows "No gateway detected" or `/api/channels` returns `connected:false`, but `hermes gateway status` is running.

## Fast diagnostic

1. Gateway service health:
   - `systemctl --user status hermes-gateway.service --no-pager`
   - `hermes gateway status`
2. Mission Control channels API:
   - `curl -sS -H 'x-api-key: <MC_API_KEY>' http://127.0.0.1:3001/api/channels`
3. Hermes CLI capability check:
   - `hermes --help` (verify whether `channels` exists)
4. Optional gateway port probe:
   - `curl -sS http://127.0.0.1:18789/health`

If gateway is up but `/api/channels` stays disconnected and `hermes channels` is absent, classify as Hermes/MC feature mismatch.

## Operational workaround (keeps MC useful)

Register each Discord bot as a Mission Control agent and send heartbeats.

Create agent:
`curl -sS -X POST http://127.0.0.1:3001/api/agents -H 'x-api-key: <MC_API_KEY>' -H 'Content-Type: application/json' -d '{"name":"archer","role":"discord-bot","source":"manual","config":{"platform":"discord","service":"hermes-discord-bots.service"}}'`

Heartbeat:
`curl -sS -X POST http://127.0.0.1:3001/api/agents/<ID>/heartbeat -H 'x-api-key: <MC_API_KEY>' -H 'Content-Type: application/json' -d '{"status":"idle","activity":"Discord bot process running"}'`

Repeat for all bots (Spartan-King, Archer, Achilles, EPSN, Jenko).

## Verify bot runtime independently

- `python3 /home/zeke/.hermes/discord-bots/status.py`
- `systemctl --user status hermes-discord-bots.service --no-pager`
- `journalctl --user -u hermes-discord-bots.service -n 120 --no-pager`

## OAuth-only bridge recipe (no API key)

Use this when operators require OAuth/session auth only and do not want `API_KEY`-based automation.

1. Create a local sync script that:
   - reads bot process liveness via `pgrep -af '/home/zeke/.hermes/discord-bots/(...)'`
   - reads latest guild counts from `journalctl --user -u hermes-discord-bots.service`
   - updates Mission Control SQLite directly at `<MC_INSTALL_DIR>/.data/mission-control.db` (`agents` table: `status`, `last_seen`, `last_activity`, JSON `config` fields)
2. Install a user-level systemd oneshot + timer (every 60s).
3. Verify with:
   - `systemctl --user status <sync>.timer --no-pager`
   - `journalctl --user -u <sync>.service -n 30 --no-pager`
   - SQL spot-check: `SELECT name,status,last_activity FROM agents WHERE name IN (...)`
4. Optional hardening: clear `API_KEY=` in Mission Control `.env` and restart `mission-control.service` if you want to enforce non-keyed operations for this bridge path.

## Notes

- This workaround restores agent visibility/status in Mission Control, not full Discord channel analytics.
- OAuth-only variant (no `x-api-key`): write bot liveness directly into Mission Control SQLite (`.data/mission-control.db`) from a local script + systemd timer. This avoids API-key auth entirely for the bridge while keeping Agent Squad status current.
- When Hermes/MC versions are aligned later, re-test `/api/channels` and remove any temporary heartbeat glue jobs if no longer needed.
