# Snowthere Quick Start

**Round 9**: Scoring Differentiation & Decimal Precision ✅ DEPLOYED
**Type**: Algorithm + Database + UX
**Status**: Live in production, all 30 resorts updated

**North Star**: "Snowthere is THE go-to source for high value, trusted information for family ski trips anywhere in the world"

**Guiding Principles**:
- Agent-native (atomic primitives, composable, full parity)
- Probabilistic for nuance, deterministic for correctness
- SEO/GEO optimized
- Autonomous operation

**Recent**:
- R9: **Scoring Differentiation & Decimal Precision** ✅ DEPLOYED (2026-01-27)
  - Changed scores from INTEGER to DECIMAL(3,1) for 90 discrete values
  - Created deterministic scoring formula (no LLM opinion)
  - Added diversity constraints to quiz (max 2 from same country)
  - UI shows decimal scores directly (6.3 not 6/10)
  - Created /methodology page for transparency
  - Backfill applied: 30 resorts updated, scores range 5.4-7.8
- R8.3: **Quiz Comprehensive Audit + Region Backfill** ✅ DEPLOYED
- R8.2: **Email Confirmation + Migration** ✅ DEPLOYED
- R8.1: **Comprehensive Audit Fixes** ✅ DEPLOYED

**Verified Working**:
- /methodology page explains scoring formula
- Quiz returns diverse results (max 2 per country)
- Decimal scores display on all resort pages
- Score distribution: 5.x (15), 6.x (13), 7.x (2)

**Key Files**:
- Scoring formula: `agents/shared/primitives/scoring.py`
- Migration: `supabase/migrations/030_decimal_scores.sql`
- Backfill: `agents/scripts/recalculate_scores.py`
- Methodology: `apps/web/app/methodology/page.tsx`
- Quiz diversity: `apps/web/lib/quiz/scoring.ts`

**Next**:
- R7.2: Apply to affiliate programs (Booking.com, Ski.com)
- Improve data quality for childcare/terrain fields
- Regenerate Quick Take content to match new scores

**Full context**: CLAUDE.md | .compound-beads/context.md
