# Snowthere Quick Start

**R15 active: GEO & Rich Results Enhancement.** Site is live, pipeline is autonomous, data quality gates active.

**North Star**: "Snowthere is THE go-to source for high value, trusted information for family ski trips anywhere in the world"

**Guiding Principles**:
- Agent-native (atomic primitives, composable, full parity)
- Store atoms, compute molecules (deterministic formulas from data)
- SEO/GEO optimized (Schema.org, llms.txt, AI crawler whitelist)
- Autonomous operation (daily cron: resorts + guides + newsletter)

**Recent**:
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

**Stats**: 38 resorts published, 10 guides published, scores 5.4-7.8

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
- **R15: GEO & Rich Results Enhancement + Data Backfill** — WebSite/Organization schema, ItemList schema, data quality backfill, image sitemap, legal pages in sitemap (ACTIVE)
- **R16: Error Handling & Polish** — Custom error boundaries, loading states, CSP tightening, GDPR data deletion
- **R17: Agent-Native Parity** — Expose remaining primitive modules as MCP tools
- **R18: Pipeline Architecture** — Decompose runner monolith, wire AgentTracer

**Also pending**:
- Request indexing for remaining GSC pages (daily quota)
- Sign up for affiliate networks + run migration 032
- Restrict Google Places API key (currently unrestricted)
- Homepage redesign (moved to after R16)

**Full context**: CLAUDE.md | .compound-beads/context.md
