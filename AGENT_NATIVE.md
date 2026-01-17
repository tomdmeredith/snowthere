# Agent Native Principles - Snowthere

> This document codifies the Agent Native principles for the Snowthere project.
> Reference: https://every.to/guides/agent-native
> Last Updated: 2026-01-16
> **Parity Status: ✅ FULL PARITY ACHIEVED** - All 50+ atomic primitives implemented

## TL;DR

Snowthere should be built so that **any action a human editor can take, an agent can achieve through tools**. Features are **outcomes described in prompts**, not code. When we want to add a new content type (ski pass comparison, regional itinerary), we write a **new prompt**, not new code.

**The Ultimate Test:** Describe an outcome to the agent that's within Snowthere's domain but that we didn't build a specific feature for. Can it figure out how to accomplish it, operating in a loop until it succeeds?

---

## The Five Principles

### 1. PARITY

> Whatever a user can do through the UI, the agent should be able to achieve through tools.

**For Snowthere:**
- If a human editor can create resort content → agent must be able to
- If a human can update prices → agent must be able to
- If a human can publish/unpublish/archive → agent must be able to
- If a human can add ski passes → agent must be able to
- If a human can view what exists → agent must be able to

**The Test:** Pick any action an editor could take in our CMS. Can our agents achieve it?

**The Discipline:** When adding any UI/editorial capability, ask: Can the agent achieve this outcome? If not, add the necessary tools or primitives.

### 2. GRANULARITY

> Tools should be atomic primitives. Features are outcomes achieved by an agent operating in a loop.

**For Snowthere:**
- A tool is: `exa_search`, `write_section`, `update_resort`, `publish_page`
- A feature is: "Create a complete family guide for Park City" (prompt + loop)
- To change behavior: edit the prompt, not refactor code

**The Test:** To add a "ski pass comparison" feature, do we edit prompts or write new agent code?

**Correct Answer:** We write a new prompt that describes the outcome. The agent uses existing tools (`search_passes`, `read_resort`, `write_section`, `generate_table`) in a loop until the comparison is complete.

### 3. COMPOSABILITY

> With atomic tools and parity, you can create new features just by writing new prompts.

**For Snowthere:**
```
# New feature: Regional Itinerary
# This is a PROMPT, not code

"Create a 7-day family ski itinerary for the Dolomites region.
Research the top 5 family-friendly resorts in the area.
For each resort, gather: family score, costs, best terrain for kids.
Create a day-by-day plan that starts easy and progresses.
Include logistics (drive times, recommended order).
Generate in instagram_mom voice.
Optimize for GEO with tables and FAQs."
```

The agent uses existing tools: `search_resorts`, `read_resort`, `write_section`, `generate_table`, `generate_faq`, `apply_voice`.

**The Constraint:** This only works if tools are atomic enough to be composed in ways we didn't anticipate.

### 4. EMERGENT CAPABILITY

> The agent can accomplish things you didn't explicitly design for.

**For Snowthere:**
- "Which Austrian resorts have free kids programs?" → Agent searches, filters, compiles
- "Compare Zermatt vs Park City for a family of 5" → Agent researches both, builds comparison
- "What's the most budget-friendly Ikon resort for toddlers?" → Agent reasons across data
- "Find resorts trending in search demand we haven't covered" → Agent analyzes gaps

**The Flywheel:**
1. Build with atomic tools + parity
2. Users/orchestrator ask for unanticipated things
3. Agent composes tools to accomplish them (or fails, revealing a gap)
4. Observe patterns in what's being requested
5. Add domain tools or prompts to make common patterns efficient
6. Repeat

**The Test:** Can Snowthere handle open-ended requests in the family ski domain?

### 5. IMPROVEMENT OVER TIME

> Agent-native applications get better through accumulated context and prompt refinement.

**For Snowthere:**

| Mechanism | Implementation |
|-----------|----------------|
| **Accumulated Context** | `context.md` file with what exists, recent activity, guidelines |
| **Developer Refinement** | Update voice profiles, section templates, research strategies |
| **Pattern Learning** | Log what's requested, optimize common patterns |

---

## Capability Map

Every action a human editor can take must be achievable by the agent.

| User/Editor Action | Agent Capability | Current Status |
|--------------------|------------------|----------------|
| **Resorts** | | |
| View all resorts | `list_resorts` | ✅ Have |
| Create resort entry | `create_resort` | ✅ Have |
| Read resort details | `get_resort` / `get_resort_by_slug` | ✅ Have |
| Update resort content | `update_resort_content` | ✅ Have |
| Delete resort | `delete_resort` | ✅ Have |
| Search/filter resorts | `search_resorts` | ✅ Have |
| Get full resort data | `get_resort_full` | ✅ Have |
| **Publishing** | | |
| Publish resort | `publish_resort` | ✅ Have |
| Unpublish resort | `unpublish_resort` | ✅ Have |
| Archive resort | `archive_resort` | ✅ Have |
| Restore archived | `restore_resort` | ✅ Have |
| Trigger page revalidation | `revalidate_page` / `revalidate_resort_page` | ✅ Have |
| Get stale resorts | `get_stale_resorts` | ✅ Have |
| **Costs** | | |
| Get resort costs | `get_resort_costs` | ✅ Have |
| Update lift ticket prices | `update_resort_costs` | ✅ Have |
| Update lodging prices | `update_resort_costs` | ✅ Have |
| **Family Metrics** | | |
| Get family metrics | `get_resort_family_metrics` | ✅ Have |
| Update family metrics | `update_resort_family_metrics` | ✅ Have |
| **Ski Passes** | | |
| List ski passes | `list_ski_passes` | ✅ Have |
| Get ski pass | `get_ski_pass` | ✅ Have |
| Get resort's passes | `get_resort_passes` | ✅ Have |
| Add pass to resort | `add_resort_pass` | ✅ Have |
| Remove pass from resort | `remove_resort_pass` | ✅ Have |
| **Ski Calendar** | | |
| Get resort calendar | `get_resort_calendar` | ✅ Have |
| Update calendar month | `update_resort_calendar` | ✅ Have |
| **Content Queue** | | |
| View queue | `list_queue` | ✅ Have |
| Get queue stats | `get_queue_stats` | ✅ Have |
| Add to queue | `queue_task` | ✅ Have |
| Get next task | `get_next_task` | ✅ Have |
| Update task status | `update_task_status` | ✅ Have |
| Clear completed | `clear_completed_tasks` | ✅ Have |
| **Research** | | |
| Search web (semantic) | `exa_search` | ✅ Have |
| Search Google | `serp_search` | ✅ Have |
| Web research | `tavily_search` | ✅ Have |
| Scrape URL | `scrape_url` | ✅ Have |
| Combined search | `search_resort_info` | ✅ Have |
| **Content Generation** | | |
| Write section | `write_section` | ✅ Have |
| Generate FAQs | `generate_faq` | ✅ Have |
| Apply voice profile | `apply_voice` | ✅ Have |
| Generate SEO meta | `generate_seo_meta` | ✅ Have |
| **System** | | |
| Log cost | `log_cost` | ✅ Have |
| Get daily spend | `get_daily_spend` | ✅ Have |
| Check budget | `check_budget` | ✅ Have |
| Get cost breakdown | `get_cost_breakdown` | ✅ Have |
| Log reasoning | `log_reasoning` | ✅ Have |
| View audit log | `read_audit_log` | ✅ Have |
| Get task audit trail | `get_task_audit_trail` | ✅ Have |
| Get recent activity | `get_recent_activity` | ✅ Have |

**Status: FULL PARITY ACHIEVED** - All CRUD and publishing tools are now available.

---

## Context System

The agent needs persistent context across sessions. Implement the `context.md` pattern:

```markdown
# Snowthere Agent Context

## Who I Am
Content generation system for Snowthere.com family ski resort guides.
I research resorts, generate family-focused content in instagram_mom voice,
and optimize for GEO (AI citation).

## What Exists
- Resorts: 47 published, 12 draft, 3 flagged for review
- Ski Passes: 23 (Epic, Ikon, regional)
- Countries covered: 15
- Queue: 4 resorts pending

## Recent Activity
- [2026-01-16] Generated Park City guide (confidence: 0.82)
- [2026-01-15] Updated Zermatt prices from official source
- [2026-01-14] Discovered 5 new resorts from search demand analysis
- [2026-01-14] St. Anton flagged - childcare info conflicting

## My Guidelines
- Voice: instagram_mom (see voice_profiles.py)
- Minimum confidence for auto-publish: 0.7
- Flag for human review: confidence < 0.6 or conflicting sources
- Always cite sources, prefer official resort sites
- Daily budget cap: $5.00 USD

## Current State
- Daily spend: $3.50 of $5.00
- Active tasks: 1 (researching Whistler)
- Blocked: 0
- Last sync: 10 minutes ago

## Priorities
1. Complete pending queue items
2. Refresh resorts > 30 days old
3. Research high-demand search terms
4. Fill content gaps (missing European resorts)
```

**Implementation:** Store as file, inject into system prompt, update after each session.

---

## Prompt Templates (Not Code)

New content types should be prompts, not new agents.

### Resort Guide Prompt
```
Research {resort_name} in {country} for a family ski guide.

Focus areas: family-friendliness, costs, logistics, terrain for kids.

Gather:
- Basic info (elevation, terrain breakdown, lifts)
- Family metrics (childcare, ski school ages, kids-free policies)
- Current prices (lift tickets, lodging ranges)
- Parent reviews and sentiment
- Getting there (airports, transfers)

Generate sections using instagram_mom voice:
- quick_take (BLUF with verdict)
- getting_there
- where_to_stay
- lift_tickets
- on_mountain
- off_mountain
- parent_reviews_summary

Generate 6 FAQs families would ask.
Generate SEO meta (title 50-60 chars, description 150-160 chars).
Optimize for GEO with tables for metrics, costs, calendar.

Confidence threshold: 0.7 for auto-publish.
Log sources and reasoning throughout.
```

### Ski Pass Comparison Prompt
```
Create a comparison guide for {pass_name} from a family perspective.

Research:
- Which resorts are included
- Which are best for families (cross-reference family scores)
- Pricing tiers and family bundles
- Blackout dates during school holidays
- Kids-free policies at each resort

Generate in practical_mom voice (budget-focused).
Include comparison tables (GEO-optimized).
Calculate "value score" for families of 4.
```

### Regional Itinerary Prompt
```
Create a {duration}-day family ski itinerary for {region}.

Research top {n} family-friendly resorts in the region.
Consider: proximity, terrain progression, cost balance.

Build day-by-day plan:
- Start with easier resorts for warm-up
- Progress to more challenging terrain
- Include rest day recommendations
- Add logistics (drive times, recommended stops)

Generate in excited_mom voice (inspirational).
Include packing checklist and budget breakdown.
```

**Key Insight:** These are prompts that an orchestrating agent executes using atomic tools. To add a new content type, write a new prompt—don't write new agent code.

---

## Anti-Patterns to Avoid

### 1. Agent as Router
❌ Agent figures out what user wants, then calls the right function.
✓ Agent pursues outcome in a loop with judgment.

### 2. Workflow-Shaped Tools
❌ `analyze_and_generate_resort_guide(resort_name)` - bundles judgment
✓ Atomic tools + prompt describing outcome

### 3. Build App Then Add Agent
❌ Build features as code, then expose to agent
✓ Build capabilities, features emerge from prompts

### 4. Defensive Over-Constraint
❌ Restrict what agent can do "just in case"
✓ Default to open; use approval flows for destructive actions

### 5. Orphan UI Actions
❌ User can do something in UI that agent can't achieve
✓ Maintain parity; update capability map with every UI change

### 6. Context Starvation
❌ Agent doesn't know what exists or what's been done
✓ Inject context.md into every session

### 7. Heuristic Completion Detection
❌ Detect completion by checking output files or iteration count
✓ Require explicit completion signal from agent

---

## Success Criteria Checklist

Use this checklist for every PR and feature:

### Architecture
- [ ] Agent can achieve anything users can through UI (PARITY)
- [ ] Tools are atomic primitives (GRANULARITY)
- [ ] New features can be added by writing prompts (COMPOSABILITY)
- [ ] Agent can accomplish unanticipated tasks (EMERGENT)
- [ ] Changing behavior = editing prompts, not code

### Implementation
- [ ] System prompt includes context (what exists, capabilities)
- [ ] Agent and editor work in same data space
- [ ] Agent actions visible in UI/logs immediately
- [ ] Every entity has full CRUD capability
- [ ] Agents explicitly signal completion

### Product
- [ ] Simple requests work immediately
- [ ] Power users can push in unexpected directions
- [ ] We learn from what agent is asked to do
- [ ] Approval requirements match stakes and reversibility

---

## Architecture Evolution

### Current (Week 2): Workflow Agents
```
research_resort → generate_guide → optimize_for_geo
```
These are workflow executors. They work, but they're not fully agent-native.

### Target: Capability Agents
```
ORCHESTRATING AGENT (Claude Code / Scheduler)
    │
    ├── research_tools (exa, serp, tavily, scrape)
    ├── content_tools (write_section, generate_faq, apply_voice)
    ├── database_tools (CRUD for resorts, passes, queue)
    ├── publishing_tools (publish, unpublish, revalidate)
    └── system_tools (log, budget, queue)
```

The orchestrator uses **prompts** to achieve outcomes. Current agents become **optimized paths** for common operations, but primitives remain available.

### Migration Path
1. ✅ Build primitives (research, content, system)
2. ✅ Build workflow agents (research_resort, generate_guide, optimize_for_geo)
3. ✅ Add missing CRUD/publishing primitives
4. 🔲 Expose all primitives as MCP tools
5. 🔲 Implement context.md system
6. 🔲 Create prompt templates for content types
7. 🔲 Orchestrator uses primitives directly for novel requests
8. 🔲 Workflow agents become optimized shortcuts

---

## Files to Maintain

| File | Purpose | Update Frequency |
|------|---------|------------------|
| `AGENT_NATIVE.md` | This document - principles and architecture | On architectural changes |
| `agents/context.md` | Persistent agent context | Every session |
| `agents/prompts/*.md` | Prompt templates for content types | When adding content types |
| `agents/shared/capability_map.py` | Programmatic capability verification | When adding tools |

---

## The Ultimate Test

> Describe an outcome to the agent that's within Snowthere's domain but that we didn't build a specific feature for. Can it figure out how to accomplish it, operating in a loop until it succeeds?

**Example tests:**

1. "Find the 3 best value European resorts for a family with a toddler and a teen"
   - Requires: search, filter, compare, reason about mixed ages

2. "Which Ikon resorts should we hit on a 2-week road trip from Denver?"
   - Requires: geographic reasoning, pass lookup, itinerary building

3. "Update all Austrian resort prices from their official websites"
   - Requires: list resorts, filter by country, scrape each, update database

4. "What resorts are people searching for that we haven't covered yet?"
   - Requires: search demand analysis, compare to existing, prioritize gaps

If the agent can accomplish these using existing tools and prompts—we're agent-native.
If it can't—we have a parity gap to fix.

---

## References

- [Agent Native Guide](https://every.to/guides/agent-native) - Source principles
- [Claude Code SDK](https://docs.anthropic.com/en/docs/claude-code) - Implementation patterns
- [IACP Pattern](https://github.com/se-yoda/specs) - Agent communication protocol
