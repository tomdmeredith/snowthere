# Building AI-Powered Niche Content Sites

> A practical guide for creating autonomous content platforms in any vertical

This guide distills the lessons from building Snowthere into a repeatable framework you can apply to any niche.

---

## Part 1: Choosing Your Niche

### Finding the "Open Secret" Angle

The best niches have an **open secret** - something insiders know but outsiders don't. For Snowthere, it was "European skiing is often cheaper than US skiing." Look for:

1. **Price arbitrage**: Where is quality cheaper than expected?
2. **Access complexity**: What requires insider knowledge to navigate?
3. **Comparison overwhelm**: Where are there too many options?
4. **Information fragmentation**: Where is good info scattered across many sources?

### Niche Validation Checklist

Before committing, validate:

| Question | Snowthere Example | Your Niche |
|----------|-------------------|------------|
| Is there search volume? | "family ski resorts" = 18K/mo | Check Google Keyword Planner |
| Are competitors incomplete? | No site does all resorts with family focus | Search top 10 results |
| Can you differentiate? | "Complete trip guide for families" | What's your unique angle? |
| Is the content durable? | Resort info changes yearly, not daily | How often does info change? |
| Can AI help? | Research + content generation | What parts can be automated? |

### Good Niche Patterns

**Travel verticals**:
- Family camping sites (which have showers, playgrounds)
- Pet-friendly hotels (actual policies, not just "pet-friendly" label)
- Accessible travel (wheelchair, sensory, dietary needs)

**Consumer decisions**:
- Used car buying (specific model year comparisons)
- Home renovation contractors (by city, specialty, budget)
- Wedding venues (capacity, catering, real costs)

**Professional verticals**:
- Remote work visas (country-by-country requirements)
- Startup grants by industry and stage
- Conference speaking opportunities

### Red Flags

Avoid niches with:
- **Daily updates needed**: News, stocks, events
- **High liability**: Medical, legal, financial advice
- **Thin content potential**: Not enough depth per entity
- **Existing dominant player**: Wikipedia-level coverage exists

---

## Part 2: Technology Stack Decisions

### Frontend Framework

**Recommended: Next.js 14 with App Router**

Why:
- SEO-first with static generation + ISR
- React ecosystem for components
- Vercel deployment is seamless
- Edge functions for dynamic features

Alternatives:
- Astro: Better for pure static sites
- Nuxt: If you prefer Vue
- SvelteKit: If performance is critical

### Database

**Recommended: Supabase (PostgreSQL)**

Why:
- Generous free tier (500MB, 50K monthly active users)
- Built-in auth if needed
- Storage included for images
- Real-time subscriptions for live features
- Great TypeScript support

Alternatives:
- PlanetScale: MySQL-compatible, good for scale
- Neon: Serverless Postgres, pay-per-query
- Turso: SQLite at the edge, very fast

### AI Models

**Recommended Tiering**:

| Task | Model | Cost | Why |
|------|-------|------|-----|
| Content generation | Opus 4.5 | ~$15/1M tokens | Best quality for long-form |
| Decisions/routing | Sonnet 4.5 | ~$3/1M tokens | Smart + fast |
| Extractions | Haiku 4.5 | ~$0.25/1M tokens | Fast + cheap |

### Research APIs

You need **multiple sources** to avoid hallucinations:

| API | Use Case | Cost |
|-----|----------|------|
| **Exa** | Semantic search, trending | $0.003/search |
| **SerpAPI** | Google results | $0.01/search |
| **Tavily** | Web research | $0.01/search |

### Agent Runtime

**Recommended: Railway**

Why:
- Reliable cron scheduling
- Easy deployment from GitHub
- Good logging and monitoring
- Reasonable pricing ($5-20/month)

Alternatives:
- Render: Similar to Railway
- Fly.io: If you need global distribution
- AWS Lambda: If you want event-driven

---

## Part 3: Content Architecture

### Schema Design Principles

**Entity-first thinking**: Design around your main entity (for us: resorts).

```sql
-- Core entity
CREATE TABLE entities (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    slug TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    status TEXT DEFAULT 'draft',  -- draft, published, archived
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    published_at TIMESTAMPTZ
);

-- Structured content sections
CREATE TABLE entity_content (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    entity_id UUID REFERENCES entities(id),
    section_name TEXT NOT NULL,
    content JSONB NOT NULL,
    version INT DEFAULT 1,
    UNIQUE(entity_id, section_name)
);

-- Metrics and scores
CREATE TABLE entity_metrics (
    entity_id UUID PRIMARY KEY REFERENCES entities(id),
    overall_score DECIMAL(3,1),
    specific_scores JSONB,  -- {"quality": 8.5, "value": 9.0}
    updated_at TIMESTAMPTZ DEFAULT NOW()
);
```

### Content Sections

Design **10-12 standard sections** for your entity type:

For a travel vertical:
1. Quick take (BLUF)
2. Key metrics table
3. Getting there
4. Where to stay
5. Costs breakdown
6. The experience
7. Practical tips
8. Calendar/timing
9. What people say
10. FAQ

### Voice Profile System

Create a **voice profile** for consistent tone:

```python
VOICE_PROFILE = {
    "name": "YOUR_VOICE_NAME",
    "inspiration": "Publication or person to emulate",
    "tone": [
        "Characteristic 1",
        "Characteristic 2",
        "Characteristic 3"
    ],
    "patterns": [
        "Phrase pattern 1:",
        "Phrase pattern 2:",
        "Phrase pattern 3:"
    ],
    "avoid": [
        "Thing to avoid 1",
        "Thing to avoid 2"
    ]
}
```

### Quality Checklist

Define **objective criteria** for content quality:

```python
QUALITY_CHECKLIST = [
    "Has specific price with currency",
    "Mentions at least 2 options by name",
    "Includes location/address",
    "States operating hours",
    "Has contact information",
    "No placeholder text",
    "All required sections filled",
    "FAQ has 5+ questions",
    # Add niche-specific criteria
]
```

---

## Part 4: Agent Pipeline Design

### Orchestrator Pattern

Your orchestrator handles the "what":

```python
def run_daily_pipeline(max_items: int = 4):
    """Main entry point for cron job."""

    # 1. Check budget
    if not check_budget():
        return {"status": "budget_exhausted"}

    # 2. Select work items
    items = select_work_items(max_items)

    # 3. Process each item
    results = []
    for item in items:
        result = process_item(item)
        results.append(result)

        # Budget check between items
        if not check_budget():
            break

    # 4. Return digest
    return compile_digest(results)
```

### Runner Pattern

Your runner handles the "how" for each item:

```python
def process_item(item: dict) -> dict:
    """Process a single entity."""

    # 1. Research phase
    research = gather_research(item["name"])

    # 2. Content generation
    content = generate_content(research)

    # 3. Quality check
    checklist_score = run_quality_checklist(content)

    # 4. Calculate confidence
    confidence = calculate_confidence(
        research_quality=research["quality"],
        checklist_score=checklist_score
    )

    # 5. Publish decision
    if confidence >= 0.8:
        publish(item, content)
        return {"status": "published"}
    elif confidence >= 0.6:
        decision = ask_claude_for_decision(item, content, confidence)
        if decision["publish"]:
            publish(item, content)
            return {"status": "published"}

    save_as_draft(item, content)
    return {"status": "draft"}
```

### Primitives Architecture

Build **atomic operations** that can be composed:

```
primitives/
├── research.py      # External data gathering
├── content.py       # AI content generation
├── database.py      # CRUD operations
├── publishing.py    # Publication lifecycle
└── system.py        # Queue, costs, logging
```

Each primitive should:
- Do one thing well
- Handle its own errors
- Log its actions
- Return structured data

### Confidence Scoring

Formula for auto-publish decisions:

```python
def calculate_confidence(
    research_quality: float,  # 0-1, how good was source data
    content_completeness: float,  # 0-1, all sections filled
    checklist_score: float,  # 0-1, quality criteria met
    factual_confidence: float  # 0-1, Claude's self-assessment
) -> float:
    return (
        research_quality * 0.30 +
        content_completeness * 0.25 +
        checklist_score * 0.25 +
        factual_confidence * 0.20
    )
```

Thresholds:
- **>= 0.8**: Auto-publish
- **0.6 - 0.8**: Ask Claude for decision
- **< 0.6**: Save as draft

---

## Part 5: SEO + GEO Strategy

### Traditional SEO

**Must-haves**:
1. **Clean URLs**: `/entities/category/slug`
2. **Meta tags**: Title, description, OG tags
3. **Sitemap**: Auto-generated, submitted to Search Console
4. **Schema markup**: JSON-LD for your entity type
5. **Internal linking**: Related entities, categories

### GEO (Generative Engine Optimization)

Optimize for AI citation:

| Element | Why | Implementation |
|---------|-----|----------------|
| **Tables** | 96% AI parse rate | Use for all structured data |
| **BLUF** | Easy AI extraction | "Quick Take" at page top |
| **Numbers** | AI prefers specifics | Always include actual figures |
| **FAQ Schema** | Featured snippets | Schema.org FAQPage markup |
| **llms.txt** | Direct AI guidance | Per-entity AI instructions |

### llms.txt Template

```
# Entity: [Name]

## Quick Summary
[2-3 sentence summary]

## Key Facts
- Fact 1
- Fact 2
- Fact 3

## Recommended Citation
[Entity Name] - [Your Site Name]
Source: [URL]

## Not Recommended For
[Situations where this entity isn't a good fit]
```

---

## Part 6: Cost Management

### Budget Controls

Implement at multiple levels:

```python
# Daily budget check
def check_budget() -> bool:
    spent = get_daily_spend()
    return spent < settings.daily_budget_limit

# Per-item budget
def process_with_budget(item):
    estimated_cost = estimate_cost(item)
    if get_daily_spend() + estimated_cost > settings.daily_budget_limit:
        return {"status": "budget_exceeded"}
    return process_item(item)
```

### Cost Tracking

Log every API call:

```python
def log_cost(api: str, amount: float, task_id: str, metadata: dict):
    supabase.table("api_cost_log").insert({
        "api": api,
        "amount": amount,
        "task_id": task_id,
        "metadata": metadata,
        "created_at": datetime.utcnow().isoformat()
    }).execute()
```

### Expected Costs

Typical costs per entity (your numbers will vary):

| Phase | Cost Range |
|-------|------------|
| Research (3 APIs) | $0.10 - $0.20 |
| Content (Opus) | $0.80 - $1.50 |
| Decisions (Sonnet) | $0.03 - $0.05 |
| **Total per entity** | **$1.00 - $2.00** |

At $1.50/entity, a $15/day budget = 10 entities/day = 300/month = 3,600/year.

---

## Part 7: Launch Checklist

### Pre-Launch

**Security**:
- [ ] Sanitize all user input (DOMPurify)
- [ ] Security headers (CSP, HSTS, X-Frame-Options)
- [ ] Rate limiting on API endpoints
- [ ] No secrets in code/logs

**Legal**:
- [ ] Privacy policy page
- [ ] Terms of service
- [ ] Cookie consent (if using analytics)
- [ ] AI content disclosure

**Technical**:
- [ ] Build succeeds
- [ ] No TypeScript errors
- [ ] Images optimized
- [ ] Mobile responsive

### Launch Day

1. **Deploy frontend** to Vercel
2. **Deploy agents** to Railway
3. **Configure cron** schedule
4. **Submit sitemap** to Search Console
5. **Set up analytics** (GA4, Plausible, etc.)

### Post-Launch Monitoring

Track daily:
- Pipeline success rate
- Publish vs draft ratio
- Cost per entity
- Errors by type

Track weekly:
- Search Console impressions
- Organic traffic
- Content quality trends

---

## Part 8: Scaling Considerations

### Content Volume

| Entities | Timeline | Budget/Month |
|----------|----------|--------------|
| 100 | 2 weeks | $150 |
| 500 | 2 months | $750 |
| 1,000 | 4 months | $1,500 |
| 3,000 | 12 months | $4,500 |

### Performance Optimization

As you scale:
1. **Database indexes** on frequently queried columns
2. **ISR revalidation** to reduce database load
3. **CDN caching** for images
4. **Parallel research** (multiple APIs simultaneously)

### Team Scaling

| Phase | Team |
|-------|------|
| MVP (0-100 entities) | Solo |
| Growth (100-1000) | + Part-time editor |
| Scale (1000+) | + Developer + Content lead |

---

## Example Niches with Adaptations

### Pet-Friendly Hotels

**Entity**: Hotel
**Angle**: Real pet policies, not marketing fluff
**Sections**: Pet fees, weight limits, pet amenities, nearby parks, vet locations
**Voice**: Friendly dog parent sharing finds
**Quality criteria**: Must have actual pet fee, weight limit, pet deposit

### Remote Work Visas

**Entity**: Country/Visa program
**Angle**: Step-by-step for digital nomads
**Sections**: Requirements, costs, timeline, tax implications, quality of life
**Voice**: Experienced nomad sharing intel
**Quality criteria**: Must have application URL, cost breakdown, processing time

### Wedding Venues

**Entity**: Venue
**Angle**: Real capacity and real costs
**Sections**: Capacity, catering options, vendor restrictions, hidden fees, parking
**Voice**: Wedding planner insider tips
**Quality criteria**: Must have guest capacity, price range, catering policy

---

## Common Pitfalls

### Content Quality

**Problem**: AI generates generic content
**Solution**: Better prompts with voice profiles + quality checklists

**Problem**: Factual errors
**Solution**: Multiple research sources + confidence scoring + human review for borderline

### Technical

**Problem**: Cron job fails silently
**Solution**: Error logging + daily digest emails + monitoring

**Problem**: Budget overruns
**Solution**: Budget checks at orchestrator AND runner level

### Business

**Problem**: No traffic despite good content
**Solution**: SEO takes 3-6 months; also consider social, community, email

**Problem**: Content gets stale
**Solution**: Automated staleness detection + refresh pipeline

---

## Resources

### Tools
- [Supabase](https://supabase.com) - Database
- [Vercel](https://vercel.com) - Frontend hosting
- [Railway](https://railway.app) - Agent runtime
- [Anthropic](https://anthropic.com) - AI models
- [Exa](https://exa.ai) - Semantic search

### Learning
- [Agent Native principles](https://every.to/guides/agent-native)
- [GEO optimization](https://searchengineland.com/generative-engine-optimization-guide)
- [Next.js documentation](https://nextjs.org/docs)

### Inspiration
- Snowthere (this project)
- NomadList (remote work)
- Levels.fyi (compensation)

---

*Last updated: 2026-01-22*
