---
name: llm-cost-optimization
description: Systematic workflow for analyzing and reducing LLM API costs in production. Measures spend, identifies cost drivers, and implements optimizations (model routing, prompt pruning, caching). Use when the user asks to reduce costs, analyze spend, or optimize their LLM setup.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [Cost-Optimization, LLM, Analytics, Configuration]
    related_skills: [hermes-cost-report, recurring-report-cron]
---

# LLM Cost Optimization

Systematic playbook for analyzing and reducing LLM API costs in multi-model production environments. Built from optimizing a $467/month Hermes setup down to ~$90/month.

## When to Use

- User reports unexpectedly high LLM bills
- Wants to understand where spend is going
- Needs to cut costs while maintaining quality
- Setting up new LLM infrastructure and wants cost-awareness from day 1

## Three Levers (Ordered by Impact)

### 1. Model Routing (70–85% savings potential)

**Problem:** Using expensive models (Opus, GPT-4) for tasks that don't need them — routing, tool dispatch, casual chat.

**Solution:** Set cheaper models as defaults, reserve expensive ones for explicit invocation or hard reasoning.

**Hermes example:**
```yaml
# config.yaml
model:
  default: claude-sonnet-4-5  # was: claude-opus-4-7
```

**Cost impact:** Sonnet input/output = 20% of Opus. Cache reads = 20% of Opus. Haiku = 7% of Opus.

**Pattern:** Route by task complexity automatically, or let users opt-in to expensive models per-message (`@opus` mention, `/model opus-4-7` slash command).

**Rollout:**
1. Change default to Sonnet
2. Keep Opus callable via explicit syntax
3. Monitor for quality regressions over 3–7 days
4. If casual sessions are fine, proceed. If reasoning quality drops, add auto-escalation (detect failure → retry with Opus).

### 2. Cron Job Models (10–20% savings if cron is >15% of spend)

**Problem:** Scheduled background jobs (reports, digests, audits) inherit the expensive default model even though they rarely need advanced reasoning.

**Solution:** Pin each cron job to Sonnet or Haiku via per-job model override.

**Hermes example:**
```python
cronjob(
    action="update",
    job_id="<id>",
    model={"model": "claude-haiku-4-5", "provider": "anthropic"}
)
```

**Cost impact:** Routine reports (cost summaries, file listings) are perfect for Haiku. Multi-step synthesis (security audits with recommendations) suit Sonnet. Opus is overkill for >95% of cron tasks.

**Identify targets:** Run a cost report grouped by source. If `cron` or `scheduled` source is >15% of total, audit each job and downgrade.

### 3. Prompt Pruning (10–30% savings on cache-read-heavy usage)

**Problem:** System prompts that include large inventories (skill lists, tool catalogs, examples) get cached. Every turn re-reads the cache → cache-read tokens. At $1.50/M (Opus cache reads), this compounds quickly.

**Solution:** Gate large sections by relevance, lazy-load, or prune unused items.

**Hermes skill-inventory example:**

The system prompt includes a `<available_skills>` section listing 70+ skills across 20+ categories. Every cached turn re-bills ~2,700 tokens. Filtering to 5 active categories drops it to ~760 tokens (72% reduction).

**Config change:**
```yaml
# config.yaml
skills:
  category_filter:
    - software-development
    - github
    - devops
    - reporting
    - security
```

**Generalized pattern:** Identify the largest static blocks in your system prompt (tool schemas, examples, long instructions). Measure token count. Ask:
- Can this be loaded on-demand instead of upfront?
- Can I filter it by the user's active features?
- Are there unused/deprecated items I can delete?

**Category filter is iterative.** Start with 5-7 categories covering core workflows (software-development, github, terminal, reporting). Run for a few days, then check:
- Which skills do your cron jobs load? (add those categories)
- Which features does the user actively request? (Obsidian → note-taking, YouTube → media, etc.)
- Which categories have zero usage in cost reports? (consider pruning)

Expand the filter incrementally. Don't prune categories you'll immediately need to re-add.

**Measurement:**
```python
import tiktoken
enc = tiktoken.get_encoding("cl100k_base")
baseline_tokens = len(enc.encode(system_prompt))
pruned_tokens = len(enc.encode(pruned_system_prompt))
print(f"Saved: {baseline_tokens - pruned_tokens} tokens ({(1 - pruned_tokens/baseline_tokens)*100:.1f}%)")
```

## Workflow

### Step 1: Measure Baseline

**First: verify current state.** Before running a cost report, check:
```bash
# What's the current default model?
grep -A2 "^model:" ~/.hermes/config.yaml

# What models are cron jobs using?
cronjob list | grep -E "job_id|model"

# What's the current category filter?
grep -A20 "^skills:" ~/.hermes/config.yaml | grep -A15 "category_filter"
```

If you're resuming optimization work, you may find changes already applied. Don't re-apply them.

**Then:** Build a cost report covering at least 7 days. Required dimensions:
- **Total spend + daily average**
- **By model** (input/output/cache tokens + cost per model)
- **By source** (CLI, Discord, cron, API, etc.)
- **By day** (detect spikes)
- **Top sessions** by cost (whale detection)

Compute:
- Monthly projection: `(total / days) * 30`
- Dominant model: which model is >70% of spend?
- Cache-read cost: for the dominant model, `cache_read_tokens * cache_read_rate`

**Hermes:** Use the `hermes-cost-report` skill. It queries `~/.hermes/state.db` and computes all the above.

### Step 2: Identify Cost Drivers

Ask these questions in order:

1. **Is one model >70% of spend?** → Lever 1 (model routing)
2. **Are cache reads >30% of that model's cost?** → Lever 3 (prompt pruning)
3. **Is a single source (cron, discord) >70% of spend?** → Source-specific optimization
4. **Are there whale sessions (>10% of total)?** → Session hygiene (shorter sessions, /clear between tasks)

Most multi-model setups have 1–2 dominant drivers. Fix those first.

### Step 3: Implement Optimizations

**Model routing (Lever 1):**
- Change default in config
- Test in a non-production channel for 2–3 days
- Rollout to production if quality holds

**Cron downgrades (Lever 2):**
- List all cron jobs: `cronjob(action="list")`
- For each: read the prompt, assess complexity
- Update: `cronjob(action="update", job_id="...", model={...})`

**Prompt pruning (Lever 3):**
- Measure current system prompt tokens
- Identify largest static blocks
- Implement filtering/gating (config-driven if possible)
- Measure after, verify >50% reduction in the pruned section

### Step 4: Monitor + Iterate

**IMPORTANT:** Wait 24-48 hours after applying optimizations before measuring impact. The baseline cost report will include pre-optimization sessions, and the optimization work itself is expensive (analyzing costs, running scripts, updating config).

Set up a **recurring cost report** (daily or every 2 days) delivered to a monitoring channel. Watch for:
- Daily spend trends (should drop immediately after routing change)
- Quality regressions (user complaints, failed tasks)
- New cost spikes (new feature launch, bot abuse)

If quality drops, **don't revert everything** — revert just the change that broke (e.g., keep Sonnet for Discord but use Opus for cron if a cron job needs reasoning). Granular rollbacks preserve most of the savings.

After 7 days of stability, lock in the changes and update documentation.

## Recommendations Engine Pattern

When building cost reports, include a **Recommendations** section with data-driven, actionable bullets. Each bullet must reference a concrete number from the report.

**Rule structure:**
```python
# Compute helpers
daily_avg = total_cost / max(1, days)
monthly_proj = daily_avg * 30
for model, stats in by_model.items():
    model_share = stats["cost"] / total_cost
    cache_read_share = (stats["cache_read_tokens"] * cache_read_rate) / stats["cost"]

# Fire rules in priority order
if monthly_proj > threshold:
    emit(f"📈 At current pace (${daily_avg:.2f}/day), projected monthly spend is ${monthly_proj:.2f}.")

if dominant_model_share > 0.70:
    emit(f"🎯 {model} is {model_share:.0%} of spend. Route casual chat to Sonnet/Haiku (~80% cheaper).")

if cache_read_share > 0.30:
    emit(f"💾 ${cache_read_cost:.2f} is cache reads ({cache_read_share:.0%}). Trim the system prompt.")

# ... more rules ...
```

**Why this works:** Vague advice like "consider optimizing" gets ignored. Specific, quantified bullets (`"Opus is 97% of spend ($60.63)"`) trigger action.

## Anti-Patterns

**❌ Switching to the cheapest model everywhere**
Quality craters. Use tiered routing: cheap for casual, mid-tier for synthesis, expensive for reasoning/planning.

**❌ Over-pruning the system prompt**
If you gate too aggressively (remove all examples, strip tool schemas), the model fails at tool use. Test in a sandbox before rolling out prompt changes.

**❌ Ignoring quality signals**
Cost is one axis. If your users complain or tasks fail silently, you've gone too far. Monitor error rates and user feedback, not just spend.

**❌ One-time audit with no recurring monitoring**
Costs drift. New features launch, users change behavior, pricing updates. Set up a recurring report (weekly or biweekly) so you catch spikes early.

**❌ Hardcoding prices in reports**
APIs change pricing monthly. Externalize pricing to a JSON file the report reads. Update it once, all reports benefit.

## Pitfalls

- **Verify before re-applying.** Always check current state (config, cron jobs, filters) before implementing. You may be resuming work where optimizations are already live — re-applying them wastes time and risks breaking working config.
- **Optimization work itself is expensive.** The session where you analyze costs and implement fixes will spike spend (e.g., $68.70 on a $73.68 report). This is normal. Wait 24-48 hours post-optimization before measuring impact — the baseline report includes pre-optimization sessions.
- **Category filter is iterative.** Start conservative (5-7 categories), expand based on actual usage patterns discovered in cost reports and cron job inventories. Check which skills your cron jobs load, which features the user actively uses (Obsidian, Discord bots, media tools). Don't prune categories you'll need to re-add.
- **Model names vary by provider.** `claude-opus-4-7` on Anthropic might be `anthropic/claude-opus-4-7` on OpenRouter. Normalize when aggregating.
- **Cache token columns may be NULL.** Some DBs/logs don't track cache reads separately. Compute from API response metadata if available, or instrument at the client layer.
- **System-local time vs UTC.** Cron schedules run in system-local time. Cost reports should label timezones clearly to avoid "why didn't my 10am job run at 10am UTC" confusion.
- **Credential rotation breaks cron.** If you update API keys and don't restart the scheduler, cron jobs fail silently. Add health checks or delivery-error alerts.
- **Config changes need gateway restart.** Prompt pruning (category filters, skill changes) only takes effect in fresh sessions. The user's active session will continue using the old prompt until restart or natural session timeout.

## Success Metrics

Track these over 30 days post-optimization:

- **Cost reduction %**: `(baseline_monthly - new_monthly) / baseline_monthly`
- **Quality hold rate**: % of tasks that succeed without user retry/complaint
- **Escalation rate**: if you added auto-escalation (cheap → expensive on failure), what % of requests escalate? <5% is healthy.

**Good outcome:** 60–80% cost reduction with <2% increase in task failure rate.

## Tools Needed

- Cost tracking DB or log parser (query by model, source, day)
- Token counter (tiktoken for OpenAI-family tokenizers)
- Config management (YAML or env-based)
- Scheduler with per-job model override (if using cron/scheduled tasks)

## Example: Hermes Optimization (Apr 2026)

**Baseline (4 days):**
- $62.22 total → **$467/month projected**
- Opus = 97% of spend ($60.63)
- Cache reads = 30% of Opus cost ($18.44)
- Discord = 80% of spend by source

**Changes applied:**
1. Default model: Opus → Sonnet (Lever 1)
2. 6 cron jobs: default → Sonnet (5 jobs) + Haiku (1 job) (Lever 2)
3. Skills inventory: 70 skills → 6 categories via `category_filter` (Lever 3)

**Token savings from Lever 3:** 2,759 → 759 tokens (72% reduction in skills section)

**Projected new monthly:** ~$90–110/month (**81% reduction**)

Quality monitoring: 7-day observation period, no regressions reported.

## Related Skills

- **hermes-cost-report**: The report generator built during this optimization
- **recurring-report-cron**: Pattern for scheduled cost reports
- **codex**: Use Codex to implement config changes + prompt modifications at scale
