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

| Decision | Mechanism | Rationale |
|----------|-----------|-----------|
| **Resort selection** | Claude picks from context | Flexibility, reasoning captured |
| **Publication** | Three-agent approval panel | Diverse perspectives, quality gate |
| **Error handling** | Claude determines action | Handle novel errors gracefully |

---

## Three-Agent Approval Panel

### The Problem with Confidence Thresholds

We previously used a formula-based confidence score (0.0-1.0) to decide publication:
- ≥0.8 → Auto-publish
- 0.6-0.8 → Ask Claude
- <0.6 → Save as draft

**Issues with this approach:**
1. Single-dimensional - one number can't capture content quality
2. Arbitrary thresholds - why 0.8? why not 0.75?
3. No diverse perspectives - misses voice/completeness/accuracy tradeoffs
4. No self-improvement loop - content that fails just fails

### The Solution: Three-Agent Approval Panel

We replaced confidence thresholds with a **three-agent approval panel** that:
- Provides diverse perspectives aligned with our mission
- Uses **2/3 majority vote** for publication
- **Iterates until approved** (up to 3 attempts)
- **Improves content** based on feedback each iteration
- Follows Agent Native principles (GRANULARITY, COMPOSABILITY)

### The Three Agents

Each agent represents a key family need aligned with our mission:

> **Mission**: Help overwhelmed families discover that international skiing is achievable and affordable

| Agent | Perspective | Key Question | Protects Against |
|-------|-------------|--------------|------------------|
| **TrustGuard** | Accuracy | "Can families trust this?" | Misinformation, outdated prices, false claims |
| **FamilyValue** | Completeness | "Can families use this to plan?" | Vague content, missing info, unusable guides |
| **VoiceCoach** | Tone | "Does this encourage, not intimidate?" | Corporate tone, jargon, overwhelming content |

### Agent 1: TrustGuard

**Mission**: Protect families from misinformation. They're making expensive trip decisions.

**Evaluates:**
- Source verification - Are facts backed by provided sources?
- Price realism - Are costs realistic for this region/tier?
- Consistency - Do metrics match narrative? Trail percentages add up?
- Red flags - Outdated info? Claims without evidence?

### Agent 2: FamilyValue

**Mission**: Ensure families can actually PLAN A TRIP from this guide.

**Evaluates:**
- Completeness - All 10 required sections present and substantive?
- Specificity - Named hotels, actual prices, specific restaurants?
- Mobile-friendliness - Short paragraphs, scannable, tables not too wide?
- GEO optimization - Tables for data, FAQs with natural questions?

**Required Sections:**
1. quick_take - BLUF verdict with "Perfect if/Skip if"
2. family_metrics - Table with actual scores
3. getting_there - Airports, transfers, times
4. where_to_stay - 3 tiers with NAMED properties
5. lift_tickets - ACTUAL prices + pass info
6. on_mountain - Terrain breakdown, ski school with ages
7. off_mountain - NAMED restaurants, activities
8. ski_calendar - Monthly table
9. faqs - 5-8 natural questions

### Agent 3: VoiceCoach

**Mission**: Make families feel "YOU CAN DO THIS."

**Evaluates:**
- Warmth - Sounds like a trusted friend, not a brochure?
- Jargon - Technical terms explained? Not assuming expert knowledge?
- Brand alignment - SPIELPLATZ feel (playful, warm)?
- Conversational openers allowed sparingly (max 1 per page) when earned with substance

**Voice Profile**: `snowthere_guide` (expert but warm, Wirecutter meets travel publication)

### Approval Flow

```
Content Generated
       │
       ▼
┌──────────────────────────────────────────────┐
│         APPROVAL PANEL (Parallel)             │
│                                              │
│   ┌──────────┐ ┌──────────┐ ┌──────────┐    │
│   │TrustGuard│ │FamilyVal │ │VoiceCoach│    │
│   │ Agent    │ │ Agent    │ │ Agent    │    │
│   └────┬─────┘ └────┬─────┘ └────┬─────┘    │
│        │            │            │           │
│        ▼            ▼            ▼           │
│   [APPROVE]    [IMPROVE]    [APPROVE]        │
│                                              │
│   VOTE: 2 approve, 1 improve                 │
│   THRESHOLD: 2/3 majority                    │
│   RESULT: ✅ APPROVED                        │
└──────────────────────────────────────────────┘
       │
       │ 2/3 approved → PUBLISH
       │
       │ <2/3 approved → ITERATE (up to 3x)
       │
       ├── Combine issues from all agents
       ├── Apply improvements via Claude
       ├── Re-run approval panel
       └── Max 3 iterations → DRAFT if still <2/3
```

### Implementation

**File:** `agents/shared/primitives/approval.py`

```python
# Atomic evaluation primitives
async def evaluate_trust(content, sources, resort_data) -> EvaluationResult
async def evaluate_completeness(content, resort_data) -> EvaluationResult
async def evaluate_voice(content, voice_profile) -> EvaluationResult

# Orchestration (runs all 3 in parallel)
async def run_approval_panel(content, sources, resort_data, voice_profile) -> PanelResult

# Content improvement
async def improve_content(content, issues, suggestions) -> dict

# Full approval loop
async def approval_loop(content, sources, resort_data, voice_profile, max_iterations=3) -> ApprovalLoopResult
```

**Data Structures:**

```python
@dataclass
class EvaluationResult:
    agent_name: str       # "TrustGuard", "FamilyValue", "VoiceCoach"
    verdict: str          # "approve", "improve", "reject"
    confidence: float     # 0.0-1.0
    issues: list[str]     # Specific problems found
    suggestions: list[str] # How to fix
    reasoning: str        # Overall assessment

@dataclass
class PanelResult:
    votes: list[EvaluationResult]
    approved: bool        # 2/3 majority
    approve_count: int
    improve_count: int
    reject_count: int
    combined_issues: list[str]
    combined_suggestions: list[str]

@dataclass
class ApprovalLoopResult:
    final_content: dict
    approved: bool
    iterations: int
    panel_history: list[PanelResult]
    final_issues: list[str]  # If not approved, why
```

### Cost Estimation

Each panel run ≈ $0.15-0.20 (3 Claude calls)
- TrustGuard: ~$0.05 (shorter context)
- FamilyValue: ~$0.07 (checklist evaluation)
- VoiceCoach: ~$0.05 (voice analysis)

With max 3 iterations: $0.45-0.60 per resort (worst case)
Still within $1.50/resort budget.

### Edge Cases

| Scenario | Outcome |
|----------|---------|
| **Unanimous approve** (3/3) | Publish immediately |
| **2/3 approve** | Publish (meets threshold) |
| **1/3 approve, 2 improve** | Iterate with combined feedback |
| **0/3 approve, 3 improve** | Iterate with combined feedback |
| **Any reject** | Iterate (reject = strong improve signal) |
| **3 iterations, still <2/3** | Save as draft with agent notes |

### Agent Prompt Templates

Located in `agents/prompts/`:
- `trustguard.md` - TrustGuard system prompt and user prompt template
- `familyvalue.md` - FamilyValue system prompt and user prompt template
- `voicecoach.md` - VoiceCoach system prompt and user prompt template

---

## Research Confidence Score (Still Used)

We still calculate a confidence score from research quality. This is used for:
- Logging and observability
- Memory context (learning from past runs)
- Potential fallback if approval panel fails

The formula remains unchanged, but it no longer gates publication directly.

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
    # Family metrics completeness (max 0.15)
    # Review data (max 0.15)

    return min(score, 1.0)
```

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
| Approval panel (3 agents × 1-3 iterations) | $0.15-0.60 |
| Content improvement (if needed) | $0.10-0.30 |
| Decision calls (Sonnet) | $0.05 |
| **Total per resort** | ~$1.30-1.95 |

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
| Level 2 | 20-30% review (low confidence only) | Past this |
| **Level 3** | <10% review (panel rejections only) | **Current** |
| Level 4 | 0% review (fully autonomous) | Goal |

### Level 3 Safeguards (Current)

- **Three-agent approval panel** - diverse perspectives before publication
- **2/3 majority required** - no single point of failure
- **Iterative improvement** - content improves until approved
- **Draft on rejection** - human review only for truly problematic content
- Budget caps with daily limits
- Full audit trail with agent reasoning
- No destructive operations without confirmation

### Why Approval Panel Enables Higher Autonomy

The approval panel provides **built-in quality gates** that were previously manual:

| Old Approach | New Approach |
|--------------|--------------|
| Human reviews all < 0.8 confidence | Panel reviews all, human only sees rejects |
| Single dimension (confidence score) | Three dimensions (trust, completeness, voice) |
| Content fails → stays draft | Content fails → improves → tries again |
| ~30% human involvement | ~5-10% human involvement |

### Graduating to Level 4

Requirements:
- 100+ successful panel approvals
- <5% post-publish corrections
- Panel agreement rate >80%
- First-pass approval rate >60%
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
│       ├── approval.py  # ⭐ Three-agent approval panel
│       ├── research.py
│       ├── content.py
│       ├── database.py
│       ├── publishing.py
│       ├── system.py
│       └── ...          # 63+ primitives total
│
├── prompts/             # ⭐ Agent prompt templates
│   ├── trustguard.md    # TrustGuard agent prompt
│   ├── familyvalue.md   # FamilyValue agent prompt
│   └── voicecoach.md    # VoiceCoach agent prompt
│
├── pipeline/            # Autonomous execution
│   ├── __init__.py      # Public interface
│   ├── orchestrator.py  # Entry point
│   ├── runner.py        # Execution logic (uses approval panel)
│   └── decision_maker.py # Intelligence
│
├── agent_layer/         # Agent infrastructure
│   ├── base.py          # BaseAgent with think→act→observe
│   ├── memory.py        # 3-tier memory system
│   └── ...
│
├── mcp_server/          # Interactive CLI tool
│   ├── server.py        # 55 MCP tools
│   └── README.md
│
├── research_resort/     # IACP agent (reference only)
├── generate_guide/      # IACP agent (reference only)
├── optimize_for_geo/    # IACP agent (reference only)
│
├── cron.py              # Railway entry point
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
