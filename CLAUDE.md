# Family Ski Directory - Agent Handoff Document

> Last Updated: 2026-01-28
> Current Round: 14 (Homepage Redesign) - pending

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
│   │   └── primitives/           # 63 atomic primitives
│   │       ├── intelligence.py   # ⭐ NEW: 6 LLM-based primitives
│   │       ├── research.py       # Exa/Brave/Tavily
│   │       ├── content.py        # Claude content generation
│   │       ├── database.py       # Resort CRUD
│   │       ├── publishing.py     # Publication lifecycle
│   │       └── system.py         # Queue, costs, logging
│   │
│   ├── agent_layer/              # ⭐ NEW: True Agent Infrastructure
│   │   ├── base.py               # BaseAgent with think→act→observe
│   │   ├── memory.py             # 3-tier memory system
│   │   ├── tracer.py             # Observability/tracing
│   │   ├── coordinator.py        # Agent-to-agent messaging
│   │   ├── hooks.py              # Human intervention points
│   │   └── agents/               # Concrete agent implementations (Phase 2)
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

## Rounds

### Round 1: Foundation ✅
> Project structure, Next.js, Supabase schema, design system

- [x] Create project directory structure
- [x] Set up Next.js 14 with App Router
- [x] Create Supabase migrations and schema
- [x] Build basic resort page component
- [x] Write manual content for 3 test resorts
- [x] Create CLAUDE.md
- [x] Design system ("Alpine Golden Hour")

### Round 2: Core Agents ✅
> Python agents, primitives, pipeline, MCP server

- [x] Python project structure (pyproject.toml, requirements.txt)
- [x] Shared agent utilities (config, supabase client)
- [x] 50+ atomic primitives (research, content, database, publishing, system)
- [x] Voice profiles (instagram_mom, practical_mom, etc.)
- [x] IACP agents (research_resort, generate_guide, optimize_for_geo)
- [x] **Autonomous pipeline** (orchestrator, runner, decision_maker)
- [x] **MCP server** (55 tools for manual intervention)
- [x] **Cron entry point** (cron.py for Railway)
- [x] **Architecture documentation** (ARCHITECTURE.md)

### Round 3: Security Audit ✅
> XSS prevention, legal pages, cookie consent, security headers

- [x] Security audit (XSS prevention, security headers, rate limiting)
- [x] Legal pages (Privacy Policy, Terms of Service)
- [x] GDPR cookie consent banner
- [x] AI content disclosure component
- [x] CAN-SPAM compliance for newsletter
- [x] Delete test resorts for fresh pipeline start

### Round 4: Production Launch ✅
> Deploy to production, configure monitoring

- [x] Supabase project in cloud (Snowthere, 23 tables)
- [x] Environment variables configured (Railway, Vercel)
- [x] Deploy agents to Railway with cron schedule (creative-spontaneity)
- [x] Vercel deployment with ISR (www.snowthere.com)
- [x] Google Search Console setup + sitemap
- [x] Google Analytics setup + link to GSC
- [x] Run automated batches (pipeline running daily, 30+ resorts published)

### Round 5: Compliance & Polish ✅
> Monitoring, accessibility, final polish

- [x] Cron failure alerts (5.11)
- [x] Accessibility audit - WCAG 2.1 AA (5.12)
- [x] Trademark notices (5.13)
- [x] Core Web Vitals reporting (5.14)

### Round 5.1: Agent-Native Scalability ✅ (Completed 2026-01-22)
> Scale duplicate detection to 3000+ resorts, improve UGC photo reliability

**Problem Solved:** Decision maker was putting ALL resort names in Claude's prompt (~22,500 tokens at 3000 resorts). This doesn't scale and violated agent-native principles.

- [x] New primitives: `check_resort_exists()`, `find_similar_resorts()`, `count_resorts()`, `get_country_coverage_summary()`
- [x] Discovery primitive: `check_discovery_candidate_exists()`
- [x] Intelligence primitive: `validate_resort_selection()` with `ResortValidationResult`
- [x] Refactored `decision_maker.py` to two-phase validation (Claude suggests → DB validates)
- [x] Context reduced from ~22,500 tokens to ~310 tokens (99% reduction)
- [x] Name variant matching (St./Sankt/Saint fuzzy matching)
- [x] UGC place_id caching (saves API calls after first lookup)
- [x] Transliteration support via `unidecode` for international names
- [x] Country name variants (Schweiz, Österreich, etc.)
- [x] Database migrations: 014 (image metadata), 015 (google_place_id)
- [x] Google Places API research: coordinates-first, Text Search (New) API preferred

**Key Learnings:**
- Agent-native principle: Primitives should be atomic; agents query them, not receive massive lists
- Two-phase validation: Claude suggests freely, database validates after
- Google Places: Place IDs can be cached indefinitely, photos cannot
- Transliteration graceful fallback ensures production stability

### Round 13: Delightful, On-Brand, Image-Rich Guide Pages ✅ (Completed 2026-01-28)
> Guide page design overhaul, Nano Banana Pro image generation, exit intent popup redesign

- [x] HTML rendering bug fixes (list descriptions + FAQ answers with `sanitizeHtml()`)
- [x] Guide page Spielplatz design overhaul (white cards, section emojis, styled tables/lists)
- [x] Exit intent popup redesigned with Spielplatz personality
- [x] Nano Banana Pro on Replicate as primary image model (4-tier fallback)
- [x] All 11 guide images generated, stored in Supabase Storage
- [x] Frontend design skill installed (`.claude/skills/frontend-design/`)
- [x] TypeScript types for new section types (image, callout)

**Key Learnings:**
- Nano Banana Pro (`google/nano-banana-pro` on Replicate): $0.15/image, best quality
- 4-tier fallback: Nano Banana Pro (Replicate) → Glif → Gemini → Flux Schnell
- Replicate URLs are temporary — always re-upload to Supabase Storage
- Browser audit before design work reveals UX issues invisible in code review

### Future Work

- [ ] Sign up for affiliate networks + run migration 032
- [ ] Investigate Google Places API errors
- [ ] Monitor and iterate on pipeline quality

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

## Security & Compliance (Completed 2026-01-20)

### Security Hardening
- **XSS Prevention:** DOMPurify sanitization on all `dangerouslySetInnerHTML` usages
- **Security Headers:** CSP, HSTS, X-Frame-Options, X-Content-Type-Options in `vercel.json`
- **ISR Revalidation:** POST-only endpoint with rate limiting and timing-safe secret comparison

### Legal Pages
- `/privacy` - GDPR/CCPA compliant privacy policy
- `/terms` - Terms of service with AI content disclaimers and liability limits

### Compliance
- **Cookie Consent:** GDPR-compliant banner blocking GA until consent given
- **AI Disclosure:** Transparent disclosure on all AI-generated resort content
- **CAN-SPAM:** Privacy notice on newsletter signup form

### Key Files
| File | Purpose |
|------|---------|
| `apps/web/lib/sanitize.ts` | DOMPurify HTML sanitization wrapper |
| `apps/web/components/CookieConsent.tsx` | GDPR cookie consent banner |
| `apps/web/components/resort/AIDisclosure.tsx` | AI content transparency component |
| `apps/web/app/privacy/page.tsx` | Privacy policy page |
| `apps/web/app/terms/page.tsx` | Terms of service page |
| `apps/web/vercel.json` | Security headers configuration |

---

## Infrastructure (Updated 2026-01-20)

### Production Services

| Service | Project | URL/Details |
|---------|---------|-------------|
| **Vercel** | snowthere | www.snowthere.com |
| **Supabase** | Snowthere | Tomme Inc org, AWS us-east-2, 23 tables |
| **Railway** | creative-spontaneity | Active cron job (daily pipeline) |

### Railway Projects

| Project | Status | Purpose |
|---------|--------|---------|
| `creative-spontaneity` | **Active** | Daily cron job running autonomous pipeline |
| `snowthere-agents` | Standby | Correctly named, needs cron schedule configured |
| `soothing-delight` | Separate | Different project (not snowthere) |

**Note:** `creative-spontaneity` currently has the active cron schedule. Consider migrating to `snowthere-agents` for clearer naming, or continue using `creative-spontaneity` as the production runner.

### Environment Variables (Railway)

```
ANTHROPIC_API_KEY      # Claude API
BRAVE_API_KEY          # Brave search
DAILY_BUDGET_LIMIT     # Cost controls
EXA_API_KEY            # Exa semantic search
SUPABASE_SERVICE_KEY   # Database admin access
SUPABASE_URL           # Database connection
TAVILY_API_KEY         # Tavily research
VERCEL_REVALIDATE_TOKEN # ISR revalidation
VERCEL_URL             # Production URL for revalidation
```

### Vercel Configuration

- **Project ID:** `prj_1jp0HFzGtliyw3oTk0gzFKGUSOZi`
- **Org:** `team_aAMyNKXNmAj9tT0XjLNydTh2` (tom-merediths-projects)
- **Framework:** Next.js with ISR
- **Security Headers:** CSP, HSTS, X-Frame-Options (see `vercel.json`)

### Google Tools (Configured 2026-01-20)

| Tool | Property | Status |
|------|----------|--------|
| **Search Console** | sc-domain:snowthere.com | Verified, sitemap submitted |
| **Analytics** | Snowthere (GA4) | Active, linked to Search Console |

**Google Search Console:**
- Domain verified: snowthere.com
- Sitemap: https://www.snowthere.com/sitemap.xml (2 pages discovered)
- Linked to Google Analytics

**Google Analytics (GA4):**
- Property: Snowthere
- Stream: Snowthere Website (https://snowthere.com)
- Stream ID: 13316125178
- Linked to Search Console for organic search data

---

## Test Resorts (Deleted 2026-01-20)

The original test resorts have been deleted and will be regenerated by the autonomous pipeline:
- Park City (US), St. Anton (Austria), Zermatt (Switzerland)

No exclusion list exists - resorts are discovered via pass networks, keyword research, and trending analysis.

---

## Compound Beads Workflow

This project uses compound-beads v2.0.

### Commands

| Command | Purpose |
|---------|---------|
| `/compound:start-round` | Begin new development round |
| `/compound:status` | Show current round state |
| `/compound:close-session` | 7-step session close protocol |
| `/compound:compound` | Extract learnings + Arc narrative |
| `/compound:panel` | Expert consultation (optional) |
| `/compound:handoff` | Context window transition |
| `/compound:research` | Search past learnings |

### Tracking Files

| File | Purpose |
|------|---------|
| `.compound-beads/QUICKSTART.md` | Instant pickup (<500 chars) |
| `.compound-beads/context.md` | Current state + recent rounds |
| `.compound-beads/rounds.jsonl` | Machine-readable history |
| `.compound-beads/learnings.md` | Knowledge with Arc narratives |

### Session Flow

```
/compound:start-round
  → Read QUICKSTART.md + context.md
  → Identify pending tasks
  → Work on round tasks

/compound:close-session (7 steps)
  1. git status
  2. git add
  3. git commit [Round N]
  4. Update rounds.jsonl
  5. Update context.md
  6. Regenerate QUICKSTART.md
  7. git push
```

### Arc Narrative (End of Each Round)

Every round captures its transformation:
```
We started believing: [Initial hypothesis]
We ended believing: [Final understanding]
The transformation: [One-sentence shift in thinking]
```

---

## How to Continue

1. Read `.compound-beads/QUICKSTART.md` for instant context
2. Check `.compound-beads/context.md` for current state
3. Run `/compound:start-round` to begin work
4. Run `/compound:close-session` when done (includes git push)

**Quick Commands:**
```bash
# Test pipeline
cd agents && python cron.py --dry-run --max-resorts 2

# Railway auto-deploys from main branch (creative-spontaneity)
```

**Immediate Next Steps:**
- Round 13 complete (guide design overhaul, Nano Banana Pro images, exit intent popup)
- Round 14: Homepage redesign
- Sign up for affiliate networks + run migration 032
- Investigate Google Places API errors

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
| **Image generation** | Nano Banana Pro on Replicate (primary) | Best quality ($0.15), 4-tier fallback ensures reliability |

See `agents/ARCHITECTURE.md` for detailed rationale on each decision.
