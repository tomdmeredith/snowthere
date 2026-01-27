# Snowthere Quick Start

**Round 9.2**: Scoring Integration + Google Places API Fix
**Type**: Bug Fix (Scoring + API Integration)
**Status**: Scoring FIXED, Google Places needs investigation

**North Star**: "Snowthere is THE go-to source for high value, trusted information for family ski trips anywhere in the world"

**Guiding Principles**:
- Agent-native (atomic primitives, composable, full parity)
- Probabilistic for nuance, deterministic for correctness
- SEO/GEO optimized
- Autonomous operation

**Recent**:
- R9.2: **Scoring Integration + Data Quality** (Active)
  - ✅ FIXED: Pipeline now uses deterministic scoring formula
  - ✅ FIXED: 5 resorts backfilled (9.0→5.4, 8.0→5.7-6.2)
  - ANALYZED: No 8.x-9.x scores due to DATA SPARSITY (not formula)
  - PENDING: Improve data extraction prompts (Phase 1)
  - PENDING: Google Places API 400 errors (blocks UGC photos)
- R9.1: **Pipeline Crash Fix** ✅ DEPLOYED & VERIFIED (2026-01-27)
  - 5/5 resorts published, 0 failed
  - PGRST204 schema mismatch resolved
  - Duplicate detection working with unidecode
- R9: **Scoring Differentiation & Decimal Precision** ✅ DEPLOYED (2026-01-27)
  - Changed scores from INTEGER to DECIMAL(3,1) for 90 discrete values
  - Created deterministic scoring formula (no LLM opinion)
  - Added diversity constraints to quiz (max 2 from same country)
- R8.3: **Quiz Comprehensive Audit + Region Backfill** ✅ DEPLOYED

**Pipeline Status (2026-01-27 10:45 PST)**:
- Published: 5 (Selva Val Gardena, Val Thorens, Heavenly, Sun Valley, Jackson Hole)
- Drafts: 0
- Failed: 0

**Known Issues**:
- Google Places API returning 400 errors (blocks UGC photos)
- Quick Take length sometimes exceeds 120 word limit (minor)
- Published resorts queued for price verification (by design)

**Key Files (R9.2)**:
- Scoring fix: `agents/pipeline/runner.py` (line ~830, calls calculate_family_score)
- Backfill script: `agents/scripts/recalculate_scores.py`
- Google Places calls: `agents/shared/primitives/research.py` (needs investigation)

**Next**:
- Investigate Google Places API 400 errors
- Fix API request format if needed
- R7.2: Apply to affiliate programs (Booking.com, Ski.com)

**Full context**: CLAUDE.md | .compound-beads/context.md
