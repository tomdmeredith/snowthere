# Snowthere Quick Start

**Round 7.4**: Outbound Link Click Tracking ✅ COMPLETE
**Type**: Analytics implementation
**Status**: GA4 event tracking for external links in UsefulLinks component

**North Star**: "Snowthere is THE go-to source for high value, trusted information for family ski trips anywhere in the world"

**Guiding Principles**:
- Agent-native (atomic primitives, composable, full parity)
- Probabilistic for nuance, deterministic for correctness
- SEO/GEO optimized
- Autonomous operation

**Recent**:
- R7.1: **External links infrastructure** - migrations 027/028, entity_link_cache, affiliate_config
- R7.3: **Link injection** - Pipeline Stage 4.9, `inject_external_links()` in external_links.py
- R7.3: **Verified** - GOOGLE_PLACES_API_KEY in Railway, migrations applied, affiliate_config seeded
- R7.4: **GA4 click tracking** - `lib/analytics.ts`, `trackOutboundClick()` in UsefulLinks

**Next**:
- R7.2: Apply to affiliate programs (Booking.com, Ski.com, Liftopia) - manual signup
- R8: Quick Takes Redesign - editorial verdict model

**Key Files**:
- Strategic plan: `/.claude/plans/snuggly-herding-liskov.md`
- Analytics utility: `apps/web/lib/analytics.ts`
- External links: `agents/shared/primitives/external_links.py`
- UsefulLinks: `apps/web/components/resort/UsefulLinks.tsx`

**Full context**: CLAUDE.md | .compound-beads/context.md
