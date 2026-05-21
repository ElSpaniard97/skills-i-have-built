# Syncing installed skills into a GitHub backup repository

Use this when asked to update a repo that backs up the current installed skills catalog.

## Workflow

1. Locate the backup repo and source skill directory.
   - Common Hermes source: `~/.hermes/skills`
   - Common backup repo in this environment: `/home/zeke/skills-i-have-built`
2. Hard-reset the local backup checkout to the remote branch before syncing if the user requested a full refresh and there is no intentional local work.
3. Replace the destination skills tree with a filtered copy of the source tree.
4. Exclude generated/runtime files:
   - `.git`, `.hg`, `.svn`
   - `__pycache__`, `*.pyc`, `.pytest_cache`, `.mypy_cache`, `.ruff_cache`
   - `.venv`, `venv`, `node_modules`
   - `.last_message_id`, `.usage.json`, `.usage.json.lock`, `.curator_state`
   - local hidden runtime directories such as `.hub` and `.curator_backups`
5. Regenerate README/index counts from discovered `SKILL.md` files rather than hard-coding counts.
6. Scan the copied tree before commit for obvious secrets/token examples.
   - Discord bot token shape: `part1.part2.part3`
   - GitHub tokens: `ghp_`, `gho_`, `ghu_`, `ghs_`, `ghr_`, `github_pat_`
   - OpenAI-style keys: `sk-...`
7. Redact token-looking strings in the source skill if they are documentation examples, then re-sync so future backups stay clean.
8. Commit and push only after verification.
9. Verify local HEAD equals remote HEAD and the worktree is clean.

## Pitfalls

- Do not commit caches or Python bytecode from skill script directories.
- Do not trust placeholder tokens just because they look fake; if they match a live token regex, redact them to `REDACTED_*` before publishing.
- Generic `git diff` or security tools may be blocked in some environments. If so, use a small Python verification script for file counts, excluded-artifact checks, and token-shape scans.
- If the user says `my-skills-i-built`, check for close repo names such as `skills-i-have-built` before assuming the repo is missing.

## Verification snippet

```bash
cd /path/to/backup-repo
python3 - <<'PY'
from pathlib import Path
import re, subprocess
base = Path('hermes/skills')
print('skill_count', sum(1 for _ in base.rglob('SKILL.md')))
print('excluded_artifacts', sum(1 for p in base.rglob('*') if p.name == '__pycache__' or p.suffix == '.pyc' or p.name in {'.last_message_id','.usage.json','.curator_state'}))
patterns = [
    re.compile(r'\b[A-Za-z0-9_-]{23,28}\.[A-Za-z0-9_-]{6,7}\.[A-Za-z0-9_-]{27,}\b'),
    re.compile(r'\b(?:gh[pousr]_[A-Za-z0-9_]{30,}|github_pat_[A-Za-z0-9_]{50,})\b'),
    re.compile(r'\bsk-(?!x{10,}\b)[A-Za-z0-9]{30,}\b'),
]
hits=[]
for p in base.rglob('*'):
    if not p.is_file() or p.stat().st_size > 2_000_000:
        continue
    text = p.read_text(errors='ignore')
    if any(pat.search(text) for pat in patterns):
        hits.append(str(p))
print('potential_secret_hits', len(hits))
for h in hits[:20]: print(h)
print('status_lines', len(subprocess.check_output(['git','status','--short'], text=True).splitlines()))
PY
```
