# Snowthere Quick Start

**All rounds through 13.2 complete.** No active round. Site is live, pipeline is autonomous, Google Places API fixed.

**North Star**: "Snowthere is THE go-to source for high value, trusted information for family ski trips anywhere in the world"

**Guiding Principles**:
- Agent-native (atomic primitives, composable, full parity)
- Store atoms, compute molecules (deterministic formulas from data)
- SEO/GEO optimized (Schema.org, llms.txt, AI crawler whitelist)
- Autonomous operation (daily cron: resorts + guides + newsletter)

**Recent**:
- R13.2: **Google Places API Fix** (Completed 2026-01-29)
  - Root cause: Places API + Places API (New) not enabled on Google Cloud project, wrong API key on Railway
  - Enabled both APIs on Snowthere Google Cloud project
  - Updated `GOOGLE_PLACES_API_KEY` on Railway with correct key from Snowthere project
  - UGC photos and entity resolution will work on next pipeline run
- R13.1: **Technical SEO Audit & Indexing** (Completed 2026-01-29)
  - Canonical tags on 8 pages, IndexNow verified, ISR bug fix
  - GSC: 7 priority pages submitted for indexing
- R13: **Delightful, On-Brand, Image-Rich Guide Pages** (Completed 2026-01-28)
  - Nano Banana Pro on Replicate as primary image model (4-tier fallback)
  - Guide page Spielplatz design overhaul, exit intent popup redesigned

**Stats**: 35+ resorts published, 10 guides published, scores 5.4-7.8

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

**Next**:
- Round 14: Homepage redesign
- Request indexing for remaining GSC pages (daily quota)
- Sign up for affiliate networks + run migration 032
- Restrict Google Places API key (currently unrestricted)

**Full context**: CLAUDE.md | .compound-beads/context.md
