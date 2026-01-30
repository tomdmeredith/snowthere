# Snowthere Quick Start

**All rounds through R16 complete.** No active round. Site is live, pipeline is autonomous, data quality gates active.

**North Star**: "Snowthere is THE go-to source for high value, trusted information for family ski trips anywhere in the world"

**Guiding Principles**:
- Agent-native (atomic primitives, composable, full parity)
- Store atoms, compute molecules (deterministic formulas from data)
- SEO/GEO optimized (Schema.org, llms.txt, AI crawler whitelist)
- Autonomous operation (daily cron: resorts + guides + newsletter)

**Intelligence Summary**:
- **Working well**: Autonomous pipeline (resorts + guides + newsletter), deterministic scoring, 4-tier image fallback, ISR revalidation
- **Needs attention**: 9 resorts at 0% completeness, 20 cost data outliers, TAVILY_API_KEY expired on Railway, migration 036 not applied
- **Watch**: Google indexing pace (~30 pages still "Discovered"), affiliate program signups pending, Google Places API key unrestricted

**Recent**:
- **R16: Error Handling & Polish** (Completed 2026-01-30)
  - Custom error boundaries (error.tsx, not-found.tsx) — branded 404 and error pages
  - Loading skeletons for resorts, resort detail, and guide pages
  - Resort filtering system: country/age/budget pills, search input, URL-synced state, sort options
  - GDPR data request form on /privacy with API route + rate limiting + migration 036
  - CSP headers tightened in vercel.json (HTTPS-only img-src, object-src none)
  - Comprehensive browser testing: 15 categories, 3 customer walkthroughs, all pass
  - BLOCKED: migration 036 not yet applied to cloud Supabase (form returns 500)
- **R15: GEO & Rich Results Enhancement + Data Backfill** (Completed 2026-01-30)
  - WebSite + Organization JSON-LD on homepage (sitelinks search box)
  - ItemList JSON-LD on /resorts and /guides index pages
  - Image sitemap extension (xmlns:image) for all resort images
  - 6 legal/static pages added to sitemap
  - Migration 033 applied: data_completeness column
  - Data backfill: 33/38 resorts updated, completeness 30%→43%, 7 resorts show full tables
  - Tavily API key refreshed
- **R14: SEO & Schema Critical Fixes + Bug Fixes** (Completed 2026-01-30)
  - Fixed duplicate title suffix, quiz page footer/title, unified footer, newsletter link
  - Kitzbühel 404: Unicode slug normalization + ASCII migration (035)
  - Already clean: AggregateRating, FAQ schema, BreadcrumbList, OG images
- **Data Quality & Scoring Overhaul** (Completed 2026-01-29)
  - Scoring: 3 false defaults fixed, completeness multiplier added
  - New primitives: `calculate_data_completeness()`, `KEY_COMPLETENESS_FIELDS`
  - Migration 033: data_completeness column on resort_family_metrics
  - Frontend: FamilyMetricsTable + CostTable unhidden with conditional rendering (>= 0.3 completeness)
  - Pipeline: data_completeness stored after extraction, tiered publication gate, dynamic quality queue
  - MCP: 3 new tools (data completeness, family score, data quality audit)
  - FamilyValue agent: data completeness check in approval criteria
  - New scripts: audit_data_quality.py, backfill_data_quality.py, validate_cross_resort.py
  - New calibration file: agents/shared/calibration/golden_resorts.json
- R13.2: **Google Places API Fix** (Completed 2026-01-29)
  - Root cause: Places API + Places API (New) not enabled on Google Cloud project, wrong API key on Railway
  - Enabled both APIs on Snowthere Google Cloud project
  - Updated `GOOGLE_PLACES_API_KEY` on Railway with correct key from Snowthere project
- R13.1: **Technical SEO Audit & Indexing** (Completed 2026-01-29)
  - Canonical tags on 8 pages, IndexNow verified, ISR bug fix
  - GSC: 7 priority pages submitted for indexing
- R13: **Delightful, On-Brand, Image-Rich Guide Pages** (Completed 2026-01-28)
  - Nano Banana Pro on Replicate as primary image model (4-tier fallback)
  - Guide page Spielplatz design overhaul, exit intent popup redesigned

**Stats**: 43 resorts published, 10 guides published, scores 3.8-8.3 (avg 5.4)

**Pipeline**: Active on Railway (snowthere-agents / creative-spontaneity)
- Resorts: ~6/day, 70% discovery, deterministic scoring
- Guides: Mon/Thu, 3-agent expert panel, auto-publish, Nano Banana Pro images
- Newsletter: Thursday 6am PT
- Email sequences: 5-email welcome series

**Infrastructure**:
- Vercel: www.snowthere.com (ISR)
- Railway: snowthere-agents (daily cron)
- Supabase: Snowthere, AWS us-east-2, 30+ tables
- GSC: 54 pages discovered, 4 indexed, 7 priority requests submitted, GSC API active
- Bing: sitemap submitted, IndexNow verified
- Google Cloud: Project "Snowthere", Search Console API + Places API + Places API (New) enabled
- Google Places: API key configured on Railway, UGC photos + entity links unblocked

**Known Issues**:
- ~30 pages "Discovered - not indexed" (normal for 11-day-old site)
- Affiliate programs: migration 032 created, manual signups pending

**Planned Rounds** (from ultimate audit 2026-01-29):

- ~~R14: SEO & Schema Critical Fixes + Bug Fixes~~ ✅
- ~~R15: GEO & Rich Results Enhancement + Data Backfill~~ ✅
- ~~R16: Error Handling & Polish~~ ✅
- **R17: Agent-Native Parity** — Expose remaining primitive modules as MCP tools
- **R18: Pipeline Architecture** — Decompose runner monolith, wire AgentTracer

**Also pending**:
- Request indexing for remaining GSC pages (daily quota)
- Sign up for affiliate networks + run migration 032
- Restrict Google Places API key (currently unrestricted)
- Homepage redesign (moved to after R16)
- Update TAVILY_API_KEY on Railway (local .env updated, Railway still has old key)
- Fix 20 cost outlier warnings (US resorts with implausibly low lift prices, Austrian resorts with EUR prices stored as USD)
- 9 resorts still at 0% completeness (Selva Val Gardena, Cortina, Stowe, Hakuba, etc.) — need targeted research

**Full context**: CLAUDE.md | .compound-beads/context.md
