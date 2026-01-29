# Snowthere Context

> Last synced: 2026-01-29 (Round 13.1)
> Agent: compound-beads v2.0

## Current State

**All rounds through 13.1 complete.** No active round. Site is live, pipeline is autonomous, all guides have Nano Banana Pro images. Technical SEO audit complete — canonical tags on all pages, IndexNow verified, GSC API working.

- **Resorts:** 35+ published, pipeline adds ~6/day
- **Guides:** 10 published (all with Nano Banana Pro featured images), autonomous generation Mon/Thu
- **Images:** Nano Banana Pro on Replicate is the default model (4-tier fallback)
- **Newsletter:** Weekly system deployed (Thursdays 6am PT)
- **SEO:** All pages have canonical tags, IndexNow verified, GSC API connected, 7 priority pages submitted for indexing
- **Indexing:** 4 indexed by Google (of 54 discovered), 7 pages manually requested for priority crawl
- **Scores:** Deterministic decimal (5.4-7.8 range)

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
| **Google Cloud** | Project "Snowthere", Search Console API enabled, service account with JSON key |
| **Resend** | Email delivery, domain verified (DKIM + SPF + MX) |
| **IndexNow** | Verification key `fecbf60e758044b59c0e84c674c47765`, Railway env var configured |

## Pipeline Status

- **Resorts:** 8/day max, 70% discovery, deterministic scoring
- **Guides:** Mon/Thu, 3-agent approval panel, auto-publish, Nano Banana Pro featured images
- **Images:** Nano Banana Pro on Replicate (primary), 4-tier fallback, permanent Supabase Storage
- **Newsletter:** Thursday 6am PT, Morning Brew style
- **Email sequences:** 5-email welcome series (Day 0/2/4/7/14)

## Known Issues

- Google Places API 400 errors (blocks UGC photos) — needs investigation
- Quick Take length occasionally exceeds 120 word limit (minor)
- Affiliate programs: migration 032 created but manual network signups pending
- ~30 pages still "Discovered - currently not indexed" in GSC (normal for new site, will resolve over 2-6 weeks)
- GSC daily quota hit — /resorts/japan needs indexing request tomorrow

## Pending Manual Work

- Sign up for affiliate networks (Travelpayouts, Awin, Impact, AvantLink, CJ, FlexOffers)
- Run migration 032_comprehensive_affiliate_programs.sql on production
- Request indexing for remaining GSC pages (daily quota, ~10/day)
- Monitor pipeline quality (guides Mon/Thu, newsletter Thursday)

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
36fc555 fix: Add canonical tags to all pages + IndexNow verification key
26db039 fix: Add /resorts revalidation on publish + Jan 28 failure remediation
087acd4 docs: Close Round 13 — Compound Beads update + session handoff
900f0f4 feat: Nano Banana Pro as primary image model (4-tier fallback)
b34fc48 feat: Guides & non-resort content workflow overhaul (3 tracks)
a1ac49b fix: Centralize SITE_URL, fix canonical URLs, www domain, homepage caching
```
