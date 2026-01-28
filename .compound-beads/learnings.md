# Learnings

Knowledge extracted across all rounds with Arc narratives.

---

## Round 13: Delightful, On-Brand, Image-Rich Guide Pages

**Arc:**
- **Started believing**: Guide pages just needed images and a few bug fixes
- **Ended believing**: Brand personality requires systematic design overhaul AND reliable image infrastructure
- **Transformation**: From patching individual issues to establishing Spielplatz as a living design standard with autonomous image generation

**Technical:**
- Nano Banana Pro on Replicate: model `google/nano-banana-pro`, version `0785fb14f5aaa30eddf06fd49b6cbdaac4541b8854eb314211666e23a29087e3`, $0.15/image at 2K resolution
- Replicate Predictions API returns a **single URI string** for Nano Banana Pro (not an array like Flux Schnell) — handle both formats with `output if isinstance(output, str) else output[0]`
- Replicate/Glif image URLs are **temporary** — always download and re-upload to Supabase Storage for permanent hosting
- 4-tier fallback chain: Nano Banana Pro (Replicate) → Nano Banana Pro (Glif) → Gemini API → Flux Schnell (Replicate)
- `dangerouslySetInnerHTML` with `sanitizeHtml()` is required for any database content that may contain HTML tags (list descriptions, FAQ answers)
- White card containers (`bg-white rounded-3xl shadow-lg`) on gradient backgrounds prevent the "floating text" UX anti-pattern
- Frontend design skills (`.claude/skills/`) codify brand standards so all future sessions follow them consistently
- Replicate Predictions API polling: create prediction → poll status every 2s → max 90 attempts (180s timeout)

**Process:**
- Browser audit before design work reveals issues invisible in code review (raw HTML tags, missing containers)
- Image generation should be part of the autonomous pipeline, not a manual post-hoc step
- 4-tier fallback ensures image generation never blocks content publication
- Design system skills ensure brand consistency across sessions and context windows

**Key Insight:**
Emoji placeholders are a false economy. Real AI-generated images at $0.15 each ($1.65 for all 11 guides) transform the perceived quality of the entire site. The cost of NOT having images far exceeds $0.15 per guide.

---

## Round 12: Content Expansion & SEO Critical Fixes

**Arc:**
- **Started believing**: SEO is about content and Schema.org markup
- **Ended believing**: A single trailing newline in an env var can block all indexing
- **Transformation**: Infrastructure correctness is the foundation of discoverability

**Technical:**
- A trailing newline in `NEXT_PUBLIC_SITE_URL` broke every canonical URL, og:url, and sitemap entry across the entire site
- Centralize environment-derived constants in one file with `.trim()` safety net
- `metadataBase` in Next.js `layout.tsx` is the canonical way to set base URL for metadata resolution
- `force-dynamic` on homepage returns `cache-control: private, no-cache, no-store` — tells crawlers the page is private
- Duplicate `robots.txt/route.ts` overrides comprehensive `robots.ts` — route handlers take precedence
- www vs non-www mismatch causes every sitemap URL to trigger a 308 redirect before reaching the page
- IndexNow protocol enables instant Bing/Yandex notification of new pages

**Process:**
- When pages aren't being indexed, check infrastructure before content
- One source of truth for derived values (`lib/constants.ts`) prevents scattered bugs
- Post-deploy verification checklist: canonical, sitemap, cache headers, robots.txt
- Manual GSC/Bing resubmission after SEO infrastructure changes

**Key Insight:**
Seven files each defined their own `BASE_URL` from the same env var. Only one had `.trim()`. The bug existed in 6 out of 7 files because there was no single source of truth.

---

## Round 11: Autonomous Content Systems

**Arc:**
- **Started believing**: Newsletter and guides need separate generation systems
- **Ended believing**: Both share the same primitive layer — newsletter queries DB, guides generate to DB
- **Transformation**: Autonomous content is just primitives composed differently on a cron schedule

**Technical:**
- Newsletter generation: query recent data → AI section generation → template rendering → batch send
- Guide generation: topic discovery → content planning → multi-section generation → expert panel → publish
- Exit intent popup with 7-day cooldown prevents annoyance
- `newsletter_issues` table tracks editions; `newsletter_sends` tracks per-subscriber delivery
- Cron entry point (`cron.py`) orchestrates email sequences, newsletter, resort pipeline, and guide pipeline

**Process:**
- Build content pipelines from existing primitives, don't create new systems
- Morning Brew style: scanning-friendly, 3-4 minute read, 600 words
- Guide cadence: Monday/Thursday allows monitoring between runs
- Newsletter cadence: Thursday 6am PT catches weekend planning behavior

**Key Insight:**
The same `generate_section()`, `query_db()`, and `send_email()` primitives power both newsletter and guides. The orchestration layer is thin — just different composition on different schedules.

---

## Round 10: Content Structure & Email Fix

**Arc:**
- **Started believing**: Guides need a new content system
- **Ended believing**: The JSONB content schema was already designed — just needed frontend rendering
- **Transformation**: From building new infrastructure to wiring existing schema to frontend

**Technical:**
- JSONB `content` field in `guides` table stores structured sections (intro, list, comparison_table, checklist, faq, cta)
- `GuideContent.tsx` renders each section type with appropriate components
- Email templates were designed (5 HTML files) but never loaded into DB — `seed_email_sequences.sql` hadn't been run
- `lib/guides.ts` provides `getGuideBySlug()`, `getAllGuideSlugs()`, `getRelatedGuides()` utilities

**Process:**
- Check if infrastructure already exists before building new
- Seed scripts must be part of deployment checklist
- Separation of concerns: immediate welcome email (simple) vs sequence emails (rich templates)

**Key Insight:**
The database schema (migration 010) and 5 HTML email templates existed for weeks but were never connected. The "email system is broken" was actually "seed script was never run on production."

---

## Round 9: Scoring & Pipeline Stability

**Arc:**
- **Started believing**: LLM-generated scores were trustworthy approximations
- **Ended believing**: Store atoms, compute molecules — deterministic formulas from data beat LLM opinion
- **Transformation**: From AI-generated quality score to calculated score from verifiable data

**Technical:**
- LLM extraction clusters scores at 7-9 (avoids extremes, "safe" answers)
- DECIMAL(3,1) provides 90 discrete values vs 10 for INTEGER
- Deterministic formula: base 5.0 + childcare(0-1.5) + ski school(0-1.0) + terrain(0-1.2) + value(0-0.8) + convenience(0-0.5)
- Score distribution shifted from clustered 7-9 to natural 5.4-7.8 spread
- Data sparsity, not formula harshness, limits high scores — most resorts lack 3-4 key fields
- `sanitize_for_schema()` with column whitelists prevents schema mismatch crashes
- `unidecode` in `_slugify()` must match across all code paths for consistent duplicate detection

**Process:**
- Expert panel (6 specialists) consensus: fix data collection before adjusting formula
- Schema mismatch caused 100% pipeline failure — `perfect_if`/`skip_if` routed to wrong table
- Column whitelists should be single source of truth for valid fields in every upsert function
- Backfill script pattern: calculate new values, compare with old, apply with logging

**Key Insight:**
"Store atoms, compute molecules" — the scoring formula is transparent and explainable. "8.2 = childcare(1.5) + ski school(0.8) + terrain(0.9) + ..." beats "an AI said 8."

---

## Round 8: Quick Takes & Site Audit

**Arc:**
- **Started believing**: Quick Takes just need a better prompt
- **Ended believing**: Quality requires structure (hook/context/tension/verdict), forbidden phrases, and specificity scoring
- **Transformation**: From prompt engineering to editorial system with quality gates

**Technical:**
- Editorial Verdict Model: hook → context → tension → verdict structure
- 31 forbidden phrases (generic words like "magic," "paradise," "nestled")
- Specificity scoring: numbers, names, concrete details increase score
- Tagline atoms: extract specific facts (numbers, landmarks, unique features) before generation
- Tagline quality evaluation: rubric-based LLM scoring (specificity, differentiation, structure novelty)
- Portfolio awareness: check recent taglines for diversity before generating new ones

**Process:**
- Structure content generation with models, not just prompts
- Forbidden phrase lists prevent generic LLM output
- Quality gates: generate → evaluate → regenerate if below threshold (up to 3 attempts)
- Temperature variation across attempts (0.7 → 0.85 → 1.0) increases diversity

**Key Insight:**
LLMs default to safe, generic language. You need structural constraints (not just instructions) to force specificity. "Here's the thing about [resort]..." beats "Welcome to [resort], a magical paradise."

---

## Round 7: External Linking & Affiliate System

**Arc:**
- **Started believing**: Affiliate links are just URL swaps
- **Ended believing**: External linking is a full pipeline stage: extract entities, resolve places, inject links, track clicks
- **Transformation**: From link insertion to entity-aware link lifecycle

**Technical:**
- Google Places entity resolution: search → get place_id → cache indefinitely
- Entity link cache (`entity_links_cache` table) stores resolved external links
- Pipeline Stage 4.9: link injection into generated content
- GA4 outbound click tracking for attribution
- 30+ affiliate programs researched across 13 categories (accommodation, packages, rentals, transport, gear, insurance)
- Affiliate config table with URL templates and domain matching rules

**Process:**
- Entity resolution before link injection ensures links point to correct businesses
- Separate research from implementation — research 30+ programs, implement top tier first
- Tiered priority: Tier 1 (must-have, high commission) → Tier 2 (high value) → Tier 3 (supplementary)
- Trust requires mixing affiliate and non-affiliate links

**Key Insight:**
Affiliate programs vary wildly: Discover Cars offers 23-54% commission with 365-day cookie, while Hotels.com offers 1-4% with 7-day cookie. Program selection matters more than link placement.

---

## Round 6: AI Discoverability & Email System

**Arc:**
- **Started believing**: Email is a simple SMTP integration
- **Ended believing**: Email is a full lifecycle system: capture, confirm, sequence, comply, track
- **Transformation**: From "send email" to email infrastructure with CAN-SPAM compliance

**Technical:**
- AI crawler whitelist in `robots.ts`: GPTBot, Claude-Web, PerplexityBot, Google-Extended, etc.
- Per-resort `llms.txt` endpoint with structured markdown for AI citation
- Global `llms.txt` indexing all resorts for AI crawler discovery
- Full email system: 7 tables (subscribers, templates, sequences, steps, sends, events, unsubscribes)
- Resend integration with DKIM + SPF + MX domain verification
- 5-email welcome sequence: Day 0 (checklist), Day 2 (Alps vs Colorado), Day 4 (age guide), Day 7 (passes), Day 14 (pick resort)
- CAN-SPAM compliance: unsubscribe endpoint, physical address, template variables
- Region extraction from resort data for location display on cards

**Process:**
- GEO (Generative Engine Optimization) is distinct from SEO — optimize for AI citation, not just crawling
- `llms.txt` format: structured markdown with citable facts, citation blocks, source attribution
- Email compliance is architecture, not an afterthought — shapes table design
- Welcome sequences build trust before selling

**Key Insight:**
AI discoverability requires active participation. Whitelisting AI crawlers in robots.txt and providing structured llms.txt endpoints makes your content citable by ChatGPT, Claude, Perplexity, etc.

---

## Round 5: Compliance & Polish

**Arc:**
- **Started believing**: These are separate compliance checkboxes
- **Ended believing**: They form an integrated observability and quality layer
- **Transformation**: From compliance tasks to quality infrastructure

**Technical:**
- Cron failure alerts via external monitoring
- WCAG 2.1 AA accessibility audit (color contrast, ARIA labels, keyboard navigation)
- Core Web Vitals reporting for performance baseline
- Trademark notices for Epic Pass, Ikon Pass references
- Internal linking between related resort pages

**Process:**
- Accessibility and compliance aren't one-time tasks — they're architectural qualities
- CWV baseline before optimization lets you measure improvement
- Internal linking improves both SEO and user navigation

---

## Round 5.2: Schema Contract Audit

**Arc:**
- **Started believing**: Schema mismatches are coding errors to fix quickly
- **Ended believing**: The extraction layer's ambition was correct — expand schema to match user needs
- **Transformation**: User-first schema design — DB should serve family budgeting needs

**Technical:**
- Extraction layer produced `lesson_group_child`, `rental_adult_daily` etc. that families need
- Database schema was designed for frontend display, not family budgeting
- Sanitization layer (`sanitize_for_schema()`) provides safety net during schema evolution
- Field name mapping handles extraction→DB name differences
- Schema whitelists are single source of truth for valid columns

**Process:**
- Convene expert panel for architectural audits
- "Autonomy in execution ≠ autonomy in evolution" — code changes need human testing
- Schema contracts must be explicit, not implicit coupling

**Key Insight:**
Ski school is often the LARGEST budget item for families with kids — more than lift tickets. The extraction layer was trying to capture what families actually need to budget.

---

## Round 5.1: Agent-Native Scalability

**Arc:**
- **Started believing**: Claude can handle lists of all 3000 resorts in context
- **Ended believing**: Primitives should be atomic; agents query, not receive lists
- **Transformation**: Two-phase validation (suggest → validate) scales infinitely

**Technical:**
- `check_resort_exists()` replaces massive name lists in prompts
- 99% token reduction (22,500 → 310 tokens)
- Transliteration via `unidecode` for international names (Zürs → Zurs)
- Country name variants (Schweiz, Österreich) handled automatically
- Google Places: Place IDs cacheable indefinitely, photos are not

**Process:**
- Measure token usage before optimization attempts
- Validate against production data, not test fixtures
- Two-phase validation: Claude suggests freely, database validates after

---

## Round 4: Production Launch

**Arc:**
- **Started believing**: Launch when feature-complete
- **Ended believing**: Launch early, iterate with real traffic
- **Transformation**: Production feedback more valuable than pre-launch polish

**Technical:**
- ISR revalidation needs POST-only endpoint with rate limiting
- Railway cron schedule syntax differs from standard cron
- Vercel deployment preview URLs differ from production for ISR

**Process:**
- Deploy to production before "ready" — real traffic reveals real issues
- Configure monitoring (Search Console, Analytics) day one
- Keep deployment simple: Railway for agents, Vercel for frontend

---

## Round 3: Security Audit

**Arc:**
- **Started believing**: Security can be added incrementally
- **Ended believing**: Legal compliance must be foundational
- **Transformation**: GDPR/CCPA compliance shapes architecture decisions

**Technical:**
- DOMPurify for all `dangerouslySetInnerHTML` usages
- Security headers in `vercel.json`: CSP, HSTS, X-Frame-Options
- Cookie consent must block GA until user consents (GDPR)
- AI disclosure component required for generated content

**Process:**
- Security audit early, not as afterthought
- Legal pages (Privacy, Terms) template from attorney review
- CAN-SPAM: privacy notice mandatory on newsletter forms

---

## Round 2: Core Agents

**Arc:**
- **Started believing**: Agents need complex orchestration frameworks
- **Ended believing**: Direct Python + Claude API simpler than MCP for autonomy
- **Transformation**: Autonomous pipelines beat interactive tools for scale

**Technical:**
- 63 atomic primitives cover all agent operations
- MCP is for interactive Claude Code sessions; cron jobs don't need it
- Voice profiles define consistent tone across all content
- Three-agent approval panel (TrustGuard, FamilyValue, VoiceCoach) for quality

**Process:**
- Build primitives first, compose into agents second
- Confidence scoring: >0.8 auto-publish, <0.6 auto-reject, middle asks Claude
- Log all reasoning for observability (`log_reasoning()`)

---

## Round 1: Foundation

**Arc:**
- **Started believing**: Need custom CMS for ski content
- **Ended believing**: Supabase + Next.js sufficient for MVP
- **Transformation**: Simplicity over features for faster launch

**Technical:**
- Next.js 14 App Router with ISR for SEO
- Supabase PostgreSQL with 23 tables (normalized schema)
- "Alpine Golden Hour" design system (coral + navy)
- TypeScript types generated from Supabase schema

**Domain:**
- Core insight: International skiing often cheaper than US resorts
- Target: Parents with kids under 12
- Voice: Instagram mom friendly (practical, encouraging, relatable)
- Content: Complete trip guides families can print and use

---

## Anti-Patterns Discovered

| Anti-Pattern | Better Approach | Round |
|--------------|-----------------|-------|
| All data in Claude's context | Atomic primitives agents query | 5.1 |
| Complex orchestration frameworks | Direct Python + Claude API | 2 |
| Security as afterthought | Legal compliance foundational | 3 |
| Launch when "ready" | Launch early, iterate | 4 |
| Formula-based confidence only | Claude for borderline decisions | 2 |
| Massive lists in prompts | Two-phase validation | 5.1 |
| Implicit schema coupling | Explicit schema whitelists + sanitization | 5.2 |
| Shrink extraction to match DB | Expand DB to match user needs | 5.2 |
| LLM opinion scores | Deterministic formulas from data | 9 |
| Generic prompt → quality | Structural models + forbidden phrases + scoring | 8 |
| Scattered env var definitions | Centralized constants with `.trim()` | 12 |
| Separate systems per content type | Shared primitive layer, different composition | 11 |
| `force-dynamic` on cacheable pages | ISR with `revalidate` | 12 |
| Building new infrastructure | Check if schema/code already exists first | 10 |
| Emoji placeholders instead of real images | AI-generated images at $0.15/ea with fallback chain | 13 |
| Rendering DB content as plain text | `dangerouslySetInnerHTML` + `sanitizeHtml()` for HTML content | 13 |
| Text floating on gradient background | White card containers with `bg-white rounded-3xl` | 13 |
| Single image provider with no fallback | 4-tier fallback chain ensures generation never blocks | 13 |

---

## Patterns That Work

| Pattern | Why It Works | Round |
|---------|--------------|-------|
| Atomic primitives | Composable, testable, cacheable | 2 |
| Two-phase validation | Claude suggests, DB validates | 5.1 |
| Three-agent approval | Diverse perspectives catch issues | 2 |
| Voice profiles | Consistent tone across content | 2 |
| Arc narratives | Capture transformation, not just tasks | 1 |
| Session close protocol | Work isn't done until pushed | 1 |
| Schema sanitization layer | Prevents failures during schema evolution | 5.2 |
| Expert panel audits | Multiple perspectives catch design issues | 5.2 |
| User-first schema design | DB should serve user needs, not technical convenience | 5.2 |
| Store atoms, compute molecules | Deterministic formulas from verifiable data | 9 |
| Editorial Verdict Model | Structure forces specificity in LLM output | 8 |
| AI crawler whitelist + llms.txt | Active participation in AI discoverability | 6 |
| Email as lifecycle system | Capture → confirm → sequence → comply → track | 6 |
| Entity-aware link injection | Resolve entities before inserting links | 7 |
| Primitive composition over new systems | Newsletter and guides share same primitives | 11 |
| Centralized constants | One source of truth prevents scattered bugs | 12 |
| Post-deploy verification checklist | Canonical, sitemap, cache headers, robots.txt | 12 |
| JSONB content schema | Structured sections render with type-specific components | 10 |
| 4-tier image fallback chain | Nano Banana → Glif → Gemini → Flux ensures generation never fails | 13 |
| Supabase Storage for permanent images | Re-upload from temporary provider URLs for permanent hosting | 13 |
| Frontend design skill | Codifies brand standards for cross-session consistency | 13 |
| Browser audit before design work | Reveals UX issues invisible in code review | 13 |
