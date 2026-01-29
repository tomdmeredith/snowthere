# Snowthere Quick Start

**All rounds through 13.1 complete.** No active round. Site is live, pipeline is autonomous, technical SEO audit complete.

**North Star**: "Snowthere is THE go-to source for high value, trusted information for family ski trips anywhere in the world"

**Guiding Principles**:
- Agent-native (atomic primitives, composable, full parity)
- Store atoms, compute molecules (deterministic formulas from data)
- SEO/GEO optimized (Schema.org, llms.txt, AI crawler whitelist)
- Autonomous operation (daily cron: resorts + guides + newsletter)

**Recent**:
- R13.1: **Technical SEO Audit & Indexing** (Completed 2026-01-29)
  - Canonical tags added to 8 pages (homepage, /resorts, /guides, /about, /methodology, /contact, /privacy, /terms)
  - IndexNow verification file + Railway env var updated to match
  - ISR revalidation bug fix for Jan 28 pipeline failure
  - GSC: 7 priority pages submitted for indexing (daily quota hit)
  - GSC API verified: service account with Full permission, JSON key active
  - Bing www property confirmed
- R13: **Delightful, On-Brand, Image-Rich Guide Pages** (Completed 2026-01-28)
  - Nano Banana Pro on Replicate as primary image model (4-tier fallback)
  - All 11 guide images generated, stored in Supabase Storage
  - Guide page Spielplatz design overhaul
  - Exit intent popup redesigned
- R12: **Content Expansion & SEO Critical Fixes** (Completed 2026-01-28)
  - Centralized `SITE_URL`, fixed canonical URLs, www domain, homepage ISR
  - 6 Olympics guides published, guides workflow overhaul

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
- Google Cloud: Project "Snowthere", Search Console API enabled

**Known Issues**:
- Google Places API 400 errors (blocks UGC photos)
- ~30 pages "Discovered - not indexed" (normal for 11-day-old site)
- Affiliate programs: migration 032 created, manual signups pending

**Next**:
- Round 14: Homepage redesign
- Request indexing for remaining GSC pages (daily quota)
- Sign up for affiliate networks + run migration 032
- Investigate Google Places API errors

**Full context**: CLAUDE.md | .compound-beads/context.md
