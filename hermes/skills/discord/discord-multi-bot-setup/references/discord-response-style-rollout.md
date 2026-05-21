# Discord Bot Response Style Rollout

Session learning: the user corrected bot output quality after EPSN/Harvey produced verbose, poorly structured Discord replies. For this fleet, response style is part of bot quality, not cosmetic.

## User-approved Discord response standard

For substantive Discord responses, bots should use:

```text
## [Task or Document Name]
**Status:** [status]  
**Date:** [YYYY-MM-DD]  
**Prepared by:** [Bot Name]
**Source:** [file name or context, if relevant]

---

### Summary
[Brief 2-4 sentence summary]

---

### Key Points
- [Point 1]
- [Point 2]
- [Point 3]

---

### Open Items
- [Item 1]
- [Item 2]
- [Item 3]

---

### Important Note
[Brief legal, security, financial, or operational caution if needed]

---

### Recommended Next Step
[One clear next action]
```

## Global style rules

- Start with a short title.
- Use markdown headings and short sections.
- Use bullets instead of long paragraphs.
- Keep legal/security/ops warnings brief but visible.
- Always include `### Recommended Next Step` for substantive replies.
- Avoid raw diffs, patches, stack traces, huge copied text blocks, long legal clauses, or technical file metadata unless explicitly requested.
- Only output raw diffs when the user asks for `diff`, `patch`, or `show exact changes`.
- In Discord, prefer filenames over full local paths unless a full path is necessary.
- Emojis are optional and should be sparse.

## EPSN MSA/legal-document format

EPSN should use this structure for MSA, contract, SOP, and business-document work:

```text
## AnchorLink Tech MSA Review
**Status:** Internal Working Draft  
**Date:** [YYYY-MM-DD]  
**Prepared by:** EPSN, Operations  
**Source:** [file name only]

---

### What Changed
[2-4 sentence explanation]

---

### Main Revision Areas
- **Business Details:** ...
- **Legal Terms:** ...
- **Security & Privacy:** ...
- **Payments & Suspension:** ...
- **Third-Party Services:** ...
- **Compliance:** ...

---

### Open Items Before Final Review
- ...

---

### Legal / Ops Control
This is an internal working draft only. It is not legal advice, not final approval, and should not be sent for signature until reviewed by Harvey/legal counsel.

---

### Recommended Next Step
[One clear next action]
```

## Implementation pattern used

Prefer a shared prompt/config change over editing every bot's response logic:

1. Update `/home/zeke/.hermes/discord-bots/bot_config.py`.
2. Put fleet-wide style in `RESPONSE_RULES`.
3. Put role-specific guidance in a `ROLE_RESPONSE_STYLES` map.
4. Append role style in `get_system_prompt(bot_name)` after global rules.
5. Compile all bot files.
6. Restart `hermes-discord-bots.service` only after approval.
7. Verify process start times are newer than the modified config file.

## Verification commands

```bash
python3 -m py_compile /home/zeke/.hermes/discord-bots/*.py
python3 - <<'PY'
import sys
sys.path.insert(0, '/home/zeke/.hermes/discord-bots')
from bot_config import get_system_prompt
for name in ['EPSN','Harvey','Spartan King','Togi']:
    p=get_system_prompt(name)
    print(name, 'has_recommended_next_step', 'Recommended Next Step' in p, 'has_role_style', 'Role-Specific Discord Response Style' in p)
print('epsn_has_msa_template', 'AnchorLink Tech MSA Review' in get_system_prompt('EPSN'))
PY
systemctl --user restart hermes-discord-bots.service
sleep 14
systemctl --user is-active hermes-discord-bots.service
journalctl --user -u hermes-discord-bots.service --since '90 seconds ago' --no-pager | grep -E 'online as|ERROR|Traceback'
```

## Pitfall

Do not hardcode brittle output post-processing unless prompt-only style rules fail. Shared prompt rules preserve natural responses and reduce maintenance across 10 bots.
