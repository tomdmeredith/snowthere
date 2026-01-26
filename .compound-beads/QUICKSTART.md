# Snowthere Quick Start

**Round 8**: Quick Takes Redesign ✅ COMPLETE
**Type**: Content quality improvement
**Status**: Editorial Verdict Model for Quick Takes, forbidden phrase detection, specificity scoring

**North Star**: "Snowthere is THE go-to source for high value, trusted information for family ski trips anywhere in the world"

**Guiding Principles**:
- Agent-native (atomic primitives, composable, full parity)
- Probabilistic for nuance, deterministic for correctness
- SEO/GEO optimized
- Autonomous operation

**Recent**:
- R7.4: **GA4 click tracking** - `lib/analytics.ts`, `trackOutboundClick()` in UsefulLinks
- R8: **Quick Take redesign** - Editorial Verdict Model replaces generic prompts
  - New primitive: `quick_take.py` with `generate_quick_take()`, `calculate_specificity_score()`
  - Context extraction: `extract_quick_take_context()` in intelligence.py
  - Quality gates: Word count (80-120), specificity > 0.6, no forbidden phrases
  - Forbidden phrases: 31 phrases detected and blocked (e.g., "Here's the thing", "amazing")
  - Pipeline integration: Stage 3.1-3.3 in runner.py

**Next**:
- R7.2: Apply to affiliate programs (Booking.com, Ski.com, Liftopia) - manual signup
- R9: ChatGPT GPT & API - Family Ski Trip Planner custom GPT

**Key Files**:
- Quick Take primitive: `agents/shared/primitives/quick_take.py`
- Context extraction: `agents/shared/primitives/intelligence.py` (extract_quick_take_context)
- Pipeline: `agents/pipeline/runner.py` (Stages 3.1-3.3)
- Strategic plan: `/.claude/plans/snuggly-herding-liskov.md`

**Full context**: CLAUDE.md | .compound-beads/context.md
