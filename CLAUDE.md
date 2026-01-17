# Family Ski Directory - Agent Handoff Document

> Last Updated: 2026-01-16
> Status: MVP Development (Week 2 - Autonomous Pipeline Complete)

## Quick Context

A family-focused ski resort directory targeting parents with kids under 12. Complete "trip guides" families can print and use. **Fully autonomous AI content generation** with daily scheduled pipeline. SEO + GEO optimized for both traditional search and AI citation.

**Core Insight:** It's often cheaper to fly to Austria, get lodging, and buy lift tickets than skiing at major US resorts. Families feel overwhelmed - we answer "How do we do this? Which ones?"

**Voice:** Instagram mom friendly - practical, encouraging, relatable, not intimidating.

---

## Project Structure

```
family-ski-directory/
├── apps/
│   └── web/                      # Next.js 14 frontend
│       ├── app/
│       │   ├── page.tsx          # Homepage
│       │   ├── resorts/
│       │   │   └── [country]/
│       │   │       └── [slug]/   # Resort pages
│       │   └── guides/           # Trip planning guides
│       ├── components/
│       │   └── resort/           # Resort page components
│       └── lib/
│           ├── supabase.ts       # Supabase client
│           └── database.types.ts # TypeScript types
│
├── agents/                       # Autonomous agents ✅
│   ├── shared/                   # Shared utilities
│   │   ├── config.py             # Pydantic settings
│   │   ├── supabase_client.py    # Database operations
│   │   ├── voice_profiles.py     # Content voices
│   │   └── primitives/           # 50+ atomic primitives
│   │
│   ├── pipeline/                 # ⭐ CORE: Autonomous execution
│   │   ├── orchestrator.py       # Daily pipeline coordination
│   │   ├── runner.py             # Per-resort execution flow
│   │   └── decision_maker.py     # Claude API for decisions
│   │
│   ├── mcp_server/               # Optional: Interactive CLI tool
│   │   ├── server.py             # 55 MCP tools
│   │   └── README.md             # Claude Code integration
│   │
│   ├── research_resort/          # IACP agent (legacy/reference)
│   ├── generate_guide/           # IACP agent (legacy/reference)
│   ├── optimize_for_geo/         # IACP agent (legacy/reference)
│   │
│   ├── cron.py                   # ⭐ Railway entry point
│   ├── ARCHITECTURE.md           # Key decisions documentation
│   ├── run.py                    # Agent runner
│   └── Procfile                  # Railway config
│
├── packages/
│   ├── database/                 # Supabase client, types
│   ├── shared/                   # Shared utilities
│   └── voice-profiles/           # Content voice configs
│
├── supabase/
│   ├── migrations/
│   │   └── 001_initial.sql       # Full database schema
│   ├── seed.sql                  # Ski passes + sample resorts
│   └── seed_content.sql          # Manual content for 3 test resorts
│
└── specs/                        # Agent specifications
```

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| **Frontend** | Next.js 14 App Router, React, Tailwind CSS |
| **Database** | Supabase (PostgreSQL) |
| **Agents** | FastAPI (Python) - IACP pattern |
| **Agent Runtime** | Railway (always-on) |
| **Research APIs** | Exa + SerpAPI + Tavily |
| **AI** | Claude Opus 4.5 |
| **Hosting** | Vercel + ISR |

---

## Current Status

### Week 1: Foundation ✅

- [x] Create project directory structure
- [x] Set up Next.js 14 with App Router
- [x] Create Supabase migrations and schema
- [x] Build basic resort page component
- [x] Write manual content for 3 test resorts
- [x] Create CLAUDE.md
- [x] Design system ("Alpine Golden Hour")

### Week 2: Core Agents ✅

- [x] Python project structure (pyproject.toml, requirements.txt)
- [x] Shared agent utilities (config, supabase client)
- [x] 50+ atomic primitives (research, content, database, publishing, system)
- [x] Voice profiles (instagram_mom, practical_mom, etc.)
- [x] IACP agents (research_resort, generate_guide, optimize_for_geo)
- [x] **Autonomous pipeline** (orchestrator, runner, decision_maker)
- [x] **MCP server** (55 tools for manual intervention)
- [x] **Cron entry point** (cron.py for Railway)
- [x] **Architecture documentation** (ARCHITECTURE.md)

### Week 2 Remaining

- [ ] Create Supabase project in cloud + run migrations
- [ ] Add environment variables to .env
- [ ] Test pipeline locally (`python cron.py --dry-run`)
- [ ] Deploy agents to Railway with cron schedule

### Week 3: Launch (TODO)

- [ ] Vercel deployment with ISR
- [ ] Newsletter signup
- [ ] Run first automated batch (10-20 resorts)
- [ ] Monitor and iterate

---

## Key Files

| File | Purpose |
|------|---------|
| **Frontend** | |
| `apps/web/app/resorts/[country]/[slug]/page.tsx` | Resort page template |
| `apps/web/components/resort/*.tsx` | Resort UI components |
| `apps/web/lib/database.types.ts` | TypeScript types from schema |
| **Database** | |
| `supabase/migrations/001_initial.sql` | Database schema |
| `supabase/seed.sql` | Initial ski passes + sample data |
| `supabase/seed_content.sql` | Manual content (instagram mom voice) |
| **Autonomous Pipeline** ⭐ | |
| `agents/cron.py` | Railway entry point for daily cron |
| `agents/pipeline/orchestrator.py` | Daily pipeline coordination |
| `agents/pipeline/runner.py` | Per-resort execution flow |
| `agents/pipeline/decision_maker.py` | Claude API for intelligent decisions |
| `agents/ARCHITECTURE.md` | Key architectural decisions |
| **MCP Server (Optional)** | |
| `agents/mcp_server/server.py` | 55 MCP tools for Claude Code |
| `agents/mcp_server/README.md` | Integration instructions |
| **Shared Primitives** | |
| `agents/shared/config.py` | Agent configuration (Pydantic settings) |
| `agents/shared/voice_profiles.py` | Voice profiles (instagram_mom, etc.) |
| `agents/shared/primitives/research.py` | Exa/SerpAPI/Tavily integrations |
| `agents/shared/primitives/content.py` | Claude content generation |
| `agents/shared/primitives/database.py` | Resort/pass CRUD operations |
| `agents/shared/primitives/publishing.py` | Publication lifecycle + revalidation |
| `agents/shared/primitives/system.py` | Queue, cost tracking, audit log |
| **Documentation** | |
| `AGENT_NATIVE.md` | Agent Native principles & capability map |

---

## Database Schema (Key Tables)

```sql
resorts                    -- Core resort info (slug, name, country, region)
resort_family_metrics      -- Family scores, age ranges, childcare
resort_content             -- All written content sections
resort_costs               -- Pricing (lift tickets, lodging, meals)
ski_quality_calendar       -- Monthly snow/crowds/recommendations
ski_passes                 -- Epic, Ikon, regional passes
resort_passes              -- Many-to-many: which passes at which resorts
content_queue              -- Agent pipeline task queue
agent_audit_log            -- Observability / reasoning trail
```

---

## Voice Profile: instagram_mom

```yaml
tone:
  - Encouraging but honest
  - Practical over perfect
  - "Real talk" moments
  - Enthusiastic without being overwhelming

patterns:
  - "Here's the thing about [resort]..."
  - "Pro tip:"
  - "Real talk:"
  - "Warning:"
  - "The good news is..."

avoid:
  - Technical ski jargon without explanation
  - Overwhelming statistics
  - Assuming unlimited budget
  - Corporate/formal tone
```

---

## Content Structure Per Resort

1. **Quick Take** - BLUF verdict with Perfect if/Skip if
2. **The Numbers** - Family metrics table (GEO-optimized)
3. **Getting There** - Airports, transfers, pro tips
4. **Where to Stay** - Budget/mid/luxury options with names
5. **Lift Tickets & Passes** - Prices + pass compatibility
6. **On the Mountain** - Terrain by skill, ski school, lunch spots
7. **Off the Mountain** - Activities, restaurants, groceries
8. **Ski Quality Calendar** - Monthly conditions table (GEO-optimized)
9. **What Parents Say** - Synthesized reviews
10. **FAQ** - 5-8 questions with Schema.org markup (GEO-optimized)

---

## Environment Variables Needed

```bash
# Supabase
NEXT_PUBLIC_SUPABASE_URL=
NEXT_PUBLIC_SUPABASE_ANON_KEY=
SUPABASE_SERVICE_ROLE_KEY=

# APIs (for agents - Week 2)
EXA_API_KEY=
SERPAPI_API_KEY=
TAVILY_API_KEY=
ANTHROPIC_API_KEY=
```

---

## Commands

```bash
# Frontend Development
pnpm install                    # Install dependencies
pnpm dev                        # Start dev server
pnpm build                      # Build for production

# Database
supabase start                  # Local Supabase
supabase db push               # Apply migrations
supabase db seed               # Run seed files

# Agents (from agents/ directory)
pip install -r requirements.txt # Install Python deps
# Or with UV:
uv sync                         # Install deps with UV

# ⭐ AUTONOMOUS PIPELINE (primary way to run)
python cron.py                             # Daily pipeline (up to 4 resorts)
python cron.py --max-resorts 2             # Limit to 2 resorts
python cron.py --dry-run                   # See what would happen
python cron.py --resort "Zermatt" --country "Switzerland"  # Single resort

# MCP Server (optional, for manual Claude Code intervention)
python -m mcp_server.server                # Start MCP server (stdio)
claude mcp add snowthere -- python -m mcp_server.server  # Add to Claude Code

# Legacy IACP agents (reference only)
python run.py research          # Research agent (port 8001)
python run.py generate          # Generate agent (port 8002)
python run.py optimize          # Optimize agent (port 8003)
```

---

## Agent Architecture ✅

### Layer 1: Atomic Primitives (agents/shared/primitives/)

**Research Primitives:** (`primitives/research.py`)
- `exa_search(query)` → Semantic search via Exa API
- `serp_search(query)` → Google results via SerpAPI
- `tavily_search(query)` → Web research via Tavily
- `search_resort_info()` → Parallel search across all sources
- `scrape_url(url)` → Fetch and parse webpage content

**Content Primitives:** (`primitives/content.py`)
- `write_section(section_name, context, voice)` → Generate content section
- `generate_faq(resort_name, context)` → Create FAQ section
- `apply_voice(content, profile)` → Transform to voice profile
- `generate_seo_meta()` → Create SEO metadata

**Database Primitives:** (`primitives/database.py`)
- `list_resorts()` / `get_resort()` / `create_resort()` → Resort CRUD
- `update_resort()` / `delete_resort()` / `search_resorts()` → Resort management
- `get_resort_content()` / `update_resort_content()` → Content CRUD
- `get_resort_costs()` / `update_resort_costs()` → Cost data
- `get_resort_family_metrics()` / `update_resort_family_metrics()` → Family metrics
- `list_ski_passes()` / `add_resort_pass()` / `remove_resort_pass()` → Ski passes
- `get_resort_calendar()` / `update_resort_calendar()` → Ski quality calendar

**Publishing Primitives:** (`primitives/publishing.py`)
- `publish_resort()` / `unpublish_resort()` / `archive_resort()` → Publication lifecycle
- `revalidate_page()` / `revalidate_resort_page()` → Vercel ISR revalidation
- `get_stale_resorts()` / `mark_resort_refreshed()` → Freshness tracking

**System Primitives:** (`primitives/system.py`)
- `log_cost(api, amount)` → Track API spend
- `get_daily_spend()` / `check_budget()` / `get_cost_breakdown()` → Budget management
- `log_reasoning(task_id, action, reasoning)` → Audit trail
- `read_audit_log()` / `get_task_audit_trail()` → Audit queries
- `queue_task()` / `list_queue()` / `get_next_task()` → Content queue
- `update_task_status()` / `get_queue_stats()` → Queue management

### Layer 2: Autonomous Pipeline ⭐ (agents/pipeline/)

**The primary way the system runs.** Direct Python + Claude API.

```
┌─────────────────────────────────────────────────────────────┐
│                     cron.py (Entry Point)                    │
│                            ↓                                 │
│  ┌──────────────────────────────────────────────────────┐   │
│  │               orchestrator.py                         │   │
│  │  - Check budget                                       │   │
│  │  - Generate system context                            │   │
│  │  - Ask Claude to pick resorts (decision_maker.py)    │   │
│  │  - Loop: run pipeline for each resort                │   │
│  │  - Compile daily digest                              │   │
│  └──────────────────────────────────────────────────────┘   │
│                            ↓                                 │
│  ┌──────────────────────────────────────────────────────┐   │
│  │               runner.py (per resort)                  │   │
│  │  - Research (Exa + SerpAPI + Tavily)                 │   │
│  │  - Calculate confidence score                         │   │
│  │  - Generate content (Claude Opus 4.5)                │   │
│  │  - Store in database                                  │   │
│  │  - Decide: publish / draft / review                  │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

**Key Design Decision:** We use direct code instead of MCP for autonomous execution.
MCP is for interactive Claude Code sessions. Autonomous cron jobs don't need protocol overhead.
See `agents/ARCHITECTURE.md` for full rationale.

### Layer 3: MCP Server (Optional - agents/mcp_server/)

55 tools exposing all primitives for manual Claude Code intervention.
Use when you need to manually research a specific resort or debug.

### Legacy: IACP Agents (agents/research_resort/, etc.)

Earlier iteration using FastAPI IACP pattern. Kept for reference.
The pipeline approach is simpler for autonomous operation.

---

## GEO Optimization Targets

| Element | Why |
|---------|-----|
| Tables | 96% AI parse rate vs 73% for prose |
| FAQs | Schema.org markup for featured snippets |
| BLUF | "Quick Take" at top for AI extraction |
| Numbers | Specific costs, ages, percentages |
| llms.txt | Per-resort AI crawler guidance |

---

## Test Resorts (Manual Content Done)

1. **Park City** (US) - Easy access, expensive, great for varied families
2. **St. Anton** (Austria) - Advanced terrain, legendary apres, European value
3. **Zermatt** (Switzerland) - Bucket-list, car-free, ski to Italy

---

## How to Continue

1. Read this CLAUDE.md for context
2. Check Current Status section for next steps
3. Reference `/Volumes/tomme 4TB/.claude/plans/noble-cooking-puddle.md` for full plan
4. Set up Supabase project and environment variables
5. Run migrations and test locally

---

## Parent Context

This project is part of the SuperTrained workspace:
- See `/Volumes/tomme 4TB/Dropbox/00_tommeco/Supertrained/CLAUDE.md` for workspace overview
- NOT part of SE-Yoda-AN (separate standalone project)
- Uses Agent Native principles from https://every.to/guides/agent-native

---

## Key Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Voice | Instagram mom | Target audience, relatable |
| Scope | Global from day 1 | Value skiing angle requires international |
| Autonomy | Fully autonomous | Scale to 3000 resorts |
| Stack | Next.js + Python agents | SEO-first, clean architecture |
| Content | Complete trip guide | Printable, actionable |
| Agent runtime | Railway | Reliable cron scheduler |
| Database | Supabase | PostgreSQL + storage |
| AI model | Opus 4.5 (content), Sonnet (decisions) | Quality vs speed tradeoff |
| **Pipeline vs MCP** | **Direct code for autonomy** | MCP is for interactive sessions; direct Python is simpler for cron |
| **Confidence scoring** | Formula-based with Claude borderline | Auto-publish >0.8, auto-reject <0.6, ask Claude 0.6-0.8 |
| **Decision making** | Claude API calls | Flexible, captures reasoning, handles nuance |

See `agents/ARCHITECTURE.md` for detailed rationale on each decision.
