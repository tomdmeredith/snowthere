# Snowthere Quick Start

**Round 9.1**: Pipeline Crash Fix ✅ READY TO DEPLOY
**Type**: Bug Fix (Storage + Duplicate Detection)
**Status**: Fixed locally, pending Railway deploy

**North Star**: "Snowthere is THE go-to source for high value, trusted information for family ski trips anywhere in the world"

**Guiding Principles**:
- Agent-native (atomic primitives, composable, full parity)
- Probabilistic for nuance, deterministic for correctness
- SEO/GEO optimized
- Autonomous operation

**Recent**:
- R9.1: **Pipeline Crash Fix** ✅ READY (2026-01-27)
  - Bug 1: `perfect_if`/`skip_if` written to wrong table (PGRST204 error)
  - Bug 2: `_slugify` didn't use unidecode (duplicate detection failed for Kitzbühel, Méribel)
  - Fixed: Added RESORT_CONTENT_COLUMNS whitelist to filter invalid columns
  - Fixed: `_slugify` now uses unidecode for consistent slug matching
  - Fixed: Route `perfect_if`/`skip_if` to `family_metrics` instead of `content`
- R9: **Scoring Differentiation & Decimal Precision** ✅ DEPLOYED (2026-01-27)
  - Changed scores from INTEGER to DECIMAL(3,1) for 90 discrete values
  - Created deterministic scoring formula (no LLM opinion)
  - Added diversity constraints to quiz (max 2 from same country)
  - Backfill applied: 30 resorts updated, scores range 5.4-7.8
- R8.3: **Quiz Comprehensive Audit + Region Backfill** ✅ DEPLOYED

**Verified Working (R9.1)**:
- `_slugify("Kitzbühel")` → "kitzbuhel" (correct transliteration)
- `check_resort_exists("Kitzbühel", "Austria")` finds existing resort
- `update_resort_content` filters out `perfect_if`/`skip_if` automatically
- All pipeline imports successful

**Key Files (R9.1)**:
- Whitelist fix: `agents/shared/primitives/database.py`
- Routing fix: `agents/pipeline/runner.py` (lines 644-656)

**Next**:
- Deploy to Railway (auto-deploys from main)
- Monitor next cron run for success
- R7.2: Apply to affiliate programs (Booking.com, Ski.com)

**Full context**: CLAUDE.md | .compound-beads/context.md
