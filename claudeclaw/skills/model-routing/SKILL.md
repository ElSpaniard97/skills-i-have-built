---
name: model-routing
description: Select the right model (Opus, Sonnet, Haiku, or a specialist agent) before executing complex tasks. Produces a consistent routing decision with rationale before work begins.
version: 1.0.0
allowed-tools: Bash Read
---

# Model Routing

## Trigger
Use this skill before starting any complex, multi-step, or high-risk task where choosing the wrong model would waste tokens, produce lower-quality output, or create safety risk. Also use when the user asks "which model should handle this?" or when a task spans multiple capability domains.

## Required Inputs
- Task description: what needs to be done.
- Risk level: Low / Medium / High (default: assess from task description).
- Verification requirement: does output need to be checked by a second pass?
- Current model context: which model/agent is active.

## Routing Matrix

| Task Type | Primary Model | Rationale |
|-----------|--------------|-----------|
| Code generation, refactoring, debugging | **Sonnet** | Strong code capability; cost-efficient |
| Repository work (commits, PRs, CI fixes) | **Sonnet** | File-aware, tool-use optimized |
| Tests, CLI flows, shell scripting | **Sonnet** | Precise, literal, command-accurate |
| Long-form reasoning, planning, strategy | **Opus** | Extended context, nuanced judgment |
| Writing, documentation, summaries | **Sonnet** | Natural language quality, structure |
| Research synthesis, analysis | **Opus** | Multi-source reasoning |
| Architecture decisions | **Both** | Sonnet for implementation feasibility; Opus for tradeoffs and documentation |
| High-risk code changes (auth, infra, secrets) | **Both** | Sonnet proposes; Opus reviews for safety and logic |
| Security-sensitive reviews | **Both** | Sonnet for code-level evidence; Opus for risk assessment |
| Memory curation, skill writing | **Opus** | Judgment-heavy, prose-quality matters |
| Career artifacts, portfolio writing | **Opus** | Persuasive prose, narrative quality |
| Simple lookups, quick answers | **Haiku** | Fastest, cheapest for low-complexity tasks |
| Specialist agent tasks (comms/ops/research) | **Delegate** | Route to the appropriate ClaudeClaw agent |

## ClaudeClaw Agent Routing

| Agent | Route when... |
|-------|--------------|
| `comms` | Email, messaging, Discord/Telegram drafts, external communication |
| `content` | Writing, editing, publishing, scripts, post drafts |
| `ops` | Linux maintenance, deployments, service health, automation |
| `research` | Source-backed investigation, competitive analysis, deep dives |

## Procedure
1. **Parse the task**
   - Extract: task type, estimated complexity, output format required, risk level.
2. **Apply routing matrix**
   - Match task type to primary model using the matrix above.
   - If task spans two or more categories, check for dual-model or agent-delegation need.
3. **Apply risk override**
   - If risk is `High` or task touches secrets/auth/infra/memory: escalate to `Both` regardless of primary match.
   - If verification is required: add an Opus review pass after Sonnet execution.
4. **Check for agent delegation**
   - If the task clearly belongs to a specialist agent, route there instead of changing model.
5. **Output routing decision**
   - Return the decision in the standard format below before proceeding.

## Guardrails
- Do **not** silently switch models mid-task without surfacing the routing decision.
- Do **not** route security-sensitive or high-risk tasks to a single model without a review pass.
- Do **not** skip routing for tasks the user marks as "quick" if they touch auth, secrets, or production systems.
- Always show rationale — a routing decision without a reason is not useful.

## Output Format

```markdown
# Model Routing Decision
- Task:
- Risk Level: Low | Medium | High
- Verification Required: Yes | No

## Decision
- Primary Model: Opus | Sonnet | Haiku | Agent(<name>)
- Review Pass: None | Opus review after Sonnet
- Rationale:

## Task Breakdown (if multi-step)
| Step | Model / Agent | Reason |
|------|---------------|--------|

## Proceed?
Confirm to continue with this routing, or override below.
```

## Verification
A run passes only if:
- A primary model or agent is named with rationale.
- Risk level is assessed, not assumed.
- High-risk tasks have a dual-model or review-pass plan.
- The routing decision is surfaced before execution begins.

## Sample Prompt
"Route this task: refactor the auth middleware and document the changes in the README. What model(s) should handle this and in what order?"

## Notes
- For simple single-step tasks, routing overhead is not worth it — use this skill for complex, multi-step, or high-stakes work only.
- As model capabilities evolve, update this matrix when a newer model demonstrably outperforms the current routing assumption.
