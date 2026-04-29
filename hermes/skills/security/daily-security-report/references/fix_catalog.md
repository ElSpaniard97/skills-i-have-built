# Fix Catalog

This skill emits each finding with a specific `fix_description`, `fix_command`, `requires_sudo`, and `auto_applicable` field.

General rules:

- Sudo fixes are never run automatically.
- Non-sudo fixes may be applied with `apply_fix.py` after explicit approval.
- Commands are intentionally explicit so they can be reviewed before use.

Common fixes:

- Listening port exposed: stop, disable, or bind the service to localhost.
- Upgradable packages: run apt update and upgrade manually.
- Kernel or Debian CVEs: install fixed packages, then reboot if the kernel changed.
- SSH password/root login: update `/etc/ssh/sshd_config` and reload SSH.
- World-writable system file: remove world-write permission after confirming ownership.
- Missing unattended upgrades: enable `unattended-upgrades`.
- Repository secret: rotate the secret, remove it from git history, and force-push only after coordination.
- Dependency CVE: upgrade the affected package to a fixed version.
- SAST issue: inspect the reported file and apply the recommended code change.
- Weak SSH key: remove or replace the key with an ed25519 key or RSA key with at least 3072 bits.
- Firewall open/default accept: enable UFW or add explicit allow rules before denying inbound traffic.
