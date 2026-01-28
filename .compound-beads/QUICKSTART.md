# Snowthere Quick Start

**Round 11**: Autonomous Content Systems
**Type**: Feature (Newsletter + Guide Generation)
**Status**: Infrastructure deployed, cron integration complete

**North Star**: "Snowthere is THE go-to source for high value, trusted information for family ski trips anywhere in the world"

**Guiding Principles**:
- Agent-native (atomic primitives, composable, full parity)
- Probabilistic for nuance, deterministic for correctness
- SEO/GEO optimized
- Autonomous operation

**Recent**:
- R11: **Autonomous Content Systems** (Active)
  - Weekly newsletter system (Thursday 6am PT, Morning Brew style)
  - Guide generation pipeline (Monday/Thursday, 2 guides/week)
  - Exit intent popup for newsletter signup
  - Migration 031_newsletter_recurring.sql applied to production
  - Removed AI disclosure references (cleaner messaging)
  - Added /methodology to footer navigation
- R10: **Content Structure + Email System Fix** (Completed)
  - Built guide page infrastructure (`/guides/[slug]`)
  - Email sequence templates loaded into database
- R9.2: **Scoring Integration** (Deployed)
  - Pipeline uses deterministic scoring formula
  - 5 resorts backfilled with new scores
  - Google Places API 400 errors still under investigation

**Pipeline Status**: Active on Railway (creative-spontaneity)
- Daily cron runs content generation
- Newsletter checks on Thursdays
- Guide generation on Mondays and Thursdays

**New Tables (Migration 031)**:
- `newsletter_issues` - Newsletter editions with content
- `newsletter_sections` - Individual sections per issue
- `newsletter_sends` - Per-subscriber send tracking

**Key Files (R11)**:
- Newsletter: `agents/shared/primitives/newsletter.py`
- Guides: `agents/shared/primitives/guides.py`, `agents/pipeline/guide_orchestrator.py`
- Cron: `agents/cron.py` (runs email, newsletter, guides)
- Exit intent: `apps/web/components/ExitIntentPopup.tsx`

**Known Issues**:
- Google Places API 400 errors (blocks UGC photos)
- Quick Take length sometimes exceeds 120 word limit (minor)

**Next**:
- Monitor first newsletter send (Thursday)
- Monitor first guide generation (Monday)
- Investigate Google Places API errors
- R7.2: Apply to affiliate programs

**Full context**: CLAUDE.md | .compound-beads/context.md
