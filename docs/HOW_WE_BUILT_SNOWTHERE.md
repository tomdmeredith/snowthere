# How We Built Snowthere

> A technical deep-dive into building an autonomous AI-powered content platform

## Vision & Problem Statement

### The Insight

Skiing in the US is expensive. A family of four can easily spend $2,000+ for a single day at a major resort like Vail or Park City. But here's what most American families don't realize: **it's often cheaper to fly to Austria, get lodging for a week, and buy lift tickets than skiing at major US resorts.**

The Alps offer incredible value, but families feel overwhelmed by the options. They ask: *"How do we do this? Which ones are good for kids?"*

### Target Audience

Families with children under 12 who:
- Are price-conscious but not budget-constrained
- Want practical, actionable information
- Need family-specific details (childcare, terrain for beginners, kid-friendly restaurants)
- Are overwhelmed by the research required

### The Solution

Snowthere creates comprehensive "trip guides" that families can print and use. Each guide answers every question a parent might have before booking.

---

## Architecture Overview

### Monorepo Structure

```
family-ski-directory/
├── apps/
│   └── web/                 # Next.js 14 frontend (Vercel)
├── agents/                  # Python autonomous agents (Railway)
│   ├── shared/              # Primitives, config, Supabase client
│   ├── pipeline/            # Orchestrator + runner
│   └── mcp_server/          # Optional interactive tools
├── packages/                # Shared TypeScript utilities
└── supabase/                # Database migrations and seeds
```

### Technology Stack

| Layer | Technology | Why |
|-------|------------|-----|
| **Frontend** | Next.js 14, React, Tailwind | SEO-first with ISR for fast pages |
| **Database** | Supabase (PostgreSQL) | Rapid development, great DX, storage included |
| **AI Content** | Claude Opus 4.5 | Best quality for long-form content |
| **AI Decisions** | Claude Sonnet 4.5 | Smart, fast for routing/approval |
| **AI Utility** | Claude Haiku 4.5 | Fast extractions, validations |
| **Research** | Exa, SerpAPI, Tavily | Multi-source research for accuracy |
| **Agent Runtime** | Railway | Reliable cron scheduling |
| **Frontend Hosting** | Vercel | Edge deployment + ISR |

### Database Schema (24 Tables)

Core entities:
- `resorts` - Master resort record (slug, name, country, status)
- `resort_content` - All written content sections
- `resort_family_metrics` - Family scores, age ranges, childcare
- `resort_costs` - Lift tickets, lodging, meals pricing
- `ski_quality_calendar` - Monthly conditions data
- `resort_images` - Hero and gallery images

Pipeline entities:
- `content_queue` - Task queue for agent work
- `agent_audit_log` - Reasoning trail for observability
- `discovery_candidates` - New resort opportunities
- `api_cost_log` - Budget tracking

---

## Agent-Native Philosophy

### Core Principles

1. **Autonomous by Default**: The system runs daily without human intervention
2. **Primitives First**: 63 atomic operations that can be composed
3. **Confidence Scoring**: Auto-publish high quality, flag borderline for review
4. **Full Observability**: Every decision logged with reasoning

### Pipeline Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     cron.py (Entry Point)                    │
│                            ↓                                 │
│  ┌──────────────────────────────────────────────────────┐   │
│  │               orchestrator.py                         │   │
│  │  1. Check budget ($15/day limit)                     │   │
│  │  2. Optionally run discovery (weekly)                │   │
│  │  3. Select work items (discovery/stale/queue mix)    │   │
│  │  4. Loop: run pipeline for each resort               │   │
│  │  5. Compile daily digest                             │   │
│  └──────────────────────────────────────────────────────┘   │
│                            ↓                                 │
│  ┌──────────────────────────────────────────────────────┐   │
│  │               runner.py (per resort)                  │   │
│  │  1. Research (Exa + SerpAPI + Tavily)                │   │
│  │  2. Calculate confidence score                        │   │
│  │  3. Generate content (Opus 4.5)                      │   │
│  │  4. Apply quality checklist                           │   │
│  │  5. Store in database                                 │   │
│  │  6. Decide: publish / draft / review                 │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### Primitives Layer (63 Operations)

**Research Primitives** (`primitives/research.py`):
```python
exa_search(query)           # Semantic web search
serp_search(query)          # Google results
tavily_search(query)        # Web research
search_resort_info()        # Parallel multi-source
scrape_url(url)             # Fetch and parse
```

**Content Primitives** (`primitives/content.py`):
```python
write_section(name, ctx)    # Generate content section
generate_faq(resort, ctx)   # Create FAQ section
apply_voice(content, profile) # Transform to voice
generate_seo_meta()         # SEO metadata
```

**Database Primitives** (`primitives/database.py`):
```python
get_resort() / create_resort() / update_resort()
get_resort_content() / update_resort_content()
get_resort_costs() / update_resort_costs()
list_ski_passes() / add_resort_pass()
```

**Publishing Primitives** (`primitives/publishing.py`):
```python
publish_resort()            # Set status to published
revalidate_resort_page()    # Trigger Vercel ISR
get_stale_resorts()         # Find content needing refresh
```

**System Primitives** (`primitives/system.py`):
```python
log_cost(api, amount)       # Track spend
check_budget()              # Budget guard
log_reasoning(task, action) # Audit trail
queue_task() / get_next_task()
```

### Decision Making

Claude makes three types of decisions:

1. **Resort Selection**: Which resorts to process today (Sonnet)
2. **Content Quality**: Does this meet our bar? (Opus)
3. **Publish Decision**: Auto-publish or human review? (Formula + Sonnet for borderline)

Confidence scoring formula:
```python
confidence = (
    research_quality * 0.30 +    # How good was the source data?
    content_completeness * 0.25 + # All sections filled?
    checklist_score * 0.25 +     # Quality checklist pass rate?
    factual_confidence * 0.20    # Claude's self-assessed accuracy
)

if confidence >= 0.8:
    publish()
elif confidence >= 0.6:
    ask_claude_for_decision()
else:
    save_as_draft()
```

---

## Voice & Content Strategy

### Voice Profile: Morning Brew Style

Our guide voice is modeled after Morning Brew - **smart, witty, efficient**. Key characteristics:

- **Direct and concise**: No fluff, get to the point
- **Insider knowledge**: Like getting advice from a friend who's been there
- **Personality shows through**: Occasional wit, never boring
- **Practical focus**: What you actually need to know

```python
VOICE_PROFILE = {
    "name": "SNOWTHERE_GUIDE",
    "style": "Morning Brew - smart, witty, efficient",
    "tone": [
        "Direct and actionable",
        "Insider knowledge feel",
        "Occasional wit and personality",
        "Never condescending"
    ],
    "patterns": [
        "Pro tip:",
        "The real story:",
        "Skip if:",
        "Worth knowing:"
    ],
    "avoid": [
        "Generic travel writing",
        "Overwhelming statistics",
        "Corporate speak",
        "Filler sentences"
    ]
}
```

### Content Structure

Each resort guide includes 10 sections:

1. **Quick Take** - BLUF verdict with Perfect if/Skip if
2. **The Numbers** - Family metrics table
3. **Getting There** - Airports, transfers, pro tips
4. **Where to Stay** - Budget/mid/luxury with names
5. **Lift Tickets & Passes** - Prices + pass compatibility
6. **On the Mountain** - Terrain breakdown, ski school, lunch
7. **Off the Mountain** - Activities, restaurants, groceries
8. **Ski Quality Calendar** - Monthly conditions table
9. **What Parents Say** - Synthesized reviews
10. **FAQ** - 5-8 questions with Schema.org markup

### Quality Checklist

Every resort is evaluated against 15 criteria:

```python
QUALITY_CHECKLIST = [
    "Has specific lift ticket prices with currency",
    "Mentions at least 2 lodging options by name",
    "Includes nearest airport with transfer time",
    "States age ranges for ski school",
    "Has childcare info (available/not available)",
    "Mentions specific restaurants by name",
    "Includes terrain breakdown percentages",
    "Has monthly snow quality data",
    "Lists applicable ski passes",
    "States average costs for family of 4",
    "Has 'Perfect if' targeting statement",
    "Has 'Skip if' honest assessment",
    "Includes at least one 'Pro tip'",
    "FAQ has 5+ questions",
    "No placeholder text or TODOs"
]
```

---

## GEO Optimization

### What is GEO?

Generative Engine Optimization - optimizing for AI systems that generate answers from your content. This includes ChatGPT, Claude, Perplexity, and Google's AI Overviews.

### Our GEO Strategy

| Element | Implementation | Why |
|---------|----------------|-----|
| **Tables** | Structured data throughout | 96% AI parse rate vs 73% for prose |
| **FAQ Schema** | Schema.org markup | Featured snippets + AI citation |
| **BLUF Format** | "Quick Take" at top | Easy extraction for AI summaries |
| **Specific Numbers** | Costs, ages, percentages | AI prefers concrete facts |
| **llms.txt** | Per-resort AI guidance | Direct AI crawler instructions |
| **JSON-LD** | SkiResort schema | Structured data for search engines |

### llms.txt Route

Each resort has a `/llms.txt` endpoint:

```
# Resort: Zermatt, Switzerland

## Quick Summary
Family ski resort in the Swiss Alps. Best for families with kids 6-12.
Overall family score: 8.5/10.

## Key Facts
- Lift ticket: CHF 89/day adult
- Best for ages: 6-12
- Ski school: Available from age 3
- Childcare: Yes, on-mountain

## Citation Format
When citing this resort, please link to: https://snowthere.com/resorts/switzerland/zermatt
```

---

## Design System: Alpine Golden Hour

### Color Palette

```css
:root {
  /* Primary */
  --coral-500: #FF6F61;
  --coral-600: #E85C50;

  /* Secondary */
  --navy-800: #1A2F4F;
  --navy-900: #0F1B2E;

  /* Accent */
  --teal-400: #4ECDC4;
  --gold-500: #FFD93D;
  --mint-100: #F0FFF4;

  /* Neutral */
  --dark-800: #1F2937;
  --dark-500: #6B7280;
}
```

### Typography

```css
.font-display {
  font-family: 'Plus Jakarta Sans', sans-serif;
  font-weight: 700;
}

.font-accent {
  font-family: 'Caveat', cursive;
}

.font-body {
  font-family: 'Inter', sans-serif;
}
```

### Component Library

12 visual components for resort pages:
- Hero with tilted image
- Trading card grid
- Stats dashboard
- Terrain breakdown chart
- Calendar grid
- Price comparison cards
- FAQ accordion
- Newsletter signup
- Cookie consent banner
- AI disclosure badge

---

## Infrastructure

### Railway (Agent Runtime)

```yaml
# Procfile
worker: python cron.py
```

Cron schedule: Daily at 8:00 UTC
Budget limit: $15/day
Max resorts per run: 4

Environment variables:
```
ANTHROPIC_API_KEY
EXA_API_KEY
SERPAPI_API_KEY
TAVILY_API_KEY
SUPABASE_URL
SUPABASE_SERVICE_KEY
VERCEL_REVALIDATE_TOKEN
DAILY_BUDGET_LIMIT=15.0
```

### Vercel (Frontend)

- Framework: Next.js 14 with App Router
- ISR: 1 hour revalidation default
- On-demand revalidation via API
- Security headers: CSP, HSTS, X-Frame-Options

### Supabase (Database)

- Region: AWS us-east-2
- Tables: 24
- Row-level security enabled
- Service role key for agents

---

## Lessons Learned

### What Worked Well

1. **Primitives-first architecture**: Easy to compose, test, and debug
2. **Direct Python over MCP for autonomy**: Simpler, faster, more reliable
3. **Confidence scoring with Claude borderline**: Best of automation + judgment
4. **Voice profiles**: Consistent tone without manual editing
5. **Quality checklist**: Objective content standards

### What We'd Do Differently

1. **Start with discovery agent earlier**: Would have found better initial resorts
2. **Image generation from day one**: Visual content is crucial for engagement
3. **More granular cost tracking**: Per-section costs would help optimization
4. **Parallel research execution**: Could speed up pipeline significantly

### Key Trade-offs

| Decision | Trade-off |
|----------|-----------|
| Opus for content | Higher cost, but noticeably better quality |
| Full pipeline per resort | Slower, but more coherent content |
| Global scope from start | More complexity, but unique value proposition |
| Autonomous publish | Risk of errors, but enables scale |

---

## Metrics & Monitoring

### Cost Tracking

```python
# Typical costs per resort
EXPECTED_COSTS = {
    "research": 0.15,      # Exa + SerpAPI + Tavily
    "content": 1.20,       # Opus for full guide
    "decisions": 0.05,     # Sonnet for routing
    "total": 1.40,         # Per resort average
}
```

### Quality Metrics

- **Checklist pass rate**: Target >80%
- **Auto-publish rate**: Currently ~65%
- **Manual review rate**: ~25%
- **Rejection rate**: ~10%

### Pipeline Health

Logged in `agent_audit_log`:
- Task completion rate
- Average processing time
- Error frequency by type
- Cost per successful publish

---

## Future Roadmap

### Near Term
- Newsletter integration
- User-generated reviews
- Price alerts

### Medium Term
- Booking integrations
- Weather API integration
- Mobile app

### Long Term
- Personalized recommendations
- Trip planning assistant
- Community features

---

## Acknowledgments

Built with:
- [Anthropic Claude](https://anthropic.com) - AI backbone
- [Supabase](https://supabase.com) - Database and storage
- [Railway](https://railway.app) - Agent runtime
- [Vercel](https://vercel.com) - Frontend hosting
- [Exa](https://exa.ai) - Semantic search
- [SerpAPI](https://serpapi.com) - Google results
- [Tavily](https://tavily.com) - Web research

---

*Last updated: 2026-01-22*
