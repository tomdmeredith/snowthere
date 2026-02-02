# Snowthere Context

> Last synced: 2026-02-02 (Linking Strategy Overhaul)
> Agent: compound-beads v2.1
> Session ID: (none — no active round)
> Sessions This Round: 0

## Current State

**All rounds through R16 + Linking Strategy Overhaul complete.** No active round. Site is live, pipeline is autonomous, data quality gates active.

- **Resorts:** 58 with entity links, pipeline adds ~6/day
- **Entity Links:** 371 in-content links across 58 resorts, 1,262 entity_link_cache entries
- **Guides:** 10 published (all with Nano Banana Pro featured images), autonomous generation Mon/Thu
- **Images:** Nano Banana Pro on Replicate is the default model (4-tier fallback); UGC photos now unblocked via Google Places API
- **Newsletter:** Weekly system deployed (Thursdays 6am PT)
- **SEO:** All pages have canonical tags, IndexNow verified, GSC API connected, JSON-LD on homepage + index pages
- **Rich Results:** WebSite + Organization schema (homepage), ItemList schema (/resorts, /guides)
- **Sitemap:** Image sitemap extension, 6 legal pages added
- **Indexing:** 4 indexed by Google (of 54 discovered), 7 pages manually requested for priority crawl
- **Scores:** Deterministic decimal (3.8-8.3 range, avg 5.4), completeness multiplier applied
- **Data Quality:** Backfill complete — 43% avg completeness, 7 resorts show full tables, 22 partial, 9 hidden
- **Linking:** Context-aware destinations (hotel→booking, restaurant→maps, ski_school→direct), UTMs on in-content links, rel allowlist validation
- **Google Places:** Both APIs enabled, correct API key deployed to Railway, type mapping fixed for API (New)

---

## Linking Strategy Overhaul (2026-02-02) ✅

**Goal:** Fix broken 3-layer linking system — context-aware entity link destinations, UTMs on in-content links, rel attribute preservation, full backfill across all published resorts.

### Phase 1: Fix Infrastructure — DEPLOYED
1. **Google Places API types fixed** — `grocery_or_supermarket` → `grocery_store`, `point_of_interest` → omit (Table B only), added `sporting_goods_store`, `tourist_attraction`, `transit_station`
2. **API key fallback** — Falls back to `settings.google_api_key` if `google_places_api_key` missing
3. **Error logging** — Response body logged on error, not just status code
4. **Entity type constraint expanded** — Migrations 037+038: added `airport`, `location`, `childcare`, `bar`, `cafe`, `spa`, `attraction`, `retail`, `transportation` to `entity_link_cache` CHECK constraint

### Phase 2: Context-Aware Link Destinations — DEPLOYED
5. **Data-driven priority table** — Replaced nested if/elif with `PRIORITY` dict per entity type:
   - Hotels/rentals → affiliate > direct > maps (parents want to book)
   - Restaurants/grocery → maps > direct (parents need directions)
   - Ski schools → direct > maps (parents want to register)
   - Activities/transport → direct > maps (booking or finding)
6. **UTMs on in-content links** — `utm_medium=in_content` distinct from sidebar's `resort_page`
7. **Dofollow for entity links** — `rel="noopener"` (sends referrer for partner attribution)
8. **Affiliate links** — `rel="sponsored noopener"` (Google-compliant)
9. **Maps links** — `rel="nofollow noopener"` (no equity, still sends referrer)

### Phase 3: Content Generation Improvements — DEPLOYED
10. **Enhanced section prompts** — Request named entities with `<strong>` tags for where_to_stay, on_mountain, off_mountain, getting_there
11. **Sidebar link curation** — Increased target from 3-8 to 8-15 links, minimums per category

### Phase 4: Frontend Polish — DEPLOYED
12. **sanitize.ts rel preservation** — Allowlist validation: only `noopener`, `noreferrer`, `nofollow`, `sponsored`, `ugc` tokens pass through
13. **html.escape defense-in-depth** — `html.escape(link_url, quote=True)` before href interpolation
14. **Parent-friendly labels** — "Where to Stay", "Ski Lessons", "Rent Gear", etc.
15. **Sidebar UsefulLinks** — Unified rel scheme matching entity links

### Phase 5: Backfill — COMPLETE
16. **New script** — `agents/scripts/backfill_links.py` with `--dry-run`, `--limit`, `--sidebar-only`, `--content-only`, `--resort` flags
17. **Results** — 371 entity links injected across 58 resorts, 1,262 entity_link_cache entries

### Phase 6: Expert Review — ALL PASS (2 rounds)
18. **Round 1** — Security Sentinel, Architecture Strategist, Code Simplicity, Data Integrity Guardian, Performance Oracle identified 6 findings
19. **Round 2** — All fixes applied, re-review: 5/5 PASS with no blocking findings

### Dead Code Removed
- `log_link_click()` (44 lines), `get_click_stats()` (53 lines), `clear_broken_link()` (19 lines), `get_broken_link_count()` (22 lines)
- Unused `hashlib` import, dead `skip_sections` set
- Dead exports removed from `__init__.py`
- Net: ~182 lines removed

### Files Modified
| File | Changes |
|------|---------|
| `agents/shared/primitives/external_links.py` | Context-aware destinations, UTMs, html.escape, dead code removal, type mapping |
| `agents/shared/primitives/__init__.py` | Removed dead exports |
| `agents/shared/primitives/content.py` | Enhanced section prompts requesting named entities |
| `agents/shared/primitives/intelligence.py` | Sidebar link curation 8-15 target |
| `agents/shared/primitives/links.py` | UTM campaign param fix |
| `agents/pipeline/runner.py` | Pass resort_slug to inject_links_in_content_sections |
| `apps/web/lib/sanitize.ts` | Rel allowlist validation, preserve existing tokens |
| `apps/web/components/resort/UsefulLinks.tsx` | Parent-friendly labels, unified rel |
| `supabase/migrations/037_expand_entity_types.sql` | Expand CHECK constraint |
| `supabase/migrations/038_add_retail_transportation_entity_types.sql` | Add retail + transportation |
| `agents/scripts/backfill_links.py` | **NEW** — backfill script |

### Key Commits
```
075f681 feat: Linking strategy overhaul — context-aware destinations, UTMs, rel preservation
32a855d fix: Use valid Places API (New) types for includedType parameter
18700fb fix: Expand entity_link_cache valid types + migration 037
1412d97 fix: Send referrer on all entity links for partner traffic attribution
ede019f refactor: Expert review fixes — html.escape, dead code removal, rel allowlist
```

### Verified on Live Site
- Zermatt page: entity links for Hotel Sonne, Hotel Astoria, Wolli Park, Chez Vrony, Coop, Skiguide Zermatt, etc.
- Sidebar links: UTM params visible in URLs
- rel attributes: correct per entity type (dofollow for entities, sponsored for affiliates)

**Arc:**
- Started believing: External linking is a flat priority chain — affiliate beats direct beats maps for everything
- Ended believing: Link destinations must match user intent by entity type — parents want to book hotels, get restaurant directions, register for ski school
- Transformation: From generic link injection to context-aware destinations that match what parents actually do with each entity type

---

## Round 16: Error Handling & Polish (2026-01-30) ✅

**Goal:** Improve resilience, edge-case handling, and interactive filtering. Comprehensive browser testing.

### Error Boundaries — DEPLOYED
1. **`error.tsx`** — Global error boundary with branded Spielplatz design, retry button, go-home fallback
2. **`not-found.tsx`** — Custom 404 page: "This trail doesn't exist" with Browse Resorts and Go Home buttons

### Loading Skeletons — DEPLOYED
3. **`resorts/loading.tsx`** — Breadcrumb, hero, filter bar, and card grid skeleton with `animate-pulse`
4. **`resorts/[country]/[slug]/loading.tsx`** — Resort detail page skeleton (hero image, content sections)
5. **`guides/[slug]/loading.tsx`** — Guide page skeleton (hero, content sections)

### Resort Filtering System — DEPLOYED
6. **`ResortFilters.tsx`** — Country pills, age group pills (0-3, 4-7, 8-12, 13+), budget pills ($-$$$$), sort options (Family Score, Price, A-Z)
7. **`ResortGrid.tsx`** — Country-grouped display (default) or flat list (when sorted by Price/A-Z), empty state with newsletter CTA
8. **`ResortCard.tsx`** — Card component with hero image, score badge, price badge ($/$$/$$$/$$$$), age range, region
9. **`SearchInput.tsx`** — Debounced (300ms) search input with URL sync, clear button
10. **`resort-filters.ts`** — Filter logic: URL search params ↔ filter state, country/age/budget/search matching
11. **`resorts/page.tsx`** — Updated to use filtering components, sticky filter bar with backdrop blur
12. **`resorts/[country]/page.tsx`** — Country-scoped filtering (no country pills, scoped search placeholder)

### GDPR Data Request — DEPLOYED (migration pending)
13. **`DataRequestForm.tsx`** — Email input + deletion/access toggle, loading/success/error states, GDPR copy
14. **`api/data-request/route.ts`** — POST endpoint with in-memory rate limiting (2/min/IP), email validation, Supabase insert
15. **`privacy/page.tsx`** — Updated with "Exercise Your Rights" section containing data request form
16. **Migration 036** — `data_requests` table with RLS, unique index per email/type/day

### CSP Headers — DEPLOYED
17. **`vercel.json`** — Tightened CSP: `img-src` now HTTPS-only, added `object-src 'none'`

### Comprehensive Browser Testing — ALL PASS
- **15 test categories** executed via Playwright browser MCP tools
- **3 customer walkthroughs**: First-time visitor, parent with toddlers, power user (direct URL)
- **Build verification**: `pnpm build` succeeded — 76 pages, 0 errors

### Blocked
- **Test 12.3 (GDPR form submission)**: Returns 500 because migration 036 not yet applied to cloud Supabase. Code is correct; needs `supabase db push` or SQL Editor apply.

**Files created:**
- `apps/web/app/error.tsx`, `apps/web/app/not-found.tsx`
- `apps/web/app/resorts/loading.tsx`, `apps/web/app/resorts/[country]/[slug]/loading.tsx`, `apps/web/app/guides/[slug]/loading.tsx`
- `apps/web/components/resort/ResortFilters.tsx`, `ResortGrid.tsx`, `ResortCard.tsx`, `SearchInput.tsx`
- `apps/web/lib/resort-filters.ts`
- `apps/web/components/DataRequestForm.tsx`, `apps/web/app/api/data-request/route.ts`
- `supabase/migrations/036_data_requests.sql`

**Arc:**
- Started believing: Error handling and polish is about adding safety nets around existing code
- Ended believing: Polish means building complete interactive experiences — filtering, loading, error recovery, and privacy rights are all user-facing quality
- Transformation: From defensive code additions to cohesive user experience where every state (loading, empty, error, filtered) is intentionally designed

---

## Round 15: GEO & Rich Results Enhancement + Data Quality Backfill (2026-01-30) ✅

**Goal:** Maximize AI citability and search rich results. Run data quality backfill.

### Schema & Sitemap — DEPLOYED
1. **WebSite JSON-LD** on homepage — includes SearchAction for sitelinks search box
2. **Organization JSON-LD** on homepage — name, URL, logo, founding date
3. **ItemList JSON-LD** on /resorts — dynamic list from published resorts with position, name, URL, tagline
4. **ItemList JSON-LD** on /guides — dynamic list from published guides with position, name, URL, excerpt
5. **Image sitemap extension** — `xmlns:image` namespace, `<image:image>` tags for all resort images
6. **Legal pages in sitemap** — /about, /methodology, /contact, /privacy, /terms, /quiz (monthly, priority 0.3)
7. **Guides revalidate** — Added `revalidate = 3600` (was missing)

### Data Quality Backfill — APPLIED
- **Migration 033 applied** via Supabase SQL Editor (`data_completeness` column + `NOTIFY pgrst, 'reload schema'`)
- **38 resorts processed**, 33 updated, 5 unchanged, 0 errors
- **Completeness: 30% → 43% average**
- **Full tables: 3 → 7 resorts** (Lake Louise, Cerro Catedral, Aspen Snowmass, Serfaus-Fiss-Ladis, Niseko, Killington, Lech-Zürs)
- **Hidden tables halved: 18 → 9 resorts**
- **Score range widened: 5.4-7.8 → 3.8-8.3** (better differentiation)
- **Tavily API key refreshed** (old key expired, new key in .env and ~/.api-keys)

### Cross-Resort Validation
- 20 cost outlier warnings (pre-existing data quality, not from backfill)
- US resorts with implausibly low lift prices (Deer Valley $37, Copper $29, Smugglers $27)
- Austrian resorts with high prices (likely EUR stored as USD without conversion)
- Grade: D (43% completeness + 20 warnings) — will improve as pipeline enriches data

### New Work Items Identified
- Update TAVILY_API_KEY on Railway (local updated, Railway still has old expired key)
- Fix cost data outliers (currency confusion, stale prices)
- 9 resorts at 0% completeness need targeted research (Selva Val Gardena, Cortina, Stowe, Deer Valley, Hakuba, Winter Park, Smugglers Notch)

**Key commit:** ee6b3ec

**Arc:**
- Started believing: Schema markup and data backfill are separate concerns
- Ended believing: They're complementary — schema makes data discoverable, backfill makes the data worth discovering
- Transformation: From adding metadata about content to ensuring the content behind the metadata is substantive

---

## Round 14: SEO & Schema Critical Fixes + Bug Fixes (2026-01-30) ✅

**Goal:** Fix everything broken or hurting search/social presence

### Fixes Applied — DEPLOYED
1. **Duplicate title suffix** — Removed `| Snowthere` from page-level titles on /resorts, /guides, /resorts/[country] (layout.tsx template already appends it)
2. **Quiz page** — Created layout.tsx with proper metadata + Footer component
3. **Unified footer** — All pages now use shared Footer component (replaced inline footer on resorts/country pages)
4. **Newsletter link** — CTA now points to `/#newsletter` (was `/`)
5. **Kitzbühel 404** — Unicode slug normalization fix: added `decodeURIComponent(slug).normalize('NFC')` to getResort()
6. **Kitzbühel duplicate** — Deleted archived record (4ce9f3b3), updated published slug to ASCII `kitzbuhel`

### Already Clean (no changes needed)
- AggregateRating: Not present in current code
- FAQ schema: Already server-rendered in page.tsx
- BreadcrumbList: Already present in page.tsx
- OG images: Using hero images (no broken /og/ route)

### Migration 035
- Applied via Supabase SQL Editor: Delete archived Kitzbühel + update published slug to ASCII

**Key commits:** cf167cd, a6a6b37, 3ef05c9, 71d7369

**Arc:**
- Started believing: The audit would find many broken things to fix
- Ended believing: Most schema items were already correct; the real bugs were Unicode normalization and template duplication
- Transformation: From expecting widespread schema gaps to discovering the codebase was healthier than the audit suggested

---

## Data Quality & Scoring Overhaul (2026-01-29) ✅

**Goal:** Fix false scoring defaults, add data completeness tracking, conditional table rendering, and publication quality gates

### Scoring Fixes
- **3 false defaults fixed** in `scoring.py`: `has_childcare`, `has_magic_carpet`, `has_ski_school` no longer default to `true` when data is missing (were inflating scores)
- **Completeness multiplier** added to formula: resorts with < 50% data completeness get penalized proportionally
- New primitive: `calculate_data_completeness()` with `KEY_COMPLETENESS_FIELDS` checklist

### Database
- **Migration 033:** Added `data_completeness` DECIMAL(4,3) column to `resort_family_metrics` (default 0.0)

### Frontend
- **FamilyMetricsTable + CostTable unhidden** with conditional rendering — only shown when `data_completeness >= 0.3`
- Data completeness < 0.6 shows disclaimer: "Some data is pending verification"

### Pipeline
- `data_completeness` stored after data extraction stage
- **Tiered publication gate:** completeness < 0.3 → draft only, 0.3-0.6 → publish with caveat, >= 0.6 → full publish
- **Dynamic quality queue:** low-completeness resorts re-queued for data enrichment

### MCP Server
- 3 new tools: `calculate_data_completeness`, `recalculate_family_score`, `audit_data_quality`

### Agent
- FamilyValue agent: data completeness check added to approval criteria

### New Files
- `agents/scripts/audit_data_quality.py` — audit current data quality across all resorts
- `agents/scripts/backfill_data_quality.py` — backfill completeness scores and recalculate family scores
- `agents/scripts/validate_cross_resort.py` — cross-resort consistency validation
- `agents/shared/calibration/golden_resorts.json` — reference data for calibration

**Arc:**
- Started believing: Scores just need the right formula
- Ended believing: Scores need the right formula AND awareness of how complete the underlying data is
- Transformation: From trusting all data equally to gating outputs by data quality

---

## Round 13.2: Google Places API Fix (2026-01-29) ✅

**Goal:** Investigate and fix Google Places API 400 errors blocking UGC photos and entity resolution

### Investigation Findings
- **Root cause:** The Snowthere Google Cloud project had **zero Maps/Places APIs enabled** and the `GOOGLE_PLACES_API_KEY` on Railway pointed to a key that didn't exist on the project
- **Two code paths affected:**
  - `ugc_photos.py` — Uses legacy Places API (`maps.googleapis.com/maps/api/place/...`) for UGC photo fetching
  - `external_links.py` — Uses Places API (New) (`places.googleapis.com/v1/places:searchText`) for entity resolution
- **Code was graceful:** Both paths silently skip when no valid key is available (print warning, return None)
- **Railway had 3 different Google keys:** `GOOGLE_API_KEY` (Gemini, from Tom Global project), `GOOGLE_PLACES_API_KEY` (invalid key), and the auto-generated Maps Platform key

### Fixes Applied — DEPLOYED

1. **Enabled Places API (legacy)** on Snowthere Google Cloud project (`places-backend.googleapis.com`)
2. **Enabled Places API (New)** on Snowthere Google Cloud project (`places.googleapis.com`)
3. **Auto-generated API key:** Google created "Maps Platform API Key" with 32 API restrictions
4. **Updated Railway env var:** `GOOGLE_PLACES_API_KEY` changed from invalid key to correct Snowthere project key (`AIzaSyCGIoU3XO17vcRfhep6UzcRQ9rsUih4_38`)
5. **Deployed** Railway service with updated variable

### Discovery
- The Snowthere project had 22 enabled APIs but zero were Maps/Places related
- There are multiple Google Cloud projects (Snowthere, Tom Global, Cold Email, etc.) — keys from other projects don't work
- The API key auto-restriction to "32 APIs" means all Maps Platform APIs are allowed by default
- `GOOGLE_API_KEY` on Railway (`AIzaSyC8mfREzkQL4MPMJDMgXNVjlaMJ2y1fFHM`) is from the Tom Global project — used for Gemini, separate concern

### Pending
- Restrict the API key to only Places API + Places API (New) for security (currently allows all 32 Maps APIs)

**Arc:**
- Started believing: The 400 errors were from a code bug or API quota issue
- Ended believing: The API wasn't enabled on the project and the key was from a non-existent credential
- Transformation: From debugging code to auditing cloud project configuration — infrastructure correctness strikes again

---

## Round 13.1: Technical SEO Audit & Indexing (2026-01-29) ✅

**Goal:** Investigate GSC/Bing indexing gaps, fix canonical tags, configure IndexNow, request priority indexing

### Investigation Findings
- **Google Search Console:** 4 indexed, 39 not indexed (37 "Discovered - currently not indexed")
- **Bing:** 0 indexed, sitemap accepted, IndexNow receiving pings
- **Root causes:** 3 fixable issues + normal new-site patience (site is 11 days old)

### Fixes Applied — DEPLOYED

1. **Canonical tags on 8 pages:** Homepage, /resorts, /guides, /about, /methodology, /contact, /privacy, /terms — all now have explicit `alternates.canonical` and `openGraph.url` via Next.js Metadata API
2. **IndexNow verification file:** Created `apps/web/public/fecbf60e758044b59c0e84c674c47765.txt`
3. **INDEXNOW_KEY Railway env var:** Updated from `snowthere8f4a2b1c9e7d3f5a` to `fecbf60e758044b59c0e84c674c47765` (matching verification file)
4. **ISR revalidation bug fix:** `26db039` — fixed Jan 28 pipeline failure, added /resorts revalidation on publish

### Manual Actions Completed (via Playwright)
5. **GSC priority indexing:** Requested indexing for 7 pages: /resorts/united-states, /resorts/canada, /resorts/canada/lake-louise, /resorts/switzerland/zermatt, /resorts/austria, /resorts/france, /resorts/switzerland
6. **GSC quota hit** on /resorts/japan — retry needed tomorrow
7. **Bing www property:** Confirmed already exists (both non-www and www properties)
8. **GSC API verified:** Service account `snowthere-gsc@snowthere.iam.gserviceaccount.com` has Full permission, JSON key active (Jan 27), Search Console API enabled with 1 successful request

### Discovery
- `/resorts/canada` was "URL is unknown to Google" — country listing pages may not all be in sitemap
- `/resorts` and `/guides` were already indexed (green checkmarks)
- GSC daily quota limits indexing requests to ~10/day

**Key commits:** `36fc555`, `26db039`

**Arc:**
- Started believing: Pages aren't indexed because the site is too new — just wait
- Ended believing: 3 real technical issues were blocking indexing alongside normal new-site patience
- Transformation: From assuming patience to systematic audit revealing fixable infrastructure gaps hidden behind normal new-site behavior

---

## Round 13: Delightful, On-Brand, Image-Rich Guide Pages (2026-01-28) ✅

**Goal:** Guide page design overhaul, Nano Banana Pro image generation, exit intent popup redesign

### Design Overhaul — DEPLOYED
- **HTML bug fixes:** `dangerouslySetInnerHTML` + `sanitizeHtml()` for list descriptions and FAQ answers
- **White card containers:** Content wrapped in `bg-white rounded-3xl shadow-lg` on gradient background
- **Section emojis:** Contextual emoji mapping by section type and title keywords
- **List item styling:** Color-coded number badges (coral odd, teal even), hover effects
- **Comparison tables:** Coral/teal gradient headers, alternating row tints
- **Callout section type:** Tip/warning/celebration variants with Spielplatz colors
- **Exit intent popup:** Full Spielplatz redesign — Fraunces headline, Caveat accent, floating snowflakes, playful CTA

### Nano Banana Pro Image Integration — DEPLOYED
- **Primary model:** `google/nano-banana-pro` on Replicate ($0.15/image, 2K resolution)
- **4-tier fallback chain:** Nano Banana Pro (Replicate) → Nano Banana Pro (Glif) → Gemini → Flux Schnell
- **All 11 guide images generated:** 11/11 success via Nano Banana Pro, stored in Supabase Storage
- **Permanent hosting:** Images downloaded from Replicate and re-uploaded to Supabase Storage (Replicate URLs are temporary)
- **Pipeline integrated:** `guide_orchestrator.py` uses `generate_image_with_fallback()` which now defaults to Nano Banana Pro

### Frontend Design Skill — INSTALLED
- `.claude/skills/frontend-design/SKILL.md` — combines Spielplatz design system with Anthropic frontend-design skill
- Ensures all future page work follows brand palette, typography, emoji conventions, and component patterns

**Key commits:** `b34fc48`, `900f0f4`

**Arc:**
- Started believing: Guide pages just needed images and a few bug fixes
- Ended believing: Brand personality requires systematic design overhaul AND reliable image infrastructure
- Transformation: From patching individual issues to establishing Spielplatz as a living design standard with autonomous image generation

---

## Round 12: Content Expansion & SEO Critical Fixes (2026-01-28) ✅

**Goal:** Olympics guides, guides workflow overhaul, canonical URL fixes, indexing

### SEO Critical Fixes — DEPLOYED
**Root cause:** `NEXT_PUBLIC_SITE_URL` on Vercel had a trailing newline, breaking every canonical URL, og:url, and sitemap entry. Combined with www vs non-www mismatch and homepage `force-dynamic`.

**Fixes applied:**
1. Created `apps/web/lib/constants.ts` — centralized `SITE_URL` with `.trim()` safety net
2. Updated 7 files to import from `lib/constants.ts` (replaced scattered `BASE_URL` definitions)
3. Added `metadataBase` to `layout.tsx` using centralized `SITE_URL`
4. Deleted duplicate `app/robots.txt/route.ts` (comprehensive `robots.ts` now serves)
5. Changed homepage from `force-dynamic` to `revalidate = 3600` (ISR)
6. Added homepage revalidation to publishing pipeline (`revalidate_page("/")`)
7. Updated Vercel env var: `https://snowthere.com` → `https://www.snowthere.com`

**Post-deploy verification (all passed):**
- Canonical URLs: `https://www.snowthere.com/...` — no newline, correct www
- Sitemap: All URLs use www domain, no `%0A` encoding
- Homepage: `x-vercel-cache: HIT` (was `private, no-cache, no-store`)
- robots.txt: Comprehensive version with AI crawler rules

**Manual actions completed:**
- Google Search Console: Sitemap resubmitted (54 pages discovered, up from 43)
- Google Search Console: Homepage indexing requested (priority crawl queue)
- Bing Webmaster Tools: Sitemap resubmitted (processing)

### Olympics Guides — 6 PUBLISHED
- `cortina-skiing-2026-olympics` — Can You Ski in Cortina During the 2026 Olympics?
- `milan-cortina-2026-family-guide` — Complete Family Guide
- `dolomites-family-resorts-olympics` — Best Dolomites Family Resorts
- `milan-to-cortina-with-kids` — Transportation Guide
- `olympics-italy-family-itinerary` — 5-Day Itinerary
- `cortina-family-budget-guide` — Budget-Friendly Guide

### Guides Workflow Overhaul — 3 TRACKS
- **Track A (SEO/GEO):** Schema.org JSON-LD (Article + FAQPage + BreadcrumbList), full metadata with OpenGraph/Twitter/canonical, `generateStaticParams()` + ISR, guide llms.txt endpoints, guides in sitemap
- **Track B (Quality):** Generalized `expert_panel.py` review primitive, expert approval loop with iteration
- **Track C (UX):** Fixed resort links in guide content, related guides section, breadcrumb navigation

### Railway Crash Fixes
- Fix #1: Exa API `type: 'neural'` → `type: 'auto'` (breaking API change) + GSC dependencies
- Fix #2: NameError in runner.py (`quick_take_context` → `qt_context_result`)

**Key commits:** `a1ac49b`, `e51bcf0`, `9b001fb`, `21198f6`, `fec6c6b`, `2255a5b`

**Arc:**
- Started believing: SEO is about content and Schema.org markup
- Ended believing: A single trailing newline in an env var can block all indexing
- Transformation: Infrastructure correctness is the foundation of discoverability

---

## Round 11: Autonomous Content Systems (2026-01-27) ✅

**Goal:** Weekly newsletter + autonomous guide generation

- Newsletter system: Migration 031, `newsletter.py`, cron integration (Thursdays 6am PT)
- Guide generation pipeline: `guide_orchestrator.py`, 3-agent approval, Mon/Thu schedule
- Exit intent popup: `ExitIntentPopup.tsx`, 7-day cooldown
- Site cleanup: Removed AI disclosure, added /methodology to footer, fixed decimal display

**Arc:** Autonomous content is just primitives composed differently on a cron schedule

---

## Round 10: Content Structure & Email Fix (2026-01-27) ✅

**Goal:** Guide pages + fix email system

- Built `/guides/[slug]` page template with GuideContent, GuideHero components
- Created `lib/guides.ts` with fetching utilities
- Loaded HTML templates into `email_templates` table
- Welcome sequence now sends properly

**Arc:** The JSONB content schema was already designed — just needed frontend rendering

---

## Round 9: Scoring & Pipeline Stability (2026-01-27) ✅

**Goal:** Deterministic decimal scores + pipeline crash fixes

- **R9:** DECIMAL(3,1) scores, deterministic formula in `scoring.py`, /methodology page, quiz diversity
- **R9.1:** Pipeline crash fix (perfect_if/skip_if schema mismatch + unidecode slugify)
- **R9.2:** Integrated scoring into pipeline, backfilled 5 resorts, improved data extraction prompts

**Score distribution:** 5.4-7.8 (was clustered at 7-9 integers). Lake Louise highest at 7.8.

**Arc:** Store atoms, compute molecules — deterministic formulas from data beat LLM opinion

---

## Rounds 6-8: Summary

**Round 8 — Quick Takes & Site Audit** (2026-01-26)
- Editorial Verdict Model: hook/context/tension/verdict structure
- 31 forbidden phrases, specificity scoring, quality gates
- Created About/Contact pages, fixed quiz match percentages
- Email confirmation on signup via Resend

**Round 7 — External Linking & Affiliate** (2026-01-26-27)
- Entity link cache (Google Places), affiliate config, pipeline link injection (Stage 4.9)
- GA4 outbound click tracking, 30+ affiliate programs researched
- Migration 032 created (pending manual network signups)

**Round 6 — AI Discoverability & Email** (2026-01-26)
- AI crawler whitelist in robots.ts (GPTBot, Claude-Web, PerplexityBot, etc.)
- Full email system: 7 tables, Resend integration, 5-email welcome sequence
- CAN-SPAM compliance: unsubscribe endpoint, physical address, template variables
- Region extraction for location display

---

## Rounds 1-5: Foundation (Summary)

| Round | Name | Key Outcome |
|-------|------|-------------|
| 1 | Foundation | Next.js 14, Supabase, 23 tables, design system |
| 2 | Core Agents | 63 primitives, autonomous pipeline, MCP server |
| 3 | Security Audit | XSS, GDPR, legal pages, security headers |
| 4 | Production Launch | Vercel + Railway + Supabase in production |
| 5 | Compliance & Polish | Alerts, WCAG 2.1 AA, CWV, internal linking, site stabilization |
| 5.1 | Agent-Native Scalability | Two-phase validation, 99% token reduction |
| 5.2 | Schema Contract Audit | sanitize_for_schema(), expanded cost columns |

---

## Infrastructure

| Service | Details |
|---------|---------|
| **Vercel** | www.snowthere.com, ISR, SPIELPLATZ design system |
| **Railway** | snowthere-agents (creative-spontaneity), daily cron (resorts + guides + newsletter) |
| **Supabase** | Snowthere, AWS us-east-2, 30+ tables |
| **Google Search Console** | sc-domain:snowthere.com, sitemap: 54 pages, GSC API connected |
| **Bing Webmaster Tools** | snowthere.com + www.snowthere.com verified, sitemap submitted, IndexNow active |
| **Google Analytics** | GA4, linked to GSC |
| **Google Cloud** | Project "Snowthere", Search Console API + Places API + Places API (New) enabled, Maps Platform API Key + service account |
| **Resend** | Email delivery, domain verified (DKIM + SPF + MX) |
| **IndexNow** | Verification key `fecbf60e758044b59c0e84c674c47765`, Railway env var configured |

## Pipeline Status

- **Resorts:** 8/day max, 70% discovery, deterministic scoring
- **Guides:** Mon/Thu, 3-agent approval panel, auto-publish, Nano Banana Pro featured images
- **Images:** Nano Banana Pro on Replicate (primary), 4-tier fallback, permanent Supabase Storage
- **Newsletter:** Thursday 6am PT, Morning Brew style
- **Email sequences:** 5-email welcome series (Day 0/2/4/7/14)

## Known Issues

- ~~Google Places API 400 errors (blocks UGC photos)~~ — **FIXED in R13.2** (APIs enabled, correct key deployed)
- ~~OG images return 404~~ — Resort pages now use hero images for OG (verified in code)
- ~~AggregateRating ratingCount: 1~~ — Removed in R14
- ~~FAQ schema client-rendered~~ — Server-side FAQPage JSON-LD added in R14 (already present in page.tsx)
- ~~BreadcrumbList missing on resort pages~~ — Added in R14 (already present in page.tsx)
- ~~Internal links open new tabs~~ — **FIXED** in sanitize.ts (internal links distinguished from external)
- ~~Entity links missing/broken~~ — **FIXED** in Linking Strategy Overhaul (371 links across 58 resorts, context-aware destinations)
- ~~sanitize.ts overwrites rel attributes~~ — **FIXED** with allowlist validation (noopener, noreferrer, nofollow, sponsored, ugc)
- ~~No UTMs on in-content links~~ — **FIXED** with utm_medium=in_content on entity links
- ~~Duplicate title suffix on index pages~~ — Fixed in R14
- ~~Quiz page missing footer~~ — Fixed in R14
- ~~Inconsistent footers~~ — Unified in R14
- ~~Kitzbühel 404~~ — Fixed in R14 (Unicode normalization + ASCII slug)
- **MCP parity at ~40%** — 58 of ~340 primitive functions exposed; 22 modules missing → R17
- **Runner monolith** — `run_resort_pipeline()` is 1,627 lines, no partial re-run → R18
- Quick Take length occasionally exceeds 120 word limit (minor)
- Quick Take score discrepancy — LLM-generated prose score may not match deterministic formula score (E1)
- Affiliate programs: migration 032 created but manual network signups pending
- ~30 pages still "Discovered - currently not indexed" in GSC (normal for new site, will resolve over 2-6 weeks)
- Google Places API key is unrestricted (allows all 32 Maps APIs) — should restrict to Places only
- ~~Data quality backfill not yet run~~ — **DONE in R15** (33/38 updated, 43% avg completeness)
- Cost data outliers: 20 warnings from cross-resort validation (US resorts with $27-37 lift prices, Austrian resorts with EUR-as-USD)
- 9 resorts at 0% completeness: Selva Val Gardena, Cortina, Stowe, Deer Valley, Hakuba, Winter Park, Smugglers Notch, Hakuba Valley, Cortina d'Ampezzo
- TAVILY_API_KEY on Railway needs updating (local .env updated, Railway still has expired key)
- Migration 036 (`data_requests` table) not yet applied to cloud Supabase — GDPR form returns 500

## Planned Rounds (Ultimate Audit — 2026-01-29)

Rounds 14-16 are user/SEO/GEO-facing. Rounds 17-18 are agent infrastructure.

### ~~Round 14: SEO & Schema Critical Fixes + Bug Fixes~~ ✅

Completed 2026-01-30. See R14 section above.

### ~~Round 15: GEO & Rich Results Enhancement + Data Quality Backfill~~ ✅

Completed 2026-01-30. See R15 section above.

### ~~Round 16: Error Handling & Polish~~ ✅

Completed 2026-01-30. See R16 section above.

- [x] Add custom error boundaries (error.tsx, not-found.tsx)
- [x] Add loading states (loading.tsx for resorts, resort detail, guide pages)
- [x] Add resort filtering system (country/age/budget/search/sort with URL state)
- [x] Tighten CSP (HTTPS-only img-src, object-src none)
- [x] Add GDPR data request form + API route + migration 036
- [x] Comprehensive browser testing (15 categories, 3 walkthroughs)
- [ ] Apply migration 036 to cloud Supabase (blocked — needs manual SQL Editor apply)
- [ ] Restrict Google Places API key (deferred)

### Round 17: Agent-Native Parity

**Goal:** Close the MCP parity gap (currently 58 tools from ~8 modules; 22 modules unexposed)

- [ ] Expose intelligence/scoring/approval/quality/image/trail_map/quick_take/discovery/newsletter/guide/email/analytics/alerts/costs/links primitives as MCP tools
- [ ] Add pipeline trigger MCP tool
- [ ] Add agent memory access MCP tools
- [ ] Update AGENT_NATIVE.md

**Files:** `agents/mcp_server/server.py`, `AGENT_NATIVE.md`

### Round 18: Pipeline Architecture

**Goal:** Decompose runner monolith, improve resilience and observability

- [ ] Decompose `run_resort_pipeline()` into individually-invocable stages
- [ ] Wire AgentTracer into pipeline
- [ ] Deterministic error dispatch for known error classes
- [ ] Add max-retry depth counter
- [ ] Remove dead code
- [ ] Fix budget context mismatch
- [ ] Wire HookRegistry into production pipeline

**Files:** `agents/pipeline/runner.py`, `agents/pipeline/decision_maker.py`, `agents/agent_layer/tracer.py`, `agents/agent_layer/hooks.py`

---

## Discovered Work

Items found mid-session that don't belong to the current round. Parked here to prevent scope creep.

_(none)_

---

## Open Questions

Unresolved questions needing human input. Carried across sessions until answered.

_(none)_

---

## Session Decisions

Key decisions made during the current session with rationale. Resets each session.

_(no active session)_

---

## Session History

Log of all sessions in the current round. Carries across sessions, resets each round.

_(no active round)_

---

## Pending Manual Work

- Sign up for affiliate networks (Travelpayouts, Awin, Impact, AvantLink, CJ, FlexOffers)
- Run migration 032_comprehensive_affiliate_programs.sql on production
- Request indexing for remaining GSC pages (daily quota, ~10/day)
- Monitor pipeline quality (guides Mon/Thu, newsletter Thursday)
- Apply migration 036 to cloud Supabase (data_requests table for GDPR form)
- Homepage redesign (moved to after R16)

## Key Files

| Category | Files |
|----------|-------|
| **Pipeline** | `agents/pipeline/runner.py`, `orchestrator.py`, `guide_orchestrator.py` |
| **Primitives** | `agents/shared/primitives/` (63+ atomic operations) |
| **Frontend** | `apps/web/app/resorts/[country]/[slug]/page.tsx`, `guides/[slug]/page.tsx` |
| **SEO** | `apps/web/lib/constants.ts`, `app/robots.ts`, `app/sitemap.xml/route.ts` |
| **IndexNow** | `apps/web/public/fecbf60e758044b59c0e84c674c47765.txt` |
| **Config** | `agents/shared/config.py`, `CLAUDE.md` |

## Recent Commits

```
ede019f refactor: Expert review fixes — html.escape, dead code removal, rel allowlist
1412d97 fix: Send referrer on all entity links for partner traffic attribution
18700fb fix: Expand entity_link_cache valid types + migration 037
32a855d fix: Use valid Places API (New) types for includedType parameter
075f681 feat: Linking strategy overhaul — context-aware destinations, UTMs, rel preservation
7047959 feat: Mobile filter collapse + Manus audit bug fixes
f55fb36 fix: Newsletter day-of-week bug + Railway project ref + R15/R16 catchup
ee6b3ec feat: R15 GEO & Rich Results — JSON-LD schemas, image sitemap, legal pages
```
