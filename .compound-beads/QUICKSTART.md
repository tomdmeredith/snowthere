# Snowthere Quick Start

**All 13 rounds complete.** No active round. Site is live, pipeline is autonomous, all guides have Nano Banana Pro images.

**North Star**: "Snowthere is THE go-to source for high value, trusted information for family ski trips anywhere in the world"

**Guiding Principles**:
- Agent-native (atomic primitives, composable, full parity)
- Store atoms, compute molecules (deterministic formulas from data)
- SEO/GEO optimized (Schema.org, llms.txt, AI crawler whitelist)
- Autonomous operation (daily cron: resorts + guides + newsletter)

**Recent**:
- R13: **Delightful, On-Brand, Image-Rich Guide Pages** (Completed 2026-01-28)
  - Nano Banana Pro on Replicate as primary image model (4-tier fallback)
  - All 11 guide images generated, stored in Supabase Storage
  - Guide page Spielplatz design overhaul (white cards, emojis, styled tables/lists)
  - HTML rendering bug fixes (list descriptions + FAQ answers)
  - Exit intent popup redesigned with Spielplatz personality
  - Frontend design skill installed (`.claude/skills/frontend-design/`)
- R12: **Content Expansion & SEO Critical Fixes** (Completed 2026-01-28)
  - Centralized `SITE_URL` with `.trim()` safety net (`lib/constants.ts`)
  - Fixed canonical URLs, www domain, homepage ISR caching
  - 6 Olympics guides published (Milan-Cortina 2026)
  - Guides workflow overhaul: Schema.org JSON-LD, full metadata, ISR, sitemap
  - Generalized `expert_panel.py` review primitive
- R11: **Autonomous Content Systems** (Completed 2026-01-27)
  - Weekly newsletter (Thursday 6am PT, Morning Brew style)
  - Guide generation pipeline (Monday/Thursday)
  - Exit intent popup, site cleanup

**Stats**: 35+ resorts published, 10 guides published (all with Nano Banana Pro images), scores 5.4-7.8

**Pipeline**: Active on Railway (creative-spontaneity)
- Resorts: ~6/day, 70% discovery, deterministic scoring
- Guides: Mon/Thu, 3-agent expert panel, auto-publish, Nano Banana Pro images
- Images: Nano Banana Pro on Replicate (primary), 4-tier fallback, Supabase Storage
- Newsletter: Thursday 6am PT
- Email sequences: 5-email welcome series

**Infrastructure**:
- Vercel: www.snowthere.com (ISR)
- Railway: creative-spontaneity (daily cron)
- Supabase: Snowthere, AWS us-east-2, 30+ tables
- GSC: 54 pages discovered, sitemap resubmitted
- Bing: sitemap resubmitted (processing)

**Known Issues**:
- Google Places API 400 errors (blocks UGC photos)
- Quick Take length occasionally exceeds 120 word limit
- Affiliate programs: migration 032 created, manual signups pending

**Next**:
- Monitor autonomous guide + image generation (Mon/Thu pipeline)
- Monitor newsletter send (Thursday)
- Sign up for affiliate networks
- Run migration 032 on production
- Investigate Google Places API errors
- Homepage redesign (Round 6 in CLAUDE.md, not yet started)

**Full context**: CLAUDE.md | .compound-beads/context.md
