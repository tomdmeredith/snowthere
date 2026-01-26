# Snowthere Quick Start

**Round 6**: AI Discoverability & Infrastructure (in progress)
**Type**: Strategic implementation
**Status**: Round 6.1 + 6.2 + 6.4 complete, starting 6.3

**North Star**: "Snowthere is THE go-to source for high value, trusted information for family ski trips anywhere in the world"

**Guiding Principles**:
- Agent-native (atomic primitives, composable, full parity)
- Probabilistic for nuance, deterministic for correctness
- SEO/GEO optimized
- Autonomous operation

**Recent**:
- R6.1: AI crawler access (OAI-SearchBot, Perplexity-User, Google-Extended, Meta-ExternalAgent, cohere-ai)
- R6.1: Per-resort llms.txt enhanced with "Citable Facts" and "Quick Answers"
- R6.2: Email system foundation - migration 026, /api/subscribe endpoint, Newsletter.tsx wired
- R6.4: Location display fix - added `extract_region()` primitive to populate region data
- Strategic plan: 9 rounds (6-14) covering email, external linking, Quick Takes redesign, GPT, content expansion, deals, newsletter

**Next**:
- R6.3: Lead magnet (Family Ski Checklist), Resend integration, welcome email sequence
- Run migration 026 via Supabase Dashboard

**Migration Pending**: `supabase/migrations/026_email_system.sql`

**Key Files**:
- Strategic plan: `/.claude/plans/snuggly-herding-liskov.md`
- robots.ts: AI crawlers
- llms.txt routes: GEO optimization
- intelligence.py: `extract_region()` primitive

**Full context**: CLAUDE.md | .compound-beads/context.md
