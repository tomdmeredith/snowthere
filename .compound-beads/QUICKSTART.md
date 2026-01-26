# Snowthere Quick Start

**Round 6**: AI Discoverability & Infrastructure (in progress)
**Type**: Strategic implementation
**Status**: Round 6.1-6.4 complete, Round 7 next

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
- R6.3: Lead magnet complete - Resend primitives, 5 welcome emails, cron integration
- R6.4: Location display fix - added `extract_region()` primitive to populate region data

**Next**:
- R7: External Linking & Affiliate System
- Run migration 026 + seed via Supabase Dashboard
- Add RESEND_API_KEY to Railway and Vercel

**Migrations Pending**:
- `supabase/migrations/026_email_system.sql`
- `supabase/seed_email_sequences.sql`

**Key Files**:
- Strategic plan: `/.claude/plans/snuggly-herding-liskov.md`
- Email primitives: `agents/shared/primitives/email.py`
- Welcome templates: `agents/templates/welcome_*.html`

**Full context**: CLAUDE.md | .compound-beads/context.md
