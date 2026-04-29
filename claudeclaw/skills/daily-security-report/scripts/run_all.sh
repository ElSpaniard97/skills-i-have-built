#!/usr/bin/env bash
set -uo pipefail
SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REPORT_DIR="${CLAUDECLAW_SECURITY_REPORT_DIR:-/home/zeke/claudeclaw/store/security-reports}"
mkdir -p "$REPORT_DIR"
export SECURITY_REPORT_DIR="$REPORT_DIR"
bash "$SKILL_DIR/scripts/scan_system.sh" > /tmp/sec_system.json 2>/tmp/sec_system.err || echo '{"findings":[],"error":true}' > /tmp/sec_system.json
bash "$SKILL_DIR/scripts/scan_repos.sh"  > /tmp/sec_repos.json  2>/tmp/sec_repos.err  || echo '{"findings":[],"error":true}' > /tmp/sec_repos.json
bash "$SKILL_DIR/scripts/scan_infra.sh"  > /tmp/sec_infra.json  2>/tmp/sec_infra.err  || echo '{"findings":[],"error":true}' > /tmp/sec_infra.json
python3 "$SKILL_DIR/scripts/generate_report.py"
echo "DONE: $(date)"
