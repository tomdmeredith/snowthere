# Learnings

Knowledge extracted across all rounds with Arc narratives.

---

## Round 22: MEO Optimization + Voice De-Mandating

**Arc:**
- **Started believing**: Prescriptive voice rules (80/20 ratio, mandatory patterns per section) produce consistent quality
- **Ended believing**: Prescriptive rules produce formulaic content — probabilistic personality guidance with anti-repetition lets the LLM internalize voice rather than mechanically satisfy checklists
- **Transformation**: From mandating voice patterns to trusting the model with personality guidance, and from traditional SEO to Meaning Engine Optimization for AI citation

**Technical:**
- Exa is trained on LINK PREDICTION ("which URL follows this text"), not text similarity — titles should match how people describe links when sharing
- Princeton GEO study (peer-reviewed, 10K queries): Quotations +41%, Statistics +33%, Fluency +29%, Citing sources +28%, Keyword stuffing -9%
- Content updated within 30 days gets 3.2x more AI citations — date freshness signals matter
- Selective entity names in headings (2 of 6) balances RAG chunk independence vs keyword stuffing penalty
- Question-based headings match how people query AI systems ("How do I get to Serfaus?")
- Self-contained paragraphs survive AI extraction independently — each paragraph must make sense without the headline
- Probabilistic voice guidance ("emerge NATURALLY, never forced") produces more varied, natural content than prescriptive rules ("Use at least ONE per section")
- Triple-layer instruction reinforcement (voice profile + system prompt + section prompts) is intentional belt-and-suspenders for LLM compliance, not duplication
- `generate_seo_meta()` fallback titles must match frontend title format — otherwise stored SEO meta creates split-brain title strategy
- `month: 'short', day: 'numeric', year: 'numeric'` for compact date displays (sidebar), `month: 'long'` for full displays

**Process:**
- Deep research before implementation: Exa, ChatGPT, Perplexity architecture research informed every MEO decision
- Browser-based UI testing catches rendering issues invisible in code (QuickScoreSummary had a second date display needing update)
- Multiple date format components need synchronized updates — search for all date formatting in the codebase
- Expert review panels (7 reviewers) catch consistency gaps across files (approval.py, MCP server still reference old voice)

**Key Insight:**
LLMs work better with internalized personality ("you write like a smart friend who respects time") than with mechanical checklists ("use at least one Pro tip per section, maintain 80/20 fragment ratio"). The former produces varied, natural content; the latter produces formulaic content where every resort reads the same.

---

## Round 21: Voice Rebalancing — Wirecutter + Personality

**Arc:**
- **Started believing**: The Instagram mom voice was the right voice for family ski content
- **Ended believing**: A Morning Brew / Wirecutter style (smart, practical, witty) serves families better than performative enthusiasm — parents are intelligent adults doing research
- **Transformation**: From performative encouragement to respectful intelligence — the voice shift from "Instagram mom" to "smart friend who respects your time"

**Technical:**
- Voice identity shift from "Instagram mom" to "Morning Brew for family ski trips" — smart, witty, efficient
- Future-casting ("You'll find...", "Your kids will...") helps readers envision themselves at the resort
- Self-contained paragraph rule: every paragraph must make sense without reading the section headline — critical for AI extraction
- Child price floor `max(child_price, adult_price * 0.5)` prevents $0 child prices from data gaps
- Multilingual research queries (searching in German/French/Japanese) improve data quality for international resorts
- Thin content gate (< 200 words per section, < 3 substantial sections per resort) catches under-researched content
- Em-dash ban is non-negotiable — LLMs default to em-dashes; explicit prohibition needed at every prompt level
- "Dropping articles" (a, the, an) is a common LLM failure mode when told to be "efficient" — must explicitly require natural prose

**Process:**
- Voice profiles define WHO you're writing as, system prompts define HOW to write — keep them separate
- Multiple rounds of expert review (3 rounds for voice changes) catches subtle inconsistencies
- Legacy aliases (`instagram_mom` → `SNOWTHERE_GUIDE`) maintain backward compatibility during transition
- Voice calibration needs concrete examples, not just descriptions — show the LLM what good looks like

**Key Insight:**
"Instagram mom" was gendered and performative. "Smart friend who respects your time" is gender-neutral and substantive. Parents researching ski trips are intelligent adults — they want intel, not encouragement. The voice should inform, not perform.

---

## Round 20: Content Quality & Linking Overhaul + Type Safety

**Arc:**
- **Started believing**: Content quality improvements and type safety are separate concerns
- **Ended believing**: Content quality, type safety, and security hardening form a single trust layer — users trust accurate content, TypeScript catches data shape bugs, sanitization prevents injection
- **Transformation**: From treating content, types, and security as independent workstreams to a unified quality-and-trust layer where each reinforces the others

**Technical:**
- Strong-tag-first entity extraction: parse `<strong>` tags from HTML content before falling back to LLM extraction — eliminates ~$0.03/resort Claude API call
- IATA code extraction from content enables automatic Skyscanner flight search URL generation (no API call needed)
- Quick Takes at 50-90 words (single paragraph, validation accepts up to 95) outperform 80-120 word 4-part editorial model for scannability
- Tagline forbidden pattern regex blocklist prevents "hidden gem", "world-class", "winter wonderland" etc. — more effective than prompt instructions alone
- Three-layer hybrid scoring (structural 30% + content LLM 50% + review 20%) provides balanced quality signal
- Completeness multiplier on structural score caused double-penalty with data_completeness gate — removed
- Dollar sign fallback (`$$` when NULL) ensures every resort card shows pricing signal, avoids blank badges
- `as unknown as T` pattern for Supabase complex join returns — safer than `as any` and preserves type checking
- Supabase returns object for 1:1 joins and array for 1:many joins — interface must handle both shapes
- `sanitizeHTML()` via `sanitize-html` library strips dangerous tags/attributes while preserving safe formatting
- `sanitizeJSON()` escapes `<`, `>`, `&` in JSON-LD `<script>` blocks to prevent script injection
- Never use `as any` for Supabase join types — define intermediate interfaces that handle both object and array returns

**Process:**
- Type safety and security hardening should be done together — both are about correctness and trust
- Expert review panels (7 reviewers across security, TypeScript, Python, simplicity, performance) catch issues invisible in self-review
- UI testing via browser (Playwright MCP) is essential — confirms components render correctly with real data
- Backfill scripts should support `--dry-run` for cost estimation before real execution

**Key Insight:**
Content quality, TypeScript type safety, and HTML/JSON sanitization form a single trust layer. Users trust accurate Quick Takes, TypeScript catches data shape bugs at build time, and sanitization prevents injection at render time. Treating them as separate workstreams leaves gaps; treating them as one layer reinforces each part.

---

## Round 19: SEO Fixes, Programmatic Pages & Country Content

**Arc:**
- **Started believing**: The homepage H1 was rendering correctly and country pages were properly configured
- **Ended believing**: Client components hide H1 from crawlers, missing generateStaticParams prevents static generation, and 12h ISR is too slow for content updates
- **Transformation**: From trusting client-rendered content to ensuring all critical SEO elements are server-rendered and statically generated

**Technical:**
- `'use client'` on a component containing H1 makes it invisible to crawlers — critical SEO elements must be server components
- `generateStaticParams()` missing from dynamic routes prevents Next.js from pre-rendering pages at build time
- ISR at 12h is too slow for content pipeline that updates daily — 6h is a better balance
- Programmatic collection pages (best-for-beginners, best-for-toddlers, etc.) provide additional crawlable entry points
- Next.js route constraint: can't have `[collection]` and `[country]` dynamic segments at the same level under `/resorts/` — use `/collections/` path instead
- Country intro content via AI generation improves thin country listing pages for SEO
- Vercel 308 redirects handle canonical normalization (www vs non-www) — duplicates in GSC are legacy entries that will resolve

**Process:**
- Always verify H1 tags are server-rendered — inspect page source, not DevTools
- Check that all dynamic routes have `generateStaticParams()` for proper static generation
- Programmatic SEO pages should be data-driven (query DB for resorts matching criteria)
- Country pages benefit from intro content to avoid thin content penalties

**Key Insight:**
The difference between "looks right in the browser" and "visible to crawlers" is server vs client rendering. A beautiful H1 inside a `'use client'` component is invisible to Google. Always verify critical SEO elements in page source.

---

## Pipeline Improvements (PI)

**Arc:**
- **Started believing**: Entity extraction confidence scores were appropriate and stale detection worked correctly
- **Ended believing**: Conservative extraction was missing valid entities; stale detection had a bug returning N oldest instead of actually stale; full refresh is overkill for maintenance
- **Transformation**: From accepting pipeline defaults to targeted improvements that increase link density 3x and reduce refresh costs 85%

**Technical:**
- LLM entity extraction defaults to conservative confidence scores — explicit guidance with concrete examples (e.g., "Kandahar Lodge → 0.9") increases yield 3x
- Multi-entity JSON examples in extraction prompts produce more entities than single-entity examples
- Confidence threshold 0.6 → 0.5 captures valid entities without introducing noise
- Major cities (Sandy, Draper, Vancouver) must be explicitly excluded from entity extraction
- Light refresh mode (~$0.50 vs ~$3) updates costs, entity links, and images without re-researching or re-generating content
- JSON serialization of dataclasses needs `json.dumps(metadata, default=str)` — dataclasses aren't JSON-serializable by default
- Stale detection bug: calculating cutoff date but not using it in the query filter — always test query results against expectations

**Key Insight:**
Pipeline defaults accumulate hidden costs: conservative extraction misses 2/3 of valid entities, stale detection refreshes wrong resorts, and full refresh wastes $2.50/resort on unchanged content. Targeted improvements to each default multiplied effectiveness without increasing complexity.

---

## Linking Strategy Overhaul (LS)

**Arc:**
- **Started believing**: External linking is a flat priority chain — affiliate beats direct beats maps for everything
- **Ended believing**: Link destinations must match user intent by entity type — parents want to book hotels, get restaurant directions, register for ski school
- **Transformation**: From generic link injection to context-aware destinations that match what parents actually do with each entity type

**Technical:**
- Data-driven priority table per entity type replaces nested if/elif chains — easier to maintain and reason about
- Hotels → affiliate > direct > maps (parents book online)
- Restaurants → maps > direct (parents need directions)
- Ski schools → direct > maps (parents register online)
- UTM medium `in_content` distinguishes entity links from sidebar links (`resort_page`) for attribution
- `rel="noopener"` (no nofollow) on entity links sends referrer for partner traffic attribution
- `rel="sponsored noopener"` on affiliate links satisfies Google's sponsored link requirement
- `html.escape(url, quote=True)` before href interpolation prevents XSS via crafted URLs
- sanitize.ts rel allowlist (`noopener`, `noreferrer`, `nofollow`, `sponsored`, `ugc`) prevents arbitrary attribute injection

**Key Insight:**
A parent looking up "Hotel Sonne Zermatt" wants to book a room. A parent looking up "Chez Vrony" wants driving directions. Link destinations should match the action users take with each entity type, not follow a universal priority order.

---

## Round 16: Error Handling & Polish

**Arc:**
- **Started believing**: Error handling and polish is about adding safety nets around existing code
- **Ended believing**: Polish means building complete interactive experiences — filtering, loading, error recovery, and privacy rights are all user-facing quality
- **Transformation**: From defensive code additions to cohesive user experience where every state (loading, empty, error, filtered) is intentionally designed

**Technical:**
- URL search params as single source of truth for filter state — `useSearchParams()` + `router.push()` makes every filter combination shareable and bookmarkable
- Debounced search input (300ms) prevents excessive URL updates while typing — `setTimeout` + cleanup in `useEffect`
- Country-grouped display (default sort) vs flat list (price/A-Z sort) gives users two mental models for browsing
- Active filter chips with `×` removal + "Clear all" provides clear escape hatch from deep filtering
- Sticky filter bar with `backdrop-blur-lg` keeps controls accessible without obscuring content
- Loading skeletons should match page structure (breadcrumb, hero, filter bar, card grid) — not generic spinners
- `animate-pulse` on skeleton blocks provides implicit loading feedback without JavaScript
- Custom 404 page with actionable CTAs ("Browse resorts", "Go home") recovers lost users
- GDPR data request form: toggle between deletion/access with coral/teal active states matches Spielplatz design language
- In-memory rate limiting (`Map<string, {count, resetAt}>`) works for single-instance deployments; use Redis for multi-instance
- Migration 036 unique index `(email, request_type, created_at::date)` prevents duplicate same-day requests at DB level
- CSP `img-src` should use `https:` not `http:` to prevent mixed content; `object-src 'none'` blocks Flash/Java embeds

**Process:**
- Browser testing with Playwright MCP tools catches issues invisible in dev: scroll behavior, sticky positioning, mobile layouts, filter chip overflow
- Test from customer perspectives (first-time visitor, parent with toddlers, power user) reveals different UX paths through the same features
- URL state testing: navigate directly to filtered URL in new tab — if filters don't restore, the URL isn't the source of truth
- Empty state design matters: "No resorts match" with clear filters button + newsletter CTA turns dead ends into engagement
- Build verification (`pnpm build`) after all changes catches SSR issues that dev mode misses

**Key Insight:**
A "polish" round isn't minor fixes — it's the difference between a site that works and a site that feels intentional. Loading skeletons, empty states, error recovery, and URL-synced filters make users trust the product. Every UI state (loading, empty, error, success, filtered) is a design decision.

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
| Generic loading spinner | Skeleton matching actual page structure (breadcrumb, hero, cards) | 16 |
| Filter state in component state | URL search params as single source of truth (shareable, bookmarkable) | 16 |
| Dead-end empty states | Actionable empty states with clear filters + newsletter CTA | 16 |
| Default browser 404 | Branded 404 with actionable recovery CTAs | 16 |
| `as any` for Supabase join types | Define intermediate interfaces handling both object and array returns | 20 |
| Flat link priority (affiliate > direct > maps for all) | Context-aware priority per entity type (hotel→book, restaurant→maps) | LS |
| 80-120 word 4-part Quick Takes | 50-90 word single paragraph (more scannable, accepts up to 95) | 20/21 |
| `'use client'` on components with H1 | Server component for all critical SEO elements | 19 |
| Missing `generateStaticParams()` on dynamic routes | Always add for proper static generation | 19 |
| LLM extraction with generic confidence guidance | Concrete confidence examples (e.g., "Kandahar Lodge → 0.9") | PI |
| Full refresh for stale resorts (~$3) | Light refresh for unchanged content (~$0.50, 85% savings) | PI |
| Nested if/elif for link destination logic | Data-driven priority table per entity type | LS |

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
| URL search params as filter state | Every filter combination is shareable and bookmarkable | 16 |
| Skeleton loaders matching page structure | Users perceive faster loading when skeleton mirrors final layout | 16 |
| Customer perspective test walkthroughs | Different user types reveal different UX paths through same features | 16 |
| Actionable error/empty states | Recovery CTAs turn dead ends into engagement | 16 |
| Sticky filter bar with backdrop blur | Controls stay accessible during scroll without obscuring content | 16 |
| `as unknown as T` for Supabase joins | Safer than `as any` — preserves downstream type checking | 20 |
| `sanitizeHTML()` on all dangerouslySetInnerHTML | Defense-in-depth against stored XSS from DB content | 20 |
| `sanitizeJSON()` on all JSON-LD blocks | Prevents script injection via crafted schema data | 20 |
| Strong-tag-first entity extraction | Parse `<strong>` from HTML before LLM fallback — saves $0.03/resort | 20 |
| Three-layer hybrid scoring | Structural + content LLM + review balances objectivity and nuance | 20 |
| Forbidden pattern regex blocklist | More effective than prompt instructions for preventing generic LLM output | 20 |
| Context-aware link destinations | Match link target to user intent per entity type | LS |
| Light refresh mode for stale resorts | Updates costs/links/images without full re-research — 85% cost reduction | PI |
| Concrete confidence examples in extraction prompts | "Kandahar Lodge → 0.9" yields 3x more entities than generic guidance | PI |
| Server components for SEO-critical elements | H1, meta tags, JSON-LD must be server-rendered for crawler visibility | 19 |
| Programmatic collection pages from DB queries | Data-driven pages (best-for-beginners, etc.) create crawlable entry points | 19 |
| `html.escape(url, quote=True)` before href interpolation | Defense-in-depth against XSS via crafted URLs in entity links | LS |
| Expert review panel (7 reviewers) | Security, TypeScript, Python, simplicity, performance catch different issues | 20 |
| Probabilistic personality guidance over prescriptive rules | LLM internalizes voice personality, produces varied natural content instead of formulaic | R22 |
| Link-predictive title format | Matches Exa's link prediction model — "which URL follows this text" | R22 |
| Question-based headings with selective entity names | 2/6 entity names balances RAG independence vs keyword stuffing (-9%) | R22 |
| Anti-repetition as explicit system prompt section | Dedicated block prevents LLMs from restating facts across sections | R22 |
| Source attribution in content | "According to..." improves AI citation rate by +28% (Princeton GEO) | R22 |
| Content freshness date with day | Precise dates signal 30-day freshness threshold for 3.2x more citations | R22 |
| Deep MEO research before implementation | Understanding how Exa/ChatGPT/Perplexity work informed every optimization | R22 |
| Future-casting ("You'll find...", "Your kids will...") | Readers envision themselves at the resort — engagement and specificity | R21 |
| Self-contained paragraphs | Each paragraph makes sense independently — critical for AI extraction | R21 |
| Multilingual research queries | Searching in local language improves data quality for international resorts | R21 |

---

## Prevention Rules

Concrete rules distilled from past failures. Never repeat these.

| Rule | What Happened | Round |
|------|---------------|-------|
| Never use `force-dynamic` on cacheable pages | Homepage returned `private, no-cache, no-store`, telling crawlers the page was private | R12 |
| Never define `BASE_URL` in multiple files | 6 of 7 files lacked `.trim()`, trailing newline broke all canonical URLs and sitemap | R12 |
| Never default boolean family metrics to `true` | `has_childcare`, `has_magic_carpet`, `has_ski_school` defaulting true inflated scores for resorts with missing data | Data Quality |
| Never put all resort names in an LLM prompt | 22,500 tokens at 3000 resorts; use atomic primitives instead | R5.1 |
| Never trust LLM-generated scores as authoritative | LLMs cluster scores at 7-9 (safe, non-committal); use deterministic formulas from data | R9 |
| Never use temporary image URLs for permanent storage | Replicate/Glif URLs expire; always re-upload to Supabase Storage | R13 |
| Never render DB content as plain text if it may contain HTML | Use `dangerouslySetInnerHTML` + `sanitizeHtml()` for any stored content | R13 |
| Never assume API keys work across Google Cloud projects | Keys from Tom Global don't work for Snowthere project APIs | R13.2 |
| Never use `as any` for Supabase complex join returns | Define proper intermediate types; use `as unknown as T` — `as any` silently disables all type checking downstream | R20 |
| Never put H1 or critical SEO elements inside `'use client'` components | Client components are invisible to crawlers — server-render all SEO-critical content | R19 |
| Never omit `generateStaticParams()` from dynamic routes | Without it, Next.js won't pre-render pages at build time, hurting crawl efficiency | R19 |
| Never use `dangerouslySetInnerHTML` without `sanitizeHTML()` | All DB content may contain malicious HTML — sanitize at every render point | R20 |
| Never inject JSON-LD without `sanitizeJSON()` | Crafted data could contain `</script>` and break out of JSON-LD block | R20 |
| Never mandate specific pattern frequencies in LLM prompts | "Use at least ONE Pro tip per section" produces mechanical, predictable content | R22 |
| Never mandate specific sentence structure ratios | "80/20 fragment ratio" and "2-3 fragments per section" produce staccato, formulaic prose | R22 |
| Never have multiple date format components without syncing them all | QuickScoreSummary.tsx had a second date display that was missed on first pass | R22 |
| Never let `generate_seo_meta()` fallback diverge from frontend title format | Split-brain title strategy: some pages use old format, some new | R22 |

---

## Dead Ends Registry

Approaches tried and abandoned. Don't revisit these.

| What Was Tried | Why It Failed | What Worked Instead | Round |
|----------------|---------------|---------------------|-------|
| Complex orchestration frameworks (MCP) for autonomous execution | Protocol overhead unnecessary for cron jobs; MCP is for interactive sessions | Direct Python + Claude API | R2 |
| LLM opinion scoring (ask Claude "rate this resort 1-10") | Scores clustered at 7-9, no differentiation, not explainable | Deterministic formula: base 5.0 + weighted components from data | R9 |
| Emoji placeholders for guide images | Looked cheap, undermined perceived quality | AI-generated images at $0.15/ea via Nano Banana Pro | R13 |
| Single image provider (no fallback) | Provider outages blocked content publication | 4-tier fallback: Nano Banana Pro → Glif → Gemini → Flux Schnell | R13 |
| Generic "loading..." spinner | Users perceived slow loading, no structural context | Skeleton loaders matching actual page structure | R16 |
| Shrinking extraction schema to match DB | Lost family-relevant budget data (lesson costs, rental prices) | Expanded DB schema to match what families actually need | R5.2 |
| `robots.txt/route.ts` alongside `robots.ts` | Route handler silently overrode the comprehensive version | Single `robots.ts` file | R12 |
| `as any` casts for Supabase joins (~15 instances) | Silently bypassed all type checking, hiding real data shape bugs | Intermediate interfaces with `as unknown as T` | R20 |
| 4-part Editorial Verdict Model for Quick Takes (80-120 words) | Too long for scanning, parents want quick verdict not structured essay | 50-90 word single paragraph with specific facts (accepts up to 95) | R20/21 |
| Completeness multiplier in structural score | Double-penalized with data_completeness gate — low completeness resorts penalized twice | Removed multiplier, kept separate data_completeness gate | R20 |
| Universal link priority (affiliate > direct > maps) | Doesn't match user intent — parent wanting restaurant directions gets booking page | Per-entity-type priority table matching user action | LS |
| Full refresh for every stale resort (~$3/resort) | Most resort data doesn't change — re-researching is waste | Light refresh (~$0.50) for costs, links, images only | PI |
| Prescriptive voice rules ("80/20 ratio", "at least ONE per section") | LLM mechanically satisfies checklists, producing formulaic content | Probabilistic personality guidance ("emerge NATURALLY, don't force a ratio") | R22 |
| Generic section headings ("Getting There") | Headings lose context when AI extracts as independent chunks | Question-based headings with selective entity names for RAG chunk independence | R22 |
| "{Resort Name} Family Ski Guide" title format | Doesn't match how people describe links when sharing | "Family Ski Guide: {Name} with Kids" (link-predictive, matches Exa's model) | R22 |
| Date showing only month+year ("Feb 2026") | Ambiguous freshness signal, doesn't satisfy 30-day freshness criteria | Include day ("Feb 7, 2026") for precise freshness signal | R22 |
| Performative "Instagram mom" voice | Gendered, patronizing; parents want intel, not encouragement | "Smart friend who respects your time" — gender-neutral, substantive | R21 |

---

## Recognized Patterns

Recurring situations and the best response. When you see X, do Y.

| When You See... | Do This | Because | Rounds |
|-----------------|---------|---------|--------|
| Pages not being indexed | Check infrastructure (env vars, headers, cache) before content | Trailing newlines, wrong domains, and cache headers block indexing silently | R12, R13.1 |
| A new content type needed (newsletter, guides, etc.) | Compose from existing primitives, don't build new system | All content types share the same generate/store/publish primitives | R10, R11 |
| Schema mismatch crash in pipeline | Add column whitelist to sanitization layer, then expand schema | Sanitize first (prevent crash), then design schema for user needs | R5.2, R9 |
| LLM output is generic/bland | Add structural constraints: forbidden phrases, editorial models, specificity scoring | Instructions alone don't force specificity; structure does | R8 |
| Data from multiple providers/APIs | Implement fallback chain with graceful degradation | Single-provider dependency blocks entire pipeline on outage | R13 |
| Environment variable used in multiple files | Centralize in one constants file with `.trim()` | Scattered definitions guarantee inconsistency | R12 |
| New feature touches user-facing states | Design all states: loading, empty, error, success, filtered | Every undesigned state is a UX gap users will find | R16 |
| Supabase query returns unexpected shape | Define interfaces handling both object (1:1) and array (1:many) join returns | Supabase join return types vary by relationship cardinality | R20 |
| `dangerouslySetInnerHTML` anywhere in codebase | Immediately add `sanitizeHTML()` wrapper — no exceptions | All DB content is potential XSS vector | R20 |
| JSON-LD `<script>` block with DB data | Wrap in `sanitizeJSON()` to escape `<`, `>`, `&` | Crafted data could break out of script block | R20 |
| Entity extraction returns few results | Add concrete confidence examples + lower threshold + multi-entity JSON template | Default LLM extraction is too conservative | PI |
| Links need different behavior per entity type | Build data-driven priority table, not nested conditionals | User intent varies: booking vs directions vs registration | LS |
| Client component renders SEO-critical content | Move to server component or extract server-rendered wrapper | Crawlers can't see client-rendered content | R19 |
