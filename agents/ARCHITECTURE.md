# Agent Architecture - Key Decisions

> This document explains WHY we built things the way we did.
> Read this before making architectural changes.

---

## Core Design Decision: MCP vs Direct Code

### The Question

We had two options for building the autonomous content system:

1. **MCP Server** - Model Context Protocol server that exposes primitives as tools
2. **Direct Code** - Python modules that call Claude API directly

### The Decision: Direct Code for Autonomy, MCP for Manual

We chose **direct Python + Claude API** for the autonomous pipeline, keeping MCP as an optional CLI tool.

### Why?

| Factor | MCP | Direct Code |
|--------|-----|-------------|
| **Use case** | Interactive Claude Code sessions | Scheduled autonomous execution |
| **Protocol overhead** | HTTP/stdio transport, JSON-RPC | None - just function calls |
| **Debugging** | Tool call traces in MCP inspector | Standard Python debugging |
| **Deployment** | Need MCP-compatible client | Just run Python |
| **Complexity** | Higher (protocol, schemas, transport) | Lower (plain Python) |

**MCP is designed for interactive use** - when a human is using Claude Code and wants Claude to call your tools. The protocol handles things like:
- Tool discovery
- Permission prompts
- Streaming responses

**Autonomous cron jobs don't need this**. The agent runs on a schedule, makes its own decisions, and logs results. There's no interactive session.

### What We Built

```
agents/
├── pipeline/           # Direct code - autonomous execution
│   ├── orchestrator.py # Main entry point for cron
│   ├── runner.py       # Per-resort pipeline logic
│   └── decision_maker.py # Claude API for smart decisions
│
├── mcp_server/         # MCP server - optional CLI tool
│   └── server.py       # 55 tools for manual intervention
│
└── shared/primitives/  # Atomic functions used by both
```

### When to Use Each

**Use Direct Pipeline (pipeline/):**
- Daily automated content generation
- Scheduled refreshes
- Any autonomous operation

**Use MCP Server (mcp_server/):**
- Manual intervention ("generate content for this specific resort")
- Debugging ("what does the queue look like?")
- One-off operations via Claude Code

---

## Decision Maker Pattern

### The Problem

Autonomous agents need to make decisions:
- Which resorts to research today?
- Should we publish this content?
- How should we handle this error?

Hardcoding rules is brittle. "If confidence > 0.8, publish" doesn't account for nuance.

### The Solution: Ask Claude

We use Claude API calls for intelligent decisions:

```python
# decision_maker.py

def pick_resorts_to_research(max_resorts: int = 4) -> dict:
    """Ask Claude to pick resorts based on current context."""
    context = generate_context()  # What exists, what's stale, budget

    response = client.messages.create(
        model="claude-sonnet-4-20250514",  # Fast, cheaper
        messages=[{"role": "user", "content": prompt_with_context}],
    )

    return parse_response(response)
```

### Why This Works

1. **Context injection**: We tell Claude what exists, what's needed, and what budget remains
2. **Reasoning capture**: Claude explains its choices, creating an audit trail
3. **Flexibility**: Changing priorities = changing the prompt, not the code
4. **Quality**: Claude understands nuance (value skiing angle, geographic diversity)

### The Three Decision Points

| Decision | Threshold Logic | Claude Involvement |
|----------|-----------------|-------------------|
| **Resort selection** | None | Always asks Claude |
| **Publication** | >0.8 = auto-publish, <0.6 = auto-reject | 0.6-0.8 asks Claude |
| **Error handling** | None | Always asks Claude |

---

## Confidence Scoring

### The Formula

```python
def calculate_confidence(research_data: dict) -> float:
    score = 0.0

    # Source count (max 0.3)
    sources = research_data.get("sources", [])
    score += min(len(sources) / 10, 0.3)

    # Official data present (0.2)
    if research_data.get("official_site_data"):
        score += 0.2

    # Price data completeness (max 0.2)
    costs = research_data.get("costs", {})
    price_fields = ["lift_adult_daily", "lodging_budget_nightly", "lodging_mid_nightly"]
    price_completeness = sum(1 for f in price_fields if costs.get(f)) / len(price_fields)
    score += price_completeness * 0.2

    # Family metrics completeness (max 0.15)
    metrics = research_data.get("family_metrics", {})
    metric_fields = ["family_overall_score", "childcare_min_age", "ski_school_min_age"]
    metric_completeness = sum(1 for f in metric_fields if metrics.get(f)) / len(metric_fields)
    score += metric_completeness * 0.15

    # Review data (max 0.15)
    reviews = research_data.get("reviews", [])
    if len(reviews) >= 5:
        score += 0.15
    elif len(reviews) >= 2:
        score += 0.08

    return min(score, 1.0)
```

### Why These Weights?

| Component | Weight | Rationale |
|-----------|--------|-----------|
| Sources | 0.30 | More sources = more confident in facts |
| Official data | 0.20 | Official site is authoritative |
| Price data | 0.20 | Users need accurate pricing |
| Family metrics | 0.15 | Core value proposition |
| Reviews | 0.15 | Social proof matters |

### Publication Thresholds

| Confidence | Action | Rationale |
|------------|--------|-----------|
| >= 0.8 | Auto-publish | High quality, ship it |
| 0.6 - 0.8 | Ask Claude | Borderline, need judgment |
| < 0.6 | Auto-reject | Too risky, needs human review |

---

## Two-Layer Architecture

### Layer 1: Atomic Primitives

```
shared/primitives/
├── research.py     # Exa, SerpAPI, Tavily
├── content.py      # Claude content generation
├── database.py     # Resort CRUD operations
├── publishing.py   # Publication lifecycle
└── system.py       # Queue, cost tracking, audit
```

**Characteristics:**
- Single responsibility
- No business logic
- Reusable across contexts
- Easy to test in isolation

### Layer 2: Pipeline (Orchestration)

```
pipeline/
├── orchestrator.py  # Daily pipeline coordination
├── runner.py        # Per-resort execution flow
└── decision_maker.py # Intelligent decisions
```

**Characteristics:**
- Composes primitives
- Contains business logic
- Handles errors and retries
- Logs all reasoning

### Why Two Layers?

**Primitives are building blocks.** They don't know about:
- The daily pipeline
- Publication workflows
- Budget constraints

**Pipeline is the brain.** It knows:
- What to do (decision maker)
- How to do it (runner)
- When to stop (budget checks)

This separation lets us:
- Test primitives independently
- Change business logic without changing APIs
- Reuse primitives in different contexts (MCP, CLI, etc.)

---

## Budget Controls

### Configuration

```python
# shared/config.py
class Settings(BaseSettings):
    daily_budget_limit: float = 5.00  # $5/day default
```

### Enforcement Points

1. **Before pipeline starts**: Check if budget allows any work
2. **Before each resort**: Check if budget allows one more (~$1.50)
3. **After each API call**: Log the cost for tracking

### Cost Estimates

| Operation | Est. Cost |
|-----------|-----------|
| Research (3 APIs) | $0.20 |
| Content generation (Claude) | $0.80 |
| Decision calls (Sonnet) | $0.05 |
| **Total per resort** | ~$1.05-1.50 |

### Budget Exhaustion Behavior

When budget is exhausted:
1. Stop processing more resorts
2. Log the stoppage reason
3. Return digest with what was completed
4. Next day, budget resets

---

## Audit Trail

### Every Decision is Logged

```python
log_reasoning(
    task_id=task_id,
    agent_name="decision_maker",
    action="pick_resorts",
    reasoning="Selected Zermatt for geographic diversity and value angle",
    metadata={"resorts": [...], "context_summary": "..."},
)
```

### What's Captured

| Field | Purpose |
|-------|---------|
| task_id | Links all entries for one task |
| agent_name | Which module made the decision |
| action | What happened |
| reasoning | Why it happened (human-readable) |
| metadata | Structured data for analysis |

### Why This Matters

1. **Debugging**: "Why did we publish that incomplete page?" → Check the audit log
2. **Learning**: "What types of errors are most common?" → Query the log
3. **Trust**: "Can we prove this was an autonomous decision?" → Yes, it's all logged
4. **Iteration**: "How can we improve decision quality?" → Review reasoning patterns

---

## Error Handling Strategy

### The Decision Tree

```
Error occurs
    │
    ▼
Is it a rate limit? ─────────────▶ Retry after delay
    │ no
    ▼
Is it "no data found"? ──────────▶ Skip this resort
    │ no
    ▼
Is it a database error? ─────────▶ Alert human
    │ no
    ▼
Is it content generation? ───────▶ Retry once, then skip
    │ no
    ▼
Unknown error ───────────────────▶ Skip and log
```

### Implementation

We don't hardcode this tree. Instead, we ask Claude:

```python
def handle_error(error, resort_name, stage, task_id) -> dict:
    """Ask Claude how to handle an error."""
    prompt = f"""
    Error: {error}
    Stage: {stage}
    Resort: {resort_name}

    What should we do: retry, skip, or alert_human?
    """
    # Claude reasons about the best action
```

This lets us handle novel errors without code changes.

---

## Autonomy Levels

### Our Journey

| Level | Human Involvement | Where We Are |
|-------|-------------------|--------------|
| Level 1 | Human reviews all | Past this |
| **Level 2** | 20-30% review (low confidence only) | **Starting here** |
| Level 3 | <10% review (emergencies only) | Goal |
| Level 4 | 0% review (fully autonomous) | Future |

### Level 2 Safeguards

- Confidence < 0.6 → Human review required
- Budget caps with daily limits
- Full audit trail
- No destructive operations without confirmation

### Graduating to Level 3

Requirements:
- 100+ successful auto-publishes
- <5% post-publish corrections
- Proven error recovery patterns
- Discovery agent operational

---

## File Organization Rationale

```
agents/
├── shared/              # Reusable across all agents
│   ├── config.py        # Centralized configuration
│   ├── supabase_client.py
│   ├── voice_profiles.py
│   └── primitives/      # Atomic building blocks
│
├── pipeline/            # Autonomous execution
│   ├── __init__.py      # Public interface
│   ├── orchestrator.py  # Entry point
│   ├── runner.py        # Execution logic
│   └── decision_maker.py # Intelligence
│
├── mcp_server/          # Interactive CLI tool
│   ├── __init__.py
│   ├── server.py        # 55 MCP tools
│   └── README.md
│
├── research_resort/     # IACP agent (optional)
├── generate_guide/      # IACP agent (optional)
├── optimize_for_geo/    # IACP agent (optional)
│
├── requirements.txt
├── ARCHITECTURE.md      # This file
└── run.py               # Agent runner
```

**Note:** The IACP agents (research_resort/, generate_guide/, optimize_for_geo/) are from an earlier iteration. The pipeline/ approach is simpler and preferred for autonomous operation. Keep the IACP agents for reference or future microservices architecture.

---

## Future Considerations

### Discovery Agent

We don't have a discovery agent yet. Currently, Claude picks from:
- Manual suggestions in prompts
- Stale content needing refresh
- General resort knowledge

Future discovery agent would:
- Monitor search trends (Google Trends API)
- Track competitor coverage
- Find content gaps
- Prioritize based on demand signals

### Multi-Model Strategy

Currently using:
- `claude-sonnet-4-20250514` for decisions (fast, cheap)
- `claude-opus-4-5-20251101` for content (quality)

Could add:
- Haiku for simple validations
- Different models for different content types

### Horizontal Scaling

Current design: Sequential processing, one resort at a time.

For scale:
- Queue-based architecture
- Multiple workers
- Regional distribution
- But: Budget controls become more complex

---

## Questions to Ask Before Changing Architecture

1. **Does this need to be autonomous?** If it's a one-off, use MCP server instead.
2. **Does this need Claude's judgment?** If rules are clear, hardcode them.
3. **Can this fail silently?** If not, add explicit error handling.
4. **Will this affect budget?** Log all API costs.
5. **Can we audit this later?** Log all decisions with reasoning.
