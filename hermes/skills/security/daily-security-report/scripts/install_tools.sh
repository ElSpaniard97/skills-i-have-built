#!/usr/bin/env bash
set -euo pipefail

need_cmd() {
  command -v "$1" >/dev/null 2>&1
}

ensure_apt() {
  local pkg="$1"
  if ! dpkg -s "$pkg" >/dev/null 2>&1; then
    sudo apt-get install -y "$pkg"
  fi
}

sudo apt-get update
ensure_apt jq
ensure_apt debsecan
ensure_apt fail2ban
ensure_apt ufw
ensure_apt unattended-upgrades
ensure_apt curl
ensure_apt tar
ensure_apt ca-certificates
ensure_apt python3-pip
ensure_apt pipx

python3 -m pipx ensurepath || true
export PATH="$HOME/.local/bin:$PATH"

if ! need_cmd pip-audit; then
  pipx install pip-audit
fi

if ! need_cmd semgrep; then
  pipx install semgrep
fi

if ! need_cmd gitleaks; then
  tmp="$(mktemp -d)"
  trap 'rm -rf "$tmp"' EXIT
  arch="$(uname -m)"
  case "$arch" in
    x86_64|amd64) asset_arch="x64" ;;
    aarch64|arm64) asset_arch="arm64" ;;
    *) echo "Unsupported arch for gitleaks: $arch"; exit 1 ;;
  esac
  url="$(curl -fsSL https://api.github.com/repos/gitleaks/gitleaks/releases/latest | jq -r --arg arch "$asset_arch" '.assets[] | select(.name|test("linux_" + $arch + "\\.tar\\.gz$")) | .browser_download_url' | head -1)"
  curl -fsSL "$url" -o "$tmp/gitleaks.tar.gz"
  tar -xzf "$tmp/gitleaks.tar.gz" -C "$tmp" gitleaks
  sudo install -m 0755 "$tmp/gitleaks" /usr/local/bin/gitleaks
fi

if ! need_cmd osv-scanner; then
  tmp="$(mktemp -d)"
  trap 'rm -rf "$tmp"' EXIT
  arch="$(uname -m)"
  case "$arch" in
    x86_64|amd64) asset_arch="amd64" ;;
    aarch64|arm64) asset_arch="arm64" ;;
    *) echo "Unsupported arch for osv-scanner: $arch"; exit 1 ;;
  esac
  url="$(curl -fsSL https://api.github.com/repos/google/osv-scanner/releases/latest | jq -r --arg arch "$asset_arch" '.assets[] | select(.name|test("linux_" + $arch + "$")) | .browser_download_url' | head -1)"
  curl -fsSL "$url" -o "$tmp/osv-scanner"
  sudo install -m 0755 "$tmp/osv-scanner" /usr/local/bin/osv-scanner
fi

echo "Security report tools installed or already present."
