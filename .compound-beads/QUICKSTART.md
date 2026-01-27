# Snowthere Quick Start

**Round 9**: Scoring Differentiation & Decimal Precision ✅ CODE COMPLETE
**Type**: Algorithm + Database + UX
**Status**: Code changes ready, migration + backfill pending deploy

**North Star**: "Snowthere is THE go-to source for high value, trusted information for family ski trips anywhere in the world"

**Guiding Principles**:
- Agent-native (atomic primitives, composable, full parity)
- Probabilistic for nuance, deterministic for correctness
- SEO/GEO optimized
- Autonomous operation

**Recent**:
- R9: **Scoring Differentiation & Decimal Precision** ✅ CODE COMPLETE
  - Changed scores from INTEGER to DECIMAL(3,1) for 90 discrete values
  - Created deterministic scoring formula (no LLM opinion)
  - Added diversity constraints to quiz (max 2 from same country)
  - UI shows decimal scores directly (8.2 not 8/10)
  - Created /methodology page for transparency
  - Backfill script ready (dry run shows 5.4-7.8 range)
- R8.3: **Quiz Comprehensive Audit + Region Backfill** ✅ DEPLOYED
- R8.2: **Email Confirmation + Migration** ✅ DEPLOYED
- R8.1: **Comprehensive Audit Fixes** ✅ DEPLOYED

**Deploy Steps**:
1. Run `supabase/migrations/030_decimal_scores.sql` in Supabase SQL editor
2. Run `cd agents && .venv/bin/python scripts/recalculate_scores.py --apply`

**Key Files**:
- Scoring formula: `agents/shared/primitives/scoring.py`
- Migration: `supabase/migrations/030_decimal_scores.sql`
- Backfill: `agents/scripts/recalculate_scores.py`
- Methodology: `apps/web/app/methodology/page.tsx`
- Quiz diversity: `apps/web/lib/quiz/scoring.ts`

**Next**:
- Deploy R9 migration + backfill
- R7.2: Apply to affiliate programs (Booking.com, Ski.com)
- Improve data quality for childcare/terrain fields

**Full context**: CLAUDE.md | .compound-beads/context.md
