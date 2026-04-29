---
name: model-routing
description: Select the right model (Codex, Claude, or both) before executing complex tasks. Produces a consistent routing decision with rationale before work begins.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [model-routing, codex, claude, orchestration, operations, planning]
    category: operations
    related_skills: [skill-quality-auditor, mission-control-report]
---

# Model Routing

## Trigger
Use this skill before starting any complex, multi-step, or high-risk task where choosing the wrong model would waste tokens, produce lower-quality output, or create safety risk. Also use when the user asks "which model should handle this?" or when a task spans multiple capability domains.

## Required Inputs
- Task description: what needs to be done.
- Risk level: Low / Medium / High (default: assess from task description).
- Verification requirement: does output need to be checked by a second pass?
- Current model context: which model is active (check `~/.hermes/config.yaml` `model.default`).

## Routing Matrix

| Task Type | Primary Model | Rationale |
|-----------|--------------|-----------|
| Code generation, refactoring, debugging | **Codex** | Optimized for code; faster, lower cost on code tasks |
| Repository work (commits, PRs, CI fixes) | **Codex** | File-aware, tool-use optimized |
| Tests, CLI flows, shell scripting | **Codex** | Precise, literal, command-accurate |
| Long-form reasoning, planning, strategy | **Claude** | Extended context, nuanced judgment |
| Writing, documentation, summaries | **Claude** | Natural language quality, structure |
| Research synthesis, analysis | **Claude** | Multi-source reasoning |
| Architecture decisions | **Both** | Codex for implementation feasibility; Claude for tradeoffs and documentation |
| High-risk code changes (auth, infra, secrets) | **Both** | Codex proposes; Claude reviews for safety and logic |
| Security-sensitive reviews | **Both** | Codex for code-level evidence; Claude for risk assessment |
| Memory curation, skill writing | **Claude** | Judgment-heavy, prose-quality matters |
| Cron/automation scripting | **Codex** | Exact syntax, idempotency checks |
| Career artifacts, portfolio writing | **Claude** | Persuasive prose, narrative quality |

## Procedure
1. **Parse the task**
   - Extract: task type, estimated complexity, output format required, risk level.
2. **Apply routing matrix**
   - Match task type to primary model using the matrix above.
   - If task spans two or more categories, check for dual-model need.
3. **Apply risk override**
   - If risk is `High` or task touches secrets/auth/infra/memory: escalate to `Both` regardless of primary match.
   - If verification is required: add a Claude review pass after Codex execution.
4. **Check current model**
   - If the active model already matches the routing decision, no switch needed — note it.
   - If a switch is needed, propose the switch command and await confirmation.
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
- Primary Model: Codex | Claude
- Review Pass: None | Claude review after Codex
- Rationale:

## Task Breakdown (if multi-step)
| Step | Model | Reason |
|------|-------|--------|
| 1.   |       |        |
| 2.   |       |        |

## Current Model
- Active: <model from config>
- Switch Required: Yes | No
- Switch Command (if needed): `hermes config set model.default <model>`

## Proceed?
Confirm to continue with this routing, or override below.
```

## Verification
A run passes only if:
- A primary model is named with rationale.
- Risk level is assessed, not assumed.
- High-risk tasks have a dual-model or review-pass plan.
- The routing decision is surfaced before execution begins.

## Sample Prompt
"Route this task: refactor the auth middleware in hermes-mission-control and document the changes in the README. What model(s) should handle this and in what order?"

## Notes
- Codex (`gpt-5.3-codex` / `gpt-5.1-codex-mini`) refers to the OpenAI Codex models configured in `~/.hermes/config.yaml`.
- Claude (`claude-sonnet-4-5` or later) refers to the Anthropic fallback configured in `fallback_providers`.
- As model capabilities converge, prefer recency: update this matrix when a new model demonstrably outperforms the current routing assumption.
- For simple single-step tasks, routing overhead is not worth it — use this skill for complex, multi-step, or high-stakes work only.
