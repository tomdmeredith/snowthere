# Snowthere Context

> Last synced: 2026-01-26
> Agent: compound-beads v2.0

## Current Round

**Round 6: AI Discoverability & Infrastructure** (in progress)
- Type: Strategic implementation
- Status: Round 6.1 + 6.4 complete, continuing to 6.2
- Goal: AI discoverability, email system, location display fixes

**North Star**: "Snowthere is THE go-to source for high value, trusted information for family ski trips anywhere in the world"

**Guiding Principles**:
- Agent-native (atomic primitives, composable, full parity)
- Probabilistic for nuance, deterministic for correctness
- SEO/GEO optimized
- Autonomous operation

**Strategic Plan**: `/.claude/plans/snuggly-herding-liskov.md`

### Round 6.1: AI Crawler Access (Completed 2026-01-26)
- Added AI crawler user agents to robots.ts: OAI-SearchBot, Perplexity-User, Google-Extended, Meta-ExternalAgent, cohere-ai
- Enhanced per-resort llms.txt with "Citable Facts" and "Quick Answers" sections for GEO optimization
- Commit: `eb6d205`

### Round 6.4: Location Display Fix (Completed 2026-01-26)
- Issue: Resorts displayed "Country" only, should show "Region, Country"
- Root cause: Region not extracted during pipeline research phase
- Fix: Added `extract_region()` primitive to intelligence.py (uses Claude Haiku)
- Integrated region extraction into runner.py after coordinates extraction
- TradingCard and resort page hero already had correct display logic
- New resorts will now have region data populated automatically

**Key Files Changed**:
- `apps/web/app/robots.ts` - AI crawler user agents
- `apps/web/app/resorts/[country]/[slug]/llms.txt/route.ts` - Citable Facts, Quick Answers
- `agents/shared/primitives/intelligence.py` - `extract_region()` primitive
- `agents/pipeline/runner.py` - Region extraction integration

### Round 6.2: Email System Foundation (Completed 2026-01-26)
- Created migration 026_email_system.sql with 7 tables:
  - subscribers: Core email list with referral tracking
  - email_templates: Reusable email templates
  - email_sequences: Automated email flows
  - email_sequence_steps: Individual steps within sequences
  - email_sends: Audit log of all emails sent
  - subscriber_sequence_progress: Track subscriber progress
  - referral_rewards: Morning Brew style referral tracking
- Created /api/subscribe endpoint with:
  - Rate limiting (5 requests/minute per IP)
  - Email validation
  - Reactivation for unsubscribed users
  - Referral code lookup
  - Auto-generated referral codes via DB trigger
- Wired Newsletter.tsx to call /api/subscribe

**Migration Pending**: Run `026_email_system.sql` via Supabase Dashboard

### Round 6.3: Lead Magnet & Welcome Sequence (Pending)
- Family Ski Trip Checklist PDF
- Resend API integration
- Welcome email series (Days 0, 2, 4, 7, 14)
- Email primitives: add_subscriber(), send_email(), trigger_sequence()

---

**Round 5.11-5.14: Compliance & Polish** (completed 2026-01-25)
- Type: infrastructure + accessibility
- Status: Complete, deployed to production
- Goal: Cron alerts, accessibility (WCAG 2.1 AA), Core Web Vitals, trademark notices

**Accomplishments**:
- **5.11 Cron Alerts**: `alert_budget_warning()`, `alert_startup_failure()`, per-resort error alerts, revalidation failure alerts
- **5.12 Accessibility**: Skip link targets on all pages, lightbox focus trap + ARIA, FAQ accordion headings, newsletter live region, mobile menu ARIA
- **5.13 Trademark**: Footer notice linking to /terms#trademark-notice
- **5.14 Core Web Vitals**: web-vitals package, WebVitalsReporter component (consent-aware), preconnect hints, hero image optimized with next/image

**Key Files Changed**:
- `agents/shared/primitives/alerts.py` - New alert primitives
- `agents/cron.py`, `agents/pipeline/orchestrator.py` - Alert integration
- `apps/web/components/WebVitalsReporter.tsx` (NEW)
- `apps/web/lib/web-vitals.ts` (NEW)
- Multiple accessibility fixes across components

**Arc Narrative**:
- We started believing: These 4 items are separate compliance checkboxes
- We ended believing: They form an integrated observability and quality layer
- The transformation: From "compliance tasks" → "quality infrastructure"

---

**Round 5.10: Internal Linking** (completed 2026-01-25)
- Type: feature
- Status: Complete, deployed to production
- Goal: Auto-link resort names in content to improve SEO, GEO, and user navigation

**Accomplishments**:
- Created `apps/web/lib/resort-linker.ts` - auto-links resort names mentioned in content
- Module-level caching for resort lookup (shared across renders)
- Name variant matching (St./Sankt/Saint, Mont/Mount, hyphenated names)
- Hyphenated resort support: "Lech-Zürs" matches "Lech" or "Zürs" separately
- Word-boundary regex matching (avoids partial matches)
- Excludes self-linking (current resort name not linked on its own page)
- Safety check for existing links (doesn't double-link)
- **SEO deduplication**: Each resort linked only once per page (first mention wins)
- Shared `linkedSlugs` tracking across all content sections
- Pre-processes content server-side in page.tsx
- Added `.resort-link` styling with coral underline
- Changed ISR revalidation from 1 hour to 12 hours
- Fixed Next.js 14.1.0 sitemap bug (converted to route handler pattern)

**Key Files Changed**:
- `apps/web/lib/resort-linker.ts` (NEW)
- `apps/web/app/resorts/[country]/[slug]/page.tsx` (MODIFIED)
- `apps/web/app/sitemap.xml/route.ts` (NEW - replaced sitemap.ts)
- `apps/web/app/globals.css` (MODIFIED)

**Arc Narrative**:
- We started believing: Internal linking needs a complex agent system with databases, APIs, Claude-generated anchor text
- We ended believing: The user's actual need is simple: when content mentions a resort, make it clickable
- The transformation: From "build a system" → "add a utility function"

## Round 5.9.8: Site Stabilization (completed 2026-01-25)
- Type: bug fixes
- Status: Completed
- Goal: Fix critical UX issues found in site audit

**Accomplishments**:
- Fixed homepage ranking: 9/10 resorts now appear before 8/10
  - Root cause: Supabase returns `family_metrics` as object (1:1), not array
  - Fix: Added `getScore()` helper to handle both object and array formats
- Fixed sidebar layout on resort pages:
  - Jump to Section now appears above Useful Links
  - Left/right columns now top-aligned (`items-start` on grid)
- Hidden social link placeholders in Footer (no accounts yet)
- Changed "See All 3,000+ Resorts" to "Browse All Resorts"
- Set homepage to `force-dynamic` for fresh data on each request

**Key Files Changed**:
- `apps/web/app/page.tsx` - Homepage ranking fix, dynamic rendering
- `apps/web/components/home/TradingCardGrid.tsx` - Interface fix
- `apps/web/components/home/Footer.tsx` - Social links hidden
- `apps/web/app/resorts/[country]/[slug]/page.tsx` - Sidebar order/alignment

**Arc Narrative**:
- We started believing: The homepage sorting code was correct
- We ended believing: Supabase's foreign table data structure differs from TypeScript expectations
- The transformation: From "sorting bug" → "data shape mismatch between DB and code"

## Round 5.9.7: Site Polish (Completed 2026-01-24)

**Goal**: Visual polish, taglines, voice improvements

**Accomplishments**:
- Added taglines to resort cards and hero sections
- Fixed voice pattern post-processing
- Location display improvements (region, country)
- Courchevel and Niseko images added
- Archived Kitzbühel duplicate

## Round 5.9.6: Growth Mode (Completed 2026-01-24)

- Type: config change
- Goal: Increase pipeline throughput to grow the site faster

**Changes**:
- `max_resorts`: 4 → 8 (process more per run)
- `discovery_pct`: 30% → 70% (prioritize new resorts)
- `quality_pct`: 50% → 10% (quality queue empty due to cooling off)
- `stale_pct`: 20% → 20% (maintain some refresh)

**Expected Output**: ~6 resorts per run (5 discovery + 1 stale)
- ~250 discovery candidates seeded from migration 017

## Round 5.9.5: Pipeline Bug Fixes (Completed)

**Bug 1: Stale Confidence Score**
- Fix: Recalculate confidence after cost acquisition

**Bug 2: Duplicate Resorts from Unicode Slugs**
- Fix: Added `unidecode` to slugify function

## Round 5.9.4: Sidebar Polish (Completed)

**Goal**: Hide incomplete data tables, fix sidebar UX

**Accomplishments**:
- Hidden FamilyMetricsTable ("The Numbers") - incomplete data showing dashes
- Fixed JumpToSection sticky offset (top-8 → top-24) - was hiding behind navbar
- Added scroll-padding-top to globals.css - anchor links now scroll correctly
- Documented future work items in Active Tasks section

## Round 6: Homepage Redesign (pending)
- Type: feature
- Status: Not started
- Goal: Implement chosen homepage design from concepts

## Round 5.9: Resort Data Gaps + Country Pages (Completed)

**Goal**: Fix issues identified in Round 5.8 audit, create country landing pages

**Accomplishments**:
- Created `apps/web/app/resorts/[country]/page.tsx` - country landing pages
- Fixed St. Anton family metrics (Score 7, Ages 8-16, ski_school_min_age 3)
- Added cost data for all 3 resorts (Park City USD, St. Anton EUR, Zermatt CHF)
- Fixed St. Anton trail map data (300 runs, 88 lifts - was incorrectly showing 13 runs)
- Fetched hero images for Park City and St. Anton via Google Places API
- Created `agents/scripts/fix_resort_data_gaps.py` for database fixes
- Created `agents/scripts/fetch_hero_images.py` for hero image pipeline
- Created migration `020_fix_resort_data_gaps.sql` (backup SQL)

**Issues Fixed**:
- C1: Missing hero images (Park City, St. Anton) → NOW HAVE REAL PHOTOS
- C2: Country pages 404 → NOW WORK (`/resorts/united-states`, `/resorts/austria`, etc.)
- C3: Missing family metrics (St. Anton) → NOW HAS SCORE 7, AGES 8-16
- M1: Cost data all empty → ALL 3 RESORTS NOW HAVE PRICING
- M2: Trail map wrong data (St. Anton) → FIXED TO 300 RUNS, 88 LIFTS

**Arc Narrative**:
- We started believing: Data gaps were systemic pipeline failures needing code fixes
- We ended believing: Data gaps were one-time extraction failures; simple SQL + scripts fix them
- The transformation: From "fix the pipeline" → "run targeted data patches then improve gates"

## Round 5.8: Resort Page Audit (Completed)

**Goal**: Comprehensive audit of 3 resort pages (Park City, St. Anton, Zermatt)

**Key Findings**:
- Zermatt = "Gold standard" with real hero photo, complete data
- Park City and St. Anton had placeholder images, missing data
- All pages had empty cost data
- St. Anton missing family metrics entirely
- Country pages returned 404 (breadcrumb links broken)

**Deliverable**: `.compound-beads/resort-page-audit-round-5.8.md`

## Round 5.7: Search API Quality + Tracking (Completed)

**Goal**: Empirically compare Exa/Brave/Tavily, implement research caching

**Accomplishments**:
- Full API comparison: 70 queries × 3 APIs × 5 results = 1050 evaluations
- **Tavily wins ALL 7 query types** (composite score 3.85 vs Exa 3.55, Brave 3.53)
- Tavily has 2x better price discovery (25.7% vs ~13%)
- URL overlap only 25.9% - each API provides unique sources (keep all 3)
- Created `agents/scripts/api_comparison/` test suite
- Created migration 019_research_cache.sql (research_cache + resort_research_sources tables)
- Added per-API cost logging to research.py
- Integrated caching into production pipeline

**Key Insight**: Data beats assumptions. We thought Exa would win for family reviews (semantic search),
but Tavily's AI synthesis outperforms on ALL categories. Keep all APIs for URL diversity.

**Arc Narrative**:
- We started believing: Three APIs must be better than one, each with different strengths
- We ended believing: Tavily dominates all categories; diversity value is in unique URLs, not specialization
- The transformation: From API routing by query type → Tavily-first with diversity fallbacks

**Migration Required**: Run `supabase/migrations/019_research_cache.sql` via Supabase Dashboard

## Round 5.2: Schema Contract Audit (Completed)

**Goal**: Fix schema mismatch causing 100% pipeline failure

**Accomplishments**:
- Identified root cause: extraction layer produced fields DB didn't have
- Added `sanitize_for_schema()` safety layer to database.py
- Created migration 016: adds lesson costs, rental costs, lift_under6
- Aligned extraction schema with database columns exactly
- Expert panel audit (Architecture, Data Integrity, FamilyValue, Philosopher)

**Key Insight**: The extraction layer was RIGHT - families need ski school and rental costs.
The DB schema was incomplete. Expand schema to match user needs, don't shrink capabilities.

## Round 5.1: Agent-Native Scalability (Completed)

**Goal**: Scale duplicate detection to 3000+ resorts

**Accomplishments**:
- New primitives: `check_resort_exists()`, `find_similar_resorts()`, `count_resorts()`
- Two-phase validation: Claude suggests → DB validates
- 99% token reduction (22,500 → 310 tokens)
- Transliteration via unidecode for international names

**Key Insight**: Primitives should be atomic; agents query, not receive massive lists.

## Round 5: Compliance & Polish (Completed 2026-01-25)

**Goal**: Monitoring, accessibility, final polish

**Completed tasks**:
- [x] Cron failure alerts (5.11)
- [x] Accessibility audit - WCAG 2.1 AA (5.12)
- [x] Trademark notices (5.13)
- [x] Core Web Vitals reporting (5.14)

## Round 4: Production Launch (Completed)

**Goal**: Deploy to production, configure monitoring

**Key outcomes**:
- www.snowthere.com live on Vercel
- Railway cron (creative-spontaneity) running daily
- Google Search Console + Analytics configured
- Supabase production with 23 tables

## Active Tasks

**Round 6: Homepage Redesign** (next)
- Finalize homepage design direction
- Implement new homepage components
- A/B test conversion

**Future Work** (moved from Round 4):
- Newsletter signup API integration
- Monitor and iterate on pipeline quality

## Future Work (Round 6+)

### Sorting UI for Listings
- Add sort dropdown to `/resorts` page (by score, by name, by country)
- Add sort dropdown to `/resorts/[country]` pages
- Consider filters (age range, budget, pass compatibility)

### Improve Data Tables
- Fix CostTable data quality (real prices from research)
- Fix The Numbers data completeness (all metrics populated)
- Re-enable CostTable and FamilyMetricsTable when data is reliable

### Checklist Download Feature
- Create actual PDF/printable checklist
- Wire up "Get the Checklist" button to download or email capture
- Consider lead magnet flow (email → checklist)

### Decimal Scores
- Migrate `family_overall_score` from INTEGER to DECIMAL(3,1)
- Enable nuanced rankings (8.6, 8.7, etc.)

### Internal Linking Enhancements (Low Priority)
> Build only if data shows need - Round 5.10 baseline is sufficient

- Click tracking for internal links (if we need to measure link CTR)
- JSON-LD `relatedLink` schema (if AI citation testing shows schema helps)
- "Also mentioned" sidebar section (if users request more discovery)
- Link hover preview showing destination (if users want to see where links go)

## Key Files

| Category | Files |
|----------|-------|
| **Pipeline** | `agents/pipeline/runner.py`, `orchestrator.py`, `decision_maker.py` |
| **Primitives** | `agents/shared/primitives/` (63 atomic operations) |
| **Frontend** | `apps/web/app/resorts/[country]/[slug]/page.tsx` |
| **Config** | `agents/shared/config.py`, `CLAUDE.md` |

## Infrastructure

| Service | Status |
|---------|--------|
| Vercel | www.snowthere.com (live) |
| Railway | creative-spontaneity (daily cron) |
| Supabase | Snowthere (23 tables, AWS us-east-2) |

## Recent Commits

- `f7390ed` Round 5.11-5.14: Cron alerts, accessibility, CWV, trademark
- `e764dac` SEO fix: Link each resort only once per page (first mention wins)
- `483a43c` Round 5.10: Auto-link resort names in content
- `9f3736c` fix: Sort resorts by family score (handle object/array family_metrics)
- `4b405a1` fix: Sidebar layout - Jump to Section above Useful Links, align top
