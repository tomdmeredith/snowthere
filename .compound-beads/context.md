# Snowthere Context

> Last synced: 2026-01-26 (Round 8.1)
> Agent: compound-beads v2.0

## Current Round

**Round 8.1: Comprehensive Site Audit & Fixes** ✅ COMPLETE
- Type: Bug fixes + missing pages
- Status: Complete - /about, /contact, /api/contact created
- Goal: Fix critical 404s on footer links discovered during comprehensive audit

### Round 8.1: Site Audit & Fixes (Completed 2026-01-26)

**Problem Statement:**
Comprehensive site audit revealed critical issues:
- `/about` returned 404 (linked in footer)
- `/contact` returned 404 (linked in footer)
- No mechanism for visitors to contact the team

**Audit Coverage:**
| Area | Status | Notes |
|------|--------|-------|
| Homepage | ✅ Pass | All sections load correctly, age selector works |
| /resorts | ✅ Pass | 29 resorts across 8 countries displayed |
| /guides | ✅ Pass | "Coming Soon" state (expected) |
| /quiz | ✅ Pass | 7-question flow works with progress tracking |
| Resort pages | ✅ Pass | All content sections render, internal links work |
| Newsletter signup | ✅ Pass | /api/subscribe returns 200, GA4 event fires |
| GA4 tracking | ✅ Pass | page_view, scroll, form_start, newsletter_signup, click events |
| Outbound click tracking | ✅ Pass | External links fire click event with outbound=true |
| /privacy | ✅ Pass | Page loads correctly |
| /terms | ✅ Pass | Page loads with trademark notice anchor |
| /about | ❌→✅ | Was 404, now created |
| /contact | ❌→✅ | Was 404, now created |

**Files Created:**
- `apps/web/app/about/page.tsx` - About page with mission, research process, trust signals
- `apps/web/app/contact/page.tsx` - Contact page with form
- `apps/web/components/ContactForm.tsx` - Client component for contact form
- `apps/web/app/api/contact/route.ts` - Contact form API endpoint
- `supabase/migrations/029_contact_submissions.sql` - Database table for submissions

**About Page Sections:**
1. Our Mission - Help families plan ski trips
2. What We Do - Complete trip guides with costs, ages, tips
3. How We Research - AI-assisted with human review
4. Why Trust Snowthere - Honest, real numbers, global, parent-focused

**Contact Form Features:**
- Fields: name, email, subject (dropdown), message
- Subject options: resort question, suggestion, feedback, correction, general, other
- Rate limiting: 3 requests/minute per IP
- Input sanitization: HTML stripping, max length 5000 chars
- Stored in `contact_submissions` table with IP, user agent, referrer

**Deployment Required:**
- [ ] Commit and push to main (Vercel auto-deploy)
- [ ] Run migration 029_contact_submissions.sql via Supabase Dashboard

---

**Round 8: Quick Takes Redesign** ✅ COMPLETE
- Type: Content quality improvement
- Status: Complete - Editorial Verdict Model implemented
- Goal: Replace generic Quick Takes with specific, memorable, honest content

### Round 8: Quick Takes Redesign (Completed 2026-01-26)

**Problem Statement:**
Quick Takes were generic and formulaic. Many started with "Here's the thing about..." - violating our voice principles. Lacked specificity, honesty about downsides, and memorable details.

**Solution - Editorial Verdict Model:**
New 4-part structure replacing generic prompts:
1. **THE HOOK** (1 sentence) - Specific, memorable insight
2. **THE CONTEXT** (1-2 sentences) - Why this matters for YOUR family
3. **THE TENSION** (1-2 sentences) - What's the catch? Be honest.
4. **THE VERDICT** (1 sentence) - Clear recommendation

**Files Created:**
- `agents/shared/primitives/quick_take.py` (NEW):
  - `QuickTakeContext` dataclass - Input context with editorial fields
  - `QuickTakeResult` dataclass - Generated content with quality metrics
  - `generate_quick_take()` - Main generation function using Opus
  - `calculate_specificity_score()` - Measures how specific vs generic content is
  - `check_forbidden_phrases()` - Detects 31 banned phrases
  - `validate_quick_take()` - Quality gate enforcement
  - `FORBIDDEN_PHRASES` - List of 31 banned phrases

**Files Modified:**
- `agents/shared/primitives/intelligence.py`:
  - `extract_quick_take_context()` - Extract editorial inputs from research
  - `QuickTakeContextResult` dataclass - Editorial extraction results

- `agents/pipeline/runner.py`:
  - Added Stage 3.1: Quick Take Context Extraction
  - Added Stage 3.2: Quick Take Generation (Editorial Verdict Model)
  - Stage 3.3: Other Content Sections (unchanged)
  - Removed "quick_take" from generic sections loop

- `agents/shared/primitives/__init__.py`:
  - Added all Quick Take exports

**Quality Gates:**
| Gate | Threshold | Purpose |
|------|-----------|---------|
| Word count | 80-120 words | Concise but complete |
| Specificity score | > 0.6 | Specific beats generic |
| Forbidden phrases | 0 | No lazy writing |
| Perfect if conditions | >= 2 | Clear recommendations |
| Skip if conditions | >= 1 | Honest about downsides |

**Forbidden Phrases (31 total):**
- Generic openers: "here's the thing", "let's be real", "the truth is"
- Empty superlatives: "world-class", "stunning", "amazing", "incredible"
- Marketing speak: "hidden gem", "must-visit", "bucket list"
- Generic qualifiers: "perfect for families", "great for families"

**Specificity Scoring:**
Positive signals (increase score):
- Numbers (ages, percentages, costs, distances)
- Age references ("ages 5-10", "under 6")
- Comparisons ("half the cost of Aspen")
- Proper nouns (specific hotels, lifts, restaurants)

Negative signals (decrease score):
- Generic adjectives (great, nice, beautiful)
- Vague quantifiers (many, various, several)
- Hedge words (might, could, perhaps)

**Pipeline Cost:**
- Quick Take context extraction: ~$0.01 (Sonnet)
- Quick Take generation: ~$0.10 (Opus)
- Total additional cost per resort: ~$0.11

**Key Files:**
- `agents/shared/primitives/quick_take.py` - Core primitive
- `agents/shared/primitives/intelligence.py` - Context extraction
- `agents/pipeline/runner.py` - Pipeline integration

---

**Round 7: External Linking & Affiliate System** ✅ COMPLETE (except manual R7.2)
- Type: Strategic implementation
- Status: R7.1 + R7.3 + R7.4 complete, pending manual affiliate signup
- Goal: External linking via Google Places, affiliate URL integration, link click tracking

### Round 7.1: External Linking Infrastructure (Completed 2026-01-26)

**Problem Statement:**
Content mentions hotels, restaurants, ski schools - but no clickable links. Missing:
- User value (quick access to booking, maps)
- SEO signals (outbound links show authority)
- Revenue opportunity (affiliate links)

**Migrations Created:**
- `027_entity_link_cache.sql` - Cache for Google Places API lookups
  - Stores place_id (indefinite TTL), resolved names, direct URLs, maps URLs
  - Entity types: hotel, restaurant, ski_school, rental, activity, grocery
  - Unique constraint on (name_normalized, entity_type, location_context)
- `028_affiliate_config.sql` - Affiliate program configuration
  - Stores program settings: url_template, affiliate_id, tracking_param, domains
  - Seeded with Booking.com, Ski.com, Liftopia placeholders
  - `link_click_log` table for analytics

**Primitives Created:**
- `agents/shared/primitives/external_links.py` (NEW):
  - `resolve_google_place()` - Resolve entity to Google Places data
  - `lookup_affiliate_url()` - Transform direct URL to affiliate URL
  - `resolve_entity_link()` - Main entry point combining Places + affiliate
  - `log_link_click()` - Track outbound clicks
  - `get_click_stats()` - Analytics queries
  - `get_rel_attribute()` - SEO-correct rel values (sponsored, nofollow)
  - `clear_expired_cache()` - Maintenance

- `agents/shared/primitives/intelligence.py` (MODIFIED):
  - `extract_linkable_entities()` - Find hotels, restaurants, etc. in content
  - `ExtractedEntity` dataclass with name, type, context_snippet, confidence
  - `EntityExtractionResult` dataclass

**Exports Added:**
- `agents/shared/primitives/__init__.py` updated with all new exports

**Next Steps (R7.2-R7.4):**
- Apply to affiliate programs (Booking.com, Ski.com, Liftopia) - manual process
- Add GOOGLE_PLACES_API_KEY to Railway environment
- Integrate entity link injection into pipeline Stage 4.9
- Add outbound link click tracking via GA4 events

**Key Files:**
- `supabase/migrations/027_entity_link_cache.sql`
- `supabase/migrations/028_affiliate_config.sql`
- `agents/shared/primitives/external_links.py`
- `agents/shared/primitives/intelligence.py` (extract_linkable_entities)
- `agents/shared/primitives/__init__.py`

### Round 7.3: Pipeline Link Injection (Completed 2026-01-26)

**Problem Statement:**
R7.1 created the primitives for external link resolution, but they weren't integrated into the autonomous pipeline. Hotel/restaurant mentions in content remained unlinked.

**Solution:**
Integrated external link injection as Stage 4.9 in the pipeline runner, processing content sections to automatically inject Google Places / affiliate links.

**Primitives Created:**
- `agents/shared/primitives/external_links.py` (MODIFIED):
  - `InjectedLink` dataclass - Record of link injection
  - `LinkInjectionResult` dataclass - Result with modified content
  - `inject_external_links()` - Inject links into single section
  - `inject_links_in_content_sections()` - Process all sections

**Pipeline Integration:**
- `agents/pipeline/runner.py` - Added Stage 4.9: External Link Injection
  - Processes sections in priority order: where_to_stay, on_mountain, off_mountain, etc.
  - Max 3 links per section to avoid over-linking
  - First mention only (SEO best practice)
  - Proper rel attributes: sponsored (affiliate), nofollow (maps)
  - Logs injection stats to audit log

**SEO Rules Enforced:**
- First mention only - no redundant links
- Affiliate links: `rel="sponsored noopener"`
- Google Maps links: `rel="nofollow noopener"`
- Other external: `rel="nofollow noopener noreferrer"`
- Content re-saved to database after injection

**Key Files:**
- `agents/shared/primitives/external_links.py` - inject_external_links(), inject_links_in_content_sections()
- `agents/pipeline/runner.py` - Stage 4.9 integration
- `agents/shared/primitives/__init__.py` - New exports

**Infrastructure Verified (2026-01-26):**
- GOOGLE_PLACES_API_KEY already configured in Railway
- Migrations 027/028 applied successfully
- affiliate_config seeded with Booking.com, Ski.com, Liftopia placeholders

**Next Steps (R7.2):**
- Apply to affiliate programs (Booking.com, Ski.com, Liftopia) - manual signup

### Round 7.4: GA4 Outbound Click Tracking (Completed 2026-01-26)

**Problem Statement:**
External links were being rendered and clicked, but no visibility into which links users actually engage with. Need analytics to understand link performance and affiliate revenue potential.

**Solution:**
Created analytics utility with GA4 event tracking, integrated into UsefulLinks component.

**Files Created:**
- `apps/web/lib/analytics.ts` (NEW):
  - `trackOutboundClick()` - Track external link clicks with category, affiliate status, resort context
  - `trackNewsletterSignup()` - Newsletter signup events
  - `trackQuizComplete()` - Quiz completion events
  - `trackResortView()` - Enhanced resort page views
  - Respects cookie consent (checks if gtag exists)
  - Uses `transport_type: 'beacon'` for reliable tracking on navigation

**Files Modified:**
- `apps/web/components/resort/UsefulLinks.tsx`:
  - Added onClick handler calling `trackOutboundClick()`
  - Tracks: url, linkText, category, isAffiliate, affiliateProgram, resortSlug

**GA4 Event Parameters:**
```javascript
{
  event_category: 'outbound',
  event_label: linkText,
  link_url: url,
  link_domain: 'extracted-from-url',
  link_category: 'lodging|dining|activity|etc',
  is_affiliate: true|false,
  affiliate_program: 'booking.com|ski.com|etc',
  resort_slug: 'zermatt|park-city|etc',
  transport_type: 'beacon'
}
```

**Key Files:**
- `apps/web/lib/analytics.ts` - Analytics utility
- `apps/web/components/resort/UsefulLinks.tsx` - Click tracking integration

**Round 7 Complete Tasks:**
- R7.1: External links infrastructure (migrations, primitives)
- R7.3: Pipeline link injection (Stage 4.9)
- R7.4: GA4 outbound click tracking

**Remaining:**
- R7.2: Manual affiliate program signups (Booking.com, Ski.com, Liftopia)

---

**Round 6: AI Discoverability & Infrastructure** ✅ COMPLETE
- Type: Strategic implementation
- Status: All tasks complete - email system fully operational
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

### Round 6.3: Lead Magnet & Welcome Sequence (Completed 2026-01-26)
- Created `agents/shared/primitives/email.py` with Resend API integration:
  - `send_email()` - Send via Resend API with tracking
  - `add_subscriber()` - Add to list with referral handling
  - `remove_subscriber()` - Soft delete/unsubscribe
  - `trigger_sequence()` - Start subscriber on sequence
  - `advance_sequences()` - Cron job to send due emails
  - `get_sequence_stats()` - Analytics for sequences
- Added `resend_api_key` to config.py settings
- Created 5 welcome email templates (HTML):
  - Day 0: Family Ski Trip Checklist
  - Day 2: Alps vs Colorado cost comparison
  - Day 4: Kids ages guide
  - Day 7: Epic vs Ikon simplified
  - Day 14: Ready to pick your resort
- Created `supabase/seed_email_sequences.sql` to seed templates and sequence
- Integrated `advance_sequences()` into daily cron.py

**Key Files Created**:
- `agents/shared/primitives/email.py` - Resend email primitives
- `agents/templates/welcome_checklist.html` - Day 0 checklist email
- `agents/templates/welcome_day2.html` - Alps vs Colorado
- `agents/templates/welcome_day4.html` - Kids ages
- `agents/templates/welcome_day7.html` - Epic vs Ikon
- `agents/templates/welcome_day14.html` - Ready to pick
- `supabase/seed_email_sequences.sql` - Welcome sequence seed data

### Round 6.5: Email System Deployment (Completed 2026-01-26)
- Ran migration 026_email_system.sql via Supabase Dashboard
- Ran seed_email_sequences.sql to create 5 templates + welcome sequence
- Added RESEND_API_KEY to Railway and Vercel environments
- Configured domain verification in Resend:
  - DKIM: TXT record `resend._domainkey` → verified
  - SPF: TXT record `send` → verified
  - MX: `send` → `feedback-smtp.us-east-1.amazonses.com` → verified
- snowthere.com is now fully verified in Resend for email sending
- Email system ready for production use (subscribers → welcome sequence → Resend delivery)

### Round 6.6: Email Compliance Fixes (Completed 2026-01-26)

**Critical Issues Found:**
1. Unsubscribe endpoint didn't exist (CAN-SPAM violation)
2. Template variables ({{name}}, {{email}}) weren't being substituted
3. Welcome sequence wasn't triggered on signup (delayed 24+ hours)
4. Email footers missing physical address (CAN-SPAM requirement)

**Fixes Implemented:**
- Created `/api/unsubscribe` endpoint (POST for unsubscribe, GET redirects to page)
- Created `/unsubscribe` page with confirmation UI
- Added `substitute_template_variables()` function to email.py
- Updated `advance_sequences()` to substitute variables before sending
- Updated `/api/subscribe` to trigger welcome sequence immediately
- Added physical address (2261 Market Street #5072, San Francisco, CA 94114) to all 5 email templates

**Key Files Created/Modified:**
- `apps/web/app/api/unsubscribe/route.ts` (NEW) - Unsubscribe API
- `apps/web/app/unsubscribe/page.tsx` (NEW) - Unsubscribe confirmation page
- `agents/shared/primitives/email.py` - Template variable substitution
- `apps/web/app/api/subscribe/route.ts` - Trigger welcome sequence
- `agents/templates/welcome_*.html` (5 files) - Physical address in footers

**Compliance Status:**
- ✅ Unsubscribe link works
- ✅ Physical address in every email
- ✅ Clear sender identity
- ✅ Template variables substituted
- ✅ Welcome sequence triggers immediately

**Future Work (Not Critical):**
- Resend webhooks for bounce/complaint tracking (when 1000+ subscribers)
- Batch sending optimization (when 500+ subscribers)

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
