#!/usr/bin/env bash
set -uo pipefail
SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
mkdir -p ~/.hermes/security-reports
bash "$SKILL_DIR/scripts/scan_system.sh" > /tmp/sec_system.json 2>/tmp/sec_system.err || echo '{"findings":[],"error":true}' > /tmp/sec_system.json
bash "$SKILL_DIR/scripts/scan_repos.sh"  > /tmp/sec_repos.json  2>/tmp/sec_repos.err  || echo '{"findings":[],"error":true}' > /tmp/sec_repos.json
bash "$SKILL_DIR/scripts/scan_infra.sh"  > /tmp/sec_infra.json  2>/tmp/sec_infra.err  || echo '{"findings":[],"error":true}' > /tmp/sec_infra.json
python3 "$SKILL_DIR/scripts/generate_report.py"
python3 "$SKILL_DIR/scripts/post_to_discord.py" || true
echo "DONE: $(date)"
