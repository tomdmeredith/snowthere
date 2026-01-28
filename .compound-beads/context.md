# Snowthere Context

> Last synced: 2026-01-28 (Round 13)
> Agent: compound-beads v2.0

## Current State

**All 13 rounds complete.** No active round. Site is live, pipeline is autonomous, all guides have Nano Banana Pro images.

- **Resorts:** 35+ published, pipeline adds ~6/day
- **Guides:** 10 published (all with Nano Banana Pro featured images), autonomous generation Mon/Thu
- **Images:** Nano Banana Pro on Replicate is the default model (4-tier fallback)
- **Newsletter:** Weekly system deployed (Thursdays 6am PT)
- **SEO:** Canonical URLs fixed, www domain, ISR caching, sitemaps resubmitted
- **Scores:** Deterministic decimal (5.4-7.8 range)

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
| **Railway** | creative-spontaneity, daily cron (resorts + guides + newsletter) |
| **Supabase** | Snowthere, AWS us-east-2, 30+ tables |
| **Google Search Console** | sc-domain:snowthere.com, sitemap: 54 pages |
| **Bing Webmaster Tools** | snowthere.com verified, sitemap submitted |
| **Google Analytics** | GA4, linked to GSC |
| **Resend** | Email delivery, domain verified (DKIM + SPF + MX) |

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

## Pending Manual Work

- Sign up for affiliate networks (Travelpayouts, Awin, Impact, AvantLink, CJ, FlexOffers)
- Run migration 032_comprehensive_affiliate_programs.sql on production
- Monitor first autonomous guide generation (Monday)
- Monitor first newsletter send (Thursday)

## Key Files

| Category | Files |
|----------|-------|
| **Pipeline** | `agents/pipeline/runner.py`, `orchestrator.py`, `guide_orchestrator.py` |
| **Primitives** | `agents/shared/primitives/` (63+ atomic operations) |
| **Frontend** | `apps/web/app/resorts/[country]/[slug]/page.tsx`, `guides/[slug]/page.tsx` |
| **SEO** | `apps/web/lib/constants.ts`, `app/robots.ts`, `app/sitemap.xml/route.ts` |
| **Config** | `agents/shared/config.py`, `CLAUDE.md` |
| **Plan** | `.claude/plans/snuggly-herding-liskov.md` |

## Recent Commits

```
900f0f4 feat: Nano Banana Pro as primary image model (4-tier fallback)
b34fc48 feat: Guides & non-resort content workflow overhaul (3 tracks)
a1ac49b fix: Centralize SITE_URL, fix canonical URLs, www domain, homepage caching
e51bcf0 feat: Guides & non-resort content workflow overhaul (3 tracks)
9b001fb feat: Expert panel review fixes + generalized review primitive
21198f6 feat: Add 6 Olympics guides for 2026 Milan-Cortina Winter Olympics
```
